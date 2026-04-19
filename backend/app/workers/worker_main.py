from __future__ import annotations

import logging
import os


logger = logging.getLogger(__name__)


def main() -> None:
    """Start RQ worker process for queued enhancement jobs."""
    try:
        from redis import Redis
        from rq import Connection, Queue, Worker
    except Exception as exc:
        raise SystemExit(f"RQ worker dependencies are unavailable: {exc}") from exc

    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    queue_name = os.getenv("RQ_QUEUE", "enhance-jobs")

    connection = Redis.from_url(redis_url)
    queue = Queue(queue_name)

    logger.info("Starting RQ worker for queue '%s' on %s", queue_name, redis_url)
    with Connection(connection):
        worker = Worker([queue])
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
