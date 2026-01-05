"""
MCP Web Search Agent - Package Setup Configuration.

This setup file allows the MCP Web Search Agent to be installed as a
Python package, making it easy to import and use in other projects.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file for the long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(
    encoding="utf-8") if readme_file.exists() else ""

# Read requirements from requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="mcp-web-search-agent",
    version="1.0.0",
    author="Christos Ploutarchou",
    author_email="cploutarchou@gmail.com",
    description="Production-ready web search API using DuckDuckGo and FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cploutarchou/duckduckgo-mcp-agent",
    project_urls={
        "Bug Tracker": "https://github.com/cploutarchou/duckduckgo-mcp-agent/issues",
        "Documentation": "https://github.com/cploutarchou/duckduckgo-mcp-agent#readme",
        "Source Code": "https://github.com/cploutarchou/duckduckgo-mcp-agent",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "flake8>=6.1.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-search=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "search",
        "api",
        "fastapi",
        "duckduckgo",
        "web-search",
        "mcp",
        "model-context-protocol",
        "llm",
        "language-model",
    ],
)
