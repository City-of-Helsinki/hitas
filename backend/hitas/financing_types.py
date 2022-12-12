from hitas.models import FinancingMethod

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


def is_before_2011(financing_method: FinancingMethod):
    return not is_2011_onwards(financing_method)


def is_2011_onwards(financing_method: FinancingMethod):
    return financing_method.value in [
        "Tuntematon",
        "Uusi Hitas I (vapaarahoitteinen)",
        "Uusi Hitas II (vapaarahoitteinen)",
    ]


def include_in_statistics(financing_method: FinancingMethod):
    return not financing_method.value.endswith("Ei Hitas") and not financing_method.value.startswith("Vuokratalo")


def is_half_hitas(financing_method: FinancingMethod):
    return financing_method.value.startswith("PUOLIHITAS")
