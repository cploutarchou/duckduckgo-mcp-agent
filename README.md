# DuckDuckGo MCP Agent

A minimal, production-ready **Model Context Protocol (MCP) server** enabling LLMs to perform web searches via DuckDuckGo. Built with FastAPI and Server-Sent Events (SSE).

**Features:**
- ✅ Single-file implementation (~324 lines)
- ✅ No API keys required
- ✅ HTTP + SSE streaming (LM Studio compatible)
- ✅ Docker-ready
- ✅ Minimal dependencies (FastAPI, Uvicorn, duckduckgo-search)

---

## Quick Start

### Prerequisites
- Python 3.10+ or Docker
- LM Studio (optional)

### Option 1: Dev Container (Recommended)
1. Install [VS Code](https://code.visualstudio.com/) and [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
3. Open folder in VS Code → "Reopen in Container"

### Option 2: Local Development
```bash
make install-dev
make run-dev
# Server: http://localhost:8000
```

### Option 3: Docker
```bash
make docker-build
make docker-run
# Or: make docker-compose
```

---

## Usage

### HTTP Request
```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "web_search",
      "arguments": {"query": "Python async", "max_results": 5, "region": "us-en", "safesearch": "moderate", "timelimit": "w"}
    }
  }'
```

### MCP Protocol

**Initialize:**
```json
{"method": "initialize", "id": 1}
```

**List Tools:**
```json
{"method": "tools/list", "id": 2}
```

**Call Search:**
```json
{
  "method": "tools/call",
  "id": 3,
  "params": {
    "name": "web_search",
    "arguments": {"query": "your query", "max_results": 5, "region": "wt-wt", "safesearch": "moderate"}
  }
}
```

### LM Studio Configuration

Add to `mcp-config.json`:
```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "type": "http",
      "url": "http://localhost:8000",
      "disabled": false
    }
  }
}
```

---

## Architecture

**Data Flow:**
```
LM Studio → POST / (JSON-RPC) → FastAPI → SSE Events → Client
                                    ↓
                            MCP Handlers (initialize, tools/list, tools/call)
                                    ↓
                            DuckDuckGo Search API
```

**Key Components:**
- `mcp_http_sse_server.py` - Single FastAPI app with async streaming
- `requirements.txt` - Dependencies only
- `Dockerfile` - Production & dev stages
- `docker-compose.yml` - Orchestration
- `test-mcp-sse.py` - Integration tests

---

## Development

### Make Commands
```bash
make help              # Show all commands
make install-dev      # Install dev dependencies
make run-dev          # Run with auto-reload
make test             # Run tests
make lint             # Ruff + mypy type checking
make format           # Black + ruff auto-format
make clean            # Remove build artifacts
make docker-build     # Build Docker image
make docker-compose   # Run with Docker Compose
```

### Code Quality
```bash
make format  # Auto-format code
make lint    # Run linters
```

---

## Configuration

### Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `MCP_DEBUG` | `false` | Verbose logging |
| `MCP_ENVIRONMENT` | `production` | Dev mode |
| `MCP_LOG_LEVEL` | `INFO` | Log level |
| `MCP_PORT` | `8000` | Server port |

### Docker
Set in `docker-compose.yml`:
```yaml
environment:
  - MCP_ENVIRONMENT=development
  - MCP_LOG_LEVEL=INFO
```

---


**Production requires:** `mcp_http_sse_server.py` + `requirements.txt`

---

## API Reference

### Response Format (SSE)
```
event: message
data: {"jsonrpc": "2.0", "id": 1, "result": {...}}

event: done
data: {}
```

### Search Tool
- Input:
  - `query` (string, required)
  - `max_results` (int, 1-20, default 5)
  - `region` (string, default `wt-wt`)
  - `safesearch` (string enum: `off|moderate|strict`, default `moderate`)
  - `timelimit` (string enum: `d|w|m|y`, optional)
- Output: Formatted markdown with title, URL, snippet

---

## Contributing

Keep this project minimal:
1. Single-file design (avoid modularization)
2. MCP protocol compliance
3. Test with real LM Studio
4. Run `make format && make lint` before submission

---

## Support
- **Examples:** [test-mcp-sse.py](test-mcp-sse.py)
- **Debugging:** Set `MCP_DEBUG=true`
- **Config:** See [mcp-config.json](mcp-config.json)

---

## Changelog

- 1.1.0: Improved DuckDuckGo search with region/safesearch/timelimit parameters; better markdown formatting; version surfaced in initialize.

## License
See [LICENSE](LICENSE)
