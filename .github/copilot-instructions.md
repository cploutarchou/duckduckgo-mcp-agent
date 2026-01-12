# Copilot Instructions for duckduckgo-mcp-agent

- **Scope & goal:** Minimal single-file MCP HTTP server that streams DuckDuckGo search results over SSE for LM Studio–style clients. Keep changes small and avoid breaking the single-file design unless explicitly requested.
- **Core entrypoint:** `mcp_http_sse_server.py` contains the entire FastAPI app, SSE helpers, JSON-RPC handling, and DuckDuckGo tool logic. New behavior almost always belongs here.
- **Protocol flow:** Clients POST JSON to `/`; handler inspects `method`, `params`, optional `id`/`jsonrpc`. Responses are streamed as SSE chunks via `create_sse_message(event, data)` with `event: message` (payload) and a final `event: done {}`.
- **Supported methods:** `initialize`, `resources/list`, `tools/list`, `notifications/initialized`, `notifications/cancelled`, and `tools/call`. Unknown or missing `method` yields JSON-RPC errors when `jsonrpc`+`id` provided, otherwise bare `error` events.
- **Tool contract (`web_search`):** Defined in `tools/list` schema; implemented in `tools/call` via `duckduckgo_search.DDGS().text`. Required `query`; optional `max_results` (default 5, capped at 20). Empty query returns JSON-RPC `-32602` or SSE error. Results formatted as numbered markdown with URL + snippet; empty set returns "No results found".
- **DuckDuckGo quirks:** Known `duckduckgo_search` TypeError on date formatting is caught; handler falls back to empty results instead of crashing. Leave this guard intact when modifying search logic.
- **Error handling:** Global exception handlers emit SSE `event: error` with JSON body; HTTP exceptions also mapped to SSE. The generator always emits a trailing `done` event unless an exception short-circuits.
- **Logging:** Root logger configured at INFO; suppresses verbose logs from `duckduckgo_search`, `httpx`, `curl_cffi`. `MCP_DEBUG` env is referenced in README but not wired into code—avoid introducing noisy logs unless gated.
- **Development commands (Makefile):**
  - `make install-dev` (deps incl. pytest/ruff/mypy/black) · `make run-dev` (uvicorn reload with MCP_DEBUG/env set)
  - `make run` (python entrypoint) · `make lint` (ruff + mypy on main file) · `make format` (black + ruff --fix)
  - `make test` currently points to `test_mcp_server.py` (nonexistent); use `python test-mcp-sse.py` to exercise SSE responses against a running server.
- **Testing note:** `test-mcp-sse.py` issues real HTTP requests to localhost:8000; start the server first (e.g., `make run-dev`) before running the script.
- **Containerization:** `Dockerfile` has base/production (runs `python mcp_http_sse_server.py`) and development stage (uvicorn reload + dev deps). `docker-compose.yml` exposes 8000, injects optional env vars, and adds a TCP healthcheck on port 8000.
- **Client config:** `mcp-config.json` shows LM Studio wiring (`type: http`, `url: http://localhost:8000`). Match this when adjusting port/host.
- **Extending tools:** To add a tool, update both the `tools/list` schema and the `tools/call` branch. Keep responses wrapped through `wrap_response` to honor JSON-RPC `id/jsonrpc` when provided.
- **Style & constraints:** Favor straightforward, synchronous-looking async FastAPI handlers; avoid over-modularizing. Preserve SSE formatting (`event: ...` + `data: <json>\n\n`).
- **Performance/limits:** `max_results` is explicitly capped at 20. Rate limiting/cache flags appear only in docker-compose and are not implemented—do not assume middleware exists.
