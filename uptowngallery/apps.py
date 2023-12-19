# apps.py
from django.apps import AppConfig
import sys


class UptowngalleryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uptowngallery"

    def ready(self):
        import uptowngallery.signals

        # Only schedule tasks if not running management commands like makemigrations or migrate
        if (
            "makemigrations" not in sys.argv
            and "migrate" not in sys.argv
        ):
            from django_q.tasks import schedule

            schedule(
                "uptowngallery.tasks.check_and_close_auctions",
                schedule_type="I",
                minutes=60,
            )
