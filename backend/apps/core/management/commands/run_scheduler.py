import logging
import signal
import threading

from django.core.management.base import BaseCommand, CommandError

from apps.content.services import cleanup_expired_bubblepops
from apps.core.scheduler import Job, Scheduler
from apps.economy.models import EconomySettings
from apps.economy.services import distribute_passive_soap


def passive_interval_seconds() -> float:
    """Follows `EconomySettings.passive_interval_minutes` (re-read after every run)."""
    return EconomySettings.load().passive_interval_minutes * 60


class Command(BaseCommand):
    help = (
        "Run the periodic jobs: distribute passive soap (every passive_interval_minutes, aligned "
        "to the interval) and clean up expired bubblepops (hourly by default)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run every job once and exit (non-zero if any failed). Useful for cron.",
        )
        parser.add_argument(
            "--cleanup-interval",
            type=int,
            default=3600,
            help="Seconds between bubblepop cleanups (default: 3600).",
        )
        parser.add_argument(
            "--passive-interval",
            type=int,
            default=None,
            help="Override the passive soap interval in seconds (default: the economy setting).",
        )
        parser.add_argument(
            "--no-run-on-start",
            action="store_true",
            help="Wait for the first interval instead of running the jobs immediately.",
        )

    def handle(self, *args, **options):
        # No-op when logging is already configured (tests, a host application).
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        passive = options["passive_interval"]
        jobs = [
            Job(
                "distribute_passive_soap",
                distribute_passive_soap,
                interval=(lambda: passive) if passive else passive_interval_seconds,
                align=True,
            ),
            Job(
                "cleanup_expired_bubblepops",
                cleanup_expired_bubblepops,
                interval=lambda: options["cleanup_interval"],
            ),
        ]
        scheduler = Scheduler(jobs, run_on_start=not options["no_run_on_start"])

        if options["once"]:
            results = [scheduler.run_job(job) for job in jobs]
            failed = [r.name for r in results if not r.ok]
            if failed:
                raise CommandError(f"Jobs failed: {', '.join(failed)}")
            return

        stop = threading.Event()
        for signum in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, lambda *_: stop.set())
        scheduler.run_forever(stop)
