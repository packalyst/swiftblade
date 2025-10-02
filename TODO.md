# SwiftBlade TODO

## Features to Implement

### hasSection() Helper

**Priority:** Medium
**Status:** Not implemented

**Description:**
Implement Laravel Blade's `hasSection()` helper to check if a child template has defined a specific section.

**Use Case:**
```blade
{{-- layout.html --}}
@if(hasSection('sidebar'))
    <div class="sidebar">
        @yield('sidebar')
    </div>
@else
    <div>Default content</div>
@endif

{{-- page.html --}}
@extends('layout')

@section('sidebar')
    <p>Custom sidebar</p>
@endsection
```

**Implementation Plan:**

1. **Modify ExtendsHandler** (`blade/handlers/extends.py`):
   ```python
   def _extract_sections(self, template):
       # ... existing code ...

       # Track which sections are defined
       section_names = set()
       for match in SECTION_PATTERN.finditer(template):
           section_name = match.group('name')
           section_names.add(section_name)

       return sections, section_names
   ```

2. **Add to context**:
   ```python
   def process(self, template, context, parser):
       # ... existing code ...
       sections, section_names = self._extract_sections(child_template)
       context['_defined_sections'] = section_names
       # ... rest of processing ...
   ```

3. **Add to safe_builtins** (`blade/evaluator.py`):
   ```python
   def hasSection(section_name):
       """Check if section is defined in template"""
       return section_name in context.get('_defined_sections', set())

   safe_builtins = {
       # ... existing ...
       "hasSection": hasSection,
   }
   ```

4. **Add tests**:
   - Test with defined sections
   - Test with undefined sections
   - Test in nested layouts

5. **Document in README**:
   - Add to Template Helpers section
   - Add usage examples
   - Document behavior with nested layouts

**References:**
- Laravel Blade: https://laravel.com/docs/blade#determining-if-a-section-has-content
- Placeholder was in blade_processor.py: `lambda section_name: False`

---

## Other Future Features

### @sectionMissing Directive
Similar to `hasSection()` but as a directive for cleaner syntax:
```blade
@sectionMissing('sidebar')
    <div>Default sidebar</div>
@endsection
```

### @env Directive
Check current environment:
```blade
@env('production')
    <script src="analytics.js"></script>
@endenv
```

### @auth / @guest Directives
Authentication helpers (framework-specific, may not be suitable for core):
```blade
@auth
    <p>Welcome, {{ user.name }}</p>
@endauth

@guest
    <p><a href="/login">Please log in</a></p>
@endguest
```

### @once Directive
Render content only once even if included multiple times:
```blade
@once
    <script src="shared-library.js"></script>
@endonce
```

---

## Performance Improvements

### Compiled Template Caching
- Pre-compile templates to Python bytecode
- Cache compiled versions on disk
- Faster than regex parsing on every render

### Async Support
- Async template rendering for I/O operations
- Async includes/components
- Better integration with async frameworks (Sanic, FastAPI)

---

## Documentation

### Interactive Examples
- Add interactive playground to docs
- Live template editor with preview
- Common use case examples

### Migration Guides
- From Jinja2
- From Mako
- From Django templates

---

## Community

### PyPI Package
- Publish to PyPI as `swiftblade`
- Set up automated releases
- Version management

### Contributing Guide
- Code style guide
- PR template
- Issue templates

---

Last Updated: 2025-10-02
