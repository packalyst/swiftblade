"""
Variable Handler
Handles {{ }} (escaped) and {!! !!} (raw) variable output
"""

from typing import Dict, Any

from .base import BaseHandler
from ..exceptions import SecurityError
from ..constants import ESCAPED_VAR_PATTERN, RAW_VAR_PATTERN


class VariableHandler(BaseHandler):
    """Handles {{ }} and {!! !!} variable output"""

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process variable output"""

        # Process {{ }} for escaped output
        template = ESCAPED_VAR_PATTERN.sub(
            lambda m: self._output_variable(m.group(1), context, escape=True),
            template
        )

        # Process {!! !!} for raw output
        template = RAW_VAR_PATTERN.sub(
            lambda m: self._output_variable(m.group(1), context, escape=False),
            template
        )

        return template

    def _output_variable(self, expr: str, context: Dict[str, Any], escape: bool = True) -> str:
        """Evaluate and output variable"""
        try:
            # Laravel Blade uses $ prefix for variables, but Python doesn't support it
            # Strip leading $ from simple variable names (e.g., $slot -> slot)
            # But preserve $ in complex expressions (e.g., keep as-is if it's in a string)
            expr_clean = expr.strip()
            if expr_clean.startswith('$'):
                # Only strip $ from variable names, not from strings
                # Simple heuristic: if it starts with $ and next char is alphanumeric or underscore
                if len(expr_clean) > 1 and (expr_clean[1].isalpha() or expr_clean[1] == '_'):
                    # Replace leading $ only at word boundaries
                    import re
                    expr_clean = re.sub(r'\$([a-zA-Z_]\w*)', r'\1', expr_clean)

            value = self.evaluator.safe_eval(expr_clean, context)
            result = str(value) if value is not None else ''

            # Check if value is marked as safe (like slot content)
            from ..utils.safe_string import SafeString
            if isinstance(value, SafeString):
                # Don't escape safe strings (already processed HTML)
                return result

            if escape:
                # Basic HTML escaping
                result = result.replace('&', '&amp;')
                result = result.replace('<', '&lt;')
                result = result.replace('>', '&gt;')
                result = result.replace('"', '&quot;')
                result = result.replace("'", '&#x27;')

            return result
        except SecurityError:
            # ALWAYS raise security errors - they should never be silenced
            raise
        except Exception as e:
            # In strict mode, raise the error; otherwise return empty
            if getattr(self.engine, 'strict_mode', False):
                raise
            return ''
