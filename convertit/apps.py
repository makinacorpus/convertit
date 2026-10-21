from django.apps import AppConfig
from django.conf import settings

from convertit import create_dir


class ConvertitConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "convertit"

    def ready(self):
        try:
            create_dir(settings.CONVERTIT_CONVERTED_PATH)
            create_dir(settings.CONVERTIT_DOWNLOADS_PATH)
        except OSError:
            pass
