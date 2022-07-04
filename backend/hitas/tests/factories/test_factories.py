import pytest

from hitas.tests import factories


@pytest.mark.django_db
def test_HousingCompanyFactory_create_simple():
    factories.HousingCompanyFactory.create()


@pytest.mark.django_db
def test_PropertyManagerFactory_create_simple():
    factories.PropertyManagerFactory.create()


@pytest.mark.django_db
def test_UserFactory_create_simple():
    factories.UserFactory.create()


@pytest.mark.django_db
def test_PostalCodeFactory_create_simple():
    factories.PostalCodeFactory.create()


@pytest.mark.django_db
def test_BuildingTypeFactory_create_simple():
    factories.BuildingTypeFactory.create()


@pytest.mark.django_db
def test_FinancingMethodFactory_create_simple():
    factories.FinancingMethodFactory.create()


@pytest.mark.django_db
def test_DeveloperFactory_create_simple():
    factories.DeveloperFactory.create()
