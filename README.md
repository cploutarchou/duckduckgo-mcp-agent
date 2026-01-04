# DuckDuckGo MCP Agent

A Model Context Protocol (MCP) server that integrates DuckDuckGo search capabilities with LLM Studio.

## Overview

This project provides an MCP server implementation that enables large language models to perform web searches using DuckDuckGo through LLM Studio integration. The server acts as a bridge between LLM applications and the DuckDuckGo search API.

## Features

- DuckDuckGo search integration
- MCP server implementation
- LLM Studio compatibility
- Docker support

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:

```bash
git clone https://github.com/cploutarchou/duckduckgo-mcp-agent.git
cd duckduckgo-mcp-agent
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the MCP Server

```bash
python mcp_server.py
```

### Docker

Build and run using Docker:

```bash
docker build -t duckduckgo-mcp-agent .
docker run duckduckgo-mcp-agent
```

## Project Structure

- `mcp_server.py` - Main MCP server implementation
- `llmstudio_integration.py` - LLM Studio integration module
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration

## Configuration

Configure your environment variables and settings in the respective Python files before running the server.

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
