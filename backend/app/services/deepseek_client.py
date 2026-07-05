"""Backend-only DeepSeek client. DeepSeek is the ONLY LLM runtime.

The API key is read from the environment and never exposed to the
frontend, logs, reports, or tests. If the key is missing, LLM features
fall back to explicit MOCK LLM OUTPUT (see llm_service).
"""

import logging
from typing import Optional

import httpx

from ..config import Settings, get_settings
from ..schemas.llm import DeepSeekStatus, LlmMessage, LlmResponse

logger = logging.getLogger(__name__)

_ALLOWED_MODEL_PREFIX = "deepseek"


class DeepSeekNotConfiguredError(RuntimeError):
    """Raised when DEEPSEEK_API_KEY is missing."""


class DeepSeekApiError(RuntimeError):
    pass


class DeepSeekClient:
    def __init__(self, settings: Optional[Settings] = None, timeout: float = 60.0):
        self._settings = settings or get_settings()
        self._timeout = timeout
        model = self._settings.deepseek_model or "deepseek-chat"
        if not model.lower().startswith(_ALLOWED_MODEL_PREFIX):
            # Never silently fall back to a non-DeepSeek model.
            raise ValueError(
                f"DEEPSEEK_MODEL must be a DeepSeek-family model, got: {model!r}"
            )
        self.model = model

    @property
    def is_configured(self) -> bool:
        return bool(self._settings.deepseek_api_key)

    def status(self) -> DeepSeekStatus:
        return DeepSeekStatus(
            configured=self.is_configured,
            model=self.model,
            mode="live" if self.is_configured else "mock",
        )

    def chat(self, messages: list[LlmMessage], temperature: float = 0.3, max_tokens: int = 1200) -> LlmResponse:
        if not self.is_configured:
            raise DeepSeekNotConfiguredError(
                "DEEPSEEK_API_KEY is not set. LLM features fall back to MOCK LLM OUTPUT."
            )
        url = f"{self._settings.deepseek_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            logger.warning("DeepSeek request failed (%s)", exc.__class__.__name__)
            raise DeepSeekApiError("DeepSeek chat completion failed") from exc

        choice = (data.get("choices") or [{}])[0]
        usage = data.get("usage") or {}
        return LlmResponse(
            content=choice.get("message", {}).get("content", ""),
            model=data.get("model", self.model),
            is_mock=False,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )
