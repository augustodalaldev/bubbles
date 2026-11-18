from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from apps.core.demo.images import ImageLibrary
from apps.core.demo.seeder import DemoSeeder, reset_demo


def check_demo_environment() -> Path:
    """Refuse to run anywhere but the dedicated demo database (never the development one)."""
    demo_db = getattr(settings, "DEMO_DB_NAME", None)
    if not settings.DEBUG or not demo_db:
        raise CommandError(
            "seed_demo only runs with the demo settings "
            "(DJANGO_SETTINGS_MODULE=config.settings.demo, "
            "DEBUG on). Use `make demo`."
        )
    if connection.settings_dict["NAME"] != demo_db:
        raise CommandError(
            f"Refusing to run on database {connection.settings_dict['NAME']!r}: "
            f"only {demo_db!r} is allowed."
        )
    return Path(getattr(settings, "DEMO_CACHE_DIR", settings.BASE_DIR / ".demo_cache"))


class Command(BaseCommand):
    help = (
        "Fill the demo database (pet communities) through the application's services. "
        "Idempotent: running again does not duplicate. Only works with config.settings.demo."
    )

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=42, help="Random seed (default 42).")
        parser.add_argument(
            "--users", type=int, default=16, help="People, in the order of personas.py (max 16)."
        )
        parser.add_argument(
            "--communities", type=int, default=8, help="Communities (max 8, default 8)."
        )
        parser.add_argument(
            "--posts-per-user",
            type=int,
            default=0,
            help="Keep only this many posts per person (0 = all the written ones).",
        )
        parser.add_argument(
            "--comments-per-post", type=int, default=4, help="Up to this many reactions per photo."
        )
        parser.add_argument(
            "--expired-bubblepops",
            type=int,
            default=2,
            help="Already expired bubblepops for the cleanup job.",
        )
        parser.add_argument(
            "--days", type=int, default=45, help="Spread dates over this many past days."
        )
        parser.add_argument(
            "--images",
            type=int,
            default=60,
            help="Download at most this many photos per pool (cats, each dog breed).",
        )
        parser.add_argument(
            "--no-images", action="store_true", help="Create everything without images."
        )
        parser.add_argument(
            "--no-download", action="store_true", help="Use only the photos already cached."
        )
        parser.add_argument(
            "--reset", action="store_true", help="Delete what the seed created and exit."
        )

    def handle(self, *args, **options):
        cache_dir = check_demo_environment()

        if options["reset"]:
            counts = reset_demo(cache_dir, log=self.stdout.write)
            if counts:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Removed: " + ", ".join(f"{n} {k}" for k, n in counts.items())
                    )
                )
            return

        images = ImageLibrary(
            cache_dir,
            enabled=not options["no_images"],
            download=not options["no_download"],
            per_species=options["images"],
            warn=lambda message: self.stderr.write(self.style.WARNING(message)),
        )
        seeder = DemoSeeder(
            cache_dir=cache_dir,
            images=images,
            seed=options["seed"],
            users=options["users"],
            communities=options["communities"],
            posts_per_user=options["posts_per_user"],
            comments_per_post=options["comments_per_post"],
            expired_bubblepops=options["expired_bubblepops"],
            days=options["days"],
            log=self.stdout.write,
        )
        result = seeder.run()

        created = result["stats"]
        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        for label, count in sorted(created.items()):
            self.stdout.write(f"  {label}: {count}")
        if not created:
            self.stdout.write("  (nothing new: the data already exists)")
        self.stdout.write("\nLogin credentials (all accounts share the password):")
        for role, username, password in result["credentials"]:
            self.stdout.write(f"  {role:<32} {username:<28} {password}")
