# SwiftBlade

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**High-performance Laravel Blade-inspired template engine for Python**

Zero dependencies. Production-ready. Blazingly fast.

---

## Features

✨ **Laravel Blade Syntax** - Familiar and elegant template syntax
🚀 **High Performance** - Sub-millisecond rendering with LRU caching
🔒 **Security First** - XSS protection, DoS prevention, safe expression evaluation
📦 **Zero Dependencies** - No external packages required
🎯 **Type Safe** - Full type hints throughout
🔧 **Highly Configurable** - Customize every aspect

---

## Quick Start

### Installation

```bash
pip install swiftblade
```

### Basic Usage

```python
from blade import BladeEngine

# Initialize engine
engine = BladeEngine(template_dir="views")

# Render a template
html = engine.render("welcome.html", {"name": "World"})
print(html)  # Hello, World!
```

**Template** (`views/welcome.html`):
```blade
Hello, {{ name }}!
```

---

## Syntax Guide

### Variables

```blade
{{-- Escaped output (safe) --}}
{{ user.name }}

{{-- Raw output (unescaped) --}}
{!! html_content !!}
```

### Conditionals

```blade
@if user
    Hello, {{ user.name }}!
@elseif guest
    Hello, Guest!
@else
    Please log in
@endif
```

### Loops

```blade
@foreach item in items
    - {{ item }}
@endforeach

@for i in range(5)
    Number: {{ i }}
@endfor
```

### Template Inheritance

**Layout** (`views/layout.html`):
```blade
<!DOCTYPE html>
<html>
<head>
    <title>@yield('title', 'Default Title')</title>
</head>
<body>
    @yield('content')
</body>
</html>
```

**Page** (`views/page.html`):
```blade
@extends('layout.html')

@section('title', 'My Page')

@section('content')
    <h1>Welcome!</h1>
@endsection
```

### Components

**Modern X-Component** (`views/components/button.html`):
```blade
@props(['variant' => 'primary', 'disabled' => false])

<button class="btn-{{ variant }}" {{ disabled ? 'disabled' : '' }}>
    {{ slot }}
</button>
```

**Usage**:
```blade
<x-button variant="success">
    Save Changes
</x-button>
```

### Includes

```blade
@include('partials.header')

@includeIf('partials.sidebar', show_sidebar)
```

### Stacks

```blade
{{-- Push to stack --}}
@push('scripts')
    <script src="app.js"></script>
@endpush

{{-- Output stack --}}
@stack('scripts')
```

---

## Advanced Features

### Caching

```python
# Memory cache (fast, volatile)
engine = BladeEngine(
    cache_enabled=True,
    cache_storage_type='memory',
    cache_max_size=1000,
    cache_ttl=3600
)

# Disk cache (persistent)
engine = BladeEngine(
    cache_enabled=True,
    cache_storage_type='disk',
    cache_dir='.cache/blade'
)
```

### Custom Directives

```python
from blade import BladeEngine

engine = BladeEngine()

# Register custom directive
@engine.directive('datetime')
def datetime_directive(timestamp):
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
```

**Usage**:
```blade
Created: @datetime(1234567890)
```

### Security Configuration

```python
engine = BladeEngine(
    max_loop_iterations=10000,     # Prevent infinite loops
    max_recursion_depth=50,        # Prevent deep recursion
    max_template_size=10_000_000,  # 10 MB limit
    allow_python_blocks=False      # Disable @python blocks (recommended)
)
```

---

## Performance

Benchmarks on standard hardware (single-threaded):

| Operation | Time | Throughput |
|-----------|------|------------|
| Simple template | 0.070 ms | ~14,000 req/s |
| Variable interpolation | 0.225 ms | ~4,400 req/s |
| Loop (10 items) | 0.897 ms | ~1,100 req/s |
| Cached render | 0.202 ms | **3.3x faster** |

**Key Optimizations:**
- ✅ LRU cache for hash computation (~300x faster)
- ✅ Centralized regex patterns (zero runtime overhead)
- ✅ Template caching (3.3x speedup)
- ✅ Optimized component resolution

---

## Architecture

```
blade-python/
├── blade/
│   ├── engine.py          # Main API
│   ├── parser.py          # Template parser
│   ├── compiler.py        # Template compiler
│   ├── evaluator.py       # Safe expression evaluation
│   ├── constants.py       # Configuration
│   ├── cache/             # Caching system
│   │   ├── memory.py      # In-memory cache
│   │   └── disk.py        # Disk cache
│   ├── handlers/          # Directive handlers
│   │   ├── variables.py   # {{ }} and {!! !!}
│   │   ├── extends.py     # @extends/@section/@yield
│   │   ├── include.py     # @include
│   │   ├── component.py   # @component
│   │   ├── x_component.py # <x-component>
│   │   └── control/       # Control structures
│   └── utils/             # Utilities
└── README.md
```

**29 modules, 3,525 lines of code**

---

## Configuration Options

```python
BladeEngine(
    template_dir='views',              # Template directory
    cache_enabled=True,                # Enable caching
    cache_storage_type='memory',       # 'memory' or 'disk'
    cache_dir='.cache/blade',          # Disk cache directory
    cache_max_size=1000,               # Max cached templates
    cache_ttl=3600,                    # Cache TTL (seconds)
    track_mtime=True,                  # Track file changes
    strict_mode=False,                 # Strict variable checking
    file_extension='.html',            # Default extension
    encoding='utf-8',                  # File encoding
    allow_python_blocks=False,         # Allow @python blocks
    max_loop_iterations=10000,         # Loop limit
    max_recursion_depth=50,            # Recursion limit
    max_template_size=10_000_000       # Template size limit
)
```

---

## Security

### XSS Protection

- `{{ variable }}` - **Auto-escaped** (safe by default)
- `{!! variable !!}` - Raw output (use with caution)
- `SafeString` - Mark pre-escaped HTML

### DoS Prevention

- Configurable loop iteration limits
- Configurable recursion depth limits
- Template size limits
- Cache size limits

### Path Traversal Protection

- Component name validation (whitelist)
- Path traversal checks
- Absolute path prevention

### Safe Expression Evaluation

- AST-based evaluation (no `eval()`)
- Whitelist of allowed operations
- Sandboxed execution

---

## Web Framework Integration

### Flask

```python
from flask import Flask
from blade import BladeEngine

app = Flask(__name__)
blade = BladeEngine(template_dir='templates')

@app.route('/')
def index():
    return blade.render('index.html', {'title': 'Home'})
```

### FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from blade import BladeEngine

app = FastAPI()
blade = BladeEngine(template_dir='templates')

@app.get('/', response_class=HTMLResponse)
async def index():
    return blade.render('index.html', {'title': 'Home'})
```

### Django

```python
# settings.py
BLADE_ENGINE = BladeEngine(template_dir='templates')

# views.py
from django.http import HttpResponse
from django.conf import settings

def index(request):
    html = settings.BLADE_ENGINE.render('index.html', {'title': 'Home'})
    return HttpResponse(html)
```

---

## Development

### Running Tests

```bash
python test_blade_refactor.py
```

### Performance Testing

See `AUDIT_REPORT.md` for comprehensive benchmarks.

---

## Comparison with Other Engines

| Feature | Blade Python | Jinja2 | Mako | Cheetah |
|---------|-------------|---------|------|---------|
| Zero dependencies | ✅ | ❌ | ❌ | ❌ |
| Laravel Blade syntax | ✅ | ❌ | ❌ | ❌ |
| Type hints | ✅ | Partial | ❌ | ❌ |
| LRU caching | ✅ | ❌ | ❌ | ❌ |
| Component system | ✅ | ❌ | ❌ | ❌ |
| Sub-millisecond rendering | ✅ | ✅ | ✅ | ✅ |

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Include tests for new features
4. Update documentation

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Changelog

### v1.0.0 (2025)

- ✅ Initial release
- ✅ Full Laravel Blade syntax support
- ✅ LRU cache optimization
- ✅ Component system (legacy + X-components)
- ✅ Template inheritance
- ✅ Control structures
- ✅ Security features (XSS, DoS protection)
- ✅ Zero dependencies
- ✅ Production-ready performance

---

## Author

Built with ❤️ by the Blade Python team

---

## Links

- **Documentation**: [Full docs](AUDIT_REPORT.md)
- **Issues**: Report bugs and request features
- **PyPI**: `pip install blade-python`

---

## Acknowledgments

Inspired by Laravel's Blade template engine.
