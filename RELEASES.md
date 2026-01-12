# DuckDuckGo MCP Agent - Release History

## v1.2.1 (Latest) - January 12, 2026

### ✨ Features
- **Result Deduplication** - Removes duplicate URLs from search results
- **Domain Hints (📍)** - Shows source domain indicator for each result
- **Snippet Optimization** - Truncates long snippets to 200 characters
- **Quality Filtering** - Removes results with missing titles or content
- **Enhanced Markdown Formatting** - Better visual presentation
- **Result Limiting** - Maximum 10 results per search (improved performance)

### 🔧 Advanced Search Parameters
- `all_results` flag - Fetch maximum results (capped at 10)
- `region` parameter - Search region control (wt-wt, us-en, uk-en, etc.)
- `safesearch` parameter - Content filtering (off, moderate, strict)
- `timelimit` parameter - Time-based filtering (d, w, m, y)

### 🐛 Bug Fixes
- Suppress verbose INFO logs from ddgs, primp, httpx libraries
- Improve network/DNS error handling with graceful fallbacks
- Reduce log verbosity for request cancellations
- Fix closure scoping bug in event generator

### 📦 Dependencies
- fastapi==0.128.0
- uvicorn==0.40.0
- ddgs==9.10.0

### 📥 Download
- `duckduckgo-mcp-agent-v1.2.1.zip` - Complete source package

---

## v1.2.0 - January 12, 2026

### ✨ Features
- **all_results flag** - Fetch up to 100 results instead of default 5
- **Advanced tuning parameters** - region, safesearch, timelimit
- **Better Markdown formatting** - Improved result presentation
- **Version tracking** - App version surfaced in MCP initialize

### 🔧 Improvements
- Pinned dependencies to latest stable versions
- Switched to new `ddgs` library (renamed from duckduckgo-search)
- Added comprehensive error handling

---

## v1.1.0 - January 12, 2026

### ✨ Features
- **DuckDuckGo tuning parameters**
  - region - Search specific regions
  - safesearch - Content filtering
  - timelimit - Time-based result filtering
- **Enhanced result formatting** - Better Markdown with URLs

---

## v1.0.0 - Initial Release

### ✨ Features
- Minimal MCP HTTP server with SSE support
- Single-file implementation
- DuckDuckGo web search integration
- LM Studio compatibility

---

## Installation

### From Release Package
```bash
unzip duckduckgo-mcp-agent-v1.2.1.zip
cd duckduckgo-mcp-agent
pip install -r requirements.txt
python mcp_http_sse_server.py
```

### With Docker
```bash
docker build -t duckduckgo-mcp:1.2.1 .
docker run -p 8000:8000 duckduckgo-mcp:1.2.1
```

---

## Changelog Links
- [Full CHANGELOG.md](https://github.com/cploutarchou/duckduckgo-mcp-agent/blob/main/CHANGELOG.md)
- [All Releases](https://github.com/cploutarchou/duckduckgo-mcp-agent/releases)

---

## Support
For issues and feature requests, visit: https://github.com/cploutarchou/duckduckgo-mcp-agent/issues
