"""
Loop Handler
Handles @foreach and @for loop directives
"""

from typing import Dict, Any

from ..base import BaseHandler
from ...exceptions import TemplateSyntaxError, BreakLoop, ContinueLoop, SecurityError
from ...constants import ERROR_TEMPLATE_PREVIEW_LENGTH, FOREACH_PATTERN, FOR_PATTERN


class LoopHandler(BaseHandler):
    """Handles @foreach and @for loop structures"""

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process @foreach and @for loops"""
        # Process @foreach
        template = self._process_foreach(template, context)

        # Process @for
        template = self._process_for(template, context)

        return template

    def _find_matching_endforeach(self, template: str, start_pos: int) -> int:
        """Find the matching @endforeach for a @foreach at start_pos, accounting for nesting"""
        import re
        depth = 1
        pos = start_pos

        while depth > 0 and pos < len(template):
            # Find next @foreach or @endforeach
            next_foreach = template.find('@foreach', pos)
            next_endforeach = template.find('@endforeach', pos)

            if next_endforeach == -1:
                raise TemplateSyntaxError("Unmatched @foreach - missing @endforeach")

            if next_foreach != -1 and next_foreach < next_endforeach:
                depth += 1
                pos = next_foreach + 8  # len('@foreach')
            else:
                depth -= 1
                if depth == 0:
                    return next_endforeach
                pos = next_endforeach + 11  # len('@endforeach')

        raise TemplateSyntaxError("Unmatched @foreach - missing @endforeach")

    def _process_foreach(self, template: str, context: Dict[str, Any]) -> str:
        """Process @foreach...@endforeach recursively with proper nesting support"""
        import re

        # Find all @foreach occurrences
        foreach_pattern = re.compile(r'@foreach\s*\((.*?)\)')

        result = template
        offset = 0

        while True:
            match = foreach_pattern.search(result, offset)
            if not match:
                break

            loop_header = match.group(1).strip()
            start_pos = match.end()

            # Find matching @endforeach accounting for nesting
            end_pos = self._find_matching_endforeach(result, start_pos)
            loop_body = result[start_pos:end_pos]

            # Parse header: "item in items"
            try:
                loop_var, iterable_expr = loop_header.split(' in ', 1)
                loop_var = loop_var.strip()

                # Try to evaluate the iterable expression
                iterable = self.evaluator.safe_eval(iterable_expr.strip(), context)
            except Exception as e:
                raise TemplateSyntaxError(f"Error in @foreach header: {e}", context=loop_header)

            output = []
            local_context = context.copy()

            try:
                # Iteration limit (DoS prevention)
                iteration_count = 0
                for value in iterable:
                    if iteration_count >= self.engine.max_loop_iterations:
                        raise SecurityError(
                            f"Maximum loop iterations exceeded: {iteration_count} (max: {self.engine.max_loop_iterations})",
                            context=f"@foreach {loop_header}"
                        )

                    loop_context = local_context.copy()
                    loop_context[loop_var] = value

                    try:
                        # First, recursively process any nested @foreach loops with updated context
                        rendered = self._process_foreach(loop_body, loop_context)

                        # Then process conditionals (@if/@else/@endif) within the loop body
                        from .conditionals import ConditionalHandler
                        cond_handler = ConditionalHandler(self.engine)
                        rendered = cond_handler.process(rendered, loop_context)

                        # Finally process variables to render {{ item }} etc.
                        from ..variables import VariableHandler
                        var_handler = VariableHandler(self.engine)
                        rendered = var_handler.process(rendered, loop_context)
                        output.append(rendered)
                    except ContinueLoop:
                        pass
                    except BreakLoop:
                        break
                    finally:
                        iteration_count += 1

                replacement = ''.join(output)

                # Replace the entire @foreach...@endforeach block
                result = result[:match.start()] + replacement + result[end_pos + 11:]  # +11 for '@endforeach'
                offset = match.start() + len(replacement)

            except SecurityError:
                raise
            except Exception as e:
                raise TemplateSyntaxError(f"Error in @foreach loop: {e}")

        return result

    def _process_for(self, template: str, context: Dict[str, Any]) -> str:
        """Process @for...@endfor recursively"""
        def replacer(match):
            loop_header = match.group(1).strip()
            loop_body = match.group(2)

            # Parse header: "i in range(3)"
            try:
                loop_var, iterable_expr = loop_header.split(' in ', 1)
                loop_var = loop_var.strip()
                iterable = self.evaluator.safe_eval(iterable_expr.strip(), context)
            except Exception as e:
                raise TemplateSyntaxError(f"Error in @for header: {e}", context=loop_header)

            output = []
            local_context = context.copy()

            try:
                # Iteration limit (DoS prevention)
                iteration_count = 0
                for value in iterable:
                    if iteration_count >= self.engine.max_loop_iterations:
                        raise SecurityError(
                            f"Maximum loop iterations exceeded: {iteration_count} (max: {self.engine.max_loop_iterations})",
                            context=f"@for {loop_header}"
                        )

                    loop_context = local_context.copy()
                    loop_context[loop_var] = value

                    try:
                        # First, recursively process any nested @for loops with updated context
                        rendered = self._process_for(loop_body, loop_context)

                        # Then process conditionals (@if/@else/@endif) within the loop body
                        from .conditionals import ConditionalHandler
                        cond_handler = ConditionalHandler(self.engine)
                        rendered = cond_handler.process(rendered, loop_context)

                        # Finally process variables to render {{ item }} etc.
                        from ..variables import VariableHandler
                        var_handler = VariableHandler(self.engine)
                        rendered = var_handler.process(rendered, loop_context)
                        output.append(rendered)
                    except ContinueLoop:
                        pass
                    except BreakLoop:
                        break
                    finally:
                        iteration_count += 1

                return ''.join(output)
            except SecurityError:
                raise
            except Exception as e:
                raise TemplateSyntaxError(f"Error in @for loop: {e}")

        return FOR_PATTERN.sub(replacer, template)
