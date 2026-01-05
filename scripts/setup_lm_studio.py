#!/usr/bin/env python3
"""
MCP Server Configuration for LM Studio
This script helps configure and test the MCP server connection with LM Studio
"""

import json
import sys
from pathlib import Path


def create_lm_studio_config(server_url: str = "http://localhost:8000") -> dict:
    """Create configuration for LM Studio integration"""

    config = {
        "mcpServers": {
            "duckduckgo-search": {
                "command": "python",
                "args": [str(Path(__file__).parent / "mcp_server.py")],
                "disabled": False,
                "alwaysAllow": [],
                "env": {
                    "MCP_ENVIRONMENT": "production",
                    "MCP_HOST": "0.0.0.0",
                    "MCP_PORT": "8000",
                    "MCP_LOG_LEVEL": "INFO",
                    "MCP_WORKERS": "2",
                    "MCP_CACHE_ENABLED": "true",
                    "MCP_RATE_LIMIT_ENABLED": "true"
                },
                "metadata": {
                    "name": "DuckDuckGo Web Search",
                    "version": "1.0.0",
                    "description": "Web search capabilities using DuckDuckGo"
                }
            }
        }
    }

    return config


def create_vscode_settings(server_url: str = "http://localhost:8000") -> dict:
    """Create VS Code settings for MCP configuration"""

    return {
        "[python]": {
            "editor.defaultFormatter": "ms-python.black-formatter"
        },
        "mcp.servers": {
            "duckduckgo-search": {
                "command": "python",
                "args": ["mcp_server.py"],
                "cwd": "${workspaceFolder}",
                "env": {
                    "MCP_ENVIRONMENT": "development",
                    "MCP_PORT": "8000"
                }
            }
        }
    }


def print_lm_studio_setup(server_url: str = "http://localhost:8000"):
    """Print setup instructions for LM Studio"""

    print("\n" + "=" * 70)
    print("LM STUDIO - MCP SERVER SETUP INSTRUCTIONS")
    print("=" * 70)

    print(f"""
🔧 MCP Server Configuration for LM Studio

📍 Server URL: {server_url}
📍 API Docs: {server_url}/docs
📍 Health Check: {server_url}/health

OPTION 1: Direct Server URL Connection
────────────────────────────────────────
In LM Studio:
1. Click Settings ⚙️ (bottom left)
2. Go to "Model Context Protocol" tab
3. Click "Add Model Context Protocol Server"
4. Enter:
   - Name: "DuckDuckGo Web Search"
   - Type: "HTTP Server"
   - URL: {server_url}
5. Click "Test Connection" to verify
6. Save settings

OPTION 2: Local Server Execution
────────────────────────────────────────
In LM Studio:
1. Click Settings ⚙️ (bottom left)
2. Go to "Model Context Protocol" tab
3. Click "Add Model Context Protocol Server"
4. Enter:
   - Name: "DuckDuckGo Web Search"
   - Type: "Direct"
   - Command: python
   - Args: ["{Path(__file__).parent / 'mcp_server.py'}"]
5. Click "Test Connection" to verify
6. Save settings

OPTION 3: Docker Container
────────────────────────────────────────
1. Build Docker image:
   docker build -t mcp-web-search .

2. Run container:
   docker run -d -p 8000:8000 --name mcp-web-search mcp-web-search

3. In LM Studio:
   - Name: "DuckDuckGo Web Search"
   - URL: http://localhost:8000

API ENDPOINTS
────────────────────────────────────────
POST   {server_url}/search          - Search the web
GET    {server_url}/health          - Health check
GET    {server_url}/ready           - Readiness probe
GET    {server_url}/metrics         - Server metrics
GET    {server_url}/docs            - API documentation

USING IN LM STUDIO PROMPTS
────────────────────────────────────────
Once configured, you can use the search in prompts:

"Use the DuckDuckGo Search MCP to:
- Search for 'latest AI breakthroughs'
- Summarize the top 3 results"

The MCP server will automatically:
✓ Search DuckDuckGo
✓ Cache results (1 hour TTL)
✓ Rate limit requests (20/minute)
✓ Track all interactions
✓ Return formatted JSON

TROUBLESHOOTING
────────────────────────────────────────
If connection fails:
1. Verify server is running:
   curl {server_url}/health

2. Check firewall rules (port 8000)

3. For remote access (127.0.0.1):
   - Server must be accessible from LM Studio
   - Update URL to: http://127.0.0.1:8000

4. Check logs:
   tail -f server.log

ENVIRONMENT VARIABLES
────────────────────────────────────────
MCP_HOST              = 0.0.0.0
MCP_PORT              = 8000
MCP_WORKERS           = 2
MCP_CACHE_ENABLED     = true
MCP_RATE_LIMIT_ENABLED = true
MCP_LOG_LEVEL         = INFO
MCP_ENVIRONMENT       = production

SECURITY NOTES
────────────────────────────────────────
⚠️  By default, CORS allows all origins (*)
⚠️  Rate limiting: 20 requests/minute per IP
⚠️  No authentication required (add if needed)

For production:
- Configure CORS_ORIGINS in .env
- Add API key authentication
- Use HTTPS with reverse proxy
- Set up firewall rules

SUPPORT & DOCUMENTATION
────────────────────────────────────────
📚 README.md           - Full documentation
📚 DEPLOYMENT.md       - Production setup
📚 QUICKSTART.md       - Quick start guide
📝 API Docs: {server_url}/docs
""")


def main():
    """Main configuration function"""

    server_url = "http://localhost:8000"

    if len(sys.argv) > 1:
        server_url = sys.argv[1]

    # Print setup instructions
    print_lm_studio_setup(server_url)

    # Generate config files
    print("\n" + "=" * 70)
    print("GENERATED CONFIGURATION FILES")
    print("=" * 70)

    # LM Studio config
    lm_config = create_lm_studio_config(server_url)
    print("\n1. LM Studio Configuration:")
    print(json.dumps(lm_config, indent=2))

    # VS Code settings
    vscode_config = create_vscode_settings(server_url)
    print("\n2. VS Code Settings (.vscode/settings.json):")
    print(json.dumps(vscode_config, indent=2))

    print("\n" + "=" * 70)
    print("✅ Configuration Ready!")
    print("=" * 70)


if __name__ == "__main__":
    main()
