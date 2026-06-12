import json
import pathlib
from datetime import datetime

DATA_DIR = pathlib.Path(__file__).parent.parent / "data" / "sessions"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_session(session_id: str, data: dict) -> None:
    path = DATA_DIR / f"{session_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_session(session_id: str) -> dict | None:
    path = DATA_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def list_sessions(limit: int = 50) -> list[dict]:
    """Retorna sessões ordenadas da mais recente para a mais antiga."""
    results = []
    paths = sorted(DATA_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in paths[:limit]:
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            score_val = None
            raw_score = data.get("score")
            if isinstance(raw_score, dict):
                score_val = raw_score.get("overall")
            elif isinstance(raw_score, str):
                try:
                    parsed = json.loads(raw_score)
                    score_val = parsed.get("overall")
                except Exception:
                    pass
            results.append({
                "session_id": p.stem,
                "idea": data.get("idea", ""),
                "score": score_val,
                "timestamp": data.get("timestamp", ""),
            })
        except Exception:
            pass
    return results
