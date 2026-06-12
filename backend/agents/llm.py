"""
Router de LLM — Gemini como provedor principal, demais como fallback.

Mapa de roteamento:
  call_fast    → Gemini 2.0 Flash  → Groq llama-3.3-70b  → OpenRouter
  call_balance → Gemini 2.0 Flash  → OpenRouter claude    → Anthropic
  call_quality → Gemini 2.0 Flash  → OpenRouter claude    → Groq
"""

import os
import asyncio
import anthropic
from groq import AsyncGroq
from openai import AsyncOpenAI

# ── clientes lazy ─────────────────────────────────────────────────────────────
_anthropic_client: anthropic.AsyncAnthropic | None = None
_groq_client: AsyncGroq | None = None
_openrouter_client: AsyncOpenAI | None = None
_gemini_client: AsyncOpenAI | None = None


def _anthropic() -> anthropic.AsyncAnthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            timeout=120.0,
        )
    return _anthropic_client


def _groq() -> AsyncGroq:
    global _groq_client
    if _groq_client is None:
        _groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", ""))
    return _groq_client


def _openrouter() -> AsyncOpenAI:
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
        )
    return _openrouter_client


_ollama_client: AsyncOpenAI | None = None

def _ollama() -> AsyncOpenAI:
    """Modelo local via Ollama — endpoint compatível com OpenAI."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = AsyncOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
    return _ollama_client


def _gemini() -> AsyncOpenAI:
    """Gemini via endpoint compatível com OpenAI — não precisa de novo SDK."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )
    return _gemini_client


# ── retry helper ──────────────────────────────────────────────────────────────
async def _retry(fn, retries=4):
    for attempt in range(retries):
        try:
            return await fn()
        except Exception as e:
            name = type(e).__name__
            msg  = str(e).lower()
            is_rate_limit = any(k in name for k in ("RateLimit", "Timeout", "Connection", "ServiceUnavailable")) \
                         or "429" in msg or "rate limit" in msg or "rate_limit" in msg
            if is_rate_limit:
                wait = min(60, 2 ** attempt * 5)  # 5, 10, 20, 40, 60s
                await asyncio.sleep(wait)
            else:
                raise
    return await fn()


# ── chamadas por provedor ─────────────────────────────────────────────────────
async def _call_gemini(system: str, prompt: str, max_tokens: int, model: str = "gemini-2.0-flash") -> str:
    async def fn():
        resp = await _gemini().chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""
    return await _retry(fn)


async def _call_groq(system: str, prompt: str, max_tokens: int) -> str:
    async def fn():
        resp = await _groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system",  "content": system},
                {"role": "user",    "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""
    return await _retry(fn)


async def _call_openrouter(system: str, prompt: str, max_tokens: int) -> str:
    async def fn():
        resp = await _openrouter().chat.completions.create(
            model="anthropic/claude-3-5-haiku",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            extra_headers={"HTTP-Referer": "https://pitchiq.app"},
        )
        return resp.choices[0].message.content or ""
    return await _retry(fn)


async def _call_anthropic(system: str, prompt: str, max_tokens: int) -> str:
    async def fn():
        resp = await _anthropic().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    return await _retry(fn)


async def _call_ollama(system: str, prompt: str, max_tokens: int, model: str = "llama3.2") -> str:
    async def fn():
        resp = await _ollama().chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""
    return await _retry(fn)


# ── disponibilidade ───────────────────────────────────────────────────────────
OPENAI_AVAILABLE     = bool(os.getenv("OPENAI_API_KEY"))
GROQ_AVAILABLE       = bool(os.getenv("GROQ_API_KEY"))
OPENROUTER_AVAILABLE = bool(os.getenv("OPENROUTER_API_KEY"))

def _ollama_available() -> bool:
    """Verifica em tempo de execução se o Ollama está rodando."""
    import socket
    try:
        s = socket.create_connection(("localhost", 11434), timeout=1)
        s.close()
        return True
    except OSError:
        return False


async def _call_openai(system: str, prompt: str, max_tokens: int) -> str:
    _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    async def fn():
        resp = await _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""
    return await _retry(fn)


# ── API pública ───────────────────────────────────────────────────────────────
async def call_fast(system: str, prompt: str, max_tokens: int = 900) -> str:
    """OpenAI → Groq → OpenRouter → Ollama (local). Para debate, score, Q&A."""
    if OPENAI_AVAILABLE:
        try:
            return await _call_openai(system, prompt, max_tokens)
        except Exception:
            pass
    if GROQ_AVAILABLE:
        try:
            return await _call_groq(system, prompt, max_tokens)
        except Exception:
            pass
    if OPENROUTER_AVAILABLE:
        try:
            return await _call_openrouter(system, prompt, max_tokens)
        except Exception:
            pass
    if _ollama_available():
        return await _call_ollama(system, prompt, max_tokens)
    return await _call_anthropic(system, prompt, max_tokens)


async def call_balance(system: str, prompt: str, max_tokens: int = 2500) -> str:
    """OpenAI → OpenRouter → Ollama (local) → Anthropic. Para síntese."""
    if OPENAI_AVAILABLE:
        try:
            return await _call_openai(system, prompt, max_tokens)
        except Exception:
            pass
    if OPENROUTER_AVAILABLE:
        try:
            return await _call_openrouter(system, prompt, max_tokens)
        except Exception:
            pass
    if _ollama_available():
        return await _call_ollama(system, prompt, max_tokens)
    return await _call_anthropic(system, prompt, max_tokens)


async def call_quality(system: str, prompt: str, max_tokens: int = 1800) -> str:
    """OpenAI → Groq → OpenRouter → Ollama (local). Tool use tratado em base.py."""
    if OPENAI_AVAILABLE:
        try:
            return await _call_openai(system, prompt, max_tokens)
        except Exception:
            pass
    if GROQ_AVAILABLE:
        try:
            return await _call_groq(system, prompt, max_tokens)
        except Exception:
            pass
    if OPENROUTER_AVAILABLE:
        try:
            return await _call_openrouter(system, prompt, max_tokens)
        except Exception:
            pass
    if _ollama_available():
        return await _call_ollama(system, prompt, max_tokens)
    return await _call_anthropic(system, prompt, max_tokens)
