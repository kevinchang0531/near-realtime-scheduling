"""Example long-running jobs — replace with real implementations."""
import logging
import time

logger = logging.getLogger(__name__)


def slow_report(report_id: str = "default") -> None:
    """Simulate a report that takes 2 minutes to generate."""
    logger.info("Starting report %s", report_id)
    time.sleep(120)
    logger.info("Report %s done", report_id)


def health_check() -> None:
    """Quick sanity check — useful for testing the scheduler is alive."""
    logger.info("Health check OK")
