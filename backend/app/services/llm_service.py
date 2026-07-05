"""LLM service boundary. All prompts and memo narration go through here.

DeepSeek is the only runtime. When the key is missing, the service returns
deterministic text clearly marked `MOCK LLM OUTPUT`, so the rest of the
pipeline (QVeris data access and deterministic calculations) keeps working.

The LLM only narrates over normalized QVeris data passed in as context.
It never invents prices, statements, valuation inputs, or metrics.
"""

import logging
from typing import Optional

from ..schemas.llm import LlmMessage, LlmResponse
from .deepseek_client import DeepSeekApiError, DeepSeekClient, DeepSeekNotConfiguredError

logger = logging.getLogger(__name__)

MOCK_MARKER = "MOCK LLM OUTPUT"

_SYSTEM_PROMPT = {
    "en": (
        "You are the narration layer of AlphaInvestPro, a research-only investment analysis tool. "
        "You write short, disciplined, plain-language commentary. "
        "Use ONLY the structured data provided in the user message; never invent numbers, prices, "
        "financial statements, or facts. Flag uncertainty explicitly. This is not financial advice."
    ),
    "zh-CN": (
        "你是 AlphaInvestPro（仅供研究的投资分析工具）的叙述层。"
        "请用简体中文撰写简短、克制、通俗的分析评论。"
        "只能使用用户消息中提供的结构化数据；不得编造任何数字、价格、财务报表或事实。"
        "必须明确指出不确定性。本内容不构成投资建议。"
    ),
}


class LlmService:
    def __init__(self, client: Optional[DeepSeekClient] = None):
        self.client = client or DeepSeekClient()

    @property
    def is_live(self) -> bool:
        return self.client.is_configured

    def narrate(self, section: str, context: str, language: str = "en") -> LlmResponse:
        """Generate a short narrative for one analysis section."""
        lang = language if language in _SYSTEM_PROMPT else "en"
        try:
            return self.client.chat(
                [
                    LlmMessage(role="system", content=_SYSTEM_PROMPT[lang]),
                    LlmMessage(
                        role="user",
                        content=(
                            f"Section: {section}\n"
                            f"Structured data (from QVeris, already validated):\n{context}\n\n"
                            "Write 2-4 sentences of commentary for this section. "
                            "Do not repeat raw numbers unless meaningful. Do not give buy/sell advice."
                        ),
                    ),
                ]
            )
        except (DeepSeekNotConfiguredError, DeepSeekApiError):
            return self._mock_response(section, lang)

    def _mock_response(self, section: str, language: str) -> LlmResponse:
        if language == "zh-CN":
            text = (
                f"[{MOCK_MARKER}] 未配置 DeepSeek API Key，本段为占位说明。"
                f"「{section}」部分的所有数值均来自确定性计算与数据源，未经大模型润色。"
                "请配置 DEEPSEEK_API_KEY 以获得真实的 AI 叙述。"
            )
        else:
            text = (
                f"[{MOCK_MARKER}] DeepSeek API key is not configured; this is placeholder narration. "
                f"All figures in the '{section}' section come from deterministic calculations and "
                "data sources, without LLM commentary. Set DEEPSEEK_API_KEY for real AI narration."
            )
        return LlmResponse(content=text, model=self.client.model, is_mock=True)
