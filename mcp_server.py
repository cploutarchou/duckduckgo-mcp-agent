from typing import List

from duckduckgo_search import DDGS
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="MCP Web Search Agent")


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str


@app.post("/search", response_model=SearchResponse)
async def search_web(request: SearchRequest):
    """
    Search web using DuckDuckGo and return results
    """
    try:
        # Perform search with DuckDuckGo
        search_results = []

        # Use DuckDuckGo search with async capability
        ddgs = DDGS()
        results = ddgs.text(request.query, max_results=request.max_results)

        # Process results
        for result in results:
            search_results.append(
                SearchResult(
                    title=result.get("title", ""),
                    url=result.get("href", ""),
                    snippet=result.get("body", ""),
                )
            )

        return SearchResponse(results=search_results, query=request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
