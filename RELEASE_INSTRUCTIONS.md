# GitHub Release Instructions for v1.2.1

## Steps to Create Release on GitHub

### 1. Go to Releases Page
https://github.com/cploutarchou/duckduckgo-mcp-agent/releases

### 2. Click "Create a New Release"

### 3. Fill in Release Details
- **Tag version:** v1.2.1
- **Release title:** Release 1.2.1 - Search Quality Improvements
- **Description:** (Use content below)

### 4. Release Description (Copy-Paste)
```
## 🎉 Release 1.2.1 - Search Quality Improvements

### ✨ What's New

#### Search Quality Enhancements
- **Result Deduplication** - No more duplicate URLs
- **Domain Hints (📍)** - Shows source for each result
- **Snippet Optimization** - Max 200 characters for readability
- **Quality Filtering** - Removes incomplete results
- **Enhanced Markdown** - Better visual presentation
- **Result Limiting** - Max 10 results per search

#### Advanced Search Parameters
- `all_results` - Fetch maximum results
- `region` - Search region control (wt-wt, us-en, uk-en, etc.)
- `safesearch` - Content filtering (off, moderate, strict)
- `timelimit` - Time-based filtering (d, w, m, y)

#### Bug Fixes & Improvements
- Suppressed verbose library logs (cleaner output)
- Improved network/DNS error handling
- Better error recovery in containerized environments
- Reduced noise from request cancellations

### 📦 Package Contents
- Single-file MCP HTTP server (mcp_http_sse_server.py)
- Smoke tests for validation
- Docker support (Dockerfile + docker-compose.yml)
- LM Studio configuration (mcp-config.json)
- Complete documentation

### 📋 System Requirements
- Python 3.10+
- pip
- Optional: Docker & Docker Compose

### 🚀 Quick Start
```bash
pip install -r requirements.txt
python mcp_http_sse_server.py
# Server running on http://0.0.0.0:8000
```

### 📚 Documentation
- [README.md](https://github.com/cploutarchou/duckduckgo-mcp-agent/blob/main/README.md) - Full usage guide
- [CHANGELOG.md](https://github.com/cploutarchou/duckduckgo-mcp-agent/blob/main/CHANGELOG.md) - Version history

### 🔗 Downloads
- Source code (zip)
- Source code (tar.gz)

### 🙏 Contributors
- All improvements and fixes applied

---

**Fully tested and production-ready!** 🎯
```

### 5. Upload Release Assets
- Click "Attach binaries..." or drag-and-drop
- Upload: `releases/duckduckgo-mcp-agent-v1.2.1.zip`

### 6. Publish Release
- Click "Publish release" button

---

## Creating Future Releases

For each new release, repeat these steps with:
1. New version tag (e.g., v1.3.0)
2. Updated release notes
3. New package file from `releases/` directory

### Automated Package Creation
```bash
# Run the package script
powershell -File create-release.ps1

# Or on Linux/Mac
bash create-release.sh
```

The script creates `releases/duckduckgo-mcp-agent-vX.Y.Z.zip` automatically.

---

## Release Checklist

- [ ] All tests passing
- [ ] Merge feature branch to main
- [ ] Create version tag (git tag -a vX.Y.Z)
- [ ] Push tags to GitHub (git push origin --tags)
- [ ] Create release package (run create-release.ps1)
- [ ] Go to GitHub Releases page
- [ ] Create new release with tag
- [ ] Add release notes
- [ ] Upload package ZIP
- [ ] Publish release

Done! ✅
