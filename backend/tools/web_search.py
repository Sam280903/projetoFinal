import os
from tavily import TavilyClient

_client: TavilyClient | None = None


def get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))
    return _client


async def search(query: str, max_results: int = 5) -> list[dict]:
    client = get_client()
    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
        )
        return response.get("results", [])
    except Exception as e:
        return [{"title": "Erro na busca", "content": str(e), "url": ""}]


def format_results(results: list[dict]) -> str:
    if not results:
        return "Nenhum resultado encontrado."
    parts = []
    for r in results:
        parts.append(f"**{r.get('title', '')}**\n{r.get('content', '')}\nFonte: {r.get('url', '')}")
    return "\n\n---\n\n".join(parts)
