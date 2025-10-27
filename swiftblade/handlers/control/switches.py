"""
Switch Handler
Handles @switch/@case/@default directives
"""

from typing import Dict, Any

from ..base import BaseHandler
from ...exceptions import TemplateSyntaxError
from ...constants import SWITCH_PATTERN, CASE_PATTERN, DEFAULT_PATTERN, BREAK_PATTERN


class SwitchHandler(BaseHandler):
    """Handles @switch/@case/@default structures"""

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process @switch...@endswitch"""
        def replacer(match):
            switch_expr = match.group(1).strip()
            switch_body = match.group(2)

            try:
                switch_value = self.evaluator.safe_eval(switch_expr, context)
            except Exception as e:
                raise TemplateSyntaxError(f"Error in @switch expression: {e}", context=switch_expr)

            # Find matching case
            for case_match in CASE_PATTERN.finditer(switch_body):
                case_expr = case_match.group(1).strip()
                case_body = case_match.group(2)

                try:
                    case_value = self.evaluator.safe_eval(case_expr, context)
                except Exception:
                    continue

                if switch_value == case_value:
                    # Remove @break
                    case_body = BREAK_PATTERN.sub('', case_body)

                    # Process the case body
                    from . import ControlStructureHandler
                    ctrl_handler = ControlStructureHandler(self.engine)
                    return ctrl_handler.process(case_body, context)

            # Check @default
            default_match = DEFAULT_PATTERN.search(switch_body)
            if default_match:
                default_body = default_match.group(1)
                default_body = BREAK_PATTERN.sub('', default_body)

                # Process the default body
                from . import ControlStructureHandler
                ctrl_handler = ControlStructureHandler(self.engine)
                return ctrl_handler.process(default_body, context)

            return ''

        return SWITCH_PATTERN.sub(replacer, template)
