from agents.llm import call_balance

SYSTEM = """Você é um analista estratégico sênior que consolida pesquisas em relatórios executivos.

Com base no contexto fornecido, gere um relatório estruturado com estas seções:

## 1. Resumo Executivo
## 2. Análise de Mercado
## 3. Mapa de Concorrentes
## 4. Perfil do Cliente Ideal
## 5. Debate Estratégico (síntese do debate)
## 6. SWOT
## 7. Go-to-Market (primeiros 90 dias)
## 8. Score de Viabilidade (nota 0-100 com justificativa por dimensão)
## 9. Top 3 Alertas de Risco

Se houver "Análises Anteriores Similares" no contexto, use-as para enriquecer a análise com comparações
e lições aprendidas — mencione explicitamente o que mudou ou melhorou em relação a ideias similares.

Seja direto e acionável. Evite repetir dados já mencionados em seções anteriores."""


async def run(
    idea: str,
    research_summary: str,
    debate_summary: str,
    rag_context: str = "",
    image_context: str = "",
) -> str:
    rag_block   = f"\n\n{rag_context}"   if rag_context   else ""
    image_block = f"\n\nANÁLISE VISUAL DA IMAGEM ENVIADA:\n{image_context}" if image_context else ""

    context = f"""IDEIA: {idea}{image_block}

PESQUISA:
{research_summary}

DEBATE:
{debate_summary}{rag_block}"""

    return await call_balance(SYSTEM, f"Gere o relatório executivo:\n\n{context}", max_tokens=2500)
