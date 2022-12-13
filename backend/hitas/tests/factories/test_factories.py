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
        factories.OldHitasFinancingMethodFactory,
        factories.HousingCompanyFactory,
        factories.OwnershipFactory,
        factories.OwnerFactory,
        factories.HitasPostalCodeFactory,
        factories.PropertyManagerFactory,
        factories.RealEstateFactory,
        factories.UserFactory,
    ],
)
def test__factory__simple_create(factory_class):
    factory_class.create()
    assert factory_class._meta.model.objects.count() == 1
