from hitas.views.apartment import ApartmentViewSet
from hitas.views.apartment_list import ApartmentListViewSet
from hitas.views.building import BuildingViewSet
from hitas.views.codes import ApartmentTypeViewSet, BuildingTypeViewSet, DeveloperViewSet, FinancingMethodViewSet
from hitas.views.housing_company import HousingCompanyViewSet
from hitas.views.indices import (
    ConstructionPriceIndexPre2005ViewSet,
    ConstructionPriceIndexViewSet,
    MarketPriceIndexPre2005ViewSet,
    MarketPriceIndexViewSet,
    MaxPriceIndexViewSet,
)
from hitas.views.owner import OwnerViewSet
from hitas.views.postal_code import HitasPostalCodeViewSet
from hitas.views.property_manager import PropertyManagerViewSet
from hitas.views.real_estate import RealEstateViewSet
