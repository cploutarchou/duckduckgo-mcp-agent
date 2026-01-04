import json
from typing import Any, Dict

import requests


class MCPWebSearchAgent:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search web using MCP server
        """
        try:
            response = self.session.post(
                f"{self.server_url}/search",
                json={"query": query, "max_results": max_results},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to search: {str(e)}")


# Example usage in LLmStudio context
def get_search_context(query: str) -> str:
    """
    Format search results for LLM consumption
    """
    agent = MCPWebSearchAgent()
    try:
        search_results = agent.search(query, max_results=3)

        # Format results for LLM
        context = f"Search results for '{query}':\n"
        for i, result in enumerate(search_results["results"], 1):
            context += f"\n{i}. {result['title']}\n"
            context += f"   URL: {result['url']}\n"
            context += f"   Snippet: {result['snippet']}\n"

        return context
    except Exception as e:
        return f"Search error: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Test the agent
    agent = MCPWebSearchAgent()

    # Perform search
    results = agent.search("Python programming", max_results=3)
    print(json.dumps(results, indent=2))
