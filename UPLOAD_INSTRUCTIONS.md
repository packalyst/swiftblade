# How to Upload SwiftBlade to GitHub

## ✅ Repository is Ready!

Your repository is initialized at: `/home/laurs/sh_cli/swiftblade/`

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in the details:
   - **Repository name**: `swiftblade`
   - **Description**: `High-performance Laravel Blade-inspired template engine for Python`
   - **Visibility**: Public (recommended) or Private
   - **❌ DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click **Create repository**

---

## Step 2: Push to GitHub

After creating the repository on GitHub, run these commands:

```bash
cd /home/laurs/sh_cli/swiftblade

# Add GitHub as remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/swiftblade.git

# Push to GitHub
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/swiftblade.git
git push -u origin main
```

---

## Step 3: Verify Upload

After pushing, visit your repository:
`https://github.com/YOUR_USERNAME/swiftblade`

You should see:
- ✅ README.md displayed on the main page
- ✅ All files and folders
- ✅ 1 commit

---

## Alternative: Using GitHub CLI (if installed)

If you have `gh` CLI installed and authenticated:

```bash
cd /home/laurs/sh_cli/swiftblade

# Create repo and push in one command
gh repo create swiftblade --public --source=. --remote=origin --push

# Or if you prefer private
gh repo create swiftblade --private --source=. --remote=origin --push
```

---

## What's Included

```
swiftblade/
├── .git/                  # Git repository
├── .gitignore            # Ignore cache, __pycache__, etc.
├── README.md             # Comprehensive documentation
├── LICENSE               # MIT License
├── setup.py              # Pip installation script
├── pyproject.toml        # Modern Python packaging
├── MANIFEST.in           # Package manifest
├── AUDIT_REPORT.md       # Full audit and performance report
└── blade/                # The actual package
    ├── __init__.py
    ├── engine.py
    ├── parser.py
    ├── compiler.py
    ├── evaluator.py
    ├── constants.py
    ├── context.py
    ├── registry.py
    ├── exceptions.py
    ├── py.typed           # Type hints marker
    ├── cache/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── memory.py
    │   └── disk.py
    ├── handlers/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── base_component.py
    │   ├── variables.py
    │   ├── extends.py
    │   ├── include.py
    │   ├── component.py
    │   ├── x_component.py
    │   ├── stacks.py
    │   └── control/
    │       ├── __init__.py
    │       ├── conditionals.py
    │       ├── loops.py
    │       ├── switches.py
    │       └── misc.py
    └── utils/
        ├── __init__.py
        └── safe_string.py
```

---

## After Upload

### Update Repository URL in Files

After creating the repository, update these lines in:

**setup.py** (line 16):
```python
url="https://github.com/YOUR_USERNAME/swiftblade",
```

**setup.py** (lines 37-40):
```python
project_urls={
    "Bug Reports": "https://github.com/YOUR_USERNAME/swiftblade/issues",
    "Source": "https://github.com/YOUR_USERNAME/swiftblade",
    "Documentation": "https://github.com/YOUR_USERNAME/swiftblade/blob/main/AUDIT_REPORT.md",
},
```

**pyproject.toml** (lines 39-42):
```toml
[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/swiftblade"
Documentation = "https://github.com/YOUR_USERNAME/swiftblade/blob/main/AUDIT_REPORT.md"
Repository = "https://github.com/YOUR_USERNAME/swiftblade"
"Bug Tracker" = "https://github.com/YOUR_USERNAME/swiftblade/issues"
```

Then commit and push the changes:
```bash
git add setup.py pyproject.toml
git commit -m "Update repository URLs"
git push
```

---

## Optional: Publish to PyPI

Once your GitHub repository is set up, you can publish to PyPI:

### 1. Install build tools
```bash
pip install build twine
```

### 2. Build package
```bash
cd /home/laurs/sh_cli/swiftblade
python -m build
```

### 3. Upload to PyPI
```bash
# Test PyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Then real PyPI
python -m twine upload dist/*
```

### 4. Install from PyPI
```bash
pip install swiftblade
```

---

## Optional: Add GitHub Actions

Create `.github/workflows/tests.yml` for automatic testing:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.7', '3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e .[dev]
    - name: Run tests
      run: |
        pytest
```

---

## Need Help?

If you encounter issues:
1. Make sure you're in the correct directory: `cd /home/laurs/sh_cli/swiftblade`
2. Check git status: `git status`
3. Verify remote: `git remote -v`
4. Check branch: `git branch`

---

**Repository is ready to upload! 🚀**
