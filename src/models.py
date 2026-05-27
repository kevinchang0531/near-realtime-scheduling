from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class TriggerType(str, Enum):
    cron = "cron"
    interval = "interval"
    date = "date"      # one-shot at specific time
    event = "event"    # manually triggered via API


class TaskInfo(BaseModel):
    job_id: str
    name: str
    trigger_type: TriggerType
    next_run_time: datetime | None = None
    status: TaskStatus = TaskStatus.pending


class CronTriggerRequest(BaseModel):
    job_id: str
    name: str
    cron_expr: str          # e.g. "0 */6 * * *"
    func_path: str          # e.g. "src.jobs.example:my_job"
    kwargs: dict[str, Any] = {}


class IntervalTriggerRequest(BaseModel):
    job_id: str
    name: str
    seconds: int
    func_path: str
    kwargs: dict[str, Any] = {}


class ManualTriggerRequest(BaseModel):
    job_id: str
    name: str
    func_path: str
    kwargs: dict[str, Any] = {}


class JobResult(BaseModel):
    job_id: str
    status: str
    message: str
