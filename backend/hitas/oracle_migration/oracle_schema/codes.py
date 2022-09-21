from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table

from hitas.oracle_migration.oracle_schema.metadata import metadata_obj
from hitas.oracle_migration.types import HitasBoolean

codebooks = Table(
    "OKOODISTO",
    metadata_obj,
    Column("KG_KOODISTO", Integer, key="id", primary_key=True),
    Column("C_KOODISTOID", String(16), key="code_type", nullable=False),
    Column("C_NIMI", String(50), nullable=False),
    Column("C_LYHENNE", String(20)),
    Column("C_SELITE", String(80)),
    Column("N_KOODIMAX", Integer, nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

codes = Table(
    "OKOODI",
    metadata_obj,
    Column("KG_OKOODI", Integer, key="id", primary_key=True),
    Column("C_KOODISTOID", String(16), key="code_type", nullable=False, index=True),
    Column("C_KOODIID", String(12), key="code_id", nullable=False, index=True),
    Column("D_ALKUPVM", Date, key="start_date", nullable=False),
    Column("D_LOPPUPVM", Date, key="end_date", nullable=False),
    Column("C_NIMI", String(50), key="value", nullable=False),
    Column("C_LYHENNE", String(20)),
    Column("C_SELITE", String(80), key="description"),
    Column("KG_KOODISTO", Integer, ForeignKey("OKOODISTO.id"), key="codebook_id", nullable=False),
    Column("C_KAYTOSSA", HitasBoolean, key="in_use", nullable=False),
    Column("N_JARJESTYS", Integer, key="order", nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)
