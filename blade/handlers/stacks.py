"""
Stack Handlers
Handles @push/@stack/@prepend directives for asset stacking
"""

from typing import Dict, Any

from ..constants import PUSH_PATTERN, STACK_PATTERN, PREPEND_PATTERN


class StackHandler:
    """
    Handles @push/@stack directives for asset stacking

    @push('scripts')
        <script src="app.js"></script>
    @endpush

    @stack('scripts')  # Outputs all pushed content
    """

    def __init__(self):
        self.stacks: Dict[str, list] = {}

    def process_push(self, template: str, context: Dict[str, Any]) -> str:
        """Process @push directives and collect content"""
        def replacer(match):
            stack_name = match.group(2).strip()
            content = match.group(3).strip()

            # Add to stack
            if stack_name not in self.stacks:
                self.stacks[stack_name] = []
            self.stacks[stack_name].append(content)

            # Remove from template (content will be rendered at @stack location)
            return ''

        return PUSH_PATTERN.sub(replacer, template)

    def process_stack(self, template: str, context: Dict[str, Any], parser) -> str:
        """Process @stack directives and output collected content"""
        def replacer(match):
            stack_name = match.group(2).strip()

            # Get all pushed content for this stack
            if stack_name not in self.stacks:
                return ''

            # Join all content with newlines
            content = '\n'.join(self.stacks[stack_name])

            # Process the content (for variables, etc.)
            return parser.process_template(content, context)

        return STACK_PATTERN.sub(replacer, template)

    def clear(self):
        """Clear all stacks"""
        self.stacks.clear()


class PrependHandler:
    """
    Handles @prepend for adding content to beginning of stack

    @prepend('scripts')
        <script src="first.js"></script>
    @endprepend
    """

    def __init__(self, stack_handler: StackHandler):
        self.stack_handler = stack_handler

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process @prepend directives"""
        def replacer(match):
            stack_name = match.group(2).strip()
            content = match.group(3).strip()

            # Add to beginning of stack
            if stack_name not in self.stack_handler.stacks:
                self.stack_handler.stacks[stack_name] = []
            self.stack_handler.stacks[stack_name].insert(0, content)

            return ''

        return PREPEND_PATTERN.sub(replacer, template)
