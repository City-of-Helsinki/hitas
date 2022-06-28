import pytest

from hitas.tests.runner import HitasTestContainer

# Container is stopped with destructor so keep a global copy
_htc = None


@pytest.fixture(scope="session")
def django_db_modify_db_settings(
    django_db_modify_db_settings_parallel_suffix: None,
) -> None:
    global _htc
    _htc = HitasTestContainer()
    _htc.start()
