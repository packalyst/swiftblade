"""
Template Engine Constants
Centralized configuration values and magic numbers
"""

import re

# ==============================================================================
# DEFAULT VALUES
# ==============================================================================

# Template Paths
DEFAULT_TEMPLATE_DIR = "views"
"""Default directory for template files"""

DEFAULT_FILE_EXTENSION = ".html"
"""Default file extension for templates"""

DEFAULT_ENCODING = "utf-8"
"""Default file encoding for reading templates"""

# Component Paths
COMPONENT_SUBDIR = "components"
"""Subdirectory for X-component templates"""

# Cache Configuration
DEFAULT_CACHE_DIR = ".cache/blade"
"""Default directory for disk cache"""

CACHE_STORAGE_MEMORY = "memory"
"""Cache storage type: in-memory"""

CACHE_STORAGE_DISK = "disk"
"""Cache storage type: disk-based"""

CACHE_KEY_SEPARATOR = ":"
"""Separator for cache key components"""

# ==============================================================================
# LIMITS AND CONSTRAINTS
# ==============================================================================

# Component Processing
MAX_COMPONENT_NESTING_ITERATIONS = 20
"""Maximum iterations for processing nested components (prevents infinite loops)"""

# Error Message Truncation
ERROR_CONTEXT_MAX_LENGTH = 100
"""Maximum length of code/template context in error messages"""

ERROR_TEMPLATE_PREVIEW_LENGTH = 50
"""Maximum length of template preview in error messages"""

# Security Limits (configured via BladeEngine, these are internal fallbacks)
DEFAULT_MAX_LOOP_ITERATIONS = 10000
"""Default maximum iterations per @foreach or @for loop"""

DEFAULT_MAX_RECURSION_DEPTH = 50
"""Default maximum @include/@extends recursion depth"""

DEFAULT_MAX_TEMPLATE_SIZE = 10_000_000
"""Default maximum template file size in bytes (10 MB)"""

# Cache Configuration
DEFAULT_CACHE_MAX_SIZE = 1000
"""Default maximum number of cached templates"""

DEFAULT_CACHE_TTL = 3600
"""Default cache time-to-live in seconds (1 hour)"""

# File Extensions
VALID_TEMPLATE_EXTENSIONS = ('.html', '.blade', '.tpl', '.txt')
"""Valid template file extensions"""


# ==============================================================================
# COMPILED REGEX PATTERNS (optimized - compiled once at import time)
# ==============================================================================

# Component Validation
COMPONENT_NAME_PATTERN = re.compile(r'^[a-z0-9\-\.]+$', re.IGNORECASE)
"""Component name validation pattern (whitelist)"""

# Variable Output Patterns
ESCAPED_VAR_PATTERN = re.compile(r'\{\{\s*(.*?)\s*\}\}')
"""Pattern for escaped variable output: {{ variable }}"""

RAW_VAR_PATTERN = re.compile(r'\{!!\s*(.*?)\s*!!\}')
"""Pattern for raw variable output: {!! variable !!}"""

# Comment Pattern
COMMENT_PATTERN = re.compile(r'\{\{--[\s\S]*?--\}\}')
"""Pattern for Blade comments: {{-- comment --}}"""

# Template Inheritance Patterns
EXTENDS_PATTERN = re.compile(r"@extends\(\s*(['\"])(.*?)\1\s*\)")
"""Pattern for @extends directive"""

SECTION_PATTERN = re.compile(
    r"@section\(\s*(['\"])(?P<name>.*?)\1\s*(?:,\s*\1(?P<inline>.*?)\1\s*\)|\)\s*(?P<block>[\s\S]*?)@endsection)",
    re.DOTALL
)
"""Pattern for @section directive (inline and block forms)"""

YIELD_PATTERN = re.compile(r"@yield\(\s*(['\"])(.*?)\1(?:\s*,\s*['\"]([^'\"]*)['\"])?\s*\)")
"""Pattern for @yield directive with optional default"""

# Include Patterns
INCLUDE_PATTERN = re.compile(r"@include\(\s*(['\"])(.*?)\1\s*\)")
"""Pattern for @include directive"""

INCLUDE_IF_PATTERN = re.compile(r"@includeIf\(\s*(['\"])(.*?)\1\s*,\s*(.*?)\s*\)")
"""Pattern for @includeIf directive"""

# Control Structure Patterns
PYTHON_PATTERN = re.compile(r'@python\s*([\s\S]*?)\s*@endpython')
"""Pattern for @python blocks"""

ISSET_PATTERN = re.compile(r'@isset\(\s*(["\'])(.*?)\1\s*\)([\s\S]*?)@endisset', re.DOTALL)
"""Pattern for @isset directive"""

EMPTY_PATTERN = re.compile(r'@empty\(\s*(["\'])(.*?)\1\s*\)([\s\S]*?)@endempty', re.DOTALL)
"""Pattern for @empty directive"""

SWITCH_PATTERN = re.compile(r'@switch\((.*?)\)([\s\S]*?)@endswitch')
"""Pattern for @switch directive"""

CASE_PATTERN = re.compile(r'@case\((.*?)\)([\s\S]*?)(?=@case\(|@default|@endswitch)', re.DOTALL)
"""Pattern for @case within @switch"""

DEFAULT_PATTERN = re.compile(r'@default([\s\S]*?)$', re.DOTALL)
"""Pattern for @default within @switch"""

BREAK_PATTERN = re.compile(r'@break')
"""Pattern for @break directive"""

FOREACH_PATTERN = re.compile(r'@foreach\s*\((.*?)\)\s*([\s\S]*?)@endforeach')
"""Pattern for @foreach loop with parentheses: @foreach(var in items)"""

FOR_PATTERN = re.compile(r'@for\s*\((.*?)\)\s*([\s\S]*?)@endfor')
"""Pattern for @for loop with parentheses: @for(i in range(10))"""

IF_PATTERN = re.compile(r'@if\(')
"""Pattern for @if directive start"""

ENDIF_PATTERN = re.compile(r'@endif')
"""Pattern for @endif directive"""

ELSEIF_PATTERN = re.compile(r'@elseif\(.*?\)|@else')
"""Pattern for @elseif and @else directives"""

# X-Component Patterns
X_COMPONENT_SELF_CLOSING_PATTERN = re.compile(
    r'<x-([a-z0-9\-\.]+)((?:\s+[^>]*)?)\s*/>',
    re.IGNORECASE
)
"""Pattern for self-closing X-components: <x-button />"""

X_COMPONENT_PAIRED_PATTERN = re.compile(
    r'<x-([a-z0-9\-\.]+)((?:\s+[^>]*)?)\s*>((?:(?!<x-).)*?)</x-\1\s*>',
    re.IGNORECASE | re.DOTALL
)
"""Pattern for paired X-components without nesting"""

X_COMPONENT_PAIRED_NESTED_PATTERN = re.compile(
    r'<x-([a-z0-9\-\.]+)((?:\s+[^>]*)?)\s*>(.*?)</x-\1\s*>',
    re.IGNORECASE | re.DOTALL
)
"""Pattern for paired X-components with nesting"""

X_PROPS_PATTERN = re.compile(r'@props\(\s*\[.*?\]\s*\)', re.DOTALL)
"""Pattern for @props directive"""

X_DYNAMIC_ATTR_PATTERN = re.compile(r':([a-z0-9\-_\.]+)\s*=\s*"([^"]*)"', re.IGNORECASE)
"""Pattern for dynamic attributes: :title="value" """

X_STATIC_ATTR_PATTERN = re.compile(r'([a-z0-9\-_\.]+)\s*=\s*"([^"]*)"', re.IGNORECASE)
"""Pattern for static attributes: title="value" (supports dots for Alpine modifiers like x-model.number) """

X_BOOLEAN_ATTR_PATTERN = re.compile(r'\b([a-z0-9\-_\.]+)\b', re.IGNORECASE)
"""Pattern for boolean attributes"""

X_SLOT_COLON_PATTERN = re.compile(
    r'<x-slot:([a-z0-9\-_]+)>(.*?)</x-slot:\1>',
    re.IGNORECASE | re.DOTALL
)
"""Pattern for X-slot with colon syntax: <x-slot:name>"""

X_SLOT_NAME_PATTERN = re.compile(
    r'<x-slot\s+name\s*=\s*["\']([a-z0-9\-_]+)["\']\s*>(.*?)</x-slot>',
    re.IGNORECASE | re.DOTALL
)
"""Pattern for X-slot with name attribute: <x-slot name="name">"""

X_PROPS_DEF_PATTERN = re.compile(r'@props\(\s*\[(.*?)\]\s*\)', re.DOTALL)
"""Pattern for @props definition"""

X_PROPS_PAIR_PATTERN = re.compile(r"['\"]([^'\"]+)['\"]\s*=>\s*([^,\]]+)")
"""Pattern for key => value pairs in @props"""

# Stack Patterns
PUSH_PATTERN = re.compile(r"@push\(\s*(['\"])(.*?)\1\s*\)([\s\S]*?)@endpush", re.DOTALL)
"""Pattern for @push directive"""

STACK_PATTERN = re.compile(r"@stack\(\s*(['\"])(.*?)\1\s*\)")
"""Pattern for @stack directive"""

PREPEND_PATTERN = re.compile(r"@prepend\(\s*(['\"])(.*?)\1\s*\)([\s\S]*?)@endprepend", re.DOTALL)
"""Pattern for @prepend directive"""
