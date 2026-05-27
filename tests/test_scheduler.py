import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_jobs_empty():
    r = client.get("/jobs/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_manual_trigger():
    r = client.post("/jobs/trigger", json={
        "job_id": "test_health",
        "name": "Test Health Check",
        "func_path": "src.jobs.example:health_check",
        "kwargs": {},
    })
    assert r.status_code == 200
    assert r.json()["status"] == "triggered"


def test_cron_job_lifecycle():
    r = client.post("/jobs/cron", json={
        "job_id": "test_cron",
        "name": "Test Cron",
        "cron_expr": "0 * * * *",
        "func_path": "src.jobs.example:health_check",
        "kwargs": {},
    })
    assert r.status_code == 200
    assert r.json()["status"] == "scheduled"

    r = client.delete("/jobs/test_cron")
    assert r.status_code == 200
    assert r.json()["status"] == "removed"


def test_delete_nonexistent_job():
    r = client.delete("/jobs/does_not_exist")
    assert r.status_code == 404
