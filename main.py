#!/usr/bin/env python3
"""
MCP Web Search Agent - Main Entry Point.

This is the main entry point for running the MCP Web Search Agent server.
It provides a simple interface to start the FastAPI application with
production-ready settings.

Usage:
    python main.py                    # Start with default settings
    python main.py --host 0.0.0.0     # Bind to all interfaces
    python main.py --port 8080        # Use custom port
    python main.py --workers 4        # Use multiple workers
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    import uvicorn

    from config import get_settings

    settings = get_settings()

    print("=" * 70)
    print(f"  🚀 Starting {settings.app_name} v{settings.app_version}")
    print("=" * 70)
    print(f"  Environment: {settings.environment}")
    print(f"  Host: {settings.host}")
    print(f"  Port: {settings.port}")
    print(f"  Workers: {settings.workers}")
    print(f"  Debug Mode: {settings.debug}")
    print(
        f"  Rate Limiting: {'Enabled' if settings.rate_limit_enabled else 'Disabled'}")
    print(f"  Caching: {'Enabled' if settings.cache_enabled else 'Disabled'}")
    print("=" * 70)

    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if settings.environment == "production" else 1,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
    )
