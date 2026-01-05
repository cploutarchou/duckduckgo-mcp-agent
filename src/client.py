"""
MCP Web Search Agent Client Library.

A production-ready Python client for integrating the MCP Web Search Agent
with LM Studio and other language model applications. Provides automatic
retries, connection pooling, and error handling for reliable search operations.

This module includes:
- MCPWebSearchAgent: Full-featured HTTP client with retry logic
- get_search_context: Helper function for LLM integration
- Comprehensive error handling and timeout management
"""
import json
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MCPWebSearchAgent:
    """
    Production-ready client for MCP Web Search Agent integration.

    Provides a robust interface to the MCP Web Search Agent API with
    automatic retries, connection pooling, and comprehensive error handling.
    Can be used standalone or with context manager for automatic cleanup.

    Attributes:
        server_url: The base URL of the MCP server.
        timeout: Default request timeout in seconds.
        session: The requests session with retry strategy.

    Example:
        >>> with MCPWebSearchAgent() as agent:
        ...     results = agent.search("Python programming", max_results=5)
        ...     print(f"Found {results['count']} results")
    """

    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the MCP Web Search Agent client.

        Args:
            server_url: The base URL of the MCP server (default: localhost:8000).
            timeout: Default request timeout in seconds (default: 30).
            max_retries: Number of retries for failed requests (default: 3).
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout

        # Create HTTP session with retry strategy for resilience
        self.session = requests.Session()

        # Configure automatic retry strategy with exponential backoff
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy, pool_connections=10, pool_maxsize=20
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set standard headers for all requests
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "MCP-WebSearch-Client/1.0",
            }
        )

    def search(
        self, query: str, max_results: int = 5, timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Search the web using the MCP server.

        Performs a web search via the configured MCP server and returns
        the results along with metadata about the search operation.

        Args:
            query: The search query string (required, 1-500 characters).
            max_results: Maximum number of results to return (1-20, default: 5).
            timeout: Request timeout in seconds; overrides the default if provided.

        Returns:
            Dictionary containing:
                - results: List of search results with title, url, and snippet
                - query: The original search query
                - count: Number of results returned
                - cached: Whether results were served from cache
                - request_id: Unique identifier for this request

        Raises:
            ValueError: If the query is empty or max_results is out of range.
            TimeoutError: If the request exceeds the timeout period.
            ConnectionError: If unable to connect to the MCP server.
            Exception: For HTTP errors or other unexpected failures.

        Example:
            >>> results = agent.search("climate change", max_results=10)
            >>> for result in results['results']:
            ...     print(f"{result['title']} - {result['url']}")
        """
        if not query or not query.strip():
            raise ValueError("The search query cannot be empty.")

        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20.")

        timeout_val = timeout or self.timeout

        try:
            response = self.session.post(
                f"{self.server_url}/search",
                json={"query": query.strip(), "max_results": max_results},
                timeout=timeout_val,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Search request timed out after {timeout_val} seconds. "
                "Please try again with a longer timeout or simpler query."
            )

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Unable to connect to the MCP server at {self.server_url}. "
                f"Please ensure the server is running. Error: {str(e)}"
            )

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise Exception(
                    "Rate limit exceeded. Please wait before making another request."
                )
            elif e.response.status_code == 503:
                raise Exception("Search service is temporarily unavailable.")
            else:
                raise Exception(
                    f"HTTP error {e.response.status_code}: {e.response.text}"
                )

        except requests.exceptions.RequestException as e:
            raise Exception(f"Web search failed: {str(e)}")

    def health_check(self) -> dict[str, Any]:
        """
        Check the health status of the MCP server.

        Performs a quick health check to determine if the server is
        operational and ready to accept requests.

        Returns:
            Dictionary with health status information including:
                - status: Either "healthy" or "unhealthy"
                - timestamp: Server timestamp (if healthy)
                - service: Service name (if healthy)
                - error: Error message (if unhealthy)

        Example:
            >>> health = agent.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Server is ready!")
        """
        try:
            response = self.session.get(
                f"{self.server_url}/health", timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_metrics(self) -> dict[str, Any]:
        """
        Retrieve performance metrics from the MCP server.

        Gets detailed metrics about server performance including cache
        statistics, request counts, and configuration information.

        Returns:
            Dictionary containing server metrics such as:
                - uptime: Server uptime information
                - cache: Cache hit/miss statistics
                - settings: Current configuration settings

        Raises:
            Exception: If metrics cannot be retrieved from the server.

        Example:
            >>> metrics = agent.get_metrics()
            >>> print(f"Cache stats: {metrics['cache']}")
        """
        try:
            response = self.session.get(
                f"{self.server_url}/metrics", timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to retrieve server metrics: {str(e)}")

    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.

        Should be called when the client is no longer needed, or use
        the context manager to automatically handle this.
        """
        self.session.close()

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point with automatic cleanup."""
        self.close()


def get_search_context(
    query: str,
    max_results: int = 3,
    server_url: str = "http://localhost:8000",
) -> str:
    """
    Format search results for language model consumption.

    A helper function that performs a web search and formats the results
    into a readable context suitable for feeding to a language model.
    Includes cache information and properly formatted result snippets.

    Args:
        query: The search query to execute.
        max_results: Number of results to retrieve (default: 3).
        server_url: URL of the MCP server (default: localhost:8000).

    Returns:
        A formatted string containing the search results, ready for
        inclusion in a language model's context window. Includes the
        query, number of results, and detailed information for each
        result (title, URL, and snippet).

    Example:
        >>> context = get_search_context("machine learning algorithms")
        >>> llm_prompt = f"Please answer this based on: {context}"
    """
    with MCPWebSearchAgent(server_url=server_url) as agent:
        try:
            # Verify server health before attempting search
            health = agent.health_check()
            if health.get("status") != "healthy":
                return (
                    f"Search service is currently unavailable. "
                    f"Error: {health.get('error', 'Unknown error')}"
                )

            # Perform the web search
            search_results = agent.search(query, max_results=max_results)

            # Add cached note if results came from cache
            cached_note = " (from cache)" if search_results.get(
                "cached", False) else ""

            # Format search results for language model
            context = f"Search Results for: '{query}'{cached_note}\n"
            context += f"Total Results: {search_results.get('count', 0)}\n\n"

            for i, result in enumerate(search_results["results"], 1):
                context += f"{i}. {result['title']}\n"
                context += f"   URL: {result['url']}\n"
                context += f"   Summary: {result['snippet']}\n\n"

            return context

        except TimeoutError as e:
            return f"Search timeout: {str(e)} Please try again."
        except ConnectionError as e:
            return f"Connection error: {str(e)} Is the server running?"
        except Exception as e:
            return f"Search failed: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic search with context manager
    print("=" * 60)
    print("Example 1: Performing a basic web search")
    print("=" * 60 + "\n")

    with MCPWebSearchAgent() as agent:
        try:
            # Check server health
            health = agent.health_check()
            print(f"Server Status: {health.get('status', 'unknown')}\n")

            # Execute search
            results = agent.search("Python web frameworks", max_results=3)
            print(f"Query: {results['query']}")
            print(f"Results Found: {results['count']}")
            print(f"From Cache: {results.get('cached', False)}\n")
            print(json.dumps(results, indent=2))

        except Exception as e:
            print(f"Error during search: {e}")

    # Example 2: Generate formatted context for LLM
    print("\n" + "=" * 60)
    print("Example 2: Formatted context for language models")
    print("=" * 60 + "\n")

    context = get_search_context(
        "distributed systems architecture", max_results=3)
    print(context)

    # Example 3: Retrieve and display server metrics
    print("\n" + "=" * 60)
    print("Example 3: Server performance metrics")
    print("=" * 60 + "\n")

    with MCPWebSearchAgent() as agent:
        try:
            metrics = agent.get_metrics()
            print(json.dumps(metrics, indent=2))
        except Exception as e:
            print(f"Error retrieving metrics: {e}")
