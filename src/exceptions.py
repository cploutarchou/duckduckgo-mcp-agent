"""
Custom exception classes and error handlers for the MCP Web Search Agent.

This module defines a hierarchy of exceptions that represent different error
conditions and provides handlers that format errors consistently for API responses.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class MCPException(Exception):
    """
    Base exception class for the MCP application.

    All custom exceptions in this application inherit from this base class
    to maintain consistent error handling and formatting.

    Attributes:
        message: A human-readable error message.
        status_code: The HTTP status code to return (default: 500).
    """

    def __init__(self, message: str, status_code: int = 500) -> None:
        """
        Initialize the exception.

        Args:
            message: A clear description of what went wrong.
            status_code: The HTTP status code (default 500 for server errors).
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SearchException(MCPException):
    """
    Exception raised when a search operation fails.

    This is typically caused by network issues or DuckDuckGo API problems.
    Returns HTTP 503 (Service Unavailable) to the client.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the search exception.

        Args:
            message: A description of what went wrong during the search.
        """
        super().__init__(message, status_code=503)


class ValidationException(MCPException):
    """
    Exception raised when input validation fails.

    This occurs when a request contains invalid parameters that don't
    meet the required constraints. Returns HTTP 422 (Unprocessable Entity).
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the validation exception.

        Args:
            message: A description of what validation constraint was violated.
        """
        super().__init__(message, status_code=422)


class RateLimitException(MCPException):
    """
    Exception raised when a client exceeds the rate limit.

    The server enforces rate limiting to prevent abuse. Clients that make
    too many requests in a short time will receive this exception.
    Returns HTTP 429 (Too Many Requests).
    """

    def __init__(self, message: str = "You have exceeded the rate limit. Please try again later.") -> None:
        """
        Initialize the rate limit exception.

        Args:
            message: A message explaining the rate limit policy.
        """
        super().__init__(message, status_code=429)


async def mcp_exception_handler(request: Request, exc: MCPException) -> JSONResponse:
    """
    Handle custom MCP exceptions and format them as JSON responses.

    Args:
        request: The incoming HTTP request.
        exc: The exception that was raised.

    Returns:
        A JSON response with error details including the exception type,
        message, and the request path that caused the error.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "path": str(request.url),
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions that are not otherwise caught.

    This is a fallback handler for programming errors or unexpected
    conditions. Returns a generic error message to the client without
    exposing internal details.

    Args:
        request: The incoming HTTP request.
        exc: The unexpected exception that was raised.

    Returns:
        A JSON response with a generic error message.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred. Please try again later.",
                "path": str(request.url),
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions and format them as JSON responses.

    Args:
        request: The incoming HTTP request.
        exc: The HTTP exception that was raised.

    Returns:
        A JSON response with error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "path": str(request.url),
            }
        },
    )
