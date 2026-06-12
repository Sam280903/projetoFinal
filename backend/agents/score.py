from agents.llm import call_fast

SYSTEM = """Você é um analista que avalia a viabilidade de ideias de negócio.

Com base no resumo da pesquisa fornecido, gere APENAS um JSON com scores de 0-100 para cada dimensão.

Responda SOMENTE com o JSON, sem texto adicional, no formato exato:
{"overall": 72, "dimensions": {"mercado": 80, "competicao": 65, "execucao": 70, "timing": 75, "monetizacao": 68, "inovacao": 72}}

Critérios:
- mercado: tamanho e crescimento do mercado (TAM/SAM)
- competicao: facilidade de diferenciação frente aos concorrentes
- execucao: viabilidade técnica e operacional
- timing: momento de mercado (por que agora?)
- monetizacao: clareza do modelo de receita
- inovacao: originalidade e diferencial da solução"""


async def run(idea: str, research_summary: str) -> str:
    """Gera apenas o JSON de score — rápido e focado."""
    prompt = f"""Ideia: "{idea}"

Resumo da pesquisa:
{research_summary[:2000]}

Gere o JSON de score."""
    return await call_fast(SYSTEM, prompt, max_tokens=150)
