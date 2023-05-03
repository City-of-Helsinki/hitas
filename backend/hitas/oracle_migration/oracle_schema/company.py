from sqlalchemy import Column, Date, Float, ForeignKey, ForeignKeyConstraint, Integer, String, Table

from hitas.oracle_migration.oracle_schema.metadata import metadata_obj
from hitas.oracle_migration.types import (
    HitasAnonymizedAddress,
    HitasAnonymizedMonthAndDay,
    HitasAnonymizedName,
    HitasAnonymizedNameCommaSeparated,
    HitasAnonymizedPropertyIdentifier,
    HitasAnonymizedSSN,
    HitasBoolean,
)

companies = Table(
    "HITYHTIO",
    metadata_obj,
    Column("KG_YTUNNUS", Integer, key="id", primary_key=True),
    Column("C_YHTNIMI", HitasAnonymizedAddress(100, unique=True), key="official_name", nullable=False),
    Column("C_HAKUNIMI", HitasAnonymizedAddress(50, unique=True), key="display_name", nullable=False),
    Column("C_KATUOS", HitasAnonymizedAddress(50), key="address", nullable=False),
    Column("C_POSKOODI", String(16), nullable=False),  # Always 'POSTINROT'
    Column("C_POSTINRO", String(12), key="postal_code_code", nullable=False),
    Column("C_PTP", String(12), nullable=False),  # Always 'Helsinki'
    Column("C_KIINTTUN", HitasAnonymizedPropertyIdentifier(14), key="property_identifier", nullable=False),
    Column("C_KUNTA", String(3), nullable=False),  # Always '091'
    Column("C_KOSAKOODI", String(16), nullable=False),  # Always 'KAUPOSA'
    Column("C_KAUPOSA", String(12), nullable=False),
    Column("C_KORTTELI", String(4), nullable=False),
    Column("C_TONTTI", String(4), nullable=False),
    Column("N_HUONELKM", Integer),
    Column("N_HPALA1M2", Integer),
    Column("N_HPALA2M2", Integer),
    Column("N_OSAKELKM1", Integer),
    Column("N_OSAKELKM2", Integer),
    Column("D_ASLTKPVM", Date),
    Column("C_ASLTKPYK", String(12)),
    Column("C_VIRAKOODI", String(16), nullable=False),  # Always 'VIRANOMAINEN'
    Column("C_VIRATYYP", String(12), nullable=False),
    Column("N_HANKARVO1", Integer, key="acquisition_price", nullable=False),
    Column("N_HANKARVO2", Integer, key="realized_acquisition_price", nullable=False),
    Column("N_ENSISIJLA1", Integer, key="primary_loan", nullable=False),
    Column("N_ENSISIJLA2", Integer, nullable=False),
    Column("N_RAKKORKO", Float, key="construction_time_interest_rate", nullable=False),
    Column("N_VIIVKORKO1", Float, nullable=False),  # Always 0
    Column("N_VIIVKORKO2", Float, nullable=False),  # Always 0
    Column("D_MHLVAHPVM", HitasAnonymizedMonthAndDay, key="sales_price_catalogue_confirmation_date"),
    Column("C_TALOKOODI", String(16), nullable=False),  # Always 'TALOTYYPPI'
    Column("C_TALOTYYP", String(12), key="building_type_code", nullable=False),
    Column("C_RAKEKOODI", String(16), nullable=False),  # Always 'RAKENTAJA'
    Column("C_RAKENTAJA", String(12), key="developer_code", nullable=False),
    Column("C_RAHAKOODI", String(16), nullable=False),  # Always 'RAHMUOTO'
    Column("C_RAHMUOTO", String(12), key="financing_method_code", nullable=False),
    Column("KG_ITUNNUS", Integer, ForeignKey("HITISANTA.id"), key="property_manager_id", nullable=False),
    Column("C_RAKVAIHE", HitasBoolean, nullable=False),
    Column("C_LISATIETO", HitasBoolean, nullable=False),
    Column("C_LISATVIITE", String(10), key="additional_info_key", nullable=False),  # Always 'HITYHTIO' or null
    Column("C_MUUTTAJA", String(10), key="last_modified_by", nullable=False),
    Column("D_MUUTETTU", Date, key="last_modified", nullable=False),
    Column("C_SAANNOSTELY", HitasBoolean, nullable=False),
    Column("C_HITVAPKOODI", String(16), key="state_codebook", nullable=False),  # Always 'HITVAPAUTUS'
    Column("C_HITVAPTYYP", String(12), key="state_code", nullable=False),
    Column("D_HITVAPILMPVM", HitasAnonymizedMonthAndDay, key="legacy_release_date"),
    Column("N_MHINDKESKIHINTA", Integer, nullable=False),
    Column("N_RAKINDKESKIHINTA", Integer, nullable=False),
    Column("C_DIAARINRO", String(10)),
    Column("C_EMAIL", String(50)),
    Column("N_MHINDEKSI", Float, nullable=False),
    Column("N_RAKINDEKSI", Float, nullable=False),
    Column("C_LASKENTAKOODI", String(16), nullable=False),  # Always 'LASKENTASAANTO'
    Column("C_LASKSAANTO", String(12), nullable=False),
    Column("D_LASKVOIMPVM", Date, nullable=False),
    Column("N_SAANTELYTARKLKM", Integer, nullable=False),
    Column("C_HINTAKONTROLLOITU", HitasBoolean, nullable=False),
    ForeignKeyConstraint(("additional_info_key", "id"), ["HITLISAT.type", "HITLISAT.object_id"]),
)

company_addresses = Table(
    "HITYHTIONOSOITE",
    metadata_obj,
    Column("KG_YOTUNNUS", Integer, key="id", primary_key=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False),
    Column("C_KATUOS", String(50), nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

real_estates = Table(
    "HITKIINTEISTO",
    metadata_obj,
    Column("KG_KTUNNUS", Integer, key="id", primary_key=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False),
    Column("C_KIINTTUN", HitasAnonymizedPropertyIdentifier(14), key="property_identifier", nullable=False),
    Column("C_KUNTA", String(3), nullable=False),
    Column("C_KOSAKOODI", String(16), nullable=False),  # Always 'KAUPOSA'
    Column("C_KAUPOSA", String(3), nullable=False),
    Column("C_KORTTELI", String(4), nullable=False),
    Column("C_TONTTI", String(4), nullable=False),
    Column("N_HUONELKM", Integer),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

apartments = Table(
    "HITHUONE",
    metadata_obj,
    Column("KG_HTUNNUS", Integer, key="id", primary_key=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False, index=True),
    Column("C_OMNIMI1", HitasAnonymizedName(50), index=True),
    Column("C_SOTU1", HitasAnonymizedSSN(11)),
    Column("C_OMNIMI2", HitasAnonymizedName(50), index=True),
    Column("C_SOTU2", HitasAnonymizedSSN(11)),
    Column("C_KATUOS", HitasAnonymizedAddress(50), key="street_address", nullable=False),
    Column("C_PORRAS", String(3), key="stair", nullable=False),
    Column("N_HUONRO", Integer, key="apartment_number", nullable=False),
    Column("C_OSOITE", String(70), nullable=False, index=True),
    Column("C_POSKOODI", String(16), nullable=False),  # Always 'POSTINROT'
    Column("C_POSTINRO", String(12), key="postal_code_code", nullable=False),
    Column("C_PTP", String(30), nullable=False),  # Always 'HELSINKI'
    Column("C_KERROS", String(3), key="floor"),
    Column("N_HUONELKM", Integer, key="rooms", nullable=False),
    Column("C_HUONKOODI", String(16), nullable=False),  # Always 'HUONETYYPPI'
    Column("C_HUONTYYP", String(12), key="apartment_type_code", nullable=False),
    Column("N_HPALA", Float, key="surface_area", nullable=False),
    Column("N_OSAKELKM1", Integer, key="share_number_start", nullable=False),
    Column("N_OSAKELKM2", Integer, key="share_number_end", nullable=False),
    Column("N_OSAKEYHT", Integer, nullable=False),
    Column("D_VALMPVM", Date, key="completion_date"),
    Column("N_LUOVHINTA", Integer, key="debt_free_purchase_price", nullable=False),
    Column("N_KAUPHINTA", Integer, key="purchase_price", nullable=False),
    Column("N_ENSIJLAINA", Integer, key="primary_loan_amount", nullable=False),
    Column("N_HANKARVO", Integer, key="acquisition_price", nullable=False),
    Column("N_RAKKORKO", Integer, key="interest_during_construction", nullable=False),
    Column("D_KAUPPVM1", Date, key="first_purchase_date"),
    Column("D_KAUPPVM2", Date, key="latest_purchase_date"),
    Column("N_RAKLAINA", Integer, key="loans_during_construction", nullable=False),
    Column("N_RALUOVHINTA", Integer, key="debt_free_purchase_price_during_construction", nullable=False),
    Column("C_LISATIET", HitasBoolean, nullable=False),
    Column("C_LISATVIITE", String(10), key="additional_info_key", nullable=False),  # Always 'HITHUONE'
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
    Column("D_LASKVERTPVM", Date),
    Column("N_HLINDEHINTA", Integer),
    Column("N_MHINDEHINTA", Integer),
    Column("N_KIINTLISA", Integer),
    Column("C_PARANNHUOM", HitasBoolean),
    Column("N_PPALA", Float, nullable=False),
    Column("N_RAKAIKLISATYOT", Integer, key="additional_work_during_construction", nullable=False),
    Column("C_MYYTAVA", HitasBoolean, nullable=False),
    Column("KG_VTUNNUS", Integer, nullable=False),
    Column("D_VARAPVM", Date),  # Always null
    ForeignKeyConstraint(("additional_info_key", "id"), ["HITLISAT.type", "HITLISAT.object_id"]),
)

apartment_ownerships = Table(
    "HITHUONEOMISTAJUUS",
    metadata_obj,
    Column("KG_HOTUNNUS", Integer, key="id", primary_key=True),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False),
    Column("C_OMNIMI", HitasAnonymizedNameCommaSeparated(50), key="name"),
    Column("C_SOTU", HitasAnonymizedSSN(11), key="social_security_number"),
    Column("C_OMNIMIUPPER", String(50)),
    Column("N_PROSENTTIOSUUS", Float, key="percentage"),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

apartment_payments = Table(
    "HITMAKSUERA",
    metadata_obj,
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), primary_key=True, key="apartment_id", nullable=False),
    Column("KG_MTUNNUS", Integer, primary_key=True, nullable=False),
    Column("N_MAKSUERA", Integer, key="percentage", nullable=False),
    Column("D_MAKSUERAPVM", Date, key="date", nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)
