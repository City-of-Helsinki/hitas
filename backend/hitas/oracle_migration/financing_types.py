import re

from hitas.models.housing_company import HitasType


def strip_financing_method_id(name: str) -> str:
    # If the name is in format '<Name> (<ID>)', strip the ID part out of the name
    # Example: 'Vapaarahoitteinen, Ei Hitas (100)'
    name_contains_id = re.match(r"(.*) \(\d{3}\)$", name)
    if name_contains_id:
        name = name_contains_id.group(1).strip()
    return name


# fmt: off
FINANCING_METHOD_TO_HITAS_TYPE_MAP: dict[str, HitasType] = {
    "tuntematon":                                       HitasType.HITAS_I,
    "vapaarahoitteinen, Ei Hitas":                      HitasType.NON_HITAS,
    "vapaarahoitteinen, Hitas I":                       HitasType.HITAS_I,
    "vapaarahoitteinen, Hitas II":                      HitasType.HITAS_II,
    "HK valtion laina, Ei Hitas":                       HitasType.NON_HITAS,
    "HK valtion laina, Hitas I":                        HitasType.HITAS_I,
    "HK valtion laina, Hitas II":                       HitasType.HITAS_II,
    "RA valtion laina, Ei Hitas":                       HitasType.NON_HITAS,
    "RA valtion laina, Hitas I":                        HitasType.HITAS_I,
    "RA valtion laina, Hitas II":                       HitasType.HITAS_II,
    "Korkotuki, Hitas I":                               HitasType.HITAS_I,
    "Korkotuki, Hitas II":                              HitasType.HITAS_II,
    "Lyhyt korkotukilaina, ns. osaomistus Hitas I":     HitasType.HITAS_I_NO_INTEREST,
    "Pitkä korkotukilaina osaomistus Hitas I":          HitasType.HITAS_I_NO_INTEREST,
    "Omaksi lunastettava vuokra-asunto, Hitas I":       HitasType.HITAS_I_NO_INTEREST,
    "Uusi Hitas I (vanhat säännöt)":                    HitasType.HITAS_I,
    "Uusi Hitas I (vapaarahoitteinen)":                 HitasType.NEW_HITAS_I,
    "Uusi Hitas II (vanhat säännöt)":                   HitasType.HITAS_II,
    "Uusi Hitas II (vapaarahoitteinen)":                HitasType.NEW_HITAS_II,
    "PUOLIHITAS (OOHK)":                                HitasType.HALF_HITAS,
    "Vuokratalo Hitas I":                               HitasType.RENTAL_HITAS_I,
    "Vuokratalo Hitas II":                              HitasType.RENTAL_HITAS_II,
}
# fmt: on
