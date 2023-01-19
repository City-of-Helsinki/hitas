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
        factories.ApartmentSaleFactory,
    ],
)
def test__factory__simple_create(factory_class):
    factory_class.create()
    assert factory_class._meta.model.objects.count() == 1


@pytest.mark.django_db
def test__factory__condition_of_sale_factory():
    owner = factories.OwnerFactory.create()
    ownership_1 = factories.OwnershipFactory.create(owner=owner)
    ownership_2 = factories.OwnershipFactory.create(owner=owner)
    factories.ConditionOfSaleFactory.create(new_ownership=ownership_1, old_ownership=ownership_2)
    assert factories.ConditionOfSaleFactory._meta.model.objects.count() == 1
