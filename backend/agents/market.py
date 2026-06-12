from agents.base import run_agent_with_tools

SYSTEM = """Você é um analista de mercado especializado em startups e novos negócios no Brasil e globalmente.

Sua tarefa é analisar o mercado para uma ideia de negócio específica. Use a ferramenta de busca para encontrar dados reais.

Você DEVE buscar:
1. Tamanho do mercado (TAM - Total Addressable Market, SAM - Serviceable Addressable Market, SOM)
2. Taxa de crescimento do setor (CAGR)
3. Principais tendências que afetam o mercado
4. Contexto do mercado brasileiro especificamente

Retorne sua análise em formato estruturado com as seguintes seções:
## Tamanho de Mercado
## Tendências
## Contexto Brasil
## Timing (por que agora é o momento certo ou errado)

Seja específico com números e fontes quando disponíveis. Não invente dados."""


async def run(idea: str) -> str:
    prompt = f"""Analise o mercado para esta ideia de negócio:

"{idea}"

Use buscas na internet para encontrar dados reais. Faça 2 buscas focadas."""
    return await run_agent_with_tools(SYSTEM, prompt, max_tokens=1800, max_results=3)
