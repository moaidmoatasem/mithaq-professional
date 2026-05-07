import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Approximate cost per 1k tokens (input+output blended), USD
_COST_PER_1K: dict[str, float] = {
    "ollama": 0.0,
    "gemini": 0.000075,   # gemini-1.5-flash
    "groq": 0.000080,     # llama-3-8b-8192
}


@dataclass
class BackendConfig:
    name: str
    url: str
    model: str
    api_key: str = ""
    timeout: float = 30.0


def _load_mode() -> str:
    """Return 'local', 'hybrid', or 'cloud' from mithaq.yaml, defaulting to 'local'."""
    config_path = Path("mithaq.yaml")
    if not config_path.exists():
        return "local"
    try:
        import yaml  # optional dep — graceful fallback
        with config_path.open() as fh:
            data = yaml.safe_load(fh) or {}
        return str(data.get("mode", "local")).lower()
    except Exception:
        return "local"


def _default_backends() -> list[BackendConfig]:
    return [
        BackendConfig(
            name="ollama",
            url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b"),
            timeout=300.0,
        ),
        BackendConfig(
            name="gemini",
            url="https://generativelanguage.googleapis.com/v1beta/models",
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            api_key=os.getenv("GEMINI_API_KEY", ""),
            timeout=60.0,
        ),
        BackendConfig(
            name="groq",
            url="https://api.groq.com/openai/v1/chat/completions",
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            api_key=os.getenv("GROQ_API_KEY", ""),
            timeout=60.0,
        ),
    ]


class ModelRouter:
    """Async LLM router: Ollama → Gemini → Groq, respecting local/hybrid/cloud mode."""

    def __init__(self, backends: Optional[list[BackendConfig]] = None, mode: Optional[str] = None):
        self.backends: list[BackendConfig] = backends or _default_backends()
        self.mode: str = mode or _load_mode()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def complete(self, prompt: str, max_tokens: int = 1000) -> str:
        for backend in self.backends:
            if self.mode == "local" and backend.name != "ollama":
                raise ValueError(
                    f"local mode forbids cloud backend '{backend.name}'. "
                    "Set mode: hybrid or cloud in mithaq.yaml to enable cloud fallback."
                )
            try:
                t0 = time.monotonic()
                text = await self._call(backend, prompt, max_tokens)
                elapsed = time.monotonic() - t0
                cost = _estimate_cost(backend.name, prompt, text)
                logger.info(
                    "model_router backend=%s model=%s tokens_est=%d cost_usd=%.6f elapsed=%.2fs",
                    backend.name,
                    backend.model,
                    _rough_tokens(prompt + text),
                    cost,
                    elapsed,
                )
                return text
            except Exception as exc:  # noqa: BLE001
                logger.warning("model_router backend=%s failed: %s — trying next", backend.name, exc)

        logger.error("model_router all backends exhausted, returning empty string")
        return ""

    # ------------------------------------------------------------------
    # Backend implementations
    # ------------------------------------------------------------------

    async def _call(self, cfg: BackendConfig, prompt: str, max_tokens: int) -> str:
        if cfg.name == "ollama":
            return await self._call_ollama(cfg, prompt, max_tokens)
        if cfg.name == "gemini":
            return await self._call_gemini(cfg, prompt, max_tokens)
        if cfg.name == "groq":
            return await self._call_groq(cfg, prompt, max_tokens)
        raise ValueError(f"Unknown backend: {cfg.name}")

    async def _call_ollama(self, cfg: BackendConfig, prompt: str, max_tokens: int) -> str:
        import aiohttp
        payload = {"model": cfg.model, "prompt": prompt, "stream": False,
                   "options": {"num_predict": max_tokens}}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{cfg.url}/api/generate", json=payload,
                timeout=aiohttp.ClientTimeout(total=cfg.timeout)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("response", "")

    async def _call_gemini(self, cfg: BackendConfig, prompt: str, max_tokens: int) -> str:
        import aiohttp
        if not cfg.api_key:
            raise ValueError("GEMINI_API_KEY not set")
        url = f"{cfg.url}/{cfg.model}:generateContent?key={cfg.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload,
                timeout=aiohttp.ClientTimeout(total=cfg.timeout)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_groq(self, cfg: BackendConfig, prompt: str, max_tokens: int) -> str:
        import aiohttp
        if not cfg.api_key:
            raise ValueError("GROQ_API_KEY not set")
        headers = {"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": cfg.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                cfg.url, headers=headers, json=payload,
                timeout=aiohttp.ClientTimeout(total=cfg.timeout)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["choices"][0]["message"]["content"]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _rough_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _estimate_cost(backend_name: str, prompt: str, response: str) -> float:
    tokens = _rough_tokens(prompt + response)
    return (tokens / 1000) * _COST_PER_1K.get(backend_name, 0.0)

