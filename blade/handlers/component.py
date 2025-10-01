"""
Component Handler
Handles legacy @component and @slot directives (Laravel Blade style)
"""

from typing import Dict, Any

from .base_component import ComponentBase
from ..exceptions import TemplateSyntaxError
from ..constants import (
    MAX_LEGACY_COMPONENT_ITERATIONS,
    COMPONENT_PATTERN,
    COMPONENT_NESTED_PATTERN,
    SLOT_PATTERN
)


class ComponentHandler(ComponentBase):
    """
    Handles @component and @slot directives

    Laravel Blade component syntax:

    @component('components.alert')
        @slot('title')
            Alert Title
        @endslot

        This is the alert message (default slot)
    @endcomponent

    Component template (components/alert.html):
    <div class="alert">
        <h4>{{ title }}</h4>
        <div>{{ slot }}</div>
    </div>
    """

    def process(self, template: str, context: Dict[str, Any], parser) -> str:
        """Process @component directives (handles nesting)"""

        # Process components from innermost to outermost to handle nesting
        iteration = 0

        while '@component' in template and iteration < MAX_LEGACY_COMPONENT_ITERATIONS:
            iteration += 1

            # Find innermost component (one without nested @component in its body)
            match = COMPONENT_PATTERN.search(template)
            if not match:
                # No more simple components, try to match any component
                match = COMPONENT_NESTED_PATTERN.search(template)

                if not match:
                    break

            component_name = match.group(2)
            component_data = match.group(3) or '{}'
            component_body = match.group(4)

            rendered = self._render_component(
                component_name,
                component_body,
                component_data,
                context,
                parser
            )

            # Replace this component in the template
            template = template[:match.start()] + rendered + template[match.end():]

        return template

    def _render_component(
        self,
        component_name: str,
        body: str,
        data_str: str,
        context: Dict[str, Any],
        parser
    ) -> str:
        """Render a component with slots"""

        # Use base class method for path resolution (includes validation)
        component_path = self._resolve_component_path(component_name, subdir=None)

        # Use base class method to load template
        component_template = self._load_component_template(component_path)

        # Extract slots from component body
        slots = self._extract_slots_generic(
            body,
            SLOT_PATTERN,
            context,
            parser,
            process_content=True
        )

        # Default slot is remaining content (after removing named slots)
        default_slot = self._extract_default_slot(body, SLOT_PATTERN)
        if default_slot.strip():
            slots['slot'] = parser.process_template(default_slot, context)

        # Parse component data if provided
        component_data = {}
        if data_str and data_str.strip() != '{}':
            try:
                data = self.evaluator.safe_eval(data_str, context)
                if isinstance(data, dict):
                    component_data = data
            except Exception as e:
                raise TemplateSyntaxError(f"Error in @component data: {e}", context=data_str)

        # Use base class method to merge contexts
        component_context = self._merge_component_context(context, component_data, slots)

        # Render component template
        return parser.process_template(component_template, component_context)
