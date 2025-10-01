"""
Context utilities for template rendering
"""

from typing import Any


class DotDict(dict):
    """
    Dictionary that supports both dict['key'] and dict.key syntax
    Makes templates cleaner and more readable
    """

    def __getattr__(self, key):
        """Allow dict.key access"""
        try:
            value = self[key]
            # Recursively convert nested dicts
            if isinstance(value, dict) and not isinstance(value, DotDict):
                return DotDict(value)
            return value
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        """Allow dict.key = value"""
        self[key] = value

    def __delattr__(self, key):
        """Allow del dict.key"""
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


def prepare_context(context: dict) -> dict:
    """
    Prepare context for template rendering
    Converts nested dicts to DotDict for attribute access

    Args:
        context: Original context dict

    Returns:
        Context with DotDict support
    """
    if context is None:
        return {}

    prepared = {}
    for key, value in context.items():
        if isinstance(value, dict) and not isinstance(value, DotDict):
            prepared[key] = DotDict(value)
        elif isinstance(value, list):
            # Convert list items that are dicts
            prepared[key] = [
                DotDict(item) if isinstance(item, dict) and not isinstance(item, DotDict) else item
                for item in value
            ]
        else:
            prepared[key] = value

    return prepared