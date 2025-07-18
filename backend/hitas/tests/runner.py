from django.conf import settings
from django.test.runner import DiscoverRunner
from testcontainers.postgres import PostgresContainer


class HitasTestContainer:
    def __init__(self):
        self.container = PostgresContainer(image="postgres:14")

    def start(self):
        self.container.start()

        for db in settings.DATABASES.values():
            if db["ENGINE"] != "django.db.backends.postgresql":
                continue

            db["USER"] = self.container.username
            db["PASSWORD"] = self.container.password
            db["NAME"] = self.container.dbname
            db["HOST"] = self.container.get_container_host_ip()
            db["PORT"] = self.container.get_exposed_port(self.container.port)

    def stop(self):
        self.container.stop()


class HitasDatabaseRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tc = HitasTestContainer()

    def setup_databases(self, **kwargs):
        self.tc.start()

        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        super().teardown_databases(old_config, **kwargs)

        self.tc.stop()
