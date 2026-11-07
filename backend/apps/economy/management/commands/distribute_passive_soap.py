from django.core.management.base import BaseCommand

from apps.economy.services import distribute_passive_soap


class Command(BaseCommand):
    help = "Distribute passive soap to active users who have been seen recently."

    def handle(self, *args, **options):
        credited = distribute_passive_soap()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully distributed passive soap to {credited} eligible user(s)."
            )
        )
