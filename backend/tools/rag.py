"""
RAG (Retrieval-Augmented Generation) — encontra análises passadas similares
para enriquecer novas sínteses com contexto histórico.
"""
import os
import json
import numpy as np
from openai import AsyncOpenAI

from tools.persistence import DATA_DIR, load_session, list_sessions

_client: AsyncOpenAI | None = None


def _openai() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    return _client


async def embed(text: str) -> list[float]:
    resp = await _openai().embeddings.create(
        model="text-embedding-3-small",
        input=text[:3000],
    )
    return resp.data[0].embedding


def _cosine(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    norm = np.linalg.norm(va) * np.linalg.norm(vb)
    if norm == 0:
        return 0.0
    return float(np.dot(va, vb) / norm)


async def find_similar(
    idea: str,
    exclude_session_id: str | None = None,
    top_k: int = 3,
    min_similarity: float = 0.45,
) -> list[dict]:
    """
    Retorna até top_k análises passadas similares à ideia.
    Cada item: {session_id, idea, score, similarity, summary}
    """
    query_emb = await embed(idea)
    candidates = []

    for info in list_sessions(limit=200):
        sid = info["session_id"]
        if sid == exclude_session_id:
            continue
        session = load_session(sid)
        if not session or "embedding" not in session:
            continue
        sim = _cosine(query_emb, session["embedding"])
        if sim >= min_similarity:
            # Extrai score numérico
            raw_score = session.get("score")
            score_val = None
            if isinstance(raw_score, dict):
                score_val = raw_score.get("overall")
            elif isinstance(raw_score, str):
                try:
                    score_val = json.loads(raw_score).get("overall")
                except Exception:
                    pass

            # Resumo curto do relatório
            report = session.get("report", "")
            summary = report[:600].strip() if report else ""

            candidates.append({
                "session_id": sid,
                "idea": session.get("idea", ""),
                "score": score_val,
                "similarity": round(sim, 3),
                "summary": summary,
                "timestamp": session.get("timestamp", ""),
            })

    candidates.sort(key=lambda x: x["similarity"], reverse=True)
    return candidates[:top_k]


def build_rag_context(similar: list[dict]) -> str:
    """Formata ideias similares como contexto para o agente de síntese."""
    if not similar:
        return ""
    parts = ["## Análises Anteriores Similares (contexto RAG)\n"]
    for i, s in enumerate(similar, 1):
        score_str = f"Score: {s['score']}/100" if s["score"] else "Score: N/A"
        parts.append(
            f"### Ideia similar {i} ({int(s['similarity'] * 100)}% de semelhança) — {score_str}\n"
            f"Ideia: {s['idea']}\n"
            f"Resumo: {s['summary'][:400]}\n"
        )
    return "\n".join(parts)
