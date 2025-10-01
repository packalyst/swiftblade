"""
Directive Registry
Registry for custom directives
Allows extending template engine with custom @directives
"""

from typing import Dict, Any, Callable

from .exceptions import DirectiveError


class DirectiveRegistry:
    """
    Registry for custom directives
    Allows extending template engine with custom @directives
    """

    def __init__(self):
        self.directives: Dict[str, Callable] = {}

    def register(self, name: str, handler: Callable):
        """
        Register a custom directive

        Args:
            name: Directive name (without @)
            handler: Function(args, context) -> str

        Example:
            registry.register('upper', lambda args, ctx: args[0].upper())
            # Usage in template: @upper('hello')
        """
        self.directives[name] = handler

    def has(self, name: str) -> bool:
        """Check if directive is registered"""
        return name in self.directives

    def process(self, name: str, args: list, context: Dict[str, Any]) -> str:
        """
        Process a directive

        Args:
            name: Directive name
            args: List of arguments
            context: Template context

        Returns:
            Processed result

        Raises:
            DirectiveError: If directive not found or fails
        """
        if name not in self.directives:
            raise DirectiveError(f"Directive '@{name}' is not registered")

        try:
            return self.directives[name](args, context)
        except Exception as e:
            raise DirectiveError(f"Error processing @{name}: {e}")

    def unregister(self, name: str):
        """Unregister a directive"""
        if name in self.directives:
            del self.directives[name]
