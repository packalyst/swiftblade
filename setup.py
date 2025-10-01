"""
SwiftBlade - High-performance Laravel Blade-inspired template engine for Python
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="swiftblade",
    version="1.0.0",
    author="SwiftBlade Contributors",
    author_email="",
    description="High-performance Laravel Blade-inspired template engine for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sapistudio/swiftblade",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    keywords="template engine blade laravel templating html",
    python_requires=">=3.7",
    install_requires=[
        # Zero dependencies!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "mypy>=0.950",
            "flake8>=4.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Sapistudio/swiftblade/issues",
        "Source": "https://github.com/Sapistudio/swiftblade",
        "Documentation": "https://github.com/Sapistudio/swiftblade/blob/main/AUDIT_REPORT.md",
    },
    include_package_data=True,
    zip_safe=False,
)
