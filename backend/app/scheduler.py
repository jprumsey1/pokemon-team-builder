"""Scheduler for PokeAPI sync."""

from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.db import session_factory
from app.services.sync import sync_pokemon

SYNC_TIMEZONE = ZoneInfo("America/New_York")


async def scheduled_sync_pokemon() -> None:
    async with session_factory() as session:
        await sync_pokemon(session)


def build_scheduler() -> AsyncIOScheduler:
    """Must be built and started inside lifespan — AsyncIOScheduler binds to the running loop."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_sync_pokemon,
        CronTrigger(hour=settings.sync_hour, timezone=SYNC_TIMEZONE),
        # After downtime, sweep once on the next start rather than once per day missed
        coalesce=True,
        misfire_grace_time=None,
    )
    return scheduler
