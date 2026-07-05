"""Analysis job and final report schemas (spec section 15 output schema)."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from .risk import RiskReview
from .valuation import Valuation

AnalysisMode = Literal["quick_screen", "full_memo", "risk_review", "valuation_check"]
FinalVerdict = Literal["avoid", "watchlist", "attractive", "uncertain"]
JobStatus = Literal["pending", "running", "completed", "failed"]


class AnalysisJobCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=16)
    analysis_mode: AnalysisMode = "full_memo"
    language: Literal["en", "zh-CN"] = "en"


class AnalysisJobOut(BaseModel):
    id: str
    ticker: str
    company: str
    analysis_mode: AnalysisMode
    language: str
    status: JobStatus
    current_step: Optional[str] = None
    error: Optional[str] = None
    report_id: Optional[str] = None
    is_mock_data: bool = False
    created_at: str
    updated_at: str


class JobEventOut(BaseModel):
    seq: int
    event_type: str  # step_started | step_completed | job_completed | job_failed
    step: Optional[str] = None
    payload: dict = {}
    created_at: str


class ChecklistItem(BaseModel):
    key: str
    label: str
    passed: bool
    detail: str


class BusinessQuality(BaseModel):
    score: float
    summary: str
    evidence: list[str]


class Moat(BaseModel):
    score: float
    summary: str
    risks: list[str]


class EvidenceSource(BaseModel):
    name: str
    provider: str
    capability_id: Optional[str] = None
    retrieval_timestamp: str
    source_timestamp: Optional[str] = None
    is_mock: bool = False
    note: str = ""


class AnalysisReport(BaseModel):
    """Final structured output. Matches spec section 15, plus provenance extras."""

    company: str
    ticker: str
    analysis_mode: AnalysisMode
    final_verdict: FinalVerdict
    confidence: float
    business_quality: BusinessQuality
    moat: Moat
    valuation: Valuation
    risk_review: RiskReview
    bull_case: list[str]
    bear_case: list[str]
    final_memo_markdown: str
    # Provenance / transparency extras (not part of the minimal spec schema).
    checklist: list[ChecklistItem] = []
    evidence_sources: list[EvidenceSource] = []
    is_mock_data: bool = False
    is_mock_llm: bool = False
    is_incomplete: bool = False
    language: str = "en"
    generated_at: str = ""
