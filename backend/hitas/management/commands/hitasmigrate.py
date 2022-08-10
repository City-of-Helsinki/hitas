import logging
import os

from django.core.management.base import BaseCommand, CommandParser
from sqlalchemy import and_, create_engine
from sqlalchemy.engine import LegacyRow
from sqlalchemy.sql import select

from hitas.management.commands.migrate.globals import anonymize_data
from hitas.management.commands.migrate.oracle_schema import (
    additional_infos,
    apartments,
    codebooks,
    codes,
    companies,
    company_addresses,
    property_managers,
    real_estates,
)
from hitas.models import HousingCompany


class Command(BaseCommand):
    help = "Hitas database migration tool."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--anonymize", action="store_true", help="Create anonymous data.")
        parser.add_argument("--debug", action="store_true", help="Show debug information.")
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

        self.run(
            options["oracle_host"],
            options["oracle_port"],
            options["oracle_user"],
            oracle_pw,
            options["debug"],
            options["anonymize"],
        )

    def run(
        self,
        oracle_host: str,
        oracle_port: str,
        oracle_user: str,
        oracle_pw: str,
        debug: bool,
        anonymize: bool,
    ) -> None:

        if debug:
            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

        if anonymize:
            anonymize_data()

        engine = create_engine(
            f"oracle+cx_oracle://{oracle_user}:{oracle_pw}@{oracle_host}:{oracle_port}/xe?"
            "encoding=UTF-8&nencoding=UTF-8"
        )

        with engine.connect() as connection:
            with connection.begin():

                # Companies

                a = additional_infos.alias("AI_COMPANY")
                b = additional_infos.alias("AI_PROPERTY_MANAGER")

                c = connection.execute(
                    select(companies, company_addresses, property_managers, a, b)
                    .join(company_addresses)
                    .join(property_managers)
                    .join(a, and_(companies.c.additional_info_key == a.c.type, companies.c.id == a.c.object_id))
                    .join(
                        b,
                        and_(
                            property_managers.c.additional_info_key == b.c.type, property_managers.c.id == b.c.object_id
                        ),
                    )
                ).fetchall()[0]

                for column in companies.c:
                    printc(str(column), c[column])

                for column in a.c:
                    printc(str(column), c[column])

                for column in company_addresses.c:
                    printc(str(column), c[column])

                for column in property_managers.c:
                    printc(str(column), c[column])

                for column in b.c:
                    printc(str(column), c[column])

                print()

                hc = HousingCompany()
                hc.official_name = c["official_name"]
                hc.display_name = c["display_name"]
                hc.street_address = c["address"]
                hc.legacy_id = c["id"]
                hc.notes = combine_notes(c)
                hc.last_modified_datetime = c["last_modified"]

                for f in HousingCompany._meta.get_fields():
                    if f.is_relation:
                        continue
                    printc(f.name, f.value_from_object(hc))

                print()

                # Real estates

                all_re = connection.execute(select(real_estates).where(real_estates.c.company_id == c.id)).fetchall()

                for re in all_re:
                    for column in real_estates.c:
                        printc(str(column), re[column])

                print()

                # Apartments

                all_apartments = connection.execute(
                    select(apartments, additional_infos)
                    .join(additional_infos)
                    .where(apartments.c.company_id == c.id)
                    .limit(3)
                ).fetchall()

                for apartment in all_apartments:
                    for column in apartments.c:
                        printc(str(column), apartment[column])

                    for column in additional_infos.c:
                        printc(str(column), apartment[column])

                    print()

                # Codebook

                codebook = connection.execute(
                    select(codebooks).where(codebooks.c.C_KOODISTOID == "OSA_ALUEET")
                ).fetchall()[0]

                for column in codebooks.c:
                    printc(str(column), codebook[column])

                print()

                # Codes

                all_codes = connection.execute(
                    select(codes).where(codes.c.codebook_id == codebook.id).limit(3)
                ).fetchall()

                for code in all_codes:
                    for column in codes.c:
                        printc(str(column), code[column])
                    print()


def combine_notes(a: LegacyRow) -> str:
    return "\n".join(
        [note for note in [a["TEKSTI1"], a["TEKSTI2"], a["TEKSTI3"], a["TEKSTI4"], a["TEKSTI5"]] if note is not None]
    )


def printc(column: str, value: str) -> None:
    print(f"{column: <40} - {value}")
