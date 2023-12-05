# apps.py
from django.apps import AppConfig


class UptowngalleryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uptowngallery"

    def ready(self):
        import uptowngallery.signals
