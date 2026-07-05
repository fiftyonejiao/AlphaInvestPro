"""End-to-end orchestrator tests over mock data (no keys configured)."""

import asyncio

import pytest

from app.schemas.analysis import AnalysisReport
from app.services.analysis_orchestrator import AnalysisOrchestrator
from app.services.llm_service import MOCK_MARKER
from app.storage.database import get_session
from app.storage.models import AnalysisJob, JobEvent, Report


def _create_job(ticker="AAPL", mode="full_memo", language="en") -> str:
    db = get_session()
    job = AnalysisJob(ticker=ticker, analysis_mode=mode, language=language, status="pending")
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()
    return job_id


def _run(job_id: str) -> None:
    asyncio.run(AnalysisOrchestrator().run(job_id))


class TestFullMemoRun:
    @pytest.fixture(scope="class")
    def completed(self):
        job_id = _create_job()
        _run(job_id)
        db = get_session()
        job = db.get(AnalysisJob, job_id)
        report = db.get(Report, job.report_id) if job.report_id else None
        events = db.query(JobEvent).filter(JobEvent.job_id == job_id).order_by(JobEvent.seq).all()
        db.close()
        return job, report, events

    def test_job_completes(self, completed):
        job, report, _ = completed
        assert job.status == "completed"
        assert report is not None
        assert job.is_mock_data is True  # no QVeris key in tests

    def test_all_steps_emitted(self, completed):
        _, _, events = completed
        steps = {e.step for e in events if e.event_type == "step_completed"}
        assert {
            "input_normalization", "identification", "quick_screen", "business_quality",
            "moat", "management", "valuation", "inversion_risk", "bull_bear", "final_memo",
        } <= steps
        assert any(e.event_type == "job_completed" for e in events)

    def test_report_matches_output_schema(self, completed):
        _, report, _ = completed
        parsed = AnalysisReport.model_validate(report.data)
        assert parsed.ticker == "AAPL"
        assert parsed.final_verdict in ("avoid", "watchlist", "attractive", "uncertain")
        assert 0.0 <= parsed.confidence <= 1.0
        assert parsed.valuation.fair_value_range.low <= parsed.valuation.fair_value_range.high
        assert parsed.valuation.assumptions, "valuation must expose assumptions"
        assert parsed.risk_review.inversion_question
        assert parsed.bull_case and parsed.bear_case
        assert parsed.final_memo_markdown

    def test_memo_flags_mock_data_and_mock_llm(self, completed):
        _, report, _ = completed
        memo = report.memo_markdown
        assert "MOCK DATA" in memo
        assert MOCK_MARKER in memo  # LLM narration fell back to mock

    def test_memo_shows_assumptions_and_sources(self, completed):
        _, report, _ = completed
        memo = report.memo_markdown
        assert "| # | Name | Value | Source |" in memo
        assert "not financial advice" in memo.lower()


class TestModesAndLanguages:
    def test_quick_screen_mode_skips_deep_steps(self):
        job_id = _create_job(mode="quick_screen")
        _run(job_id)
        db = get_session()
        events = db.query(JobEvent).filter(JobEvent.job_id == job_id).all()
        db.close()
        steps = {e.step for e in events if e.event_type == "step_completed"}
        assert "quick_screen" in steps
        assert "valuation" not in steps

    def test_chinese_report_language(self):
        job_id = _create_job(ticker="KO", language="zh-CN")
        _run(job_id)
        db = get_session()
        job = db.get(AnalysisJob, job_id)
        report = db.get(Report, job.report_id)
        db.close()
        assert "投资备忘录" in report.memo_markdown
        assert "不构成投资建议" in report.memo_markdown


class TestLlmServiceBoundary:
    def test_memo_generation_goes_through_deepseek_service(self, monkeypatch):
        """All narration must pass through LlmService.narrate (DeepSeek boundary)."""
        calls: list[str] = []
        from app.services.llm_service import LlmService
        original = LlmService.narrate

        def spy(self, section, context, language="en"):
            calls.append(section)
            return original(self, section, context, language)

        monkeypatch.setattr(LlmService, "narrate", spy)
        job_id = _create_job(ticker="MSFT")
        _run(job_id)
        assert "business_quality" in calls
        assert "final_memo" in calls
