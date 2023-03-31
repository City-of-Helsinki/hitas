import re

from hitas.models import FinancingMethod
from hitas.models.housing_company import HitasType

# +----------------------------------------------+--------------+----------------------+------------+
# | Name                                         | 2011 onwards | Skip from statistics | Half-Hitas |
# +----------------------------------------------+--------------+----------------------+------------+
# | Tuntematon                                   | ?            |                      |            |
# | Vapaarahoitteinen, Ei Hitas                  |              | x                    |            |
# | Vapaarahoitteinen, Hitas I                   |              |                      |            |
# | Vapaarahoitteinen, Hitas II                  |              |                      |            |
# | HK valtion laina, Ei Hitas                   |              | x                    |            |
# | HK valtion laina, Hitas I                    |              |                      |            |
# | HK valtion laina, Hitas II                   |              |                      |            |
# | RA valtion laina, Ei Hitas                   |              | x                    |            |
# | RA valtion laina, Hitas I                    |              |                      |            |
# | RA valtion laina, Hitas II                   |              |                      |            |
# | HK valtion laina, Ei Hitas                   |              | x                    |            |
# | HK valtion laina, Hitas I                    |              |                      |            |
# | HK valtion laina, Hitas II                   |              |                      |            |
# | RA valtion laina, Ei Hitas                   |              | x                    |            |
# | RA valtion laina, Hitas I                    |              |                      |            |
# | RA valtion laina, Hitas II                   |              |                      |            |
# | Korkotuki, Hitas I                           |              |                      |            |
# | Korkotuki, Hitas II                          |              |                      |            |
# | Lyhyt korkotukilaina, ns. osaomistus Hitas I |              |                      |            |
# | Pitkä korkotukilaina osaomistus Hitas I      |              |                      |            |
# | Omaksi lunastettava vuokra-asunto, Hitas I   |              |                      |            |
# | Uusi Hitas II (vanhat säännöt)               |              |                      |            |
# | Uusi Hitas II (vapaarahoitteinen)            | x            |                      |            |
# | Uusi Hitas I (vanhat säännöt)                |              |                      |            |
# | Uusi Hitas I (vapaarahoitteinen)             | x            |                      |            |
# | PUOLIHITAS (OOHK)                            |              | x                    | x          |
# | Vuokratalo Hitas I                           |              | x                    |            |
# | Vuokratalo Hitas II                          |              | x                    |            |
# +----------------------------------------------+--------------+----------------------+------------+


def financing_method_is_pre_2011(financing_method: str):
    return not financing_method_is_2011_onwards(financing_method)


def financing_method_is_2011_onwards(financing_method: str):
    return financing_method in [
        "Tuntematon",
        "Uusi Hitas I (vapaarahoitteinen)",
        "Uusi Hitas II (vapaarahoitteinen)",
    ]


def financing_method_include_in_statistics(financing_method: str):
    return not financing_method.endswith("Ei Hitas") and not financing_method.startswith("Vuokratalo")


def financing_method_is_half_hitas(financing_method: str):
    return financing_method.startswith("PUOLIHITAS")


def format_financing_method(fm: FinancingMethod) -> None:
    # Only capitalize those with first letter lowercased
    # Don't capitalize all - there's some that would suffer from it
    if fm.value[0].islower():
        fm.value = fm.value[0].upper() + fm.value[1:]

    fm.value = strip_financing_method_id(fm.value)

    fm.include_in_statistics = financing_method_include_in_statistics(fm.value)
    fm.half_hitas = financing_method_is_half_hitas(fm.value)
    fm.old_hitas_ruleset = financing_method_is_pre_2011(fm.value)


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
