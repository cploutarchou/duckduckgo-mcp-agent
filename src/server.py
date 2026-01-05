"""
Production-ready MCP Web Search Agent.

A FastAPI application that provides web search capabilities through the
DuckDuckGo API. Features include caching, rate limiting, structured logging,
and comprehensive error handling.

The application follows Model Context Protocol (MCP) standards and is designed
to integrate with LM Studio for adding search capabilities to language models.
"""
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from duckduckgo_search import DDGS
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from cache import cache
from config import Settings, get_settings
from exceptions import (
    MCPException,
    SearchException,
    ValidationException,
    general_exception_handler,
    http_exception_handler,
    mcp_exception_handler,
)
from logger import logger
from middleware import MetricsMiddleware, RequestTrackingMiddleware

# Suppress verbose logging from the DuckDuckGo search library
logging.getLogger("duckduckgo_search").setLevel(logging.CRITICAL)
logging.getLogger("duckduckgo_search.duckduckgo_search_async").setLevel(
    logging.CRITICAL
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifecycle.

    This context manager handles startup and shutdown events for the
    FastAPI application. On startup, it logs the application version
    and environment. On shutdown, it clears any cached data.

    Args:
        app: The FastAPI application instance.
    """
    settings = get_settings()
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version}",
        extra={"environment": settings.environment},
    )
    yield
    logger.info("Shutting down application")
    cache.clear()


# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create the FastAPI application instance
app = FastAPI(
    title="MCP Web Search Agent",
    version="1.0.0",
    description="Production-ready web search API using DuckDuckGo",
    lifespan=lifespan,
)

# Attach the rate limiter to the app state
app.state.limiter = limiter

# Register exception handlers for consistent error responses
app.add_exception_handler(MCPException, mcp_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """
    Configure application middleware.

    Sets up CORS, request tracking, and metrics collection middleware
    based on the application settings.

    Args:
        app: The FastAPI application instance.
        settings: The application settings.
    """
    # Configure CORS (Cross-Origin Resource Sharing)
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add request tracking middleware for logging and monitoring
    app.add_middleware(RequestTrackingMiddleware)

    # Add metrics collection middleware
    app.add_middleware(MetricsMiddleware)


# Initialize middleware
setup_middleware(app, get_settings())


class SearchRequest(BaseModel):
    """
    Request model for web search operations.

    Attributes:
        query: The search query (1-500 characters).
        max_results: Number of results to return (1-20, default 5).
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The search query to execute",
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results to return",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        """
        Validate and clean the search query.

        Removes leading and trailing whitespace and ensures the query
        is not empty after trimming.

        Args:
            value: The query to validate.

        Returns:
            The cleaned and validated query.

        Raises:
            ValidationException: If the query is empty after trimming.
        """
        value = value.strip()
        if not value:
            raise ValidationException("The search query cannot be empty.")
        return value


class SearchResult(BaseModel):
    """
    A single search result.

    Attributes:
        title: The title of the search result.
        url: The URL of the result page.
        snippet: A brief text excerpt from the result.
    """

    title: str
    url: str
    snippet: str


class SearchResponse(BaseModel):
    """
    Response model for web search operations.

    Attributes:
        results: List of search results found.
        query: The original search query.
        count: Number of results returned.
        cached: Whether the results were served from cache.
        request_id: Unique identifier for tracking the request.
    """

    results: list[SearchResult]
    query: str
    count: int
    cached: bool = False
    request_id: Optional[str] = None


@app.post("/search", response_model=SearchResponse)
@limiter.limit("20/minute")
async def search_web(
    request: Request,
    search_request: SearchRequest,
    settings: Settings = Depends(get_settings),
) -> SearchResponse:
    """
    Execute a web search using DuckDuckGo.

    Searches the web using the provided query and returns up to max_results
    results. Results are cached for 1 hour to improve performance. Requests
    are rate-limited to 20 per minute per IP address.

    Args:
        request: The FastAPI request object (used for tracking).
        search_request: The search request containing query and max_results.
        settings: Application settings (injected dependency).

    Returns:
        SearchResponse containing search results, query info, and metadata.

    Raises:
        SearchException: If the DuckDuckGo API call fails.
        ValidationException: If the search request is invalid.
        HTTPException: For unexpected server errors.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # Check if results are already cached
        cached_result = cache.get(
            search_request.query, search_request.max_results
        )
        if cached_result:
            logger.info(
                f"Returning cached results for query: {search_request.query}",
                extra={"request_id": request_id},
            )
            cached_result["cached"] = True
            cached_result["request_id"] = request_id
            return SearchResponse(**cached_result)

        # Log the search request
        logger.info(
            f"Executing search for query: {search_request.query}",
            extra={
                "request_id": request_id,
                "max_results": search_request.max_results,
            },
        )

        search_results = []
        ddgs = DDGS()

        # Perform the search
        try:
            results = ddgs.text(
                search_request.query, max_results=search_request.max_results
            )

            # Convert search results to our model format
            for result in results:
                search_results.append(
                    SearchResult(
                        title=result.get("title", ""),
                        url=result.get("href", ""),
                        snippet=result.get("body", ""),
                    )
                )

        except Exception as e:
            logger.error(
                f"DuckDuckGo API request failed: {str(e)}",
                extra={"request_id": request_id,
                       "query": search_request.query},
                exc_info=True,
            )
            raise SearchException(f"Web search failed: {str(e)}")

        # Build the response
        response_data = {
            "results": search_results,
            "query": search_request.query,
            "count": len(search_results),
            "cached": False,
            "request_id": request_id,
        }

        # Cache the results for future requests
        cache.set(search_request.query,
                  search_request.max_results, response_data)

        logger.info(
            f"Search successful: found {len(search_results)} results",
            extra={"request_id": request_id},
        )

        return SearchResponse(**response_data)

    except SearchException:
        raise
    except ValidationException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during web search: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check() -> dict:
    """
    Check the health status of the application.

    This endpoint performs a basic health check and returns the current
    server status, timestamp, and service name.

    Returns:
        A dictionary containing status, current timestamp, and service name.
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "mcp-web-search-agent",
    }


@app.get("/metrics")
async def get_metrics(request: Request) -> dict:
    """
    Retrieve application performance metrics.

    Returns current metrics including request counts, error counts,
    and cache performance statistics.

    Args:
        request: The FastAPI request object.

    Returns:
        A dictionary containing metrics such as total requests, errors,
        and cache hit/miss statistics.
    """
    # Return basic metrics and cache statistics
    metrics_data = {
        "uptime": time.time(),
        "cache": cache.get_stats(),
        "settings": {
            "rate_limit_enabled": get_settings().rate_limit_enabled,
            "cache_enabled": get_settings().cache_enabled,
            "environment": get_settings().environment,
        },
    }

    return metrics_data


@app.get("/ready")
async def readiness_check() -> dict:
    """
    Check if the service is ready to accept requests.

    Performs a connectivity test with the DuckDuckGo API to ensure
    the service can handle search requests.

    Returns:
        A dictionary indicating the service readiness status and
        health of external service dependencies.

    Raises:
        HTTPException: If any critical service dependency is unavailable.
    """
    try:
        # Test DuckDuckGo connectivity with a simple query
        ddgs = DDGS()
        test_results = ddgs.text("test", max_results=1)
        return {"status": "ready", "checks": {"duckduckgo": "ok"}}
    except Exception as e:
        logger.error(
            f"Readiness check failed - DuckDuckGo connection error: {str(e)}"
        )
        raise HTTPException(
            status_code=503,
            detail="Service not ready: Unable to reach DuckDuckGo API",
        )


@app.post("/cache/clear")
async def clear_cache() -> dict:
    """
    Clear all cached search results.

    Removes all results from the in-memory cache. Note that in a
    production environment, this endpoint should be protected with
    authentication and authorization.

    Returns:
        A dictionary indicating the operation was successful.
    """
    cache.clear()
    logger.info("Cache cleared by administrator")
    return {"status": "success", "message": "All cached results have been cleared"}


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "mcp_server:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if settings.environment == "production" else 1,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
    )
