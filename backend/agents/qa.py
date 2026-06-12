from agents.llm import call_fast

SYSTEM = """Você é um assistente estratégico que responde perguntas baseando-se EXCLUSIVAMENTE no relatório de análise fornecido.

Regras:
- Responda apenas com base nos dados do relatório. Não invente informações novas.
- Se a pergunta não puder ser respondida com os dados do relatório, diga claramente: "Esta informação não foi coberta na análise."
- Seja conciso: máximo 200 palavras por resposta.
- Cite a seção do relatório quando relevante.
- Você pode fazer inferências lógicas a partir dos dados, mas sempre deixe claro que é uma inferência."""


async def answer(question: str, report: str, idea: str) -> str:
    prompt = f"""Ideia de negócio analisada: "{idea}"

RELATÓRIO DE ANÁLISE:
{report}

PERGUNTA DO USUÁRIO:
{question}"""
    return await call_fast(SYSTEM, prompt, max_tokens=512)
