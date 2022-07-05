import os

import pytest

from hitas.tests.runner import HitasTestContainer
from rest_framework.test import APIClient

# Container is stopped with destructor so keep a global copy
_htc = None


@pytest.fixture(scope="session")
def django_db_modify_db_settings(
    django_db_modify_db_settings_parallel_suffix: None,
) -> None:
    if os.getenv("HITAS_TESTS_NO_DOCKER") is not None:
        return

    global _htc
    _htc = HitasTestContainer()
    _htc.start()


@pytest.fixture()
def api_client():
    api_client = APIClient()
    return api_client
