import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import router
from .config import settings
from .scheduler import scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "running_jobs": len(scheduler.get_jobs())}
