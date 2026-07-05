"""Report listing / retrieval schemas."""

from pydantic import BaseModel

from .analysis import AnalysisReport


class ReportSummary(BaseModel):
    id: str
    job_id: str
    ticker: str
    company: str
    analysis_mode: str
    final_verdict: str
    confidence: float
    is_mock_data: bool
    created_at: str


class ReportDetail(BaseModel):
    id: str
    job_id: str
    created_at: str
    report: AnalysisReport
