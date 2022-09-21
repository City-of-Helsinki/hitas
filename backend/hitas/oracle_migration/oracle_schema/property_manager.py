from sqlalchemy import Column, Date, ForeignKeyConstraint, Integer, String, Table

from hitas.oracle_migration.oracle_schema.metadata import metadata_obj
from hitas.oracle_migration.types import HitasBoolean

property_managers = Table(
    "HITISANTA",
    metadata_obj,
    Column("KG_ITUNNUS", Integer, key="id", primary_key=True),
    Column("C_TOIMISTO", String(100), key="name", nullable=False),
    Column("C_SUKUNIMI", String(50)),
    Column("C_ETUNIMI", String(30)),
    Column("C_KATUOS", String(50), key="address", nullable=False),
    Column("C_POSKOODI", String(16), nullable=False),  # Always 'POSTINROT'
    Column("C_POSTINRO", String(12), key="postal_code", nullable=False),
    Column("C_PTP", String(30), key="city", nullable=False),
    Column("C_PUHELIN", String(20)),
    Column("C_GSM", String(20)),
    Column("C_TELEFAX", String(20)),
    Column("C_EMAIL", String(50), key="email"),
    Column("C_LISATIETO", HitasBoolean, nullable=False),
    Column("C_LISATVIITE", String(10), key="additional_info_key"),  # Always 'HITISANTA'
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
    ForeignKeyConstraint(("additional_info_key", "id"), ["HITLISAT.type", "HITLISAT.object_id"]),
)
