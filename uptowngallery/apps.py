import sys
from django.apps import AppConfig
from django.utils import timezone

"""
Cofig class that schedules django q tasks
"""


class UptowngalleryConfig(AppConfig):
    name = "uptowngallery"

    def ready(self):
        import uptowngallery.signals
        from django_q.models import Schedule

        task_name = "uptowngallery.tasks.check_and_close_auctions"
        if not Schedule.objects.filter(
            func=task_name, next_run__gt=timezone.now()
        ).exists():
            from django_q.tasks import schedule

            schedule(
                func=task_name,
                schedule_type="I",
                minutes=60,
                name="Unique Name for My Task",
            )
