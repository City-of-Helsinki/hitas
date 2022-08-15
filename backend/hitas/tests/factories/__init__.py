import factory

from hitas.tests.factories.codes import (
    ApartmentTypeFactory,
    BuildingTypeFactory,
    DeveloperFactory,
    FinancingMethodFactory,
    PostalCodeFactory,
)
from hitas.tests.factories.housing_company import (
    ApartmentFactory,
    BuildingFactory,
    HousingCompanyFactory,
    RealEstateFactory,
)
from hitas.tests.factories.person import OwnerFactory, PersonFactory
from hitas.tests.factories.property_manager import PropertyManagerFactory
from hitas.tests.factories.user import UserFactory

# Force faker to always use finnish locale - otherwise we would either
# need to pass the locale on each attribute or use contextlibs
factory.Faker._DEFAULT_LOCALE = "fi_FI"
