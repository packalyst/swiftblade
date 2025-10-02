"""
Blade Template Engine for Python
A fast, production-ready template engine with Laravel Blade syntax
"""

# Core classes
from .engine import BladeEngine, TemplateEngine
from .compiler import TemplateCompiler, TokenType, Token
from .parser import TemplateParser
from .evaluator import SafeEvaluator
from .registry import DirectiveRegistry
from .context import DotDict, prepare_context

# Cache
from .cache import (
    BaseCacheInterface,
    CacheEntry,
    MemoryCache,
    DiskCache,
    TemplateCache,
    create_cache
)

# Exceptions
from .exceptions import (
    TemplateException,
    TemplateNotFoundException,
    TemplateSyntaxError,
    DirectiveError,
    CompilationError,
    SecurityError,
    BreakLoop,
    ContinueLoop
)

# Utilities
from .utils import SafeString

# Constants
from .constants import (
    MAX_COMPONENT_NESTING_ITERATIONS,
    ERROR_CONTEXT_MAX_LENGTH,
    ERROR_TEMPLATE_PREVIEW_LENGTH,
    DEFAULT_MAX_LOOP_ITERATIONS,
    DEFAULT_MAX_RECURSION_DEPTH,
    DEFAULT_MAX_TEMPLATE_SIZE,
    DEFAULT_CACHE_MAX_SIZE,
    DEFAULT_CACHE_TTL,
    VALID_TEMPLATE_EXTENSIONS
)

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    # Core
    "BladeEngine",
    "TemplateEngine",
    "TemplateCompiler",
    "TemplateParser",
    "SafeEvaluator",
    "DirectiveRegistry",
    "DotDict",
    "prepare_context",
    # Cache
    "BaseCacheInterface",
    "CacheEntry",
    "MemoryCache",
    "DiskCache",
    "TemplateCache",
    "create_cache",
    # Exceptions
    "TemplateException",
    "TemplateNotFoundException",
    "TemplateSyntaxError",
    "DirectiveError",
    "CompilationError",
    "SecurityError",
    "BreakLoop",
    "ContinueLoop",
    # Utilities
    "SafeString",
    # Compiler
    "TokenType",
    "Token",
    # Constants
    "MAX_COMPONENT_NESTING_ITERATIONS",
    "ERROR_CONTEXT_MAX_LENGTH",
    "ERROR_TEMPLATE_PREVIEW_LENGTH",
    "DEFAULT_MAX_LOOP_ITERATIONS",
    "DEFAULT_MAX_RECURSION_DEPTH",
    "DEFAULT_MAX_TEMPLATE_SIZE",
    "DEFAULT_CACHE_MAX_SIZE",
    "DEFAULT_CACHE_TTL",
    "VALID_TEMPLATE_EXTENSIONS",
    # Metadata
    "__version__",
    "__author__",
    "__license__",
]
