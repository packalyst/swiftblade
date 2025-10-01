"""
Template Engine Exceptions
Enhanced error handling with line numbers and context
"""


class TemplateException(Exception):
    """Base exception for all template errors"""

    def __init__(self, message: str, template_name: str = None, line_number: int = None, context: str = None):
        self.message = message
        self.template_name = template_name
        self.line_number = line_number
        self.context = context
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with file and line info"""
        parts = []
        if self.template_name:
            parts.append(f"Template: {self.template_name}")
        if self.line_number:
            parts.append(f"Line: {self.line_number}")
        parts.append(self.message)
        if self.context:
            parts.append(f"\nContext: {self.context}")
        return " | ".join(parts) if len(parts) > 1 else parts[0]


class TemplateNotFoundException(TemplateException):
    """Raised when a template file is not found"""
    pass


class TemplateSyntaxError(TemplateException):
    """Raised when template has invalid syntax"""
    pass


class DirectiveError(TemplateException):
    """Raised when a directive fails"""
    pass


class CompilationError(TemplateException):
    """Raised when template compilation fails"""
    pass


class SecurityError(TemplateException):
    """Raised when unsafe code is detected"""
    pass


class BreakLoop(Exception):
    """Internal exception for @break directive"""
    pass


class ContinueLoop(Exception):
    """Internal exception for @continue directive"""
    pass