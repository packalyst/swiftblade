"""
X-Component Handler
Handles modern Laravel Blade X-component syntax (<x-button>, etc.)
"""

from typing import Dict, Any

from .base_component import ComponentBase
from ..constants import (
    MAX_COMPONENT_NESTING_ITERATIONS,
    COMPONENT_SUBDIR,
    X_COMPONENT_SELF_CLOSING_PATTERN,
    X_COMPONENT_PAIRED_PATTERN,
    X_COMPONENT_PAIRED_NESTED_PATTERN,
    X_PROPS_PATTERN,
    X_DYNAMIC_ATTR_PATTERN,
    X_STATIC_ATTR_PATTERN,
    X_BOOLEAN_ATTR_PATTERN,
    X_SLOT_COLON_PATTERN,
    X_SLOT_NAME_PATTERN,
    X_PROPS_DEF_PATTERN,
    X_PROPS_PAIR_PATTERN
)
from ..utils.safe_string import SafeString


class XComponentHandler(ComponentBase):
    """
    Handles modern Laravel Blade X-component syntax

    Modern component syntax:

    <x-button variant="primary" size="lg">
        Save
    </x-button>

    With dynamic attributes:
    <x-card :title="$pageTitle" :user="$currentUser">
        Content here
    </x-card>

    With named slots:
    <x-layout>
        <x-slot:header>
            Page Title
        </x-slot:header>

        Main content

        <x-slot:footer>
            Footer content
        </x-slot:footer>
    </x-layout>

    Component template (components/button.html):
    @props(['variant' => 'primary', 'size' => 'md', 'disabled' => false])

    <button class="btn-{{ $variant }} btn-{{ $size }}" {{ $disabled ? 'disabled' : '' }}>
        {{ $slot }}
    </button>
    """

    def process(self, template: str, context: Dict[str, Any], parser) -> str:
        """Process X-component tags (handles nesting)"""

        # Process components from innermost to outermost
        iteration = 0

        while '<x-' in template and iteration < MAX_COMPONENT_NESTING_ITERATIONS:
            iteration += 1

            # Find innermost component (self-closing or paired tag without nested x-components)
            # Try self-closing first: <x-button ... />
            match = X_COMPONENT_SELF_CLOSING_PATTERN.search(template)

            if match:
                component_name = match.group(1)
                attributes_str = match.group(2).strip()
                body = ''

                rendered = self._render_x_component(
                    component_name,
                    attributes_str,
                    body,
                    context,
                    parser
                )

                template = template[:match.start()] + rendered + template[match.end():]
                continue

            # Try paired tags: <x-button>...</x-button>
            # Find innermost (no nested <x- in body)
            match = X_COMPONENT_PAIRED_PATTERN.search(template)

            if not match:
                # Try matching any paired component (may have nesting)
                match = X_COMPONENT_PAIRED_NESTED_PATTERN.search(template)

            if not match:
                break

            component_name = match.group(1)
            attributes_str = match.group(2).strip()
            body = match.group(3)

            rendered = self._render_x_component(
                component_name,
                attributes_str,
                body,
                context,
                parser
            )

            template = template[:match.start()] + rendered + template[match.end():]

        return template

    def _render_x_component(
        self,
        component_name: str,
        attributes_str: str,
        body: str,
        context: Dict[str, Any],
        parser
    ) -> str:
        """Render an X-component"""

        # Use base class method for path resolution (includes validation)
        # X-components are in the COMPONENT_SUBDIR subdirectory
        component_path = self._resolve_component_path(component_name, subdir=COMPONENT_SUBDIR)

        # Use base class method to load template
        component_template = self._load_component_template(component_path)

        # Parse attributes
        attributes = self._parse_attributes(attributes_str, context)

        # Extract named slots from body
        slots = self._extract_x_slots(body, context, parser)

        # Default slot is remaining content (after removing named slots)
        default_slot = self._extract_default_x_slot(body)
        if default_slot.strip():
            # Mark as safe to prevent escaping when rendered
            slots['slot'] = SafeString(parser.process_template(default_slot, context))
        else:
            slots['slot'] = SafeString('')

        # Process @props directive in component template
        props_defaults = self._extract_props(component_template)

        # Merge contexts: defaults < attributes < slots
        component_data = {**props_defaults, **attributes}

        # Use base class method to merge contexts
        component_context = self._merge_component_context(context, component_data, slots)

        # Add $attributes for pass-through (attributes not in @props)
        pass_through = {k: v for k, v in attributes.items() if k not in props_defaults}
        # Mark as safe since it's already properly formatted HTML attributes
        component_context['attributes'] = SafeString(self._format_attributes(pass_through))

        # Remove @props directive from template
        component_template = X_PROPS_PATTERN.sub('', component_template)

        # Render component template
        return parser.process_template(component_template, component_context)

    def _parse_attributes(self, attributes_str: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse component attributes

        Static: variant="primary"
        Dynamic: :title="$pageTitle" or :title="some_var"
        Boolean: disabled (true if present)
        """
        attributes = {}

        if not attributes_str:
            return attributes

        # Pattern for attributes:
        # - :name="value" (dynamic - evaluate)
        # - name="value" (static string)
        # - name (boolean - true)

        # First, extract and remove dynamic attributes: :name="expression"
        # Remove dynamic attrs from string and process them
        remaining_str = attributes_str
        for match in X_DYNAMIC_ATTR_PATTERN.finditer(attributes_str):
            attr_name = match.group(1).replace('-', '_')
            expression = match.group(2)

            # Evaluate expression
            try:
                value = self.evaluator.safe_eval(expression, context)
                attributes[attr_name] = value
            except:
                # If evaluation fails, use as string
                attributes[attr_name] = expression

        # Remove all dynamic attributes from the string
        remaining_str = X_DYNAMIC_ATTR_PATTERN.sub('', remaining_str)

        # Static attributes: name="value"
        for match in X_STATIC_ATTR_PATTERN.finditer(remaining_str):
            attr_name = match.group(1).replace('-', '_')
            if attr_name not in attributes:
                attributes[attr_name] = match.group(2)

        # Remove static attributes
        remaining_str = X_STATIC_ATTR_PATTERN.sub('', remaining_str)

        # Find standalone words
        for match in X_BOOLEAN_ATTR_PATTERN.finditer(remaining_str):
            attr_name = match.group(1).replace('-', '_')
            if attr_name and attr_name not in attributes:
                attributes[attr_name] = True

        return attributes

    def _extract_props(self, component_template: str) -> Dict[str, Any]:
        """
        Extract @props defaults from component template

        @props(['variant' => 'primary', 'size' => 'md', 'disabled' => false])
        """
        props = {}

        # Find @props directive
        match = X_PROPS_DEF_PATTERN.search(component_template)

        if not match:
            return props

        props_str = match.group(1)

        # Parse key => value pairs
        # Support: 'key' => 'value', 'key' => 123, 'key' => false, etc.
        for pair_match in X_PROPS_PAIR_PATTERN.finditer(props_str):
            key = pair_match.group(1).strip()
            value_str = pair_match.group(2).strip()

            # Parse value
            value = self._parse_prop_value(value_str)
            props[key] = value

        return props

    def _parse_prop_value(self, value_str: str) -> Any:
        """Parse a prop default value"""
        value_str = value_str.strip()

        # String: 'value' or "value"
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]

        # Boolean
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False

        # Null
        if value_str.lower() in ('null', 'none'):
            return None

        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Default: return as string
        return value_str

    def _extract_x_slots(self, body: str, context: Dict[str, Any], parser) -> Dict[str, str]:
        """
        Extract named slots from X-component body

        <x-slot:header>Content</x-slot:header>
        or
        <x-slot name="header">Content</x-slot>
        """
        slots = {}

        # Pattern 1: <x-slot:name>...</x-slot:name>
        for match in X_SLOT_COLON_PATTERN.finditer(body):
            slot_name = match.group(1).replace('-', '_')
            slot_content = match.group(2)
            # Mark as safe to prevent escaping when rendered
            slots[slot_name] = SafeString(parser.process_template(slot_content, context))

        # Pattern 2: <x-slot name="name">...</x-slot>
        for match in X_SLOT_NAME_PATTERN.finditer(body):
            slot_name = match.group(1).replace('-', '_')
            slot_content = match.group(2)
            # Mark as safe to prevent escaping when rendered
            slots[slot_name] = SafeString(parser.process_template(slot_content, context))

        return slots

    def _extract_default_x_slot(self, body: str) -> str:
        """Extract default slot content (not in named slots)"""
        # Remove all named slots
        remaining = X_SLOT_COLON_PATTERN.sub('', body)
        remaining = X_SLOT_NAME_PATTERN.sub('', remaining)

        return remaining.strip()

    def _format_attributes(self, attributes: Dict[str, Any]) -> str:
        """Format attributes dict as HTML attribute string"""
        parts = []
        for key, value in attributes.items():
            html_key = key.replace('_', '-')
            if value is True:
                parts.append(html_key)
            elif value is False or value is None:
                continue
            else:
                # Escape quotes in value
                safe_value = str(value).replace('"', '&quot;')
                parts.append(f'{html_key}="{safe_value}"')

        return ' '.join(parts)
