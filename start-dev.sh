#!/bin/bash
# Development startup script with hot reload

set -e

echo "Starting MCP Web Search Agent in development mode..."

# Set development environment variables
export MCP_DEBUG=true
export MCP_ENVIRONMENT=development
export MCP_LOG_LEVEL=DEBUG
export MCP_WORKERS=1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run with uvicorn in development mode
echo "Starting development server with auto-reload..."
uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --reload --log-level debug
