from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Table

from hitas.oracle_migration.oracle_schema.metadata import metadata_obj
from hitas.oracle_migration.types import (
    HitasAnonymizedName,
    HitasAnonymizedSSN,
    HitasBoolean,
    HitasDuration,
    HitasYearMonth,
)

#
# max price index 'enimmäishintaindeksi'
#

max_price_indices = Table(
    "HITEHIND",
    metadata_obj,
    Column("KG_EHIND", Integer, key="id", primary_key=True),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False, index=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False, index=True),
    Column("C_DIANRO", String(10)),
    Column("C_OMNIMI1", HitasAnonymizedName(50)),
    Column("C_OMNIMI2", HitasAnonymizedName(50)),
    Column("C_OSOITE", String(70), nullable=False),
    Column("C_POSKOODI", String(16), nullable=False),  # Always 'POSTINROT'
    Column("C_POSTINRO", String(12), nullable=False),
    Column("C_PTP", String(30), nullable=False),
    Column("D_KAUPPVM1", Date, nullable=False),
    Column("N_EHINDKPVM", Float, nullable=False),
    Column("D_EHLASKPVM", Date, nullable=False),
    Column("N_EHINDLPVM", Float, nullable=False),
    Column("N_HANKARVO", Integer, nullable=False),
    Column("N_KORKOPROS", Float, nullable=False),
    Column("N_RAKKORKO", Integer, nullable=False),
    Column("N_PERHINTA", Integer, nullable=False),
    Column("N_INDNOUSU", Integer, nullable=False),
    Column("N_HUONPAR", Integer, nullable=False),
    Column("N_YHTPAR", Integer, nullable=False),
    Column("N_VELHINTA", Integer, nullable=False),
    Column("N_YHTLAINA", Integer, nullable=False),
    Column("N_HUOVAH", Integer, nullable=False),
    Column("N_EHINTA", Integer, nullable=False),
    Column("N_EHINTAM2", Integer, nullable=False),
    Column("C_LASKAAVA", String(50)),
    Column("C_LISATIETO1", HitasBoolean, nullable=False),
    Column("C_LISATVIITE1", String(10), nullable=False),  # Always 'HITEHIND'
    Column("C_LISATIETO2", HitasBoolean, nullable=False),
    Column("C_LISATVIITE2", String(10), nullable=False),  # Always 'HITHLIHU'
    Column("C_LISATIETO3", HitasBoolean, nullable=False),
    Column("C_LISATVIITE3", String(10), nullable=False),  # Always 'HITHLIYH'
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

#
# hitas selling price index 'hitas-luovutushintaindeksi'
#

apartment_selling_price_indices = Table(
    "HITHLIHU",
    metadata_obj,
    Column("KG_HLIHUOPAR", Integer, key="id", primary_key=True),
    Column("KG_EHIND", Integer, ForeignKey("HITEHIND.id"), key="max_price_index_id", nullable=False, index=True),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False, index=True),
    Column("D_LASKPVM", Date, key="calculation_date", nullable=False),
    Column("N_HLILASKPVM", Float, key="calculation_date_index", nullable=False),
    Column("C_VALMPVM", HitasYearMonth, key="completion_date", nullable=False),
    Column("N_HLIVALMPVM", Float, key="ready_date_index", nullable=False),
    Column("C_HUOPAR", String(100), key="name", nullable=False),
    Column("N_HARVO", Integer, key="value", nullable=False),
    Column("N_HLILARVO", Float, key="calculated_value", nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

company_selling_price_indices = Table(
    "HITHLIYH",
    metadata_obj,
    Column("KG_HLIYHTPAR", Integer, key="id", primary_key=True),
    Column("KG_EHIND", Integer, ForeignKey("HITEHIND.id"), key="max_price_index_id", nullable=False, index=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False, index=True),
    Column("D_LASKPVM", Date, key="calculation_date", nullable=False),
    Column("N_HLILASKPVM", Float, key="calculation_date_index", nullable=False),
    Column("C_VALMPVM", HitasYearMonth, key="completion_date", nullable=False),
    Column("N_HLIVALMPVM", Float, key="ready_date_index", nullable=False),
    Column("C_ISJAKOPER", HitasBoolean, key="custom_price_distribution", nullable=False),
    Column("C_JAKOKOODI", String(16), nullable=False),  # Always 'HLIJAKOPER'
    Column("C_JAKOPER", String(12), key="price_distribution", nullable=False),  # 0000, 0001, 0002, 0003, 0004
    Column("N_JAKOYHTIO", Integer, key="company_portion", nullable=False),
    Column("N_JAKOHUONE", Float, key="apartment_portion", nullable=False),
    Column("C_YHTPAR", String(100), key="name", nullable=False),
    Column("N_HARVO", Integer, key="value", nullable=False),
    Column("N_HLIYHTARVO", Float, key="calculated_value_company", nullable=False),
    Column("N_HLIHUOARVO", Float, key="calculated_value_apartment", nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

#
# construction price index 'rakennuskustannusindeksi' calculations (confirmed or unconfirmed)
#

construction_price_indices = Table(
    "HITRAKIND",
    metadata_obj,
    Column("KG_EHIND", Integer, key="id", primary_key=True),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False, index=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False, index=True),
    Column("C_DIANRO", String(10)),
    Column("C_OMNIMI1", HitasAnonymizedName(50)),
    Column("C_OMNIMI2", HitasAnonymizedName(50)),
    Column("C_OSOITE", String(70), nullable=False),
    Column("C_POSKOODI", String(16), nullable=False),  # Always 'POSTINROT'
    Column("C_POSTINRO", String(12), nullable=False),
    Column("C_PTP", String(30), nullable=False),
    Column("D_KAUPPVM1", Date, nullable=False),
    Column("N_RAKINDKPVM", Float, nullable=False),
    Column("D_VALMPVM", Date, nullable=False),
    Column("N_RAKINDVPVM", Float, nullable=False),
    Column("D_LASKPVM", Date, key="calculation_date", nullable=False),
    Column("N_RAKINDLPVM", Float, nullable=False),
    Column("C_POISTOAIKA", HitasDuration, key="depreciation_period", nullable=False),
    Column("N_POISTOKER", Float, nullable=False),
    Column("N_HANKARVO1", Integer, nullable=False),
    Column("N_YHTPAR1", Integer, nullable=False),
    Column("N_PERHINTA1", Integer, nullable=False),
    Column("N_OSAKEOS1", Integer, nullable=False),
    Column("N_KORKOPROS1", Float, nullable=False),
    Column("N_RAKKORKO1", Integer, nullable=False),
    Column("N_HUONPAR1", Integer, nullable=False),
    Column("N_VELHINTA1", Integer, nullable=False),
    Column("N_HUOVAH1", Integer, nullable=False),
    Column("N_YHTLAINA1", Integer, nullable=False),
    Column("N_EHINTAM21", Integer, nullable=False),
    Column("N_EHINTA1", Integer, nullable=False),
    Column("N_HANKARVO2", Integer, nullable=False),
    Column("N_YHTPAR2", Integer, nullable=False),
    Column("N_PERHINTA2", Integer, nullable=False),
    Column("N_OSAKEOS2", Integer, nullable=False),
    Column("N_KORKOPROS2", Float, nullable=False),
    Column("N_RAKKORKO2", Integer, nullable=False),
    Column("N_HUONPAR2", Integer, nullable=False),
    Column("N_VELHINTA2", Integer, nullable=False),
    Column("N_HUOVAH2", Integer, nullable=False),
    Column("N_YHTLAINA2", Integer, nullable=False),
    Column("N_EHINTAM22", Integer, nullable=False),
    Column("N_EHINTA2", Integer, key="max_price", nullable=False),
    Column("C_LASKAAVA", String(50)),
    Column("C_LISATIETO1", HitasBoolean, nullable=False),
    Column("C_LISATVIITE1", String(10), nullable=False),  # Always 'HITRAKIND'
    Column("C_LISATIETO2", HitasBoolean, nullable=False),
    Column("C_LISATVIITE2", String(10), nullable=False),  # Always 'HITRAKIHU'
    Column("C_LISATIETO3", HitasBoolean, nullable=False),
    Column("C_LISATVIITE3", String(10), nullable=False),  # Always 'HITRAKIYH'
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, key="last_modified", nullable=False),
)

company_construction_price_indices = Table(
    "HITRAKIYH",
    metadata_obj,
    Column("KG_RAKIYHTPAR", Integer, key="id", primary_key=True),
    Column("KG_EHIND", Integer, ForeignKey("HIRAKIND.KG_EHIND"), key="max_price_index_id", nullable=False, index=True),
    Column(
        "KG_YTUNNUS",
        Integer,
        ForeignKey("HITYHTIO.id"),
        key="company_id",
        nullable=False,
        index=True,
    ),
    Column("D_LASKPVM", Date, key="calculation_date", nullable=False),
    Column("C_VALMPVM", HitasYearMonth, key="completion_date", nullable=False),
    Column("C_YHTPAR", String(100), key="name", nullable=False),
    Column("N_HARVO", Integer, key="value", nullable=False),
    Column("N_HYVARVO", Float, nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

apartment_construction_price_indices = Table(
    "HITRAKIHU",
    metadata_obj,
    Column("KG_RAKHUOPAR", Integer, key="id", primary_key=True),
    Column("KG_EHIND", Integer, ForeignKey("HIRAKIND.KG_EHIND"), key="max_price_index_id", nullable=False, index=True),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False, index=True),
    Column("D_LASKPVM", Date, key="calculation_date", nullable=False),
    Column("N_RAKILASKPVM", Float, key="index_on_calculation_date", nullable=False),
    Column("C_VALMPVM", HitasYearMonth, key="completion_date", nullable=False),
    Column("N_RAKIVALMPVM", Float, key="index_on_completion_date", nullable=False),
    Column("C_POISTOKOODI", String(16), nullable=False),  # Always 'HITRAKHUONE'
    Column(
        "C_POISTOPROS", String(12), key="depreciation_percentage", nullable=False
    ),  # Always '000', '001', '002' == 0%, 2.5%, 10%
    Column("C_POISTOAIKA", HitasDuration, key="depreciation_period", nullable=False),
    Column("C_HUOPAR", String(100), key="name", nullable=False),
    Column("N_HARVO", Integer, key="value", nullable=False),
    Column("N_RAKIARVO", Float, nullable=False),  # Indeksin tarkistus arvo
    Column("N_POISTOARVO", Float, nullable=False),  # Poisto
    Column("N_HYVARVO", Float, key="accepted_value", nullable=False),  # Hyväksytty arvo
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

#
# market price index 'markkinahintaindeksi' calculations (confirmed or unconfirmed)
#

market_price_indices = Table(
    "HITMHIND",
    metadata_obj,
    Column("KG_EHIND", Integer, key="id", primary_key=True, index=True),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False, index=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False, index=True),
    Column("C_DIANRO", String(10)),
    Column("C_OMNIMI1", HitasAnonymizedName(50)),
    Column("C_OMNIMI2", HitasAnonymizedName(50)),
    Column("C_OSOITE", String(70), nullable=False),
    Column("C_POSKOODI", String(16), nullable=False),  # Always 'POSTINROT'
    Column("C_POSTINRO", String(12), nullable=False),
    Column("C_PTP", String(30), nullable=False),
    Column("D_VALMPVM", Date, key="completion_date"),
    Column("N_EHINDVPVM", Float, nullable=False),
    Column("D_EHLASKPVM", Date, key="calculation_date", nullable=False),
    Column("N_EHINDLPVM", Float, nullable=False),
    Column("N_HANKARVO", Integer, nullable=False),
    Column("N_KORKOPROS", Float, nullable=False),
    Column("N_RAKKORKO", Integer, nullable=False),
    Column("N_PERHINTA", Integer, nullable=False),
    Column("N_INDNOUSU", Integer, nullable=False),
    Column("N_HUONPAR", Integer, nullable=False),
    Column("N_YHTPAR", Integer, nullable=False),
    Column("N_VELHINTA", Integer, nullable=False),
    Column("N_YHTLAINA", Integer, nullable=False),
    Column("N_HUOVAH", Integer, nullable=False),
    Column("N_EHINTA", Integer, key="max_price", nullable=False),
    Column("N_EHINTAM2", Integer, nullable=False),
    Column("C_LASKAAVA", String(50)),
    Column("C_LISATIETO1", HitasBoolean, nullable=False),
    Column("C_LISATVIITE1", String(10), nullable=False),  # Always 'HITMHIND'
    Column("C_LISATIETO2", HitasBoolean, nullable=False),
    Column("C_LISATVIITE2", String(10), nullable=False),  # Always 'HITMHIHU'
    Column("C_LISATIETO3", HitasBoolean, nullable=False),
    Column("C_LISATVIITE3", String(10), nullable=False),  # Always 'HITMHIYH'
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, key="last_modified", nullable=False),
    Column("D_VIIMVALMPVM", Date, nullable=False),
    Column("N_RAKINDVPVM", Float, nullable=False),
    Column("N_RAKINDLPVM", Float, nullable=False),
)

company_market_price_indices = Table(
    "HITMHIYH",
    metadata_obj,
    Column("KG_MHYHTPAR", Integer, key="id", primary_key=True),
    Column("KG_EHIND", Integer, ForeignKey("HITMHIND.id"), key="max_price_index_id", nullable=False, index=True),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False, index=True),
    Column("D_LASKPVM", Date, key="calculation_date", nullable=False),
    Column("C_VALMPVM", HitasYearMonth, key="completion_date", nullable=False),
    Column("C_POISTOKOODI", String(16), nullable=False),  # Always 'HITMHRAJAT' or 'HLIJAKOPER'
    Column("C_POISTOVUODET", String(12), nullable=False),  # Always '000', '001', '002', '003', '010'
    Column("C_OMAVASTUU", String(12), nullable=False),  # Always 'K', 'E', '005', '011'
    Column("C_POISTOAIKA", HitasDuration, key="depreciation_period", nullable=False),
    Column("C_YHTPAR", String(100), key="name", nullable=False),
    Column("N_HARVO", Integer, key="value", nullable=False),
    Column("N_ARVOLISAYS", Float, nullable=False),
    Column("N_POISTOARVO", Float, nullable=False),
    Column("N_HYVARVO", Float, nullable=False),
    Column("N_HUONOSUUS", Float, nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

apartment_market_price_indices = Table(
    "HITMHIHU",
    metadata_obj,
    Column("KG_MHHUOPAR", Integer, key="id", primary_key=True),
    Column("KG_EHIND", Integer, ForeignKey("HITMHIND.id"), key="max_price_index_id", nullable=False, index=True),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False, index=True),
    Column("D_LASKPVM", Date, key="calculation_date", nullable=False),
    Column("C_VALMPVM", HitasYearMonth, key="completion_date", nullable=False),
    Column("C_POISTOKOODI", String(16), nullable=False),  # Always 'HITMHRAJAT'
    Column("C_POISTOVUODET", String(12), nullable=False),  # Always '000' or '002'
    Column("C_OMAVASTUU", String(12), key="excess", nullable=False),  # Always '000' or '004'.
    Column("C_POISTOAIKA", HitasDuration, key="depreciation_period", nullable=False),
    Column("C_HUOPAR", String(100), key="name", nullable=False),
    Column("N_HARVO", Integer, key="value", nullable=False),
    Column("N_ARVOLISAYS", Float, nullable=False),  # Arvon lisäys
    Column("N_POISTOARVO", Float, nullable=False),  # Poisto
    Column("N_HYVARVO", Float, key="accepted_value", nullable=False),  # Hyväksytty arvo
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
)

# Table contains confirmed maximum price calculations.
# When calculations are made, only the highest value calculation is transferred here.
hitas_monitoring = Table(
    "HITVALVO",
    metadata_obj,
    Column("KG_VTUNNUS", Integer, key="id", primary_key=True, nullable=False),
    Column("KG_HTUNNUS", Integer, ForeignKey("HITHUONE.id"), key="apartment_id", nullable=False),
    Column("KG_YTUNNUS", Integer, ForeignKey("HITYHTIO.id"), key="company_id", nullable=False),
    Column(
        "C_LASKNIMI", String(15), key="max_price_index_name", nullable=False
    ),  # The type of calculation this is. Always one of [EI LASKELMAA, RAKINDEKSI, RAJAHINTA, HITINDEKSI, MHINDEKSI]
    Column("D_LASKPVM", Date, key="calculation_date"),
    Column("KG_EHIND", Integer, key="max_price_index_id", nullable=False),  # Actually FK to max price calculation table
    Column("D_ILMPVM", Date, key="notification_date", nullable=False),
    Column("C_MYYJA", String(250), nullable=False),
    Column("N_EHINTA", Integer, key="maximum_price", nullable=False),
    Column("N_KAUPHINTA", Integer, key="purchase_price", nullable=False),
    Column("D_KAUPPVM", Date, key="purchase_date"),
    Column("C_OSTAJA1", HitasAnonymizedName(50), key="buyer_name_1", nullable=False),
    Column("C_OSTAJA2", HitasAnonymizedName(50), key="buyer_name_2"),
    Column("C_SOTU1", HitasAnonymizedSSN(11), key="buyer_identifier_1"),
    Column("C_SOTU2", HitasAnonymizedSSN(11), key="buyer_identifier_2"),
    Column("N_VEHINTA", Integer, nullable=False),
    Column("N_YHTLAINA", Integer, key="apartment_share_of_housing_company_loans", nullable=False),
    Column("N_EHINTAM2", Integer, nullable=False),
    Column("C_VALVKOODI", String(16), nullable=False),
    Column("C_VALVTILA", String(12), key="monitoring_state", nullable=False),
    Column("C_LISATIETO", String(1), nullable=False),
    Column("C_LISATVIITE", String(10), nullable=False),
    Column("C_MUUTTAJA", String(10), nullable=False),
    Column("D_MUUTETTU", Date, nullable=False),
    Column("C_SIIRRETTY", String(20)),
)
