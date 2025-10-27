"""
Control Structure Handler
Orchestrates all control structure handlers
"""

from typing import Dict, Any

from ..base import BaseHandler
from .conditionals import ConditionalHandler
from .loops import LoopHandler
from .switches import SwitchHandler
from .misc import MiscHandler


class ControlStructureHandler(BaseHandler):
    """
    Orchestrates all control structure handlers

    Delegates to specialized handlers:
    - ConditionalHandler: @if/@elseif/@else/@endif
    - LoopHandler: @foreach/@for
    - SwitchHandler: @switch/@case/@default
    - MiscHandler: @isset/@empty/@python/comments
    """

    def __init__(self, engine):
        super().__init__(engine)
        self.misc = MiscHandler(engine)
        self.switch = SwitchHandler(engine)
        self.loop = LoopHandler(engine)
        self.conditional = ConditionalHandler(engine)

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """Process all control structures"""

        # Process in order of precedence
        # 1. Remove comments and process @python first
        template = self.misc.process(template, context)

        # 2. Process @switch
        template = self.switch.process(template, context)

        # 3. Process loops (@foreach/@for)
        template = self.loop.process(template, context)

        # 4. Process conditionals (@if/@elseif/@else)
        template = self.conditional.process(template, context)

        return template
