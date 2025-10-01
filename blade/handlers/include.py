"""
Include Handler
Handles @include and @includeIf directives
"""

import os
from typing import Dict, Any

from .base import BaseHandler
from ..exceptions import TemplateNotFoundException, TemplateSyntaxError, SecurityError
from ..constants import INCLUDE_PATTERN, INCLUDE_IF_PATTERN


class IncludeHandler(BaseHandler):
    """Handles @include and @includeIf directives"""

    def process(self, template: str, context: Dict[str, Any], parser) -> str:
        """Process @include and @includeIf directives"""

        # Process @include
        def include_replacer(match):
            template_name = match.group(2)
            return self._get_included(template_name, context, parser)

        template = INCLUDE_PATTERN.sub(include_replacer, template)

        # Process @includeIf
        def include_if_replacer(match):
            template_name = match.group(2)
            condition = match.group(3).strip()

            try:
                if self.evaluator.safe_eval(condition, context):
                    return self._get_included(template_name, context, parser)
            except Exception as e:
                raise TemplateSyntaxError(f"Error in @includeIf condition: {e}", context=condition)

            return ''

        template = INCLUDE_IF_PATTERN.sub(include_if_replacer, template)

        return template

    def _get_included(self, template_name: str, context: Dict[str, Any], parser) -> str:
        """Load and process included template"""
        # Check recursion depth (DoS prevention)
        parser._recursion_depth += 1
        if parser._recursion_depth > self.engine.max_recursion_depth:
            parser._recursion_depth -= 1
            raise SecurityError(
                f"Maximum recursion depth exceeded: {parser._recursion_depth} (max: {self.engine.max_recursion_depth})",
                context=f"@include('{template_name}')"
            )

        try:
            # Use engine's template resolution to handle file extensions
            template_path = self.engine._resolve_template_path(template_name)

            if not os.path.exists(template_path):
                raise TemplateNotFoundException(f"Included template '{template_name}' not found", template_name=template_name)

            with open(template_path, "r", encoding=self.engine.encoding) as f:
                included_template = f.read()

            # Process included template
            return parser.process_template(included_template, context)
        finally:
            # Always decrement depth, even if error occurs
            parser._recursion_depth -= 1
