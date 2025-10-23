"""
Custom Directive Handler
Handles custom directives registered via engine.register_directive()
"""

import re
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import BladeEngine

from .base import BaseHandler
from ..utils.safe_string import SafeString


class CustomDirectiveHandler(BaseHandler):
    """Handles custom directives registered by users"""

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process all registered custom directives"""

        # Get all registered directives from the engine
        registry = self.engine.directive_registry

        # Process each registered directive
        for directive_name in registry.directives.keys():
            template = self._process_directive(template, directive_name, context)

        return template

    def _process_directive(self, template: str, directive_name: str, context: Dict[str, Any]) -> str:
        """
        Process a single custom directive

        Supports both patterns:
        - @directiveName(args)  - with arguments
        - @directiveName        - without parentheses (calls with empty args)
        """
        # Pattern 1: @directiveName(...) - with parentheses
        pattern_with_parens = rf'@{directive_name}\s*\(((?:[^()]*|\([^)]*\))*)\)'

        # Pattern 2: @directiveName - without parentheses (must not be followed by '(')
        pattern_without_parens = rf'@{directive_name}(?!\s*\()'

        def replacer_with_args(match):
            """Replace directive with arguments"""
            args_str = match.group(1).strip()
            args = self._parse_args(args_str, context)

            try:
                result = self.engine.directive_registry.process(directive_name, args, context)
                return SafeString(str(result)) if result is not None else ''
            except Exception as e:
                print(f"Error in @{directive_name}: {e}")
                return match.group(0)

        def replacer_without_args(match):
            """Replace directive without arguments (call with empty args list)"""
            try:
                result = self.engine.directive_registry.process(directive_name, [], context)
                return SafeString(str(result)) if result is not None else ''
            except Exception as e:
                print(f"Error in @{directive_name}: {e}")
                return match.group(0)

        # First, replace directives WITH parentheses
        template = re.sub(pattern_with_parens, replacer_with_args, template)

        # Then, replace directives WITHOUT parentheses
        template = re.sub(pattern_without_parens, replacer_without_args, template)

        return template

    def _parse_args(self, args_str: str, context: Dict[str, Any]) -> list:
        """
        Parse directive arguments

        Example:
            'hello', 'world' -> ['hello', 'world']
            name, 24 -> [value_of_name, 24]
            'route', {'key': 'value'} -> ['route', {'key': 'value'}]
        """
        if not args_str:
            return []

        # Split by commas (but respect quotes, parentheses, and braces)
        args = []
        current_arg = ''
        paren_depth = 0
        brace_depth = 0
        bracket_depth = 0
        in_string = False
        string_char = None

        for char in args_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                current_arg += char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
                current_arg += char
            elif char == '(' and not in_string:
                paren_depth += 1
                current_arg += char
            elif char == ')' and not in_string:
                paren_depth -= 1
                current_arg += char
            elif char == '{' and not in_string:
                brace_depth += 1
                current_arg += char
            elif char == '}' and not in_string:
                brace_depth -= 1
                current_arg += char
            elif char == '[' and not in_string:
                bracket_depth += 1
                current_arg += char
            elif char == ']' and not in_string:
                bracket_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0 and brace_depth == 0 and bracket_depth == 0 and not in_string:
                if current_arg.strip():
                    args.append(current_arg.strip())
                current_arg = ''
            else:
                current_arg += char

        # Add last argument
        if current_arg.strip():
            args.append(current_arg.strip())

        # Evaluate each argument
        evaluated_args = []
        for arg in args:
            try:
                # Try to evaluate as expression
                value = self.evaluator.safe_eval(arg, context)
                evaluated_args.append(value)
            except:
                # If evaluation fails, use as string
                evaluated_args.append(arg)

        return evaluated_args
