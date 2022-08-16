from django.apps import AppConfig
from health_check.plugins import plugin_dir

from hitas.healthcheck import HitasDatabaseHealthCheck


class HitasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hitas"

    def ready(self):
        plugin_dir.register(HitasDatabaseHealthCheck)
