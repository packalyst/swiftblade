"""
Extends Handler
Handles @extends, @section, and @yield directives for template inheritance
"""

import os
from typing import Dict, Any, Tuple

from .base import BaseHandler
from ..exceptions import TemplateNotFoundException
from ..constants import EXTENDS_PATTERN, SECTION_PATTERN, YIELD_PATTERN


class ExtendsHandler(BaseHandler):
    """Handles @extends and @section/@yield directives"""

    def process(self, template: str, context: Dict[str, Any], parser) -> str:
        """Process @extends directive"""
        match = EXTENDS_PATTERN.search(template)

        if not match:
            # No @extends, but clean up any standalone @yield directives with their defaults
            template = self._replace_yields(template, {}, context, parser)

            # Also remove any standalone @section directives that shouldn't be there
            template = SECTION_PATTERN.sub('', template)

            return template

        parent_name = match.group(2)
        # Use engine's template resolution to handle file extensions
        parent_path = self.engine._resolve_template_path(parent_name)

        if not os.path.exists(parent_path):
            raise TemplateNotFoundException(f"Parent template '{parent_name}' not found", template_name=parent_name)

        with open(parent_path, "r", encoding=self.engine.encoding) as f:
            parent_template = f.read()

        # Remove @extends from child
        template = EXTENDS_PATTERN.sub('', template)

        # Extract sections from child
        sections, remaining = self._extract_sections(template)

        # Add remaining content to default 'content' section
        if remaining.strip():
            sections.setdefault('content', '')
            sections['content'] += '\n' + remaining.strip()

        # Replace @yield in parent with child sections
        result = self._replace_yields(parent_template, sections, context, parser)

        return result

    def _extract_sections(self, template: str) -> Tuple[Dict[str, str], str]:
        """Extract @section directives"""
        sections = {}

        # Match both inline and block sections
        for match in SECTION_PATTERN.finditer(template):
            name = match.group('name').strip()
            content = match.group('inline') or match.group('block') or ''
            sections[name] = content.strip()

        # Remove all sections
        template = SECTION_PATTERN.sub('', template)

        return sections, template

    def _replace_yields(self, template: str, sections: Dict[str, str], context: Dict[str, Any], parser) -> str:
        """Replace @yield directives with section content"""
        def replacer(match):
            name = match.group(2).strip()
            default = match.group(3) or ''
            content = sections.get(name, default)

            if content:
                # Process the content for nested directives
                content = parser.process_template(content, context)

            return content

        return YIELD_PATTERN.sub(replacer, template)
