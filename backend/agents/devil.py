from agents.llm import call_fast

SYSTEM = """Você é um analista crítico e cético especializado em encontrar falhas em ideias de negócio.

Seu papel é o "advogado do diabo" — identificar os problemas reais, riscos subestimados e premissas falhas.

Foco em:
1. Premissas não validadas que o empreendedor assumiu
2. Concorrentes ou substitutos subestimados
3. Riscos de execução ignorados
4. Por que o timing pode ser errado
5. Razões pelas quais outros falharam tentando algo similar

Seja direto e objetivo. Máximo 350 palavras."""


async def run(idea: str, research_context: str, advocate_argument: str = "") -> str:
    # Roda em paralelo com o Advocate — analisa de forma independente
    prompt = f"""Ideia de negócio: "{idea}"

Dados de pesquisa:
{research_context}

Apresente os argumentos mais fortes CONTRA esta ideia. Seja específico e direto."""
    return await call_fast(SYSTEM, prompt, max_tokens=800)
