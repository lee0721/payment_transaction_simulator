"""
Entrypoint for launching an RQ worker that processes RiskOps jobs.
"""

from __future__ import annotations

from rq import Connection, Queue, Worker
from redis import Redis

from app.core import config
from worker import tasks  # noqa: F401 - ensure tasks are registered


def main() -> None:
    settings = config.get_settings()
    redis_conn = Redis.from_url(settings.redis_url)
    queues = [Queue("riskops", connection=redis_conn)]
    with Connection(redis_conn):
        Worker(queues).work(burst=False)


if __name__ == "__main__":
    main()
