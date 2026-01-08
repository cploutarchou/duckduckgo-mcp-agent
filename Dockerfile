FROM python:3.10-slim as base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
	pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Production stage
FROM base as production
COPY . .
CMD ["python", "mcp_http_sse_server.py"]

# Development stage
FROM base as development
RUN pip install --no-cache-dir pytest pytest-asyncio httpx black ruff mypy
COPY . .
CMD ["python", "-m", "uvicorn", "mcp_http_sse_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
