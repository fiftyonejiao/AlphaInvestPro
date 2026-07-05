"""Schemas for the DeepSeek-only LLM service boundary."""

from typing import Optional

from pydantic import BaseModel


class LlmMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class LlmRequest(BaseModel):
    messages: list[LlmMessage]
    temperature: float = 0.3
    max_tokens: int = 1200


class LlmResponse(BaseModel):
    content: str
    model: str
    is_mock: bool = False
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


class DeepSeekStatus(BaseModel):
    configured: bool
    model: str
    mode: str  # "live" | "mock"
