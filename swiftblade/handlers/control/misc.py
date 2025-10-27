"""
Misc Control Handler
Handles @isset, @empty, @python, and comment directives
"""

from typing import Dict, Any

from ..base import BaseHandler
from ...exceptions import SecurityError
from ...constants import COMMENT_PATTERN, PYTHON_PATTERN, ISSET_PATTERN, EMPTY_PATTERN


class MiscHandler(BaseHandler):
    """Handles miscellaneous control structures: @isset, @empty, @python, comments"""

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process miscellaneous control structures"""
        # Remove comments first
        template = self._process_comments(template)

        # Process @python blocks
        template = self._process_python(template, context)

        # Process @isset and @empty
        template = self._process_isset_empty(template, context)

        return template

    def _process_comments(self, template: str) -> str:
        """Remove {{-- comments --}}"""
        return COMMENT_PATTERN.sub('', template)

    def _process_python(self, template: str, context: Dict[str, Any]) -> str:
        """Process @python...@endpython blocks"""

        # Security check: Ensure @python blocks are explicitly enabled
        if '@python' in template and not self.engine.allow_python_blocks:
            raise SecurityError(
                "@python blocks are disabled for security. "
                "Set allow_python_blocks=True in BladeEngine() to enable (not recommended)."
            )

        def replacer(match):
            code = match.group(1)

            # Manual dedent: find common leading whitespace (ignoring first/last empty lines)
            lines = code.split('\n')

            # Remove completely empty first/last lines
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()

            if not lines:
                return ''

            # Find minimum indentation from non-empty lines
            min_indent = float('inf')
            for line in lines:
                if line.strip():  # Skip empty lines
                    stripped = line.lstrip()
                    indent = len(line) - len(stripped)
                    min_indent = min(min_indent, indent)

            # Remove min_indent from all lines
            if min_indent != float('inf') and min_indent > 0:
                dedented = []
                for line in lines:
                    if line.strip():
                        dedented.append(line[min_indent:])
                    else:
                        dedented.append('')
                code = '\n'.join(dedented)
            else:
                code = '\n'.join(lines)

            self.evaluator.safe_exec(code, context)
            return ''

        return PYTHON_PATTERN.sub(replacer, template)

    def _process_isset_empty(self, template: str, context: Dict[str, Any]) -> str:
        """Process @isset and @empty"""

        # @isset
        def isset_replacer(match):
            var_name = match.group(2).strip()
            body = match.group(3)
            if var_name in context and context[var_name] is not None:
                # Process the body
                from . import ControlStructureHandler
                ctrl_handler = ControlStructureHandler(self.engine)
                return ctrl_handler.process(body, context)
            return ''

        template = ISSET_PATTERN.sub(isset_replacer, template)

        # @empty
        def empty_replacer(match):
            var_name = match.group(2).strip()
            body = match.group(3)
            if not context.get(var_name):
                # Process the body
                from . import ControlStructureHandler
                ctrl_handler = ControlStructureHandler(self.engine)
                return ctrl_handler.process(body, context)
            return ''

        return EMPTY_PATTERN.sub(empty_replacer, template)
