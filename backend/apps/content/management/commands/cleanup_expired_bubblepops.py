from django.core.management.base import BaseCommand

from apps.content.services import cleanup_expired_bubblepops


class Command(BaseCommand):
    help = "Hard-delete expired Bubblepop stories and clean up associated media files."

    def handle(self, *args, **options):
        deleted = cleanup_expired_bubblepops()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {deleted} expired Bubblepop(s).")
        )
