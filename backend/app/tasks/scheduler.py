"""Background scheduler setup."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.db import async_session_maker
from app.services.renewal_service import RenewalService

scheduler = AsyncIOScheduler()


async def run_renewal_check() -> None:
    """Run one mock renewal check."""
    async with async_session_maker() as session:
        await RenewalService(session).renew_expiring_certificates()


def start_scheduler() -> None:
    """Start configured background jobs."""
    if not settings.SCHEDULER_ENABLED or scheduler.running:
        return

    scheduler.add_job(
        run_renewal_check,
        "interval",
        hours=settings.RENEWAL_CHECK_INTERVAL_HOURS,
        id="mock_certificate_renewal",
        replace_existing=True,
    )
    scheduler.start()


def shutdown_scheduler() -> None:
    """Stop background jobs."""
    if scheduler.running:
        scheduler.shutdown()
