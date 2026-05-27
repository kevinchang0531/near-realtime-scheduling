import importlib
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from apscheduler.executors.pool import ThreadPoolExecutor as APSThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .config import settings

logger = logging.getLogger(__name__)


def _build_scheduler() -> BackgroundScheduler:
    jobstores = {
        "default": SQLAlchemyJobStore(url=settings.db_url),
    }
    executors = {
        "default": APSThreadPoolExecutor(max_workers=settings.max_workers),
    }
    job_defaults = {
        "coalesce": True,       # skip missed runs instead of piling up
        "max_instances": 1,     # prevent overlapping runs of the same job
    }
    return BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=settings.timezone,
    )


scheduler = _build_scheduler()


def resolve_func(func_path: str) -> Callable:
    """Load a callable from a dotted path, e.g. 'src.jobs.example:my_job'."""
    module_path, func_name = func_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def add_cron_job(job_id: str, func_path: str, cron_expr: str, kwargs: dict[str, Any] = {}) -> None:
    func = resolve_func(func_path)
    # cron_expr: standard 5-field cron "min hour dom mon dow"
    minute, hour, day, month, day_of_week = cron_expr.split()
    trigger = CronTrigger(
        minute=minute, hour=hour, day=day,
        month=month, day_of_week=day_of_week,
        timezone=settings.timezone,
    )
    scheduler.add_job(func, trigger, id=job_id, kwargs=kwargs, replace_existing=True)
    logger.info("Registered cron job %s [%s]", job_id, cron_expr)


def add_interval_job(job_id: str, func_path: str, seconds: int, kwargs: dict[str, Any] = {}) -> None:
    func = resolve_func(func_path)
    trigger = IntervalTrigger(seconds=seconds, timezone=settings.timezone)
    scheduler.add_job(func, trigger, id=job_id, kwargs=kwargs, replace_existing=True)
    logger.info("Registered interval job %s [every %ds]", job_id, seconds)


def trigger_now(job_id: str, func_path: str, kwargs: dict[str, Any] = {}) -> None:
    """Fire a one-shot job immediately."""
    func = resolve_func(func_path)
    trigger = DateTrigger(timezone=settings.timezone)
    scheduler.add_job(func, trigger, id=f"{job_id}_manual", kwargs=kwargs, replace_existing=True)
    logger.info("Triggered manual job %s", job_id)


def remove_job(job_id: str) -> bool:
    try:
        scheduler.remove_job(job_id)
        return True
    except Exception:
        return False


def list_jobs() -> list[dict]:
    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        }
        for job in scheduler.get_jobs()
    ]
