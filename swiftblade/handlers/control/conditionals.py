"""
Conditional Handler
Handles @if/@elseif/@else/@endif directives
Optimized with depth-aware parsing and control handler caching
"""

from typing import Dict, Any, List

from ..base import BaseHandler
from ...exceptions import TemplateSyntaxError
from ...constants import IF_PATTERN, ENDIF_PATTERN


class ConditionalHandler(BaseHandler):
    """Handles @if/@elseif/@else/@endif conditional structures (optimized)"""

    def __init__(self, engine):
        super().__init__(engine)
        self._ctrl_handler_cache = None  # Lazy-load control handler

    def _get_ctrl_handler(self):
        """Get cached control structure handler (lazy initialization)"""
        if self._ctrl_handler_cache is None:
            from . import ControlStructureHandler
            self._ctrl_handler_cache = ControlStructureHandler(self.engine)
        return self._ctrl_handler_cache

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
        """Process a single @if block with @elseif and @else (depth-aware)"""
        import re

        # Split into @if, @elseif, @else blocks with depth awareness
        parts = self._split_conditional_branches(body)

        # Get cached control handler
        ctrl_handler = self._get_ctrl_handler()

        # Evaluate @if condition
        try:
            if self.evaluator.safe_eval(condition.strip(), context):
                true_block = parts[0]['body'] if parts else ''
                # Need to recursively process for nested control structures
                return ctrl_handler.process(true_block, context)
        except (NameError, Exception) as e:
            # Check if it's an undefined variable error - treat as falsy
            if "is not defined" in str(e):
                pass  # Undefined variable, fall through to @else
            else:
                raise TemplateSyntaxError(f"Error in @if condition: {e}", context=condition.strip())

        # Check @elseif and @else
        for i in range(1, len(parts)):
            branch = parts[i]

            if branch['type'] == 'elseif':
                try:
                    if self.evaluator.safe_eval(branch['condition'].strip(), context):
                        return ctrl_handler.process(branch['body'], context)
                except Exception:
                    pass

            elif branch['type'] == 'else':
                return ctrl_handler.process(branch['body'], context)

        return ''

    def _split_conditional_branches(self, body: str) -> List[dict]:
        """
        Split body into conditional branches while respecting nested @if blocks.
        Returns list of dicts: [{'type': 'if'|'elseif'|'else', 'condition': str, 'body': str}]

        OPTIMIZED: Uses string slicing instead of character-by-character appending
        """
        branches = []
        body_start = 0  # Start position of current body segment
        depth = 0
        i = 0
        body_len = len(body)

        # First branch is the @if body (no directive)
        branches.append({'type': 'if', 'condition': '', 'body': ''})
        current_branch_idx = 0

        while i < body_len:
            # Check for nested @if
            if i + 4 <= body_len and body[i:i+4] == '@if(':
                depth += 1
                i += 4
                continue

            # Check for @endif
            if i + 6 <= body_len and body[i:i+6] == '@endif':
                if depth > 0:
                    depth -= 1
                    i += 6
                    continue

            # Only process @elseif/@else at depth 0 (not inside nested @if)
            if depth == 0:
                # Check for @elseif
                if i + 8 <= body_len and body[i:i+8] == '@elseif(':
                    # Save current branch body using string slice
                    branches[current_branch_idx]['body'] = body[body_start:i]

                    # Extract condition
                    paren_start = i + 7
                    condition = self._extract_balanced_parens(body, paren_start)

                    # Add new elseif branch
                    branches.append({'type': 'elseif', 'condition': condition, 'body': ''})
                    current_branch_idx += 1

                    # Move past @elseif(condition)
                    i = paren_start + len(condition) + 2  # +2 for ()
                    body_start = i
                    continue

                # Check for @else (but not @elseif)
                if i + 5 <= body_len and body[i:i+5] == '@else':
                    # Check it's not @elseif (already handled above)
                    if i + 6 > body_len or body[i+5] != 'i':
                        # Save current branch body using string slice
                        branches[current_branch_idx]['body'] = body[body_start:i]

                        # Add new else branch
                        branches.append({'type': 'else', 'condition': '', 'body': ''})
                        current_branch_idx += 1

                        i += 5
                        body_start = i
                        continue

            i += 1

        # Save final branch body using string slice
        branches[current_branch_idx]['body'] = body[body_start:]

        return branches

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
