import os
import asyncio
import json
from openai import AsyncOpenAI
from tools import web_search

_openai_client: AsyncOpenAI | None = None

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Busca informações atualizadas na internet sobre um tema. Use para pesquisar dados de mercado, concorrentes, tendências e estatísticas.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A consulta de busca em português ou inglês",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Número máximo de resultados (padrão: 5)",
                },
            },
            "required": ["query"],
        },
    },
}


def get_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            timeout=120.0,
        )
    return _openai_client


async def _create_with_retry(client, **kwargs):
    for attempt in range(5):
        try:
            return await client.chat.completions.create(**kwargs)
        except Exception as e:
            name = type(e).__name__
            if any(k in name for k in ("RateLimit", "Timeout", "Connection", "ServiceUnavailable")):
                wait = 2 ** attempt * 2
                await asyncio.sleep(wait)
            else:
                raise
    return await client.chat.completions.create(**kwargs)


async def run_agent_with_tools(
    system: str,
    user_message: str,
    max_iterations: int = 3,
    max_tokens: int = 1800,
    max_results: int = 3,
) -> str:
    client = get_client()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]

    for _ in range(max_iterations):
        response = await _create_with_retry(
            client,
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            messages=messages,
            tools=[SEARCH_TOOL],
            tool_choice="auto",
        )

        choice = response.choices[0]

        if choice.finish_reason == "stop":
            return choice.message.content or ""

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "web_search":
                    args = json.loads(tool_call.function.arguments)
                    results = await web_search.search(
                        query=args.get("query", ""),
                        max_results=args.get("max_results", max_results),
                    )
                    formatted = web_search.format_results(results)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": formatted,
                    })
        else:
            return choice.message.content or ""

    last = messages[-1]
    return last.get("content", "") if isinstance(last, dict) else ""


async def call_llm(system: str, user_message: str, max_tokens: int = 1024) -> str:
    client = get_client()
    response = await _create_with_retry(
        client,
        model="gpt-4o-mini",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""
