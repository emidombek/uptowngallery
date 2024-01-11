# apps.py

import sys
from django.apps import AppConfig
from django.utils import timezone


class UptowngalleryConfig(AppConfig):
    name = "uptowngallery"

    def ready(self):
        import uptowngallery.signals

        # Import models when the app is ready
        from django_q.models import Schedule

        task_name = "uptowngallery.tasks.check_and_close_auctions"

        # Check if the task is already scheduled
        if not Schedule.objects.filter(
            func=task_name, next_run__gt=timezone.now()
        ).exists():
            from django_q.tasks import schedule

            schedule(
                func=task_name,
                schedule_type="I",
                minutes=60,
                name="Unique Name for My Task",  # Adding a unique name to the task
            )
