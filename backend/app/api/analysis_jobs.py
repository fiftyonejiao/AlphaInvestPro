"""Analysis job endpoints: create, poll, SSE event stream, and report."""

import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..schemas.analysis import AnalysisJobCreate, AnalysisJobOut, JobEventOut
from ..schemas.report import ReportDetail
from ..services.analysis_orchestrator import AnalysisOrchestrator
from ..storage.database import get_db, get_session
from ..storage.models import AnalysisJob, JobEvent, Report

router = APIRouter(prefix="/api/analysis-jobs", tags=["analysis-jobs"])

_orchestrator = AnalysisOrchestrator()


def _job_out(job: AnalysisJob) -> AnalysisJobOut:
    return AnalysisJobOut(
        id=job.id,
        ticker=job.ticker,
        company=job.company,
        analysis_mode=job.analysis_mode,
        language=job.language,
        status=job.status,
        current_step=job.current_step,
        error=job.error,
        report_id=job.report_id,
        is_mock_data=job.is_mock_data,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.post("", response_model=AnalysisJobOut, status_code=201)
async def create_job(body: AnalysisJobCreate, background: BackgroundTasks, db: Session = Depends(get_db)):
    job = AnalysisJob(
        ticker=body.ticker.upper().strip(),
        analysis_mode=body.analysis_mode,
        language=body.language,
        status="pending",
    )
    db.add(job)
    db.commit()
    background.add_task(_orchestrator.run, job.id)
    return _job_out(job)


@router.get("", response_model=list[AnalysisJobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(AnalysisJob).order_by(AnalysisJob.created_at.desc()).limit(50).all()
    return [_job_out(j) for j in jobs]


@router.get("/{job_id}", response_model=AnalysisJobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(AnalysisJob, job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    return _job_out(job)


@router.get("/{job_id}/events")
async def stream_events(job_id: str):
    """Server-Sent Events stream of job progress."""
    db = get_session()
    exists = db.get(AnalysisJob, job_id) is not None
    db.close()
    if not exists:
        raise HTTPException(404, "Job not found")

    async def generator():
        last_seq = 0
        idle_cycles = 0
        while True:
            db = get_session()
            try:
                events = (
                    db.query(JobEvent)
                    .filter(JobEvent.job_id == job_id, JobEvent.seq > last_seq)
                    .order_by(JobEvent.seq)
                    .all()
                )
                job = db.get(AnalysisJob, job_id)
            finally:
                db.close()

            for ev in events:
                last_seq = ev.seq
                out = JobEventOut(
                    seq=ev.seq, event_type=ev.event_type, step=ev.step,
                    payload=ev.payload or {}, created_at=ev.created_at,
                )
                yield f"data: {json.dumps(out.model_dump())}\n\n"

            if job and job.status in ("completed", "failed") and not events:
                yield f"data: {json.dumps({'event_type': 'stream_end', 'status': job.status, 'report_id': job.report_id})}\n\n"
                return

            idle_cycles = idle_cycles + 1 if not events else 0
            if idle_cycles > 600:  # ~5 minutes safety cutoff
                return
            await asyncio.sleep(0.5)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{job_id}/report", response_model=ReportDetail)
def get_job_report(job_id: str, db: Session = Depends(get_db)):
    job = db.get(AnalysisJob, job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    if not job.report_id:
        raise HTTPException(409, "Report not ready")
    report = db.get(Report, job.report_id)
    if report is None:
        raise HTTPException(404, "Report not found")
    return ReportDetail(id=report.id, job_id=job_id, created_at=report.created_at, report=report.data)
