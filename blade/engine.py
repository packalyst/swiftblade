"""
Blade Template Engine
Production-ready, fast template engine based on Laravel Blade syntax
"""

import os
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from .parser import TemplateParser
from .cache import create_cache, BaseCacheInterface
from .compiler import TemplateCompiler
from .registry import DirectiveRegistry
from .exceptions import TemplateNotFoundException, TemplateException
from .context import prepare_context
from .constants import (
    VALID_TEMPLATE_EXTENSIONS,
    DEFAULT_TEMPLATE_DIR,
    DEFAULT_FILE_EXTENSION,
    DEFAULT_ENCODING,
    DEFAULT_CACHE_DIR,
    DEFAULT_CACHE_MAX_SIZE,
    DEFAULT_CACHE_TTL,
    DEFAULT_MAX_LOOP_ITERATIONS,
    DEFAULT_MAX_RECURSION_DEPTH,
    DEFAULT_MAX_TEMPLATE_SIZE,
    CACHE_STORAGE_MEMORY,
    CACHE_STORAGE_DISK,
)


class BladeEngine:
    """
    High-performance template engine with Blade-like syntax

    Features:
    - Template inheritance (@extends, @section, @yield)
    - Includes (@include, @includeIf)
    - Control structures (@if, @foreach, @for, @switch)
    - Variables ({{ }}, {!! !!})
    - Comments ({{-- --}})
    - Python blocks (@python...@endpython)
    - Custom directives
    - Advanced caching with file watching
    - Safe expression evaluation
    """

    def __init__(
        self,
        template_dir: Optional[str] = None,
        cache_enabled: bool = True,
        cache_storage_type: str = CACHE_STORAGE_MEMORY,
        cache_dir: str = DEFAULT_CACHE_DIR,
        cache_max_size: int = DEFAULT_CACHE_MAX_SIZE,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        track_mtime: bool = True,
        strict_mode: bool = False,
        file_extension: str = DEFAULT_FILE_EXTENSION,
        allow_python_blocks: bool = False,
        max_loop_iterations: int = DEFAULT_MAX_LOOP_ITERATIONS,
        max_recursion_depth: int = DEFAULT_MAX_RECURSION_DEPTH,
        max_template_size: int = DEFAULT_MAX_TEMPLATE_SIZE,
        encoding: str = DEFAULT_ENCODING
    ):
        """
        Initialize the Blade template engine

        Args:
            template_dir: Directory containing template files
            cache_enabled: Enable template caching
            cache_storage_type: 'memory' (fast, volatile) or 'disk' (slower, persistent)
            cache_dir: Directory for disk cache (only used if storage_type='disk')
            cache_max_size: Maximum number of cached templates
            cache_ttl: Cache time-to-live in seconds (0 = infinite)
            track_mtime: Track file modification times for auto-invalidation
            strict_mode: Raise exceptions for missing variables
            file_extension: Default file extension (default: '.html')
            allow_python_blocks: Allow @python...@endpython blocks (default: False)
                                WARNING: Enabling this is a security risk. Only enable
                                if you trust all template authors.
            max_loop_iterations: Maximum iterations per loop (default: 10000)
            max_recursion_depth: Maximum @include/@extends depth (default: 50)
            max_template_size: Maximum template file size in bytes (default: 10MB)
            encoding: File encoding for reading templates (default: 'utf-8')
        """
        # Input validation
        if cache_storage_type not in (CACHE_STORAGE_MEMORY, CACHE_STORAGE_DISK):
            raise ValueError(
                f"cache_storage_type must be '{CACHE_STORAGE_MEMORY}' or '{CACHE_STORAGE_DISK}', "
                f"got '{cache_storage_type}'"
            )
        if cache_max_size <= 0:
            raise ValueError(f"cache_max_size must be > 0, got {cache_max_size}")
        if cache_ttl < 0:
            raise ValueError(f"cache_ttl must be >= 0, got {cache_ttl}")
        if max_loop_iterations <= 0:
            raise ValueError(f"max_loop_iterations must be > 0, got {max_loop_iterations}")
        if max_recursion_depth <= 0:
            raise ValueError(f"max_recursion_depth must be > 0, got {max_recursion_depth}")
        if max_template_size <= 0:
            raise ValueError(f"max_template_size must be > 0, got {max_template_size}")
        if not file_extension.startswith('.'):
            raise ValueError(f"file_extension must start with '.', got '{file_extension}'")
        if not isinstance(encoding, str):
            raise TypeError(f"encoding must be str, got {type(encoding).__name__}")
        if not encoding:
            raise ValueError("encoding cannot be empty")

        self.template_dir = template_dir or os.path.join(os.getcwd(), DEFAULT_TEMPLATE_DIR)
        self.strict_mode = strict_mode
        self.file_extension = file_extension
        self.allow_python_blocks = allow_python_blocks
        self.encoding = encoding

        # Rate limiting (DoS prevention)
        self.max_loop_iterations = max_loop_iterations
        self.max_recursion_depth = max_recursion_depth
        self.max_template_size = max_template_size

        # Initialize cache
        if cache_enabled:
            cache_kwargs = {
                'max_size': cache_max_size,
                'ttl': cache_ttl,
                'track_mtime': track_mtime,
            }
            if cache_storage_type == CACHE_STORAGE_DISK:
                cache_kwargs['cache_dir'] = cache_dir

            self.cache = create_cache(cache_storage_type, **cache_kwargs)
        else:
            self.cache = None

        self.compiler = TemplateCompiler()
        self.parser = TemplateParser(self)
        self.directive_registry = DirectiveRegistry()

        # Ensure template directory exists
        Path(self.template_dir).mkdir(parents=True, exist_ok=True)

    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template file with the provided context

        Args:
            template_name: Template file name (relative to template_dir)
            context: Dictionary of variables to pass to template

        Returns:
            Rendered template string

        Raises:
            TemplateNotFoundException: If template file not found
            TemplateException: If rendering fails

        Example:
            engine = BladeEngine(template_dir="views")
            html = engine.render("home.html", {"user": "Alice"})
        """
        # Input validation
        if not template_name:
            raise ValueError("template_name cannot be empty")
        if not isinstance(template_name, str):
            raise TypeError(f"template_name must be str, got {type(template_name).__name__}")
        if '\x00' in template_name:
            raise ValueError("template_name cannot contain null bytes")
        if context is not None and not isinstance(context, dict):
            raise TypeError(f"context must be dict or None, got {type(context).__name__}")

        context = prepare_context(context or {})
        template_path = self._resolve_template_path(template_name)

        # Try to get cached raw template content
        raw_template = None
        if self.cache:
            raw_template = self.cache.get(template_path)

        # If not cached, load from disk
        if raw_template is None:
            # Check if template exists
            if not os.path.exists(template_path):
                raise TemplateNotFoundException(
                    f"Template '{template_name}' not found",
                    template_name=template_name
                )

            # Check template size (DoS prevention)
            try:
                file_size = os.path.getsize(template_path)
                if file_size > self.max_template_size:
                    from .exceptions import SecurityError
                    raise SecurityError(
                        f"Template file too large: {file_size} bytes (max: {self.max_template_size})",
                        context=template_name
                    )
            except SecurityError:
                raise
            except Exception:
                pass  # If we can't get file size, proceed anyway

            # Load template from disk
            try:
                with open(template_path, "r", encoding=self.encoding) as f:
                    raw_template = f.read()
            except Exception as e:
                raise TemplateException(
                    f"Error reading template '{template_name}': {e}",
                    template_name=template_name
                )

            # Cache the RAW template content (not rendered output)
            if self.cache:
                self.cache.store(template_path, raw_template)

        # Parse and render with current context (always re-render with fresh data)
        try:
            rendered = self.parser.parse(raw_template, context)
        except TemplateException:
            raise
        except Exception as e:
            raise TemplateException(
                f"Error rendering template '{template_name}': {e}",
                template_name=template_name
            )

        return rendered

    def render_string(self, template_string: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template directly from a string

        Args:
            template_string: Raw template string
            context: Dictionary of variables

        Returns:
            Rendered string

        Example:
            engine = BladeEngine()
            html = engine.render_string("Hello {{ name }}!", {"name": "World"})
        """
        # Input validation
        if not template_string:
            raise ValueError("template_string cannot be empty")
        if not isinstance(template_string, str):
            raise TypeError(f"template_string must be str, got {type(template_string).__name__}")
        if len(template_string) > self.max_template_size:
            raise ValueError(f"template_string too large: {len(template_string)} bytes (max: {self.max_template_size})")
        if context is not None and not isinstance(context, dict):
            raise TypeError(f"context must be dict or None, got {type(context).__name__}")

        context = prepare_context(context or {})

        try:
            return self.parser.parse(template_string, context)
        except TemplateException:
            raise
        except Exception as e:
            raise TemplateException(f"Error rendering string template: {e}")

    def register_directive(self, name: str, handler: Callable):
        """
        Register a custom directive

        Args:
            name: Directive name (without @)
            handler: Function(args, context) -> str

        Example:
            def uppercase_directive(args, context):
                return args[0].upper() if args else ''

            engine.register_directive('upper', uppercase_directive)

            # In template: @upper('hello') -> HELLO
        """
        # Input validation
        if not name:
            raise ValueError("Directive name cannot be empty")
        if not isinstance(name, str):
            raise TypeError(f"Directive name must be str, got {type(name).__name__}")
        if not name.replace('_', '').isalnum():
            raise ValueError(f"Directive name must be alphanumeric (with underscores), got '{name}'")
        if name.startswith('_'):
            raise ValueError(f"Directive name cannot start with underscore: '{name}'")
        if not callable(handler):
            raise TypeError(f"Directive handler must be callable, got {type(handler).__name__}")

        self.directive_registry.register(name, handler)

    def add_global(self, name: str, value: Any):
        """
        Add a global variable available to all templates

        Args:
            name: Variable name
            value: Variable value

        Example:
            engine.add_global('app_name', 'My App')
            # Now {{ app_name }} is available in all templates
        """
        # Input validation
        if not name:
            raise ValueError("Global variable name cannot be empty")
        if not isinstance(name, str):
            raise TypeError(f"Global variable name must be str, got {type(name).__name__}")
        if not name.isidentifier():
            raise ValueError(f"Global variable name must be valid Python identifier, got '{name}'")
        if name.startswith('_'):
            raise ValueError(f"Global variable name cannot start with underscore: '{name}'")

        if not hasattr(self, '_globals'):
            self._globals = {}
        self._globals[name] = value

    def get_globals(self) -> Dict[str, Any]:
        """Get all global variables"""
        return getattr(self, '_globals', {})

    def add_globals(self, globals_dict: Dict[str, Any] = None, **kwargs):
        """
        Add multiple global variables/functions to all templates at once

        Args:
            globals_dict: Dictionary of name->value pairs
            **kwargs: Keyword arguments as name=value pairs

        Example:
            # Using dict
            engine.add_globals({
                'app_name': 'My App',
                'version': '1.0.0',
                'DownloadStatus': DownloadStatus
            })

            # Using kwargs
            engine.add_globals(
                app_name='My App',
                version='1.0.0',
                DownloadStatus=DownloadStatus
            )

            # Combine both
            engine.add_globals(
                {'app_name': 'My App'},
                version='1.0.0'
            )
        """
        # Add from dict
        if globals_dict:
            for name, value in globals_dict.items():
                self.add_global(name, value)

        # Add from kwargs
        for name, value in kwargs.items():
            self.add_global(name, value)

    def clear_cache(self):
        """Clear all cached templates"""
        if self.cache:
            self.cache.invalidate()
        self.compiler.clear_cache()

    def invalidate_template(self, template_name: str):
        """
        Invalidate cache for a specific template

        Args:
            template_name: Template file name
        """
        if self.cache:
            template_path = self._resolve_template_path(template_name)
            self.cache.invalidate(template_path)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get engine statistics

        Returns:
            Dictionary with cache stats and compiler stats
        """
        stats = {
            "template_dir": self.template_dir,
            "strict_mode": self.strict_mode,
        }

        if self.cache:
            stats["cache"] = self.cache.get_stats()
        else:
            stats["cache"] = {"enabled": False}

        stats["compiler"] = self.compiler.get_stats()

        return stats

    def _resolve_template_path(self, template_name: str) -> str:
        """
        Resolve template name to full path with security validation

        Args:
            template_name: Template name (may include subdirectories)

        Returns:
            Full path to template file

        Raises:
            SecurityError: If path traversal is detected
        """
        # Reject absolute paths BEFORE normalization
        if os.path.isabs(template_name) or template_name.startswith('/') or template_name.startswith('\\'):
            from .exceptions import SecurityError
            raise SecurityError(f"Absolute template paths are not allowed: {template_name}")

        # Normalize path and strip leading slashes
        template_name = os.path.normpath(template_name).lstrip('/').lstrip('\\')

        # Reject parent directory traversal
        if template_name.startswith('..') or '/..' in template_name or '\\..' in template_name:
            from .exceptions import SecurityError
            raise SecurityError(f"Path traversal detected: {template_name}")

        # Auto-append extension if not present
        if not any(template_name.endswith(ext) for ext in VALID_TEMPLATE_EXTENSIONS):
            template_name += self.file_extension

        # Resolve to canonical paths
        template_dir = Path(self.template_dir).resolve()
        template_path = (template_dir / template_name).resolve()

        # CRITICAL: Verify resolved path is within template_dir
        try:
            template_path.relative_to(template_dir)
        except ValueError:
            from .exceptions import SecurityError
            raise SecurityError(
                f"Path traversal detected: '{template_name}' resolves outside template directory"
            )

        return str(template_path)

    def _merge_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Merge global variables with context"""
        merged = self.get_globals().copy()
        merged.update(context)
        return merged


# Convenience alias
TemplateEngine = BladeEngine