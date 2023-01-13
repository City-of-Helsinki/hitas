from functools import cache
from pathlib import Path

import tomli


@cache
def get_current_version() -> str:
    base_dir = Path(__file__).parent.parent
    with open(base_dir / "pyproject.toml", mode="rb") as f:
        data = tomli.load(f)

    return data["tool"]["poetry"]["version"]
