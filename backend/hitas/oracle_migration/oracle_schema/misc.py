from sqlalchemy import Column, Date, Integer, String, Table

from hitas.oracle_migration.oracle_schema.metadata import metadata_obj
from hitas.oracle_migration.types import HitasBoolean

additional_infos = Table(
    "HITLISAT",
    metadata_obj,
    Column("C_LISATVIITE", String(10), key="type", primary_key=True, nullable=False),
    Column("KG_LTUNNUS", Integer, key="object_id", primary_key=True, nullable=False),
    Column("TEKSTI1", String(100), nullable=False),
    Column("TEKSTI2", String(100)),
    Column("TEKSTI3", String(100)),
    Column("TEKSTI4", String(100)),
    Column("TEKSTI5", String(100)),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

users = Table(
    "HITKAYTT",
    metadata_obj,
    Column("KG_KOODI", Integer, key="id", primary_key=True),
    Column("C_KAYTTUNN", String(10), key="username", nullable=False),
    Column("C_SALASANA", String(10), key="password", nullable=False),
    Column("C_KRYHKOODI", String(16), nullable=False),
    Column("C_KAYRYHMA", String(12), nullable=False),
    Column("C_SELITE", String(50), key="name", nullable=False),
    Column("C_KAYTOSSA", HitasBoolean, key="is_active", nullable=False),
    Column("C_SISKIRJ", HitasBoolean, nullable=False),
    Column("D_SISKAIKA", Date),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)
