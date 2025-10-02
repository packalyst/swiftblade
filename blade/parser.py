"""
Template Parser
Main template parser that orchestrates all handlers
"""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import BladeEngine

from .handlers import (
    ExtendsHandler,
    IncludeHandler,
    ControlStructureHandler,
    VariableHandler,
    XComponentHandler,
    StackHandler,
    PrependHandler,
    CustomDirectiveHandler
)


class TemplateParser:
    """Main template parser orchestrator"""

    def __init__(self, engine: 'BladeEngine'):
        self.engine = engine
        self.extends_handler = ExtendsHandler(engine)
        self.include_handler = IncludeHandler(engine)
        self.control_handler = ControlStructureHandler(engine)
        self.variable_handler = VariableHandler(engine)
        self.x_component_handler = XComponentHandler(engine)
        self.stack_handler = StackHandler()
        self.prepend_handler = PrependHandler(self.stack_handler)
        self.custom_directive_handler = CustomDirectiveHandler(engine)

        # Recursion depth tracking (DoS prevention)
        self._recursion_depth = 0

    def parse(self, template: str, context: Dict[str, Any]) -> str:
        """Parse template with all directives"""

        # 1. Process @extends first (loads parent template)
        template = self.extends_handler.process(template, context, self)

        # 2. Process remaining template
        template = self.process_template(template, context)

        return template

    def process_template(self, template: str, context: Dict[str, Any]) -> str:
        """Process template directives and variables"""

        # Process @push and @prepend first (collect stacks)
        template = self.stack_handler.process_push(template, context)
        template = self.prepend_handler.process(template, context)

        # Process X-components (modern syntax: <x-button>)
        template = self.x_component_handler.process(template, context, self)

        # Process @include
        template = self.include_handler.process(template, context, self)

        # Process custom directives (registered via engine.register_directive)
        template = self.custom_directive_handler.process(template, context)

        # Process control structures
        template = self.control_handler.process(template, context)

        # Process @stack (output collected stacks)
        template = self.stack_handler.process_stack(template, context, self)

        # Process variables last
        template = self.variable_handler.process(template, context)

        return template
