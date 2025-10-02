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
🧩 **Modern Components** - X-components with props, slots, and attribute pass-through

---

## Quick Start

### Installation

**Install directly from GitHub:**

```bash
pip install git+https://github.com/Sapistudio/swiftblade.git
```

**Or clone and install locally:**

```bash
git clone https://github.com/Sapistudio/swiftblade.git
cd swiftblade
pip install -e .
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
{{ $user.name }}  {{-- $ prefix supported (Laravel style) --}}

{{-- Raw output (unescaped) --}}
{!! html_content !!}
{!! $html_content !!}

{{-- With default values --}}
{{ title or 'Default Title' }}
```

**Note:** The `$` prefix is optional and automatically stripped. Both `{{ name }}` and `{{ $name }}` work identically.

### Comments

```blade
{{-- This is a comment --}}

{{--
    Multi-line comment
    Won't appear in rendered output
--}}
```

### Conditionals

```blade
{{-- Basic if/else --}}
@if(user)
    Hello, {{ user.name }}!
@elseif(guest)
    Hello, Guest!
@else
    Please log in
@endif

{{-- Unless (negated if) --}}
@unless(user.banned)
    Welcome back!
@endunless

{{-- Check if variable is set --}}
@isset('variable_name')
    Variable is defined
@endisset

{{-- Check if variable is empty --}}
@empty('items')
    No items found
@endempty
```

**Undefined Variable Handling:**
If a variable doesn't exist in `@if()` conditions, it's treated as falsy (returns false) instead of throwing an error.

```blade
@if(optional_slot)
    {{-- Only renders if optional_slot exists and is truthy --}}
    {{ $optional_slot }}
@else
    {{-- Renders if optional_slot doesn't exist or is falsy --}}
    Default content
@endif
```

### Loops

```blade
{{-- Foreach loop --}}
@foreach(item in items)
    - {{ item }}
@endforeach

{{-- Alternative syntax with parentheses --}}
@foreach(user in users)
    Name: {{ user.name }}
@endforeach

{{-- For loop --}}
@for(i in range(5))
    Number: {{ i }}
@endfor

{{-- While loop --}}
@while(count < 10)
    Count: {{ count }}
@endwhile
```

### Switch Statements

```blade
@switch(status)
    @case('pending')
        Order is pending
    @case('processing')
        Order is being processed
    @case('completed')
        Order completed!
    @default
        Unknown status
@endswitch
```

### Template Inheritance

**Layout** (`views/layouts/main.html`):
```blade
<!DOCTYPE html>
<html>
<head>
    <title>@yield('title', 'Default Title')</title>
    @stack('styles')
</head>
<body>
    <header>
        @yield('header')
    </header>

    <main>
        @yield('content')
    </main>

    <footer>
        @yield('footer', 'Default Footer')
    </footer>

    @stack('scripts')
</body>
</html>
```

**Page** (`views/pages/home.html`):
```blade
@extends('layouts/main')

@section('title', 'Home Page')

@section('header')
    <h1>Welcome to Our Site</h1>
@endsection

@section('content')
    <p>This is the main content.</p>
@endsection

@push('scripts')
    <script src="home.js"></script>
@endpush
```

### Includes

```blade
{{-- Simple include --}}
@include('components/header')

{{-- Include with data --}}
@include('components/alert', {'type': 'success', 'message': 'Saved!'})

{{-- Conditional include --}}
@includeIf('components/sidebar', show_sidebar)
```

### Stacks (for assets)

```blade
{{-- In layout --}}
@stack('scripts')

{{-- In templates --}}
@push('scripts')
    <script src="app.js"></script>
@endpush

@prepend('scripts')
    <script src="jquery.js"></script>  {{-- Added to beginning --}}
@endprepend
```

---

## Components

### X-Components (Modern Syntax)

**Component** (`views/components/button.html`):
```blade
@props(['variant' => 'primary', 'size' => 'md', 'disabled' => false])

<button
    class="btn btn-{{ $variant }} btn-{{ $size }}"
    {{ $disabled ? 'disabled' : '' }}
    {{ $attributes }}
>
    {{ $slot }}
</button>
```

**Usage:**
```blade
{{-- Basic usage --}}
<x-button variant="success">
    Save Changes
</x-button>

{{-- With custom attributes (passed through) --}}
<x-button
    variant="danger"
    size="lg"
    onclick="confirmDelete()"
    data-id="123"
>
    Delete
</x-button>

{{-- Self-closing --}}
<x-button variant="primary" disabled />
```

### Named Slots

**Component** (`views/components/modal.html`):
```blade
@props(['id' => '', 'title' => ''])

<div class="modal" id="{{ $id }}">
    <div class="modal-header">
        <h3>{{ $title }}</h3>
    </div>

    @if(body)
        <div class="modal-body">
            {!! $body !!}
        </div>
    @else
        {!! $slot !!}
    @endif

    @if(footer)
        <div class="modal-footer">
            {!! $footer !!}
        </div>
    @endif
</div>
```

**Usage:**
```blade
{{-- With named slots --}}
<x-modal id="confirm-modal" title="Confirm Action">
    <x-slot:body>
        <p>Are you sure you want to proceed?</p>
    </x-slot:body>

    <x-slot:footer>
        <button class="btn btn-secondary">Cancel</button>
        <button class="btn btn-primary">Confirm</button>
    </x-slot:footer>
</x-modal>

{{-- With default slot --}}
<x-modal id="simple-modal" title="Notice">
    <p>This goes in the default slot</p>
</x-modal>

{{-- Any slot name works! --}}
<x-card>
    <x-slot:header>
        Card Header
    </x-slot:header>

    <x-slot:custom_section>
        Custom content here
    </x-slot:custom_section>
</x-card>
```

**Slot Syntax Options:**
```blade
{{-- Colon syntax (recommended) --}}
<x-slot:name>Content</x-slot:name>

{{-- Name attribute syntax --}}
<x-slot name="name">Content</x-slot>
```

### Props with Defaults

```blade
@props([
    'variant' => 'primary',
    'size' => 'md',
    'disabled' => false,
    'icon' => ''
])

<button class="btn-{{ $variant }} btn-{{ $size }}" {{ $attributes }}>
    @if(icon)
        <i class="icon-{{ $icon }}"></i>
    @endif
    {{ $slot }}
</button>
```

### Attribute Pass-Through

Attributes not defined in `@props()` are automatically available via `{{ $attributes }}`:

```blade
{{-- Component definition --}}
@props(['variant' => 'primary'])

<button class="btn-{{ $variant }}" {{ $attributes }}>
    {{ $slot }}
</button>

{{-- Usage --}}
<x-button
    variant="success"
    onclick="save()"
    data-id="42"
    aria-label="Save button"
>
    Save
</x-button>

{{-- Renders as: --}}
<button
    class="btn-success"
    onclick="save()"
    data-id="42"
    aria-label="Save button"
>
    Save
</button>
```

**Individual attribute access:**
```blade
@props(['variant' => 'primary'])

{{-- Access individual pass-through attributes --}}
@if(data_action)
    <button data-action="{{ $data_action }}" class="btn-{{ $variant }}">
        {{ $slot }}
    </button>
@endif

{{-- Note: hyphens in attributes are converted to underscores --}}
{{-- data-action becomes data_action --}}
```

### Nested Components

```blade
{{-- components/card.html --}}
@props(['title' => ''])

<div class="card">
    @if(title)
        <div class="card-header">{{ $title }}</div>
    @endif
    <div class="card-body">
        {{ $slot }}
    </div>
</div>

{{-- components/alert.html --}}
@props(['type' => 'info'])

<div class="alert alert-{{ $type }}">
    {{ $slot }}
</div>

{{-- Usage --}}
<x-card title="Notifications">
    <x-alert type="success">
        Your changes have been saved!
    </x-alert>

    <x-alert type="warning">
        Please review the updated terms.
    </x-alert>
</x-card>
```

### Legacy Components (Deprecated)

```blade
{{-- Legacy @component syntax (still supported) --}}
@component('components.alert', {'type': 'success'})
    @slot('title')
        Success!
    @endslot

    Your changes have been saved.
@endcomponent
```

**Note:** Use X-components (`<x-name>`) instead for modern projects.

---

## Advanced Features

### Custom Directives

```python
from blade import BladeEngine

engine = BladeEngine()

# Simple directive
def icon_directive(args, context):
    """Usage: @icon('home', 'tabler', 24, 24)"""
    name = args[0] if args else 'default'
    library = args[1] if len(args) > 1 else 'tabler'
    width = args[2] if len(args) > 2 else 20
    height = args[3] if len(args) > 3 else 20

    return f'<svg class="icon-{name}" width="{width}" height="{height}">...</svg>'

engine.register_directive('icon', icon_directive)

# DateTime directive
def datetime_directive(args, context):
    """Usage: @datetime(timestamp, 'Y-m-d H:i:s')"""
    from datetime import datetime
    timestamp = args[0] if args else None
    format_str = args[1] if len(args) > 1 else '%Y-%m-%d %H:%M:%S'

    if timestamp is None:
        return ''

    return datetime.fromtimestamp(int(timestamp)).strftime(format_str)

engine.register_directive('datetime', datetime_directive)
```

**Usage in templates:**
```blade
@icon('home', 'tabler', 24, 24)
@datetime(1234567890, '%Y-%m-%d')
```

### Global Functions & Helpers

```python
from blade import BladeEngine

engine = BladeEngine()

# Add global functions
def format_currency(amount):
    return f"${amount:,.2f}"

engine.add_global('format_currency', format_currency)
engine.add_global('app_name', 'My Application')
```

**Usage:**
```blade
{{ format_currency(1234.56) }}  {{-- $1,234.56 --}}
{{ app_name }}  {{-- My Application --}}
```

### Caching

```python
# Memory cache (fast, volatile)
engine = BladeEngine(
    cache_enabled=True,
    cache_storage_type='memory',
    cache_max_size=1000,
    cache_ttl=3600,
    track_mtime=True  # Auto-reload on file changes
)

# Disk cache (persistent)
engine = BladeEngine(
    cache_enabled=True,
    cache_storage_type='disk',
    cache_dir='.cache/blade',
    track_mtime=True
)

# Clear cache programmatically
engine.clear_cache()
```

### Security Configuration

```python
engine = BladeEngine(
    max_loop_iterations=10000,     # Prevent infinite loops
    max_recursion_depth=50,        # Prevent deep recursion
    max_template_size=10_000_000,  # 10 MB limit
    allow_python_blocks=False,     # Disable @python blocks (recommended)
    strict_mode=False              # Don't raise on missing variables
)
```

### SafeString (Prevent Double-Escaping)

```python
from blade.utils.safe_string import SafeString

# Mark strings as already-safe HTML
html_content = SafeString('<div>Safe HTML</div>')

# In templates
context = {'safe_html': SafeString('<b>Bold</b>')}
html = engine.render('page.html', context)
```

**In templates:**
```blade
{{ safe_html }}  {{-- Won't be escaped --}}
{!! safe_html !!}  {{-- Also won't be escaped --}}
```

---

## Built-in Functions Reference

SwiftBlade includes a comprehensive set of built-in functions available in all templates without any configuration.

### Type Constructors

| Function | Description | Example |
|----------|-------------|---------|
| `str(value)` | Convert to string | `{{ str(123) }}` → `"123"` |
| `int(value)` | Convert to integer | `{{ int("42") }}` → `42` |
| `float(value)` | Convert to float | `{{ float("3.14") }}` → `3.14` |
| `bool(value)` | Convert to boolean | `{{ bool(1) }}` → `True` |
| `list(iterable)` | Convert to list | `{{ list(range(3)) }}` → `[0, 1, 2]` |
| `dict()` | Create dictionary | `{{ dict(a=1, b=2) }}` → `{'a': 1, 'b': 2}` |
| `tuple(iterable)` | Create tuple | `{{ tuple([1, 2]) }}` → `(1, 2)` |
| `set(iterable)` | Create set | `{{ set([1, 1, 2]) }}` → `{1, 2}` |

**Examples:**
```blade
{{ str(user.id) }}  {{-- Convert ID to string --}}
{{ int(request.query.page) }}  {{-- Parse page number --}}
{{ float(product.price) }}  {{-- Ensure price is float --}}
```

### Collection Operations

| Function | Description | Example |
|----------|-------------|---------|
| `len(collection)` | Get length/count | `{{ len(items) }}` → `5` |
| `count(collection)` | Alias for len | `{{ count(users) }}` → `10` |
| `first(collection, default=None)` | Get first item | `{{ first(items) }}` |
| `last(collection, default=None)` | Get last item | `{{ last(items) }}` |
| `sorted(iterable)` | Sort collection | `{{ sorted(numbers) }}` |
| `sum(iterable)` | Sum of numbers | `{{ sum([1, 2, 3]) }}` → `6` |
| `min(iterable)` | Minimum value | `{{ min(prices) }}` |
| `max(iterable)` | Maximum value | `{{ max(scores) }}` |

**Examples:**
```blade
{{-- Get collection length --}}
<p>Total: {{ len(products) }} products</p>
<p>{{ count(users) }} users online</p>

{{-- Get first/last with fallback --}}
{{ first(items, 'No items') }}
{{ last(history, 'No history') }}

{{-- Sort and aggregate --}}
@foreach(product in sorted(products))
    {{ product.name }}
@endforeach

<p>Total price: ${{ sum(cart.prices) }}</p>
<p>Cheapest: ${{ min(prices) }}</p>
<p>Most expensive: ${{ max(prices) }}</p>
```

### String Operations

| Function | Description | Example |
|----------|-------------|---------|
| `upper(string)` | Convert to uppercase | `{{ upper("hello") }}` → `"HELLO"` |
| `lower(string)` | Convert to lowercase | `{{ lower("WORLD") }}` → `"world"` |
| `capitalize(string)` | Capitalize first char | `{{ capitalize("hello") }}` → `"Hello"` |
| `title(string)` | Title case | `{{ title("hello world") }}` → `"Hello World"` |
| `strip(string)` | Remove whitespace | `{{ strip("  hi  ") }}` → `"hi"` |
| `replace(str, old, new)` | Replace substring | `{{ replace(text, "old", "new") }}` |
| `split(string, sep)` | Split string | `{{ split("a,b,c", ",") }}` → `['a','b','c']` |
| `join(separator, list)` | Join list | `{{ join(", ", items) }}` |

**Examples:**
```blade
{{-- Case conversion --}}
<h1>{{ upper(title) }}</h1>  {{-- WELCOME --}}
<p>{{ title(user.name) }}</p>  {{-- John Doe --}}

{{-- Clean input --}}
{{ strip(user_input) }}

{{-- String manipulation --}}
{{ replace(content, "\n", "<br>") }}
{{ join(", ", tags) }}  {{-- "python, web, api" --}}

@foreach(word in split(sentence, " "))
    <span>{{ word }}</span>
@endforeach
```

### JSON Operations

| Function | Description | Example |
|----------|-------------|---------|
| `json_encode(value)` | Encode to JSON | `{{ json_encode(data) }}` |
| `json_decode(string)` | Decode from JSON | `{{ json_decode('{"a":1}') }}` |

**Examples:**
```blade
{{-- Pass Python data to JavaScript --}}
<script>
    var userData = {!! json_encode(user) !!};
    var settings = {!! json_encode(app_settings) !!};
</script>

{{-- Parse JSON string --}}
@foreach(item in json_decode(json_string))
    {{ item.name }}
@endforeach
```

### Math Operations

| Function | Description | Example |
|----------|-------------|---------|
| `abs(number)` | Absolute value | `{{ abs(-5) }}` → `5` |
| `round(number, digits=0)` | Round number | `{{ round(3.14159, 2) }}` → `3.14` |

**Examples:**
```blade
<p>Temperature: {{ abs(temperature) }}°C</p>
<p>Price: ${{ round(price, 2) }}</p>
<p>Count: {{ round(average) }}</p>
```

### Iteration Helpers

| Function | Description | Example |
|----------|-------------|---------|
| `range(stop)` | Create range | `{{ range(5) }}` → `[0,1,2,3,4]` |
| `range(start, stop)` | Create range | `{{ range(1, 4) }}` → `[1,2,3]` |
| `enumerate(iterable)` | Index + value pairs | `enumerate(items)` |
| `zip(iter1, iter2)` | Combine iterables | `zip(names, ages)` |
| `map(func, iterable)` | Apply function | `map(upper, names)` |
| `filter(func, iterable)` | Filter items | `filter(is_active, users)` |

**Examples:**
```blade
{{-- Generate numbers --}}
@for(i in range(5))
    <div>Item {{ i }}</div>
@endfor

@for(i in range(1, 11))
    <p>{{ i }}. Product</p>
@endfor

{{-- Enumerate with index --}}
@foreach((index, item) in enumerate(products))
    <tr>
        <td>{{ index + 1 }}</td>
        <td>{{ item.name }}</td>
    </tr>
@endforeach

{{-- Zip parallel lists --}}
@foreach((name, age) in zip(names, ages))
    <p>{{ name }} is {{ age }} years old</p>
@endforeach
```

### Type Checking

| Function | Description | Example |
|----------|-------------|---------|
| `is_list(value)` | Check if list | `{{ is_list(items) }}` → `True/False` |
| `is_dict(value)` | Check if dict | `{{ is_dict(data) }}` → `True/False` |
| `is_string(value)` | Check if string | `{{ is_string(text) }}` → `True/False` |
| `is_number(value)` | Check if number | `{{ is_number(count) }}` → `True/False` |

**Examples:**
```blade
@if(is_list(data))
    @foreach(item in data)
        {{ item }}
    @endforeach
@elseif(is_dict(data))
    @foreach((key, value) in data.items())
        {{ key }}: {{ value }}
    @endforeach
@else
    {{ data }}
@endif

@if(is_string(value))
    <p>String: {{ value }}</p>
@endif

@if(is_number(age))
    <p>Age: {{ age }} years</p>
@endif
```

### Template Helpers

| Function | Description | Example |
|----------|-------------|---------|
| `isset(var_name)` | Check if var exists | `{{ isset('user') }}` → `True/False` |
| `default(value, fallback='')` | Fallback value | `{{ default(title, 'Untitled') }}` |

**Examples:**
```blade
{{-- Check variable existence --}}
@if(isset('user'))
    Hello, {{ user.name }}!
@endif

{{-- Provide defaults --}}
<img src="{{ default(user.avatar, '/default-avatar.png') }}" />
<h1>{{ default(page_title, 'Welcome') }}</h1>
<p>{{ default(description, 'No description available') }}</p>

{{-- Chain with other operations --}}
{{ upper(default(user.name, 'guest')) }}  {{-- GUEST --}}
```

### Combining Functions

Functions can be combined for powerful transformations:

```blade
{{-- Uppercase first item --}}
{{ upper(first(items, 'none')) }}

{{-- Count filtered items --}}
{{ len(filter(lambda x: x.active, users)) }}

{{-- Format list as string --}}
{{ join(", ", map(upper, tags)) }}  {{-- "PYTHON, WEB, API" --}}

{{-- Safe chain with defaults --}}
{{ title(strip(default(user.bio, 'No bio'))) }}

{{-- JSON encode sorted data --}}
<script>
    var data = {!! json_encode(sorted(items, key=lambda x: x.name)) !!};
</script>
```

### Common Patterns

**Display count with pluralization:**
```blade
{{ count(items) }} item{{ count(items) != 1 ? 's' : '' }}
```

**Format list of names:**
```blade
{{ join(", ", map(title, names)) }}
```

**Get first 5 items:**
```blade
@foreach(item in list(sorted(items))[:5])
    {{ item }}
@endforeach
```

**Safe navigation with default:**
```blade
{{ default(user.profile.bio, 'No bio available') }}
```

**Format prices:**
```blade
${{ round(price, 2) }}
```

---

## Complete Directive Reference

### Control Structures

| Directive | Description | Example |
|-----------|-------------|---------|
| `@if(condition)` | Conditional rendering | `@if(user.active)...@endif` |
| `@elseif(condition)` | Else-if branch | `@if(x)...@elseif(y)...@endif` |
| `@else` | Else branch | `@if(x)...@else...@endif` |
| `@unless(condition)` | Negated if | `@unless(user.banned)...@endunless` |
| `@isset('var')` | Check if set | `@isset('user')...@endisset` |
| `@empty('var')` | Check if empty | `@empty('items')...@endempty` |

### Loops

| Directive | Description | Example |
|-----------|-------------|---------|
| `@foreach(item in list)` | Iterate over list | `@foreach(user in users)...@endforeach` |
| `@for(i in range())` | For loop | `@for(i in range(5))...@endfor` |
| `@while(condition)` | While loop | `@while(count < 10)...@endwhile` |

### Template Organization

| Directive | Description | Example |
|-----------|-------------|---------|
| `@extends('layout')` | Extend layout | `@extends('layouts/main')` |
| `@section('name')` | Define section | `@section('content')...@endsection` |
| `@yield('name')` | Output section | `@yield('content', 'default')` |
| `@include('partial')` | Include template | `@include('components/header')` |
| `@includeIf('partial', condition)` | Conditional include | `@includeIf('sidebar', show_it)` |

### Stacks

| Directive | Description | Example |
|-----------|-------------|---------|
| `@push('stack')` | Push to stack | `@push('scripts')...@endpush` |
| `@prepend('stack')` | Prepend to stack | `@prepend('scripts')...@endprepend` |
| `@stack('name')` | Output stack | `@stack('scripts')` |

### Components

| Directive | Description | Example |
|-----------|-------------|---------|
| `@props([...])` | Define component props | `@props(['variant' => 'primary'])` |
| `@component('name')` | Legacy component | `@component('alert')...@endcomponent` |
| `<x-name>` | Modern component | `<x-button>Click</x-button>` |
| `<x-slot:name>` | Named slot | `<x-slot:footer>...</x-slot:footer>` |

### Variables

| Syntax | Description | Example |
|--------|-------------|---------|
| `{{ var }}` | Escaped output | `{{ user.name }}` |
| `{!! var !!}` | Raw output | `{!! html_content !!}` |
| `{{-- comment --}}` | Comment | `{{-- TODO: fix this --}}` |

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
    return blade.render('index.html', {
        'title': 'Home',
        'user': {'name': 'John'}
    })

if __name__ == '__main__':
    app.run()
```

### Sanic

```python
from sanic import Sanic, response
from blade import BladeEngine

app = Sanic(__name__)
blade = BladeEngine(template_dir='views')

@app.route('/')
async def index(request):
    html = blade.render('index.html', {
        'title': 'Home',
        'user': request.ctx.user
    })
    return response.html(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
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
    return blade.render('index.html', {
        'title': 'Home',
        'items': [1, 2, 3]
    })
```

### Django

```python
# settings.py
from blade import BladeEngine

BLADE_ENGINE = BladeEngine(
    template_dir=BASE_DIR / 'templates',
    cache_enabled=True
)

# views.py
from django.http import HttpResponse
from django.conf import settings

def index(request):
    html = settings.BLADE_ENGINE.render('index.html', {
        'title': 'Home',
        'user': request.user
    })
    return HttpResponse(html)
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
| Component render | 1.2 ms | ~830 req/s |

**Key Optimizations:**
- ✅ LRU cache for hash computation (~300x faster)
- ✅ Centralized regex patterns (zero runtime overhead)
- ✅ Template caching (3.3x speedup)
- ✅ Optimized component resolution
- ✅ SafeString prevents double-escaping

---

## Security

### XSS Protection

- `{{ variable }}` - **Auto-escaped** (safe by default)
- `{!! variable !!}` - Raw output (use with trusted content only)
- `SafeString` - Mark pre-escaped HTML as safe

```python
from blade.utils.safe_string import SafeString

# This won't be escaped
safe_html = SafeString('<b>Bold text</b>')
```

### DoS Prevention

- Configurable loop iteration limits (`max_loop_iterations`)
- Configurable recursion depth limits (`max_recursion_depth`)
- Template size limits (`max_template_size`)
- Cache size limits (`cache_max_size`)

### Path Traversal Protection

- Component name validation (alphanumeric, hyphens, dots only)
- Path traversal checks (no `../` or absolute paths)
- Whitelisted file extensions

### Safe Expression Evaluation

- AST-based evaluation (no `eval()` or `exec()`)
- Whitelist of allowed operations and built-ins
- Sandboxed execution environment
- No access to dunder methods (`__import__`, `__class__`, etc.)

---

## Configuration Reference

```python
BladeEngine(
    # Template Settings
    template_dir='views',              # Template directory
    file_extension='.html',            # Default file extension
    encoding='utf-8',                  # File encoding

    # Caching
    cache_enabled=True,                # Enable caching
    cache_storage_type='memory',       # 'memory' or 'disk'
    cache_dir='.cache/blade',          # Disk cache directory
    cache_max_size=1000,               # Max cached templates
    cache_ttl=3600,                    # Cache TTL in seconds (0 = infinite)
    track_mtime=True,                  # Auto-reload on file changes

    # Security
    strict_mode=False,                 # Raise on undefined variables
    allow_python_blocks=False,         # Allow @python blocks (dangerous!)
    max_loop_iterations=10000,         # Maximum loop iterations
    max_recursion_depth=50,            # Maximum recursion depth
    max_template_size=10_000_000       # Max template size (bytes)
)
```

---

## Best Practices

### 1. Always Escape User Input

```blade
{{-- Good: Auto-escaped --}}
{{ user_input }}

{{-- Bad: Raw output of user data --}}
{!! user_input !!}  {{-- XSS vulnerability! --}}
```

### 2. Use Components for Reusability

```blade
{{-- Instead of repeating HTML --}}
<x-button variant="primary">Save</x-button>
<x-button variant="danger">Delete</x-button>

{{-- Not this --}}
<button class="btn btn-primary">Save</button>
<button class="btn btn-danger">Delete</button>
```

### 3. Leverage Template Inheritance

```blade
{{-- layouts/app.html --}}
<!DOCTYPE html>
<html>
    <head>
        <title>@yield('title', 'My App')</title>
    </head>
    <body>
        @yield('content')
    </body>
</html>

{{-- pages/home.html --}}
@extends('layouts/app')

@section('title', 'Home')

@section('content')
    <h1>Welcome!</h1>
@endsection
```

### 4. Use Stacks for Asset Management

```blade
{{-- In layout --}}
<head>
    @stack('styles')
</head>
<body>
    @yield('content')
    @stack('scripts')
</body>

{{-- In page --}}
@push('styles')
    <link rel="stylesheet" href="page-specific.css">
@endpush

@push('scripts')
    <script src="page-specific.js"></script>
@endpush
```

### 5. Enable Caching in Production

```python
# Development
engine = BladeEngine(
    cache_enabled=True,
    track_mtime=True  # Auto-reload on changes
)

# Production
engine = BladeEngine(
    cache_enabled=True,
    cache_storage_type='disk',  # Persist across restarts
    track_mtime=False  # Disable for performance
)
```

---

## Troubleshooting

### Template Not Found

```python
# Error: TemplateNotFoundException
# Solution: Check template_dir and file paths
engine = BladeEngine(template_dir='views')
html = engine.render('pages/home.html', {})  # Must exist at views/pages/home.html
```

### Undefined Variable Errors

```python
# Error: DirectiveError: name 'user' is not defined
# Solution: Either pass the variable or use @if checks

# Option 1: Pass all variables
html = engine.render('page.html', {'user': None})

# Option 2: Check in template
@if(user)
    {{ user.name }}
@endif
```

### Component Not Rendering

```blade
{{-- Error: Component 'button' not found --}}
{{-- Solution: Check component path --}}

{{-- Components must be in components/ subdirectory --}}
<x-button>  {{-- Looks for: components/button.html --}}

{{-- Nested components use dot notation --}}
<x-forms.input>  {{-- Looks for: components/forms/input.html --}}
```

### Slot Content Not Showing

```blade
{{-- Issue: Slot variable might not exist --}}
{{-- Solution: Always check if slot exists --}}

@if(custom_slot)
    {!! $custom_slot !!}
@else
    {!! $slot !!}  {{-- Fallback to default slot --}}
@endif
```

---

## Changelog

### v1.0.0 (2025)

- ✅ Initial release
- ✅ Full Laravel Blade syntax support
- ✅ **$ variable prefix support** (Laravel-style)
- ✅ **Flexible named slots** (any slot name supported)
- ✅ **Undefined variable handling** in @if conditions
- ✅ **Attribute pass-through** with $attributes
- ✅ LRU cache optimization
- ✅ X-component system with props and slots
- ✅ Template inheritance (@extends, @section, @yield)
- ✅ Control structures (@if, @foreach, @switch)
- ✅ Security features (XSS, DoS protection)
- ✅ Zero dependencies
- ✅ Production-ready performance

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

## Author

Built with ❤️ by the SwiftBlade team

---

## Links

- **GitHub**: https://github.com/Sapistudio/swiftblade
- **Issues**: Report bugs and request features
- **Documentation**: This README

---

## Acknowledgments

Inspired by Laravel's Blade template engine. Built for Python developers who want elegant, powerful templates without the complexity.
