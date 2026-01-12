#!/usr/bin/env python3
"""
MCP HTTP Server with SSE (Server-Sent Events) Support.

Implements the MCP protocol over HTTP using Server-Sent Events for streaming.
Compatible with LM Studio's HTTP MCP client.

Usage:
    python mcp_http_sse_server.py
    # Runs on http://0.0.0.0:8000
"""

import json
import logging
from typing import Any, AsyncGenerator, Dict
from urllib.parse import urlparse

import uvicorn
try:
    from ddgs import DDGS  # preferred new package name
except Exception:  # pragma: no cover - fallback when ddgs not available
    from duckduckgo_search import DDGS  # legacy package name
from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Application version
APP_VERSION = "1.2.1"

# Result caps
MAX_RESULTS_CAP = 10  # default safety cap
MAX_ALL_RESULTS_CAP = 10  # cap used when all_results=true

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress verbose logging from DuckDuckGo and HTTP libraries
logging.getLogger("duckduckgo_search").setLevel(logging.WARNING)
logging.getLogger("ddgs").setLevel(logging.WARNING)
logging.getLogger("ddgs.ddgs").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("primp").setLevel(logging.WARNING)
logging.getLogger("curl_cffi").setLevel(logging.WARNING)

app = FastAPI(
    title="DuckDuckGo MCP Server",
    description="MCP server providing DuckDuckGo web search via HTTP with SSE",
)


def create_sse_message(event: str, data: Dict[str, Any]) -> str:
    """Create a Server-Sent Event message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# Custom exception handler to return SSE format errors
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions and return SSE format response."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    error_message = f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"

    return Response(
        content=error_message,
        status_code=500,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions and return SSE format response."""
    logger.error(f"HTTP exception {exc.status_code}: {exc.detail}")

    error_message = (
        f"event: error\ndata: {json.dumps({'message': str(exc.detail)})}\n\n"
    )

    return Response(
        content=error_message,
        status_code=exc.status_code,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/")
async def mcp_endpoint(request: Request):
    """
    MCP HTTP endpoint - main entry point for LM Studio.
    Handles all MCP requests via SSE streaming.
    """
    # Read request body first before creating generator
    try:
        body = await request.json()
        logger.info(f"Received request body: {body}")
    except Exception as json_error:
        logger.error(f"Error parsing JSON: {str(json_error)}", exc_info=True)
        error_msg = create_sse_message(
            "error", {"message": f"Invalid JSON: {str(json_error)}"}
        )
        return StreamingResponse(
            iter([error_msg]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    async def event_generator(body=body) -> AsyncGenerator[str, None]:
        try:
            # Parse MCP request
            method = body.get("method")
            params = body.get("params", {})
            request_id = body.get("id")
            is_jsonrpc = body.get("jsonrpc") == "2.0"

            logger.info(
                f"MCP request: {method} with params: {params} (JSON-RPC: {is_jsonrpc}, id: {request_id})"
            )

            def wrap_response(result: Any) -> Any:
                """Wrap response in JSON-RPC format if needed."""
                if is_jsonrpc and request_id is not None:
                    return {"jsonrpc": "2.0", "id": request_id, "result": result}
                return result

            if method == "initialize":
                # MCP initialization handshake
                result: Dict[str, Any] = {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {
                        "name": "DuckDuckGo Web Search",
                        "version": APP_VERSION,
                    },
                }
                yield create_sse_message("message", wrap_response(result))

            elif method == "resources/list":
                # MCP resources listing
                resources_result: Dict[str, Any] = {
                    "resources": [
                        {
                            "uri": "mcp://duckduckgo/search",
                            "name": "DuckDuckGo Search",
                            "description": "Web search via DuckDuckGo",
                        }
                    ]
                }
                yield create_sse_message("message", wrap_response(resources_result))

            elif method == "tools/list":
                # MCP tools listing
                tools_result: Dict[str, Any] = {
                    "tools": [
                        {
                            "name": "web_search",
                            "description": "Search the web using DuckDuckGo",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The search query",
                                    },
                                    "max_results": {
                                        "type": "integer",
                                        "description": "Maximum number of results (capped at 10)",
                                        "default": 5,
                                        "minimum": 1,
                                        "maximum": MAX_RESULTS_CAP,
                                    },
                                    "all_results": {
                                        "type": "boolean",
                                        "description": "Fetch maximum results (capped at 10)",
                                        "default": False,
                                    },
                                    "region": {
                                        "type": "string",
                                        "description": "Search region, e.g., wt-wt (global), us-en, uk-en",
                                        "default": "wt-wt",
                                    },
                                    "safesearch": {
                                        "type": "string",
                                        "description": "SafeSearch level: off | moderate | strict",
                                        "default": "moderate",
                                        "enum": ["off", "moderate", "strict"],
                                    },
                                    "timelimit": {
                                        "type": "string",
                                        "description": "Time limit for results: d (day), w (week), m (month), y (year)",
                                        "enum": ["d", "w", "m", "y"],
                                    },
                                },
                                "required": ["query"],
                            },
                        }
                    ]
                }
                yield create_sse_message("message", wrap_response(tools_result))

            elif method == "notifications/initialized":
                # LM Studio sends this after initialization - just acknowledge
                logger.info("Client initialized notification received")
                # No response needed for notifications (no id)

            elif method == "notifications/cancelled":
                # LM Studio sends this when aborting a request
                cancelled_id = params.get("requestId")
                reason = params.get("reason", "Unknown")
                logger.debug(f"Request {cancelled_id} was cancelled: {reason}")
                # No response needed for notifications (no id)

            elif method == "tools/call":
                # MCP tool calling
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "web_search":
                    query = arguments.get("query")
                    if not query:
                        if is_jsonrpc and request_id is not None:
                            yield create_sse_message(
                                "message",
                                {
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "error": {
                                        "code": -32602,
                                        "message": "query parameter is required",
                                    },
                                },
                            )
                        else:
                            yield create_sse_message(
                                "error", {"message": "query parameter is required"}
                            )
                        return

                    # Determine effective max results
                    all_results = bool(arguments.get("all_results", False))
                    if all_results:
                        effective_max = MAX_ALL_RESULTS_CAP
                    else:
                        try:
                            requested = int(arguments.get("max_results", 5))
                        except Exception:
                            requested = 5
                        effective_max = max(1, min(requested, MAX_RESULTS_CAP))

                    # Optional tuning parameters with sane defaults/validation
                    region = str(arguments.get("region", "wt-wt")).strip() or "wt-wt"
                    safesearch = str(arguments.get("safesearch", "moderate")).lower()
                    if safesearch not in {"off", "moderate", "strict"}:
                        safesearch = "moderate"
                    timelimit = arguments.get("timelimit")
                    if timelimit is not None:
                        timelimit = str(timelimit).lower()
                        if timelimit not in {"d", "w", "m", "y"}:
                            timelimit = None

                    logger.info(
                        f"Searching: {query} (effective_max={effective_max}, all_results={all_results}, region={region}, safesearch={safesearch}, timelimit={timelimit})"
                    )

                    # Perform search
                    try:
                        ddgs = DDGS()
                        # First try with enhanced parameters
                        try:
                            results_iter = ddgs.text(
                                query,
                                region=region,
                                safesearch=safesearch,
                                timelimit=timelimit,
                                max_results=effective_max,
                            )
                            raw_results = list(results_iter)
                        except TypeError as e:
                            # If library signature differs (unexpected kwargs), fallback to minimal call
                            if "unexpected keyword" in str(e) or "got an unexpected keyword argument" in str(e):
                                logger.warning(
                                    "duckduckgo_search param mismatch; falling back to default call"
                                )
                                raw_results = list(ddgs.text(query, max_results=effective_max))
                            # Handle duckduckgo_search library format errors
                            elif "datetime.timedelta" in str(e) or "unsupported format string" in str(e):
                                logger.warning(
                                    "duckduckgo_search format bug, returning empty results"
                                )
                                raw_results = []
                            else:
                                raise
                    except TypeError as e:
                        # Outer guard for known library issues
                        if "datetime.timedelta" in str(e) or "unsupported format string" in str(e):
                            logger.warning(
                                "duckduckgo_search format bug, returning empty results"
                            )
                            raw_results = []
                        else:
                            raise
                    except (ConnectionError, OSError, Exception) as e:
                        # Handle network/DNS errors gracefully
                        # Common in containerized or restricted network environments
                        error_str = str(e).lower()
                        if any(x in error_str for x in ["dns", "connection", "timeout", "refused", "unreachable"]):
                            logger.warning(
                                f"Network/DNS error during search (expected in some environments): {type(e).__name__}"
                            )
                            raw_results = []
                        else:
                            # Re-raise unexpected errors
                            raise

                    # Filter and deduplicate results
                    seen_hrefs = set()
                    results = []
                    for item in raw_results:
                        href = item.get("href", "").strip()
                        title = item.get("title", "").strip()
                        body = item.get("body", "").strip()

                        # Skip results without titles or bodies
                        if not title or not body:
                            continue

                        # Skip duplicates (by URL)
                        if href and href in seen_hrefs:
                            continue

                        if href:
                            seen_hrefs.add(href)

                        results.append(item)

                    if not results:
                        empty_result: Dict[str, Any] = {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"No results found for: {query}",
                                }
                            ]
                        }
                        yield create_sse_message("message", wrap_response(empty_result))
                    else:
                        # Format results as rich Markdown with improved presentation
                        lines = []
                        for i, item in enumerate(results, 1):
                            title = item.get("title", "No title").strip()
                            href = item.get("href", "").strip()
                            body = item.get("body", "").strip()

                            # Clean up body: remove extra whitespace, truncate long snippets
                            body = " ".join(body.split())
                            if len(body) > 200:
                                body = body[:197] + "..."

                            # Build enhanced result entry
                            if href:
                                # Link with domain hint for better context
                                try:
                                    domain = urlparse(href).netloc or "link"
                                except Exception:
                                    domain = "link"
                                line = f"**{i}. [{title}]({href})**\n   📍 {domain}\n   {body}"
                            else:
                                line = f"**{i}. {title}**\n   {body}"
                            lines.append(line)

                        # Build summary header
                        response_text = (
                            f"## Search Results for: _{query}_\n"
                            f"**Found {len(results)} result{'s' if len(results) != 1 else ''}**\n\n"
                            + "\n\n".join(lines)
                        )

                        result_data: Dict[str, Any] = {
                            "content": [{"type": "text", "text": response_text}]
                        }
                        yield create_sse_message("message", wrap_response(result_data))
                else:
                    error_result = {"message": f"Unknown tool: {tool_name}"}
                    if is_jsonrpc and request_id is not None:
                        yield create_sse_message(
                            "message",
                            {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "error": {
                                    "code": -32601,
                                    "message": f"Unknown tool: {tool_name}",
                                },
                            },
                        )
                    else:
                        yield create_sse_message("error", error_result)

            elif method is None:
                error_result = {"message": "No method specified in request"}
                if is_jsonrpc and request_id is not None:
                    yield create_sse_message(
                        "message",
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32600,
                                "message": "No method specified in request",
                            },
                        },
                    )
                else:
                    yield create_sse_message("error", error_result)
            else:
                error_result = {"message": f"Unknown method: {method}"}
                if is_jsonrpc and request_id is not None:
                    yield create_sse_message(
                        "message",
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Unknown method: {method}",
                            },
                        },
                    )
                else:
                    yield create_sse_message("error", error_result)

            # Always send completion
            yield create_sse_message("done", {})

        except Exception as e:
            logger.error(f"Error in event generator: {str(e)}", exc_info=True)
            yield create_sse_message("error", {"message": f"Error: {str(e)}"})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
