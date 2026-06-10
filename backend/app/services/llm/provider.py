"""
VANTAGE — LLM Provider Layer
Unified interface for OpenAI and Ollama with hot-switching support.
"""
import json
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.llm.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE
from app.schemas.schemas import LLMAnalysisResult, EntitySentiment


# ─────────────────────────────────────────────────────────
#  Abstract Base
# ─────────────────────────────────────────────────────────
class BaseLLMProvider(ABC):
    @abstractmethod
    async def analyze_article(self, article_text: str) -> LLMAnalysisResult:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

    def _parse_llm_json(self, raw: str) -> dict:
        """Strip markdown fences and parse JSON safely."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])
        return json.loads(cleaned)

    def _build_result(self, data: dict, provider: str, model: str, latency_ms: int) -> LLMAnalysisResult:
        entities = []
        for e in data.get("entities", []):
            try:
                entities.append(EntitySentiment(
                    name=e.get("name", "Unknown"),
                    type=e.get("type", "PERSON"),
                    sentiment=e.get("sentiment", "neutral"),
                    sentiment_score=float(e.get("sentiment_score", 0.0)),
                    framing=e.get("framing", "neutral"),
                    context_snippet=e.get("context_snippet", ""),
                ))
            except Exception:
                continue

        return LLMAnalysisResult(
            entities=entities,
            bias_score=float(data.get("bias_score", 0.0)),
            framing_analysis=data.get("framing_analysis", ""),
            bias_reasoning=data.get("bias_reasoning", ""),
            event_summary=data.get("event_summary", ""),
            overall_sentiment=data.get("overall_sentiment", "neutral"),
            provider=provider,
            model_name=model,
            latency_ms=latency_ms,
        )


# ─────────────────────────────────────────────────────────
#  OpenAI Provider
# ─────────────────────────────────────────────────────────
class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_article(self, article_text: str) -> LLMAnalysisResult:
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(article_text=article_text[:6000])
        start = time.monotonic()

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2000,
        )

        latency_ms = int((time.monotonic() - start) * 1000)
        raw = response.choices[0].message.content
        data = self._parse_llm_json(raw)
        return self._build_result(data, "openai", self.model, latency_ms)

    async def is_available(self) -> bool:
        return bool(settings.openai_api_key and settings.openai_api_key.startswith("sk-"))


# ─────────────────────────────────────────────────────────
#  Ollama Provider
# ─────────────────────────────────────────────────────────
class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def analyze_article(self, article_text: str) -> LLMAnalysisResult:
        prompt = f"{SYSTEM_PROMPT}\n\n{ANALYSIS_PROMPT_TEMPLATE.format(article_text=article_text[:4000])}"
        start = time.monotonic()

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.1},
                },
            )
            response.raise_for_status()

        latency_ms = int((time.monotonic() - start) * 1000)
        raw = response.json().get("response", "{}")
        data = self._parse_llm_json(raw)
        return self._build_result(data, "ollama", self.model, latency_ms)

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                if r.status_code != 200:
                    return False
                models = (r.json() or {}).get("models", [])
                names = [m.get("name", "") for m in models if isinstance(m, dict)]
                return any(
                    name == self.model or name.startswith(f"{self.model}:")
                    for name in names
                )
        except Exception:
            return False


# ─────────────────────────────────────────────────────────
#  LLM Router — hot-switchable at runtime
# ─────────────────────────────────────────────────────────
class LLMRouter:
    """
    Central LLM access point. Provider can be switched at runtime
    via the /api/llm/provider endpoint without restarting the server.
    """
    def __init__(self):
        self._provider_override: str | None = None
        self._openai = OpenAIProvider()
        self._ollama = OllamaProvider()

    def set_provider(self, provider: str) -> None:
        if provider not in ("openai", "ollama"):
            raise ValueError(f"Unknown provider: {provider}")
        self._provider_override = provider

    def get_active_provider_name(self) -> str:
        return self._provider_override or settings.llm_provider

    def _get_provider(self) -> BaseLLMProvider:
        name = self.get_active_provider_name()
        return self._openai if name == "openai" else self._ollama

    async def analyze_article(self, article_text: str) -> LLMAnalysisResult:
        return await self._get_provider().analyze_article(article_text)

    async def get_status(self) -> dict:
        openai_ok = await self._openai.is_available()
        ollama_ok = await self._ollama.is_available()
        active = self.get_active_provider_name()
        model = settings.openai_model if active == "openai" else settings.ollama_model
        return {
            "current_provider": active,
            "available_providers": ["openai", "ollama"],
            "openai_configured": openai_ok,
            "ollama_available": ollama_ok,
            "current_model": model,
        }


# Singleton
llm_router = LLMRouter()
