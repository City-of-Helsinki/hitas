import openapi_core
import yaml
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.validation.response.validators import ResponseValidator
from rest_framework.response import Response

from hitas.models.housing_company import Building, HousingCompany, RealEstate


def validate_openapi(response: Response) -> None:
    with open("openapi.yaml", "r") as spec_file:
        openapi = yaml.safe_load(spec_file)

    result = ResponseValidator(openapi_core.create_spec(openapi)).validate(
        DjangoOpenAPIRequest(response.wsgi_request),
        DjangoOpenAPIResponse(response),
    )

    result.raise_for_errors()


def create_test_housing_company(idx: int) -> HousingCompany:
    return HousingCompany.objects.create(
        display_name=f"test-housing-company-{idx}",
        official_name=f"test-housing-company-{idx}-as-oy",
        street_address=f"test-street-address-{idx}",
        business_id="1234567-8",
        acquisition_price=10.0,
        primary_loan=10.0,
        building_type_id=1,
        developer_id=1,
        financing_method_id=1,
        postal_code_id=1,
        property_manager_id=1,
    )


def create_test_real_estate(hc: HousingCompany, idx: int) -> RealEstate:
    return RealEstate.objects.create(
        housing_company=hc,
        postal_code_id=1,
        property_identifier="091-020-0015-0003",
        street_address=f"test-re-street-address-{idx}",
    )


def create_test_building(re: RealEstate, idx: int, completion_date=None) -> Building:
    return Building.objects.create(
        housing_company=re.housing_company,
        real_estate=re,
        postal_code_id=1,
        street_address=f"test-b-street-address-{idx}",
        completion_date=completion_date,
    )
