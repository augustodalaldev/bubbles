import logging
import threading

from apps.core.scheduler import Job, Scheduler


class FakeClock:
    def __init__(self, now=1_000_000.0):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def make(jobs, clock, **kwargs):
    return Scheduler(jobs, clock=clock, manage_connections=False, **kwargs)


def test_jobs_run_immediately_on_start_then_wait_for_their_interval():
    clock, calls = FakeClock(), []
    job = Job("a", lambda: calls.append(clock.now) or "ok", interval=lambda: 300)
    scheduler = make([job], clock)

    assert [r.name for r in scheduler.tick()] == ["a"]
    assert scheduler.tick() == []  # not due yet
    clock.advance(299)
    assert scheduler.tick() == []
    clock.advance(1)
    assert [r.result for r in scheduler.tick()] == ["ok"]
    assert len(calls) == 2


def test_run_on_start_false_waits_one_interval_first():
    clock = FakeClock()
    job = Job("a", lambda: None, interval=lambda: 60)
    scheduler = make([job], clock, run_on_start=False)

    assert scheduler.tick() == []
    clock.advance(60)
    assert len(scheduler.tick()) == 1


def test_aligned_jobs_run_at_multiples_of_the_interval():
    clock = FakeClock(now=1_000_100.0)  # 100 s into a 300 s window
    job = Job("passive", lambda: None, interval=lambda: 300, align=True)
    scheduler = make([job], clock)

    assert len(scheduler.tick()) == 1  # immediate first run
    assert job.next_run == (1_000_100 // 300 + 1) * 300
    clock.now = job.next_run - 1
    assert scheduler.tick() == []
    clock.now = job.next_run
    assert len(scheduler.tick()) == 1


def test_interval_is_read_again_after_every_run():
    clock = FakeClock()
    interval = {"value": 60}
    job = Job("a", lambda: None, interval=lambda: interval["value"])
    scheduler = make([job], clock)

    scheduler.tick()
    assert job.next_run == clock.now + 60
    interval["value"] = 600
    clock.advance(60)
    scheduler.tick()
    assert job.next_run == clock.now + 600


def test_a_failing_job_does_not_stop_the_others_or_itself(caplog):
    clock = FakeClock()
    state = {"b_runs": 0}

    def explode():
        raise RuntimeError("boom")

    def healthy():
        state["b_runs"] += 1
        return state["b_runs"]

    a = Job("a", explode, interval=lambda: 60)
    b = Job("b", healthy, interval=lambda: 60)
    scheduler = make([a, b], clock)

    with caplog.at_level(logging.INFO, logger="bubbles.scheduler"):
        first = scheduler.tick()
    assert [(r.name, r.ok) for r in first] == [("a", False), ("b", True)]
    assert first[0].error == "RuntimeError: boom"
    assert "job a: FAILED" in caplog.text
    assert "job b: finished" in caplog.text

    clock.advance(60)
    second = scheduler.tick()  # the failed job is still scheduled and tried again
    assert [(r.name, r.ok) for r in second] == [("a", False), ("b", True)]
    assert a.failures == 2 and b.runs == 2


def test_run_forever_stops_when_asked_and_logs_start_and_stop(caplog):
    Scheduler.MIN_INTERVAL = 0.01
    try:
        stop = threading.Event()
        runs = []

        def job():
            runs.append(1)
            if len(runs) == 3:
                stop.set()

        scheduler = Scheduler([Job("tick", job, interval=lambda: 0.01)], manage_connections=False)
        with caplog.at_level(logging.INFO, logger="bubbles.scheduler"):
            scheduler.run_forever(stop)
    finally:
        Scheduler.MIN_INTERVAL = 1.0

    assert len(runs) == 3
    assert "scheduler started" in caplog.text
    assert "scheduler stopped" in caplog.text
