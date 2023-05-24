import factory

from hitas.tests.factories.apartment import (
    ApartmentConstructionPriceImprovementFactory,
    ApartmentFactory,
    ApartmentMarketPriceImprovementFactory,
)
from hitas.tests.factories.apartment_sale import ApartmentSaleFactory
from hitas.tests.factories.codes import (
    ApartmentTypeFactory,
    BuildingTypeFactory,
    DeveloperFactory,
)
from hitas.tests.factories.condition_of_sale import ConditionOfSaleFactory
from hitas.tests.factories.housing_company import (
    BuildingFactory,
    HousingCompanyConstructionPriceImprovementFactory,
    HousingCompanyFactory,
    HousingCompanyMarketPriceImprovementFactory,
    RealEstateFactory,
)
from hitas.tests.factories.owner import OwnerFactory, OwnershipFactory
from hitas.tests.factories.postal_code import HitasPostalCodeFactory
from hitas.tests.factories.property_manager import PropertyManagerFactory
from hitas.tests.factories.user import UserFactory

# Force faker to always use finnish locale - otherwise we would either
# need to pass the locale on each attribute or use contextlibs
factory.Faker._DEFAULT_LOCALE = "fi_FI"
