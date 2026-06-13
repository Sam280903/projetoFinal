import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator
from agents import market, competitor, audience, risk, advocate, devil, mediator, synthesis, score, qa
from tools import persistence, rag

# Sessões em memória (cache para a sessão ativa)
_sessions: dict[str, dict] = {}

_RESEARCH_TRUNCATE = 1200
_DEBATE_TRUNCATE   = 800


def _trunc(text: str, limit: int) -> str:
    return text[:limit] + "…" if len(text) > limit else text


def _research_summary(research: dict) -> str:
    labels = {
        "market":     "MERCADO",
        "competitor": "CONCORRENTES",
        "audience":   "CLIENTE",
        "risk":       "RISCOS",
    }
    parts = []
    for key, label in labels.items():
        if key in research:
            parts.append(f"[{label}]\n{_trunc(research[key], _RESEARCH_TRUNCATE)}")
    return "\n\n".join(parts)


def _debate_summary(debate: dict) -> str:
    parts = []
    if "advocate" in debate:
        parts.append(f"[DEFENSOR]\n{_trunc(debate['advocate'], _DEBATE_TRUNCATE)}")
    if "devil" in debate:
        parts.append(f"[CRITICO]\n{_trunc(debate['devil'], _DEBATE_TRUNCATE)}")
    if "mediator" in debate:
        parts.append(f"[MEDIADOR]\n{_trunc(debate['mediator'], _DEBATE_TRUNCATE)}")
    return "\n\n".join(parts)


def _event(agent_name: str, status: str, data: str = "") -> str:
    payload = json.dumps({"agent": agent_name, "status": status, "data": data})
    return f"data: {payload}\n\n"


async def _persist_session(session_id: str, session: dict) -> None:
    """Salva sessão em disco com embedding da ideia para RAG."""
    try:
        embedding = await rag.embed(session.get("idea", ""))
        to_save = {
            "idea":      session.get("idea", ""),
            "report":    session.get("report", ""),
            "score":     session.get("score"),
            "debate":    session.get("debate"),
            "timestamp": datetime.now().isoformat(),
            "embedding": embedding,
        }
        persistence.save_session(session_id, to_save)
    except Exception as e:
        print(f"[persistence] Erro ao salvar sessão {session_id}: {e}")


async def run_pipeline(idea: str, session_id: str, image_context: str | None = None) -> AsyncGenerator[str, None]:
    session = {"idea": idea, "research": {}, "report": None, "debate": None, "score": None}
    _sessions[session_id] = session

    # Emite contexto visual se houver imagem
    if image_context:
        yield _event("vision", "done", image_context)

    # Tenta carregar sessão persistida (retomada após restart)
    saved = persistence.load_session(session_id)
    if saved:
        _sessions[session_id].update({
            "report": saved.get("report"),
            "debate": saved.get("debate"),
            "score":  saved.get("score"),
        })

    # ── FASE 1: Pesquisa em paralelo + heartbeat ──────────────────────────────
    yield _event("market",     "running")
    yield _event("competitor", "running")
    yield _event("audience",   "running")
    yield _event("risk",       "running")

    t_market     = asyncio.create_task(market.run(idea))
    t_competitor = asyncio.create_task(competitor.run(idea))
    t_audience   = asyncio.create_task(audience.run(idea))
    t_risk       = asyncio.create_task(risk.run(idea))

    # RAG em paralelo com a pesquisa — sem custo de latência extra
    t_similar = asyncio.create_task(
        rag.find_similar(idea, exclude_session_id=session_id, top_k=3)
    )

    pending = {t_market, t_competitor, t_audience, t_risk}
    while pending:
        _, pending = await asyncio.wait(pending, timeout=20)
        if pending:
            yield ": ping\n\n"

    def _safe_result(task, name: str) -> str:
        try:
            return task.result()
        except Exception as e:
            return f"[Erro no agente {name}: {type(e).__name__}: {e}]"

    results = [
        _safe_result(t_market,     "market"),
        _safe_result(t_competitor, "competitor"),
        _safe_result(t_audience,   "audience"),
        _safe_result(t_risk,       "risk"),
    ]

    session["research"] = {
        "market":     results[0],
        "competitor": results[1],
        "audience":   results[2],
        "risk":       results[3],
    }

    yield _event("market",     "done", results[0])
    yield _event("competitor", "done", results[1])
    yield _event("audience",   "done", results[2])
    yield _event("risk",       "done", results[3])

    # Coleta resultado do RAG (já deveria estar pronto)
    try:
        similar_ideas = await asyncio.wait_for(t_similar, timeout=10)
    except Exception:
        similar_ideas = []

    if similar_ideas:
        yield _event("rag", "done", json.dumps(similar_ideas, ensure_ascii=False))

    try:
        # ── FASE 2: Debate + Score em paralelo ───────────────────────────────
        research_ctx = _research_summary(session["research"])

        yield _event("advocate", "running")
        yield _event("devil",    "running")
        yield _event("score",    "running")

        advocate_result, devil_result, score_result = await asyncio.gather(
            advocate.run(idea, research_ctx),
            devil.run(idea, research_ctx),
            score.run(idea, research_ctx),
            return_exceptions=True,
        )

        advocate_result = advocate_result if isinstance(advocate_result, str) else "[Erro no Advocate]"
        devil_result    = devil_result    if isinstance(devil_result,    str) else "[Erro no Devil]"
        score_result    = score_result    if isinstance(score_result,    str) else '{"overall":0,"dimensions":{}}'

        session["debate"] = {"advocate": advocate_result, "devil": devil_result}
        session["score"]  = score_result

        yield _event("advocate", "done", advocate_result)
        yield _event("devil",    "done", devil_result)
        yield _event("score",    "done", score_result)

        yield _event("mediator", "running")
        mediator_result = await mediator.run(idea, advocate_result, devil_result)
        session["debate"]["mediator"] = mediator_result
        yield _event("mediator", "done", mediator_result)

        # ── FASE 3: Síntese com contexto RAG ─────────────────────────────────
        yield _event("synthesis", "running")

        rag_context = rag.build_rag_context(similar_ideas)

        report_result = await synthesis.run(
            idea,
            research_ctx,
            _debate_summary(session["debate"]),
            rag_context=rag_context,
            image_context=image_context or "",
        )

        session["report"] = report_result
        yield _event("synthesis", "done", report_result)
        yield _event("pipeline",  "complete")

        # Persiste em disco de forma assíncrona (não bloqueia o stream)
        asyncio.create_task(_persist_session(session_id, session))

    except Exception as e:
        yield _event("pipeline", "error", str(e))


def get_session(session_id: str) -> dict | None:
    # Primeiro tenta memória (sessão ativa)
    if session_id in _sessions:
        return _sessions[session_id]
    # Fallback: carrega do disco (sessão de análise anterior)
    saved = persistence.load_session(session_id)
    if saved:
        _sessions[session_id] = saved
        return saved
    return None
