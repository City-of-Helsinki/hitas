from collections import defaultdict
from typing import List

_hitas_cost_areas = defaultdict(lambda: 4)


def init_cost_areas() -> None:
    def init_cost_areas(index: int, postal_codes: List[str]) -> None:
        for postal_code in postal_codes:
            _hitas_cost_areas[postal_code] = index

    init_cost_areas(1, ["00100", "00120", "00130", "00140", "00150", "00160", "00170", "00180", "00220", "00260"])
    init_cost_areas(
        2,
        [
            "00200",
            "00210",
            "00250",
            "00270",
            "00280",
            "00290",
            "00300",
            "00310",
            "00320",
            "00330",
            "00340",
            "00380",
            "00500",
            "00510",
            "00520",
            "00530",
            "00540",
            "00550",
            "00560",
            "00570",
            "00580",
            "00590",
            "00610",
            "00810",
            "00850",
            "00990",
        ],
    )
    init_cost_areas(
        3,
        [
            "00240",
            "00350",
            "00360",
            "00370",
            "00400",
            "00430",
            "00440",
            "00620",
            "00650",
            "00660",
            "00670",
            "00680",
            "00690",
            "00730",
            "00780",
            "00790",
            "00800",
            "00830",
            "00840",
            "00950",
        ],
    )


def hitas_cost_area(postal_code: str) -> int:
    return _hitas_cost_areas[postal_code]
