from hitas.views.apartment import ApartmentViewSet
from hitas.views.apartment_list import ApartmentListViewSet
from hitas.views.apartment_max_price import ApartmentMaximumPriceViewSet
from hitas.views.apartment_sale import ApartmentSaleViewSet
from hitas.views.building import BuildingViewSet
from hitas.views.codes import ApartmentTypeViewSet, BuildingTypeViewSet, DeveloperViewSet, FinancingMethodViewSet
from hitas.views.condition_of_sale import ConditionOfSaleViewSet
from hitas.views.housing_company import HousingCompanyViewSet
from hitas.views.indices import (
    ConstructionPriceIndex2005Equal100ViewSet,
    ConstructionPriceIndexViewSet,
    MarketPriceIndex2005Equal100ViewSet,
    MarketPriceIndexViewSet,
    MaximumPriceIndexViewSet,
    SurfaceAreaPriceCeilingViewSet,
)
from hitas.views.owner import OwnerViewSet
from hitas.views.postal_code import HitasPostalCodeViewSet
from hitas.views.property_manager import PropertyManagerViewSet
from hitas.views.real_estate import RealEstateViewSet
