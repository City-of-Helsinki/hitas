import pytest

from hitas.tests import factories


@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory_class",
    [
        factories.ApartmentFactory,
        factories.ApartmentTypeFactory,
        factories.BuildingFactory,
        factories.BuildingTypeFactory,
        factories.DeveloperFactory,
        factories.FinancingMethodFactory,
        factories.HousingCompanyFactory,
        factories.OwnerFactory,
        factories.PersonFactory,
        factories.PostalCodeFactory,
        factories.PropertyManagerFactory,
        factories.RealEstateFactory,
        factories.UserFactory,
    ],
)
def test__factory__simple_create(factory_class):
    factory_class.create()
    assert factory_class._meta.model.objects.count() == 1
