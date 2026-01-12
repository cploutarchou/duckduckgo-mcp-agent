#!/bin/bash
# Create release packages for GitHub releases

VERSION="1.2.1"
RELEASE_DIR="releases"

mkdir -p "$RELEASE_DIR"

# Create tarball
tar -czf "$RELEASE_DIR/duckduckgo-mcp-agent-v${VERSION}.tar.gz" \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='.mypy_cache' \
  --exclude='.ruff_cache' \
  .

# Create zip file
zip -r "$RELEASE_DIR/duckduckgo-mcp-agent-v${VERSION}.zip" \
  . \
  -x '.git/*' '.venv/*' '__pycache__/*' '.pytest_cache/*' '.mypy_cache/*' '.ruff_cache/*' '*.pyc' '.vscode/*' '.idea/*'

echo "✅ Release packages created:"
ls -lh "$RELEASE_DIR/"
