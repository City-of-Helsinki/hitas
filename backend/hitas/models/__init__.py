from hitas.models.apartment import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
    DepreciationPercentage,
)
from hitas.models.apartment_sale import ApartmentSale
from hitas.models.building import Building
from hitas.models.codes import AbstractCode, ApartmentType, BuildingType, Developer
from hitas.models.condition_of_sale import ConditionOfSale
from hitas.models.document import AparmentDocument, HousingCompanyDocument
from hitas.models.email_template import EmailTemplate
from hitas.models.external_sales_data import ExternalSalesData
from hitas.models.housing_company import (
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
)
from hitas.models.indices import (
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    MaximumPriceIndex,
    SurfaceAreaPriceCeiling,
    SurfaceAreaPriceCeilingCalculationData,
)
from hitas.models.job_performance import JobPerformance
from hitas.models.migration_done import MigrationDone
from hitas.models.owner import NonObfuscatedOwner, Owner
from hitas.models.ownership import Ownership
from hitas.models.pdf_body import PDFBody
from hitas.models.postal_code import HitasPostalCode
from hitas.models.property_manager import PropertyManager
from hitas.models.real_estate import RealEstate
from hitas.models.thirty_year_regulation import ThirtyYearRegulationResults, ThirtyYearRegulationResultsRow
