"""A tiny in-process scheduler for the periodic maintenance jobs.

No Celery/Redis: a loop that runs each job when it is due. A job that raises is logged and
rescheduled, so one failure never stops the scheduler or the other jobs.
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from django.db import close_old_connections, connection

logger = logging.getLogger("bubbles.scheduler")

MAX_IDLE_SECONDS = 30.0  # wake up regularly so a stop request is noticed quickly


@dataclass
class Job:
    name: str
    run: Callable[[], Any]
    #: Seconds between runs; a callable so it can follow a setting changed at runtime.
    interval: Callable[[], float]
    #: Run at the next multiple of the interval (epoch-aligned) instead of "interval after the
    #: last run". Aligned jobs run once per window, which matches window-based idempotency.
    align: bool = False
    next_run: float = field(default=0.0, init=False)
    runs: int = field(default=0, init=False)
    failures: int = field(default=0, init=False)


@dataclass(frozen=True)
class JobResult:
    name: str
    ok: bool
    result: Any = None
    error: str | None = None


class Scheduler:
    MIN_INTERVAL = 1.0  # guards against a misconfigured 0-second interval busy-looping

    def __init__(
        self,
        jobs: list[Job],
        *,
        clock: Callable[[], float] = time.time,
        run_on_start: bool = True,
        manage_connections: bool = True,
    ):
        self.jobs = jobs
        self.clock = clock
        self.manage_connections = manage_connections
        now = clock()
        for job in jobs:
            self._schedule(job, now, first=True, run_on_start=run_on_start)

    # ------------------------------------------------------------------ scheduling
    def _schedule(self, job: Job, now: float, *, first: bool = False, run_on_start: bool = True):
        interval = max(self.MIN_INTERVAL, float(job.interval()))
        if first and run_on_start:
            job.next_run = now
        elif job.align:
            job.next_run = (now // interval + 1) * interval
        else:
            job.next_run = now + interval

    def seconds_until_next(self) -> float:
        return max(0.0, min(job.next_run for job in self.jobs) - self.clock())

    # ------------------------------------------------------------------ execution
    def run_job(self, job: Job) -> JobResult:
        started = self.clock()
        logger.info("job %s: started", job.name)
        if self.manage_connections:
            close_old_connections()  # a long-lived process must not keep a dead DB connection
        try:
            result = job.run()
        except Exception as exc:  # noqa: BLE001 - the scheduler must survive any job failure
            job.failures += 1
            logger.exception(
                "job %s: FAILED after %.2fs (failure #%d)",
                job.name,
                self.clock() - started,
                job.failures,
            )
            if self.manage_connections:
                connection.close()  # drop a possibly broken connection; Django reconnects
            return JobResult(job.name, ok=False, error=f"{type(exc).__name__}: {exc}")
        job.runs += 1
        logger.info("job %s: finished in %.2fs -> %s", job.name, self.clock() - started, result)
        return JobResult(job.name, ok=True, result=result)

    def tick(self) -> list[JobResult]:
        """Run every job that is due and reschedule it. Returns what happened."""
        results: list[JobResult] = []
        for job in self.jobs:
            if self.clock() >= job.next_run:
                results.append(self.run_job(job))
                self._schedule(job, self.clock())
        return results

    def run_forever(self, stop: threading.Event) -> None:
        logger.info("scheduler started with jobs: %s", ", ".join(j.name for j in self.jobs))
        while not stop.is_set():
            self.tick()
            stop.wait(min(self.seconds_until_next(), MAX_IDLE_SECONDS))
        logger.info("scheduler stopped")
