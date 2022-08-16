from django.db import connection
from health_check.backends import BaseHealthCheckBackend


class HitasDatabaseHealthCheck(BaseHealthCheckBackend):
    def check_status(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
