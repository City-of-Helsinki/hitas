import pytest

from hitas.tests import factories


@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory_class",
    [
        factories.HousingCompanyFactory,
        factories.PropertyManagerFactory,
        factories.UserFactory,
        factories.PostalCodeFactory,
        factories.BuildingTypeFactory,
        factories.FinancingMethodFactory,
        factories.DeveloperFactory,
    ],
)
def test__factory__simple_create(factory_class):
    factory_class.create()
    assert factory_class._meta.model.objects.count() == 1
