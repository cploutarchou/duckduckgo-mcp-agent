"""
Middleware for request tracking, logging, and metrics
"""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from logger import logger


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track requests and add request ID"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Track request start time
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration": f"{duration:.3f}s",
                },
            )

            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.3f}"

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "duration": f"{duration:.3f}s",
                },
                exc_info=True,
            )
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect metrics"""

    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
        self.total_duration = 0.0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        self.request_count += 1

        try:
            response = await call_next(request)

            # Track errors
            if response.status_code >= 400:
                self.error_count += 1

            # Track duration
            duration = time.time() - start_time
            self.total_duration += duration

            return response

        except Exception:
            self.error_count += 1
            duration = time.time() - start_time
            self.total_duration += duration
            raise
