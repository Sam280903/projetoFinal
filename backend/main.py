import os
import uuid
from dotenv import load_dotenv
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv(override=True)

from models.schemas import AnalysisRequest, QARequest
from agents import orchestrator, qa
from tools import report_builder, persistence, rag

app = FastAPI(title="PitchIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app", "https://*.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# ── Diretório do build estático do Next.js ─────────────────────────────────────
_BASE = os.path.dirname(__file__)
OUT_DIR = os.path.join(_BASE, "out")
_has_static = os.path.isdir(OUT_DIR)


def _page(path: str):
    """Retorna a FileResponse para uma página estática do Next.js."""
    full = os.path.join(OUT_DIR, path)
    if os.path.isfile(full):
        return FileResponse(full)
    return FileResponse(os.path.join(OUT_DIR, "index.html"))


# ── Rotas de API ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    if not req.idea.strip():
        raise HTTPException(status_code=400, detail="Ideia não pode estar vazia.")

    session_id = req.session_id or str(uuid.uuid4())

    async def event_stream():
        import json
        yield f"data: {json.dumps({'agent': 'session', 'status': 'start', 'data': session_id})}\n\n"
        async for event in orchestrator.run_pipeline(req.idea, session_id):
            yield event

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/qa")
async def ask_question(req: QARequest):
    session = orchestrator.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada. Execute uma análise primeiro.")

    report = session.get("report")
    if not report:
        raise HTTPException(status_code=400, detail="Análise ainda não concluída.")

    answer = await qa.answer(req.question, report, session["idea"])
    return {"answer": answer}


@app.get("/export-pdf/{session_id}")
async def export_pdf(session_id: str):
    session = orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    report = session.get("report")
    if not report:
        raise HTTPException(status_code=400, detail="Análise ainda não concluída.")

    score = None
    raw_score = session.get("score")
    if raw_score:
        try:
            score = json.loads(raw_score) if isinstance(raw_score, str) else raw_score
        except Exception:
            pass

    try:
        pdf_bytes = report_builder.generate_pdf(session["idea"], report, score)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")

    import re
    import unicodedata
    normalized = unicodedata.normalize('NFKD', session["idea"])
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    safe_name = re.sub(r'[^\w\s-]', '', ascii_name)
    safe_name = re.sub(r'\s+', '-', safe_name.strip())[:50].rstrip('-').lower()
    filename = f"pitchiq-{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    session = orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return {
        "idea": session.get("idea"),
        "report": session.get("report"),
        "has_debate": session.get("debate") is not None,
        "debate": session.get("debate"),
    }


@app.get("/sessions")
async def list_sessions():
    return {"sessions": persistence.list_sessions()}


@app.get("/similar/{session_id}")
async def get_similar(session_id: str):
    session = orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    idea = session.get("idea", "")
    if not idea:
        return {"similar": []}
    similar = await rag.find_similar(idea, exclude_session_id=session_id)
    return {"similar": similar}


# ── Frontend estático (Next.js output: export) ────────────────────────────────
if _has_static:
    # Assets JS/CSS gerados pelo Next.js
    app.mount("/_next", StaticFiles(directory=os.path.join(OUT_DIR, "_next")), name="next-assets")

    @app.get("/")
    async def index():
        return _page("index.html")

    @app.get("/analysis/")
    async def analysis_page():
        return _page("analysis/index.html")

    @app.get("/historico/")
    async def historico_page():
        return _page("historico/index.html")

    @app.get("/resultado/{session_id}/")
    async def resultado_page(session_id: str):
        # Servir o template gerado para o placeholder; o JS usa a URL real
        return _page("resultado/placeholder/index.html")

    # Arquivos públicos (favicon, svg, etc.)
    @app.get("/{filename}")
    async def public_file(filename: str):
        return _page(filename)
