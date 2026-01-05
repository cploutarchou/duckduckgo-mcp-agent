"""
Structured logging configuration for production deployments.

This module sets up JSON-formatted logging that is suitable for production
environments and log aggregation systems. All log entries include structured
metadata for better searchability and analysis.
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from config import get_settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging output.

    Converts log records into JSON format, making them suitable for
    ingestion by log aggregation systems like ELK Stack, Splunk, or Datadog.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            A JSON string containing the log entry and all metadata.
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add optional metadata fields if present in the record
        if hasattr(record, "request_id") and record.request_id:
            log_data["request_id"] = str(record.request_id)
        if hasattr(record, "user_id") and record.user_id:
            log_data["user_id"] = str(record.user_id)
        if hasattr(record, "duration") and record.duration:
            log_data["duration"] = str(record.duration)
        if hasattr(record, "status_code") and record.status_code:
            log_data["status_code"] = record.status_code
        if hasattr(record, "method") and record.method:
            log_data["method"] = str(record.method)
        if hasattr(record, "path") and record.path:
            log_data["path"] = str(record.path)
        if hasattr(record, "client") and record.client:
            log_data["client"] = str(record.client)

        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """
    Configure the logging system for the application.

    Sets up handlers and formatters based on the configuration settings.
    Supports both JSON and plain text log formats, with optional file output.

    Returns:
        The configured logger instance for the application.
    """
    settings = get_settings()

    # Create and configure the logger
    logger = logging.getLogger("mcp_server")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove any existing handlers to avoid duplicates
    logger.handlers = []

    # Set up console output handler
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Set up file output handler if configured
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file)
        if settings.log_format == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create the global logger instance
logger = setup_logging()
