from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import Settings


logger = logging.getLogger(__name__)


def cleanup_directory(directory: Path, cutoff_time: datetime) -> int:
    """Delete files older than cutoff from a directory."""
    removed = 0
    if not directory.exists():
        return removed

    for file_path in directory.glob("*"):
        if not file_path.is_file():
            continue
        modified_at = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        if modified_at < cutoff_time:
            file_path.unlink(missing_ok=True)
            removed += 1
    return removed


def run_cleanup_once(settings: Settings) -> int:
    """Cleanup stale temp and output files once and return removed count."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=settings.cleanup_hours)
    temp_removed = cleanup_directory(settings.resolved_temp_dir, cutoff_time)
    output_removed = cleanup_directory(settings.resolved_output_dir, cutoff_time)
    total_removed = temp_removed + output_removed
    if total_removed:
        logger.info("Removed %s stale files.", total_removed)
    return total_removed


async def cleanup_loop(settings: Settings, stop_event: asyncio.Event) -> None:
    """Periodically remove stale temp and output files."""
    while not stop_event.is_set():
        run_cleanup_once(settings)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=settings.cleanup_interval_seconds)
        except TimeoutError:
            continue
