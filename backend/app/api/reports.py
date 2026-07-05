"""Report history endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas.report import ReportDetail, ReportSummary
from ..storage.database import get_db
from ..storage.models import Report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportSummary])
def list_reports(db: Session = Depends(get_db)):
    rows = db.query(Report).order_by(Report.created_at.desc()).limit(100).all()
    return [
        ReportSummary(
            id=r.id, job_id=r.job_id, ticker=r.ticker, company=r.company,
            analysis_mode=r.analysis_mode, final_verdict=r.final_verdict,
            confidence=r.confidence, is_mock_data=r.is_mock_data, created_at=r.created_at,
        )
        for r in rows
    ]


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(report_id: str, db: Session = Depends(get_db)):
    r = db.get(Report, report_id)
    if r is None:
        raise HTTPException(404, "Report not found")
    return ReportDetail(id=r.id, job_id=r.job_id, created_at=r.created_at, report=r.data)
