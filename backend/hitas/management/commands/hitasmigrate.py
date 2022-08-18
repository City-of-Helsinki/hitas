import os

from django.core.management.base import BaseCommand, CommandParser

from hitas.oracle_migration.runner import run


class Command(BaseCommand):
    help = "Hitas database migration tool."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--anonymize", action="store_true", help="Create anonymous data.")
        parser.add_argument("--debug", action="store_true", help="Show debug information.")
        parser.add_argument(
            "--truncate", action="store_true", help="Truncate hitas tables before starting the migration."
        )
        parser.add_argument("--oracle-host", default="localhost", help="Oracle database host (default: 'localhost').")
        parser.add_argument("--oracle-port", type=int, default=1521, help="Oracle database port (default: 1521).")
        parser.add_argument("--oracle-user", default="system", help="Oracle database user (default: 'system').")
        parser.add_argument(
            "--oracle-password",
            default="oracle",
            help="Oracle database password (default 'oracle')."
            " Can be also set with 'HITAS_ORACLE_PASSWORD' environment variable.",
        )

    def handle(self, *args, **options) -> None:
        try:
            oracle_pw = os.environ["HITAS_ORACLE_PASSWORD"]
        except KeyError:
            oracle_pw = options["oracle_password"]

        run(
            options["oracle_host"],
            options["oracle_port"],
            options["oracle_user"],
            oracle_pw,
            options["debug"],
            options["anonymize"],
            options["truncate"],
        )
