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


def financing_method_is_before_2011(financing_method: str):
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
