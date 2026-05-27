from fastapi import APIRouter, HTTPException

from .models import (
    CronTriggerRequest,
    IntervalTriggerRequest,
    JobResult,
    ManualTriggerRequest,
)
from .scheduler import add_cron_job, add_interval_job, list_jobs, remove_job, trigger_now

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/")
def get_jobs() -> list[dict]:
    return list_jobs()


@router.post("/cron", response_model=JobResult)
def create_cron_job(req: CronTriggerRequest) -> JobResult:
    try:
        add_cron_job(req.job_id, req.func_path, req.cron_expr, req.kwargs)
        return JobResult(job_id=req.job_id, status="scheduled", message=f"Cron job scheduled: {req.cron_expr}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/interval", response_model=JobResult)
def create_interval_job(req: IntervalTriggerRequest) -> JobResult:
    try:
        add_interval_job(req.job_id, req.func_path, req.seconds, req.kwargs)
        return JobResult(job_id=req.job_id, status="scheduled", message=f"Interval job scheduled: every {req.seconds}s")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trigger", response_model=JobResult)
def manual_trigger(req: ManualTriggerRequest) -> JobResult:
    try:
        trigger_now(req.job_id, req.func_path, req.kwargs)
        return JobResult(job_id=req.job_id, status="triggered", message="Job triggered immediately")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{job_id}", response_model=JobResult)
def delete_job(job_id: str) -> JobResult:
    removed = remove_job(job_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found")
    return JobResult(job_id=job_id, status="removed", message="Job removed")
