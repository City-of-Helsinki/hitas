from sqlalchemy import Column, Date, Integer, String, Table

from hitas.oracle_migration.oracle_schema.metadata import metadata_obj
from hitas.oracle_migration.types import HitasAnonymizedName, HitasAnonymizedText, HitasAnonymizedWord, HitasBoolean

additional_infos = Table(
    "HITLISAT",
    metadata_obj,
    # Possible type values:
    # HITYHTIO HITHUONE HITISANTA
    # HITVALVO
    # HITEHIND HITHLIYH HITHLIHU
    # HITRAKIND HITRAKIYH HITRAKIHU
    # HITMHIND HITMHIYH HITMHIHU
    Column("C_LISATVIITE", String(10), key="type", primary_key=True, nullable=False),
    Column("KG_LTUNNUS", Integer, key="object_id", primary_key=True, nullable=False),
    Column("TEKSTI1", HitasAnonymizedText(100), nullable=False),
    Column("TEKSTI2", HitasAnonymizedText(100)),
    Column("TEKSTI3", HitasAnonymizedText(100)),
    Column("TEKSTI4", HitasAnonymizedText(100)),
    Column("TEKSTI5", HitasAnonymizedText(100)),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

users = Table(
    "HITKAYTT",
    metadata_obj,
    Column("KG_KOODI", Integer, key="id", primary_key=True),
    Column("C_KAYTTUNN", HitasAnonymizedWord(10, unique=True), key="username", nullable=False),
    Column("C_SALASANA", HitasAnonymizedWord(10), key="password", nullable=False),
    Column("C_KRYHKOODI", String(16), nullable=False),
    Column("C_KAYRYHMA", String(12), nullable=False),
    Column("C_SELITE", HitasAnonymizedName(50), key="name", nullable=False),
    Column("C_KAYTOSSA", HitasBoolean, key="is_active", nullable=False),
    Column("C_SISKIRJ", HitasBoolean, nullable=False),
    Column("D_SISKAIKA", Date),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)
