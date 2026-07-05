"""DeepSeek-only runtime tests: missing key behavior, model-family guard,
service boundary, and no non-DeepSeek provider code."""

from pathlib import Path

import pytest

from app.config import Settings
from app.schemas.llm import LlmMessage
from app.services.deepseek_client import DeepSeekClient, DeepSeekNotConfiguredError
from app.services.llm_service import MOCK_MARKER, LlmService


def make_settings(**overrides) -> Settings:
    s = Settings()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


class TestMissingKey:
    def test_unconfigured_without_key(self):
        client = DeepSeekClient(make_settings(deepseek_api_key=""))
        assert client.is_configured is False
        assert client.status().mode == "mock"

    def test_chat_raises_without_key(self):
        client = DeepSeekClient(make_settings(deepseek_api_key=""))
        with pytest.raises(DeepSeekNotConfiguredError):
            client.chat([LlmMessage(role="user", content="hi")])

    def test_llm_service_falls_back_to_mock_output(self):
        service = LlmService(DeepSeekClient(make_settings(deepseek_api_key="")))
        resp = service.narrate("business_quality", "quality_score=8.0", "en")
        assert resp.is_mock is True
        assert MOCK_MARKER in resp.content

    def test_mock_output_respects_chinese_language(self):
        service = LlmService(DeepSeekClient(make_settings(deepseek_api_key="")))
        resp = service.narrate("final_memo", "verdict=watchlist", "zh-CN")
        assert resp.is_mock is True
        assert MOCK_MARKER in resp.content
        assert "DeepSeek" in resp.content


class TestModelFamilyGuard:
    def test_default_model_is_deepseek_chat(self):
        client = DeepSeekClient(make_settings(deepseek_api_key="k"))
        assert client.model == "deepseek-chat"

    def test_non_deepseek_model_rejected(self):
        with pytest.raises(ValueError):
            DeepSeekClient(make_settings(deepseek_model="gpt-4o"))


class TestNoOtherProviders:
    """Prove no non-DeepSeek provider env vars, imports, or SDKs exist."""

    FORBIDDEN = [
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY",
        "MISTRAL_API_KEY", "COHERE_API_KEY", "GROQ_API_KEY", "XAI_API_KEY",
        "import openai", "import anthropic", "import cohere", "import mistralai",
        "from openai", "from anthropic", "ollama",
    ]

    def test_backend_sources_have_no_other_llm_providers(self):
        app_dir = Path(__file__).resolve().parents[1] / "app"
        offenders = []
        for py in app_dir.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            for token in self.FORBIDDEN:
                if token.lower() in text.lower():
                    offenders.append(f"{py.name}: {token}")
        assert offenders == [], f"Non-DeepSeek provider references found: {offenders}"

    def test_requirements_have_no_llm_sdks(self):
        req = (Path(__file__).resolve().parents[1] / "requirements.txt").read_text()
        for sdk in ("openai", "anthropic", "cohere", "mistral", "google-genai", "ollama"):
            assert sdk not in req.lower()
