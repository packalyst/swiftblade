"""
Base Handler
Base class for all directive handlers
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import BladeEngine


class BaseHandler:
    """Base class for directive handlers"""

    def __init__(self, engine: 'BladeEngine'):
        self.engine = engine
        # Use shared evaluator instance for better performance
        self.evaluator = engine._shared_evaluator
