"""Analysis orchestrator: runs the visible step-by-step research workflow.

Steps (spec section 14): input normalization, identification, quick screen,
business quality, moat, management, valuation, inversion/risk, bull/bear,
final memo. Each step emits a job event consumed by the SSE endpoint so the
UI can show a live agent timeline.

Deterministic services produce all numbers; the DeepSeek-only LLM service
adds narration; QVeris (or explicit mock data) provides all market facts.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from ..config import get_settings
from ..schemas.analysis import AnalysisReport
from ..schemas.risk import RiskReview
from ..storage.database import get_session
from ..storage.models import AnalysisJob, JobEvent, Report
from . import buffett_skill_service, evidence_service, valuation_service
from .llm_service import LlmService
from .market_data_service import MarketDataService
from .report_service import render_memo_markdown

logger = logging.getLogger(__name__)

STEPS_BY_MODE: dict[str, list[str]] = {
    "quick_screen": ["input_normalization", "identification", "quick_screen", "final_memo"],
    "full_memo": [
        "input_normalization", "identification", "quick_screen", "business_quality",
        "moat", "management", "valuation", "inversion_risk", "bull_bear", "final_memo",
    ],
    "risk_review": ["input_normalization", "identification", "quick_screen", "inversion_risk", "bull_bear", "final_memo"],
    "valuation_check": ["input_normalization", "identification", "quick_screen", "valuation", "final_memo"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AnalysisOrchestrator:
    def __init__(self, market_data: Optional[MarketDataService] = None, llm: Optional[LlmService] = None):
        self.market_data = market_data or MarketDataService()
        self.llm = llm or LlmService()
        self._settings = get_settings()

    # -- persistence helpers -------------------------------------------------

    def _emit(self, job_id: str, event_type: str, step: Optional[str] = None, payload: Optional[dict] = None) -> None:
        db = get_session()
        try:
            seq = db.query(JobEvent).filter(JobEvent.job_id == job_id).count() + 1
            db.add(JobEvent(job_id=job_id, seq=seq, event_type=event_type, step=step, payload=payload or {}))
            db.commit()
        finally:
            db.close()

    def _update_job(self, job_id: str, **fields) -> None:
        db = get_session()
        try:
            job = db.get(AnalysisJob, job_id)
            if job:
                for k, v in fields.items():
                    setattr(job, k, v)
                job.updated_at = _now()
                db.commit()
        finally:
            db.close()

    # -- main entrypoint -----------------------------------------------------

    async def run(self, job_id: str) -> None:
        db = get_session()
        job = db.get(AnalysisJob, job_id)
        db.close()
        if job is None:
            return
        try:
            await self._run_steps(job)
        except Exception as exc:  # surface failure to the UI instead of hanging
            logger.exception("Analysis job %s failed", job_id)
            self._update_job(job_id, status="failed", error=str(exc))
            self._emit(job_id, "job_failed", payload={"error": str(exc)})

    async def _step(self, job_id: str, step: str, payload: dict) -> None:
        self._emit(job_id, "step_started", step=step)
        self._update_job(job_id, current_step=step)
        await asyncio.sleep(self._settings.step_delay_seconds)
        self._emit(job_id, "step_completed", step=step, payload=payload)

    async def _run_steps(self, job: AnalysisJob) -> None:
        job_id = job.id
        language = job.language or "en"
        mode = job.analysis_mode
        steps = STEPS_BY_MODE.get(mode, STEPS_BY_MODE["full_memo"])
        self._update_job(job_id, status="running")

        # Step: input normalization
        ticker = job.ticker.upper().strip()
        await self._step(job_id, "input_normalization", {"ticker": ticker})

        # Step: identification + data retrieval (QVeris or MOCK DATA)
        bundle = await asyncio.to_thread(self.market_data.get_bundle, ticker)
        company = bundle.profile.name
        self._update_job(job_id, company=company, is_mock_data=bundle.is_mock)
        await self._step(
            job_id, "identification",
            {
                "company": company, "sector": bundle.profile.sector,
                "price": bundle.quote.price, "is_mock_data": bundle.is_mock,
            },
        )

        complete, missing = evidence_service.required_fields_present(bundle)

        # Step: quick screen (always runs)
        checklist = buffett_skill_service.quick_screen(bundle.fundamentals)
        passed = sum(1 for c in checklist if c.passed)
        await self._step(
            job_id, "quick_screen",
            {"passed": passed, "total": len(checklist),
             "items": [c.model_dump() for c in checklist]},
        )

        # Optional deep steps
        quality = buffett_skill_service.business_quality(bundle)
        moat = buffett_skill_service.moat_review(bundle)
        if "business_quality" in steps:
            await self._step(job_id, "business_quality", {"score": quality.score, "summary": quality.summary})
        if "moat" in steps:
            await self._step(job_id, "moat", {"score": moat.score, "summary": moat.summary})
        if "management" in steps:
            mgmt = buffett_skill_service.management_review(bundle)
            await self._step(job_id, "management", mgmt)

        valuation = valuation_service.compute_valuation(bundle)
        pv = valuation_service.price_vs_value(bundle, valuation)
        if "valuation" in steps:
            await self._step(
                job_id, "valuation",
                {"method": valuation.method,
                 "fair_value_range": valuation.fair_value_range.model_dump(),
                 "price": pv["price"], "discount_to_base": pv["discount_to_base"]},
            )

        risk = self._risk_review(bundle, checklist, moat, language)
        if "inversion_risk" in steps:
            await self._step(job_id, "inversion_risk", risk.model_dump())

        bull, bear = self._bull_bear(bundle, quality, moat, pv, language)
        if "bull_bear" in steps:
            await self._step(job_id, "bull_bear", {"bull_case": bull, "bear_case": bear})

        # Verdict + confidence (deterministic rules, then LLM narration only)
        verdict, confidence = self._verdict(passed, len(checklist), quality.score, moat.score, pv, complete)

        # DeepSeek narration over the deterministic results
        narration_quality = self.llm.narrate(
            "business_quality",
            f"company={company}, quality_score={quality.score}/10, evidence={quality.evidence}",
            language,
        )
        narration_memo = self.llm.narrate(
            "final_memo",
            (
                f"company={company}, verdict={verdict}, confidence={confidence}, "
                f"quality={quality.score}/10, moat={moat.score}/10, "
                f"fair_value={valuation.fair_value_range.model_dump()}, price={pv['price']}, "
                f"top_risks={risk.top_risks}"
            ),
            language,
        )
        is_mock_llm = narration_quality.is_mock or narration_memo.is_mock

        report = AnalysisReport(
            company=company,
            ticker=ticker,
            analysis_mode=mode,
            final_verdict=verdict,
            confidence=confidence,
            business_quality=quality,
            moat=moat,
            valuation=valuation,
            risk_review=risk,
            bull_case=bull,
            bear_case=bear,
            final_memo_markdown="",
            checklist=checklist,
            evidence_sources=evidence_service.collect_evidence(bundle),
            is_mock_data=bundle.is_mock,
            is_mock_llm=is_mock_llm,
            is_incomplete=not complete,
            language=language,
            generated_at=_now(),
        )
        if not complete:
            # Validation gate: don't silently ship reports missing required data.
            report.risk_review.top_risks.insert(0, f"Report incomplete — missing fields: {', '.join(missing)}")

        report.final_memo_markdown = render_memo_markdown(
            report,
            {"business_quality": narration_quality.content, "final_memo": narration_memo.content},
        )

        # Persist report + finish job
        db = get_session()
        try:
            row = Report(
                job_id=job_id,
                ticker=ticker,
                company=company,
                analysis_mode=mode,
                final_verdict=verdict,
                confidence=confidence,
                data=report.model_dump(),
                memo_markdown=report.final_memo_markdown,
                is_mock_data=bundle.is_mock,
            )
            db.add(row)
            db.commit()
            report_id = row.id
        finally:
            db.close()

        await self._step(job_id, "final_memo", {"report_id": report_id, "verdict": verdict, "confidence": confidence})
        self._update_job(job_id, status="completed", report_id=report_id, current_step=None)
        self._emit(job_id, "job_completed", payload={"report_id": report_id})

    # -- deterministic judgment helpers ---------------------------------------

    @staticmethod
    def _verdict(passed: int, total: int, quality: float, moat: float, pv: dict, complete: bool):
        if not complete:
            return "uncertain", 0.3
        screen_ratio = passed / max(total, 1)
        discount = pv["discount_to_base"]
        strong_business = quality >= 6.5 and moat >= 6.0 and screen_ratio >= 0.66
        if strong_business and discount >= 0.10:
            return "attractive", round(min(0.55 + discount, 0.85), 2)
        if strong_business:
            return "watchlist", 0.6
        if screen_ratio < 0.4 or (quality < 4 and moat < 4):
            return "avoid", 0.65
        return "uncertain", 0.45

    @staticmethod
    def _risk_review(bundle, checklist, moat, language: str) -> RiskReview:
        f = bundle.fundamentals
        top_risks: list[str] = list(moat.risks)
        killers: list[str] = []
        for c in checklist:
            if not c.passed:
                top_risks.append(f"Failed screen: {c.label} ({c.detail})")
        if (f.debt_to_equity or 0) > 1.5:
            killers.append("Leverage spiral: high debt could impair the business in a downturn.")
        if (f.pe_ratio or 0) > 40:
            killers.append("Valuation compression: a de-rating from a high multiple could dominate returns.")
        if not killers:
            killers.append("Permanent loss of competitive position or a structural demand shift.")
        negative_news = [n.title for n in bundle.news.items if n.sentiment == "negative"]
        for title in negative_news[:2]:
            top_risks.append(f"News flag: {title}")
        if language == "zh-CN":
            question = f"反过来想：什么情况会让持有 {bundle.profile.name} 成为明显的错误？"
        else:
            question = f"Invert: what would have to be true for owning {bundle.profile.name} to be an obvious mistake?"
        return RiskReview(top_risks=top_risks[:6], thesis_killers=killers[:4], inversion_question=question)

    @staticmethod
    def _bull_bear(bundle, quality, moat, pv, language: str):
        f = bundle.fundamentals
        bull: list[str] = []
        bear: list[str] = []
        if quality.score >= 6.5:
            bull.append("High-quality economics: strong returns on capital and margins.")
        if moat.score >= 6.0:
            bull.append("Moat indicators suggest durable pricing power.")
        if (f.revenue_growth_5y or 0) >= 0.08:
            bull.append(f"Revenue compounding at ~{(f.revenue_growth_5y or 0) * 100:.0f}%/yr over five years.")
        if pv["discount_to_base"] > 0.05:
            bull.append(f"Price sits ~{pv['discount_to_base'] * 100:.0f}% below base-case fair value.")
        if not bull:
            bull.append("Limited bull case on current data; a materially lower price would improve the setup.")

        if pv["discount_to_base"] < -0.05:
            bear.append(f"Price sits ~{abs(pv['discount_to_base']) * 100:.0f}% above base-case fair value.")
        if (f.pe_ratio or 0) > 30:
            bear.append(f"Elevated earnings multiple ({f.pe_ratio:.0f}x) leaves little room for disappointment.")
        for r in moat.risks[:2]:
            bear.append(r)
        if not bear:
            bear.append("Execution slips, competitive pressure, or macro shocks could impair intrinsic value.")

        for n in bundle.news.items:
            if n.sentiment == "positive" and len(bull) < 5:
                bull.append(f"Supporting news: {n.title}")
            elif n.sentiment == "negative" and len(bear) < 5:
                bear.append(f"Cautionary news: {n.title}")
        return bull[:5], bear[:5]
