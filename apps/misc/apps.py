from django.apps import AppConfig


class MiscConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.misc"

    def ready(self):
        import apps.misc.signals
