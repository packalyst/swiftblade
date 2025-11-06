"""
Variable Handler
Handles {{ }} (escaped) and {!! !!} (raw) variable output
"""

import re
import keyword
from typing import Dict, Any

from .base import BaseHandler
from ..exceptions import SecurityError
from ..constants import ESCAPED_VAR_PATTERN, RAW_VAR_PATTERN


class VariableHandler(BaseHandler):
    """Handles {{ }} and {!! !!} variable output"""

    # Keywords that should NOT be translated (used as operators/syntax)
    OPERATOR_KEYWORDS = {
        'and', 'or', 'not',      # Boolean operators
        'in', 'is',              # Comparison operators
        'if', 'else',            # Ternary operator
        'True', 'False', 'None', # Literals
        'for',                   # List comprehension
        'lambda',                # Lambda expressions
    }

    # Pre-compiled regex patterns (class-level to avoid recompilation)
    _IDENTIFIER_PATTERN = re.compile(r'(?<![.\'\"])\b([a-zA-Z_]\w*)\b(?![.\'\"])')
    _SIMPLE_VAR_PATTERN = re.compile(r'^\$([a-zA-Z_]\w*)$')
    _DOLLAR_VAR_PATTERN = re.compile(r'\$([a-zA-Z_]\w*)')

    def _translate_reserved_keywords(self, expr: str, context: Dict[str, Any]) -> str:
        """
        Translate Python reserved keywords to context.get() calls

        Example:
            'class if class else ""'
            -> 'context.get("class","") if context.get("class","") else ""'
        """
        # Find all standalone identifiers that are reserved keywords
        def replace_keyword(match):
            word = match.group(0)
            # Only translate if it's a keyword AND not an operator AND exists in context
            if keyword.iskeyword(word) and word not in self.OPERATOR_KEYWORDS:
                # Use context.get() for safe access
                return f'context.get("{word}","")'
            return word

        # Use pre-compiled pattern
        return self._IDENTIFIER_PATTERN.sub(replace_keyword, expr)

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
            expr_clean = expr.strip()

            # Check if it's a simple $variable access for a reserved keyword
            simple_var_match = self._SIMPLE_VAR_PATTERN.match(expr_clean)
            if simple_var_match:
                var_name = simple_var_match.group(1)
                if keyword.iskeyword(var_name):
                    # Reserved keyword - use direct dict access
                    value = context.get(var_name, '')
                else:
                    # Normal variable - strip $ and eval
                    value = self.evaluator.safe_eval(var_name, context)
            else:
                # Complex expression - strip $ and translate reserved keywords
                if expr_clean.startswith('$'):
                    if len(expr_clean) > 1 and (expr_clean[1].isalpha() or expr_clean[1] == '_'):
                        expr_clean = self._DOLLAR_VAR_PATTERN.sub(r'\1', expr_clean)

                # Translate reserved keywords to context.get() calls
                # This allows expressions like: class if class else ''
                # To become: context.get('class','') if context.get('class','') else ''
                expr_clean = self._translate_reserved_keywords(expr_clean, context)

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
