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

    def _process_foreach(self, template: str, context: Dict[str, Any]) -> str:
        """Process @foreach...@endforeach"""
        def replacer(match):
            loop_header = match.group(1).strip()
            loop_body = match.group(2)

            # Parse header: "item in items"
            try:
                loop_var, iterable_expr = loop_header.split(' in ', 1)
                loop_var = loop_var.strip()
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
                        # Process control structures first
                        from . import ControlStructureHandler
                        ctrl_handler = ControlStructureHandler(self.engine)
                        rendered = ctrl_handler.process(loop_body, loop_context)

                        # Then process variables to render {{ item }} etc.
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
                raise TemplateSyntaxError(f"Error in @foreach loop: {e}")

        return FOREACH_PATTERN.sub(replacer, template)

    def _process_for(self, template: str, context: Dict[str, Any]) -> str:
        """Process @for...@endfor"""
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
                        # Process control structures first
                        from . import ControlStructureHandler
                        ctrl_handler = ControlStructureHandler(self.engine)
                        rendered = ctrl_handler.process(loop_body, loop_context)

                        # Then process variables to render {{ item }} etc.
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
