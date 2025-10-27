"""
Conditional Handler
Handles @if/@elseif/@else/@endif directives
"""

from typing import Dict, Any

from ..base import BaseHandler
from ...exceptions import TemplateSyntaxError
from ...constants import IF_PATTERN, ENDIF_PATTERN


class ConditionalHandler(BaseHandler):
    """Handles @if/@elseif/@else/@endif conditional structures"""

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process @if...@endif"""
        # Use a simpler pattern to find @if, then extract balanced parens
        result = template
        offset = 0

        while True:
            match = IF_PATTERN.search(result[offset:])
            if not match:
                break

            match_start = offset + match.start()
            paren_start = offset + match.end() - 1  # Position of '('

            # Extract balanced parentheses
            condition = self._extract_balanced_parens(result, paren_start)
            if not condition:
                offset = match_start + 1
                continue

            # Find the corresponding @endif
            body_start = paren_start + len(condition) + 2  # After )

            # Find matching @endif (accounting for nesting)
            depth = 1
            search_pos = body_start
            body_end = -1

            while depth > 0 and search_pos < len(result):
                # Check for nested @if
                nested_if = IF_PATTERN.search(result[search_pos:])
                endif_match = ENDIF_PATTERN.search(result[search_pos:])

                if endif_match and (not nested_if or endif_match.start() < nested_if.start()):
                    if depth == 1:
                        body_end = search_pos + endif_match.start()
                        break
                    depth -= 1
                    search_pos += endif_match.end()
                elif nested_if:
                    depth += 1
                    search_pos += nested_if.end()
                else:
                    break

            if body_end == -1:
                offset = match_start + 1
                continue

            body = result[body_start:body_end]

            # Process this @if block
            replacement = self._process_if_block(condition, body, context)
            endif_end = body_end + len('@endif')

            result = result[:match_start] + replacement + result[endif_end:]
            offset = match_start + len(replacement)

        return result

    def _process_if_block(self, condition: str, body: str, context: Dict[str, Any]) -> str:
        """Process a single @if block with @elseif and @else"""
        import re

        # Split into @if, @elseif, @else blocks
        parts = re.split(r'(@elseif\(.*?\)|@else)', body)

        # Evaluate @if condition
        try:
            if self.evaluator.safe_eval(condition.strip(), context):
                true_block = parts[0] if parts else ''
                # Need to recursively process for nested control structures
                from . import ControlStructureHandler
                ctrl_handler = ControlStructureHandler(self.engine)
                return ctrl_handler.process(true_block, context)
        except (NameError, Exception) as e:
            # Check if it's an undefined variable error - treat as falsy
            if "is not defined" in str(e):
                pass  # Undefined variable, fall through to @else
            else:
                raise TemplateSyntaxError(f"Error in @if condition: {e}", context=condition.strip())

        # Check @elseif and @else
        i = 1
        while i < len(parts):
            directive = parts[i]

            if directive.startswith('@elseif'):
                # Extract balanced parens for @elseif
                elseif_paren_pos = directive.find('(')
                if elseif_paren_pos != -1:
                    elseif_cond = self._extract_balanced_parens(directive, elseif_paren_pos)
                    if elseif_cond and i + 1 < len(parts):
                        try:
                            if self.evaluator.safe_eval(elseif_cond.strip(), context):
                                from . import ControlStructureHandler
                                ctrl_handler = ControlStructureHandler(self.engine)
                                return ctrl_handler.process(parts[i + 1], context)
                        except Exception:
                            pass
                i += 2

            elif directive == '@else':
                if i + 1 < len(parts):
                    from . import ControlStructureHandler
                    ctrl_handler = ControlStructureHandler(self.engine)
                    return ctrl_handler.process(parts[i + 1], context)
                break
            else:
                i += 1

        return ''

    def _extract_balanced_parens(self, text: str, start_pos: int) -> str:
        """Extract content within balanced parentheses starting from start_pos"""
        if start_pos >= len(text) or text[start_pos] != '(':
            return ''

        depth = 0
        result = []
        i = start_pos + 1  # Skip opening paren

        while i < len(text):
            char = text[i]
            if char == '(':
                depth += 1
                result.append(char)
            elif char == ')':
                if depth == 0:
                    return ''.join(result)
                depth -= 1
                result.append(char)
            else:
                result.append(char)
            i += 1

        return ''.join(result)
