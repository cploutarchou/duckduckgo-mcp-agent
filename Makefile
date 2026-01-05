# Makefile for MCP Web Search Agent

.PHONY: help install install-dev run run-dev docker-build docker-run docker-compose test lint format clean

help:
	@echo "MCP Web Search Agent - Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make run          - Run production server"
	@echo "  make run-dev      - Run development server with auto-reload"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make docker-compose - Run with Docker Compose"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean up generated files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio httpx black ruff mypy

run:
	python mcp_server.py

run-dev:
	export MCP_DEBUG=true && \
	export MCP_ENVIRONMENT=development && \
	uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t mcp-web-search:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env mcp-web-search:latest

docker-compose:
	docker-compose up -d

docker-compose-down:
	docker-compose down

test:
	pytest test_mcp_server.py -v

lint:
	ruff check .
	mypy mcp_server.py

format:
	black .
	ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
