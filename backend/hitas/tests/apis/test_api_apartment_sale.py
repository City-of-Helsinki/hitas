import datetime

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from hitas.models import Apartment, ApartmentSale, ConditionOfSale, Owner, Ownership
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.tests.apis.helpers import HitasAPIClient, InvalidInput, parametrize_helper
from hitas.tests.factories import (
    ApartmentFactory,
    ApartmentSaleFactory,
    ConditionOfSaleFactory,
    OwnerFactory,
    OwnershipFactory,
)
from hitas.views.apartment_sale import ApartmentSaleSerializer
from hitas.views.ownership import OwnershipSerializer

# List tests


@pytest.mark.django_db
def test__api__apartment_sale__list__empty(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create(sales=[])

    url = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []
    assert response.json()["page"] == {
        "size": 0,
        "current_page": 1,
        "total_items": 0,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


@pytest.mark.django_db
def test__api__apartment_sale__list(api_client: HitasAPIClient):
    ownership: Ownership = OwnershipFactory.create()

    url = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": ownership.sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": ownership.sale.apartment.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": ownership.sale.uuid.hex,
            "ownerships": [
                {
                    "owner": {
                        "id": ownership.owner.uuid.hex,
                        "name": ownership.owner.name,
                        "email": ownership.owner.email,
                        "identifier": ownership.owner.identifier,
                        "non_disclosure": ownership.owner.non_disclosure,
                    },
                    "percentage": float(ownership.percentage),
                }
            ],
            "notification_date": ownership.sale.notification_date.isoformat(),
            "purchase_date": ownership.sale.purchase_date.isoformat(),
            "purchase_price": float(ownership.sale.purchase_price),
            "apartment_share_of_housing_company_loans": float(ownership.sale.apartment_share_of_housing_company_loans),
            "exclude_from_statistics": ownership.sale.exclude_from_statistics,
        }
    ]
    assert response.json()["page"] == {
        "size": 1,
        "current_page": 1,
        "total_items": 1,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


@pytest.mark.django_db
def test__api__apartment_sale__list__dont_include_sales_for_other_apartments(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create(sales=[])

    # Sale for some other apartment
    ApartmentSaleFactory.create()

    url = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []
    assert response.json()["page"] == {
        "size": 0,
        "current_page": 1,
        "total_items": 0,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


# Retrieve tests


@pytest.mark.django_db
def test__api__apartment_sale__retrieve(api_client: HitasAPIClient):
    ownership: Ownership = OwnershipFactory.create()
    sale: ApartmentSale = ApartmentSaleFactory.create(ownerships=[ownership])

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
            "uuid": sale.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": sale.uuid.hex,
        "ownerships": [
            {
                "owner": {
                    "id": ownership.owner.uuid.hex,
                    "name": ownership.owner.name,
                    "email": ownership.owner.email,
                    "identifier": ownership.owner.identifier,
                    "non_disclosure": ownership.owner.non_disclosure,
                },
                "percentage": float(ownership.percentage),
            },
        ],
        "notification_date": sale.notification_date.isoformat(),
        "purchase_date": sale.purchase_date.isoformat(),
        "purchase_price": float(sale.purchase_price),
        "apartment_share_of_housing_company_loans": float(sale.apartment_share_of_housing_company_loans),
        "exclude_from_statistics": sale.exclude_from_statistics,
    }


# Create tests


@pytest.mark.django_db
def test__api__apartment_sale__create(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales=[],
    )
    owner: Owner = OwnerFactory.create()

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data

    assert response_data.pop("conditions_of_sale_created", None) is False

    sales: list[ApartmentSale] = list(ApartmentSale.objects.all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_data["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 1

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
            "uuid": response_data["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_data


@pytest.mark.django_db
def test__api__apartment_sale__create__multiple_owners(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales=[],
    )
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner_1.uuid.hex,
                },
                "percentage": 40.0,
            },
            {
                "owner": {
                    "id": owner_2.uuid.hex,
                },
                "percentage": 60.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data

    assert response_data.pop("conditions_of_sale_created", None) is False

    sales: list[ApartmentSale] = list(ApartmentSale.objects.all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_data["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 2

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
            "uuid": response_data["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_data


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Empty Ownerships": InvalidInput(
                invalid_data={"ownerships": []},
                fields=[
                    {
                        "field": "ownerships",
                        "message": "Sale must have ownerships.",
                    }
                ],
            ),
            "Ownership percentage under 100": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": {
                                "id": ...,
                            },
                            "percentage": 50.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.percentage",
                        "message": (
                            "Ownership percentage of all ownerships combined must be equal to 100. Given sum was 50.00."
                        ),
                    },
                ],
            ),
            "Ownership percentage over 100": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": {
                                "id": ...,
                            },
                            "percentage": 150.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.percentage",
                        "message": (
                            "Ownership percentage must be greater than 0 and less than or equal to 100. "
                            "Given value was 150.00."
                        ),
                    },
                ],
            ),
            "Multiple ownerships for the same owner": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": {
                                "id": ...,
                            },
                            "percentage": 50.0,
                        },
                        {
                            "owner": {
                                "id": ...,
                            },
                            "percentage": 50.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships",
                        "message": "All ownerships must be for different owners.",
                    },
                ],
            ),
            "'Notification date' can't be null": InvalidInput(
                invalid_data={"notification_date": None},
                fields=[
                    {
                        "field": "notification_date",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Purchase date' can't be null": InvalidInput(
                invalid_data={"purchase_date": None},
                fields=[
                    {
                        "field": "purchase_date",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Purchase price' can't be null": InvalidInput(
                invalid_data={"purchase_price": None},
                fields=[
                    {
                        "field": "purchase_price",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Apartment share of housing company loans' can't be null": InvalidInput(
                invalid_data={"apartment_share_of_housing_company_loans": None},
                fields=[
                    {
                        "field": "apartment_share_of_housing_company_loans",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Exclude in statistics' can't be null": InvalidInput(
                invalid_data={"exclude_from_statistics": None},
                fields=[
                    {
                        "field": "exclude_from_statistics",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "Owner is a string": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": "foo",
                            "percentage": 100.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.owner",
                        "message": "Invalid data. Expected a dictionary, but got str.",
                    },
                ],
            ),
            "Owner is empty": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": {},
                            "percentage": 100.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.owner.id",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Owner is None": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": None,
                            "percentage": 100.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.owner",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Owner ID is None": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": {
                                "id": None,
                            },
                            "percentage": 100.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.owner.id",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Owner ID is the empty string": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": {
                                "id": "",
                            },
                            "percentage": 100.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.owner.id",
                        "message": "This field is mandatory and cannot be blank.",
                    },
                ],
            ),
            "Owner ID is not an ID for an Owner": InvalidInput(
                invalid_data={
                    "ownerships": [
                        {
                            "owner": {
                                "id": "foo",
                            },
                            "percentage": 100.0,
                        },
                    ],
                },
                fields=[
                    {
                        "field": "ownerships.owner.id",
                        "message": "Object does not exist with given id 'foo'.",
                    },
                ],
            ),
        }
    ),
)
@pytest.mark.django_db
def test__api__apartment_sale__create__invalid_data(api_client: HitasAPIClient, invalid_data: dict, fields: list):
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    owner: Owner = OwnerFactory.create()

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }
    data.update(invalid_data)

    # Set back Owner ID if set to ... on parametrize
    ownerships = data.get("ownerships", [{}])
    for index, ownership in enumerate(ownerships):
        owner_ = ownership.get("owner", {})
        if isinstance(owner_, dict):
            owner_id = owner_.get("id", None)
            if owner_id is ...:
                data["ownerships"][index]["owner"]["id"] = owner.uuid.hex

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.post(url_1, data=data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__apartment_sale__create__replace_old_ownerships(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        completion_date=datetime.date(2022, 1, 1),
        sales=[],
    )
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    owner_3: Owner = OwnerFactory.create()
    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=datetime.date(2022, 1, 1),
        ownerships=[],
    )
    OwnershipFactory.create(sale=sale, owner=owner_1, percentage=60.0)
    OwnershipFactory.create(sale=sale, owner=owner_2, percentage=40.0)

    apartment_sales_pre = list(apartment.sales.all())
    apartment_ownerships_pre = list(sale.ownerships.all())
    assert len(apartment_sales_pre) == 1
    assert len(apartment_ownerships_pre) == 2
    assert apartment_ownerships_pre[0].owner.uuid.hex == owner_1.uuid.hex
    assert apartment_ownerships_pre[1].owner.uuid.hex == owner_2.uuid.hex

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner_3.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-02-01",
        "purchase_date": "2023-02-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    apartment.refresh_from_db()
    apartment_sales_post = list(apartment.sales.all())
    apartment_ownerships_post = list(apartment.latest_sale().ownerships.all())
    assert len(apartment_sales_post) == 2
    assert len(apartment_ownerships_post) == 1
    assert apartment_ownerships_post[0].owner.uuid.hex == owner_3.uuid.hex


@pytest.mark.django_db
def test__api__apartment_sale__create__condition_of_sale_fulfilled(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        owner=owner_1,
        sale__purchase_date=datetime.date(2023, 1, 1),
    )
    old_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        owner=owner_1,
        sale__purchase_date=datetime.date(2022, 1, 1),
    )
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
    )

    ownerships_pre = list(owner_1.ownerships.all())
    assert len(ownerships_pre) == 2
    assert condition_of_sale.fulfilled is None

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner_2.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-02-01",
        "purchase_date": "2023-02-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": old_ownership.apartment.housing_company.uuid.hex,
            "apartment_uuid": old_ownership.apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    # Old ownership released, new one is maintained
    owner_1.refresh_from_db()
    ownerships_post = list(owner_1.ownerships.all())
    assert len(ownerships_post) == 1
    assert ownerships_post[0].id == new_ownership.id

    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None


@pytest.mark.django_db
def test__api__apartment_sale__create__new_apartment__create_condition_of_sale(api_client: HitasAPIClient):
    old_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        completion_date=None,
        sales=[],
    )

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": old_ownership.owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data

    assert response_data.pop("conditions_of_sale_created", None) is True

    sales: list[ApartmentSale] = list(ApartmentSale.objects.filter(apartment=new_apartment).all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_data["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 2

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].new_ownership.apartment == new_apartment
    assert conditions_of_sale[0].old_ownership.apartment == old_ownership.apartment

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
            "uuid": response_data["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_data


@pytest.mark.django_db
def test__api__apartment_sale__create__new_apartment__condition_of_sale_not_created(api_client: HitasAPIClient):
    # Condition of sale is not created, since the apartment
    # the owner has had previously has been released from regulation
    old_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
    )
    new_apartment: Apartment = ApartmentFactory.create(
        completion_date=None,
        sales=[],
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": old_ownership.owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data

    assert response_data.pop("conditions_of_sale_created", None) is False
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__apartment_sale__create__new_apartment__no_other_apartments(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        completion_date=None,
        sales=[],
    )

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data

    assert response_data.pop("conditions_of_sale_created", None) is False

    sales: list[ApartmentSale] = list(ApartmentSale.objects.all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_data["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 1

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0  # No conditions of sale created

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
            "uuid": response_data["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_data


@pytest.mark.django_db
def test__api__apartment_sale__create__multiple_owners__new_apartment(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()

    # One owner has an old apartment
    old_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        owner=owner_1,
    )
    new_apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        completion_date=None,
        sales=[],
    )

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner_1.uuid.hex,
                },
                "percentage": 40.0,
            },
            {
                "owner": {
                    "id": owner_2.uuid.hex,
                },
                "percentage": 60.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data

    assert response_data.pop("conditions_of_sale_created", None) is True

    sales: list[ApartmentSale] = list(ApartmentSale.objects.filter(apartment=new_apartment).all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_data["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 3

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].new_ownership.apartment == new_apartment
    assert conditions_of_sale[0].old_ownership.apartment == old_ownership.apartment

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
            "uuid": response_data["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_data


@pytest.mark.django_db
def test__api__apartment_sale__create__new_apartment__is_new_before_cos_fulfilled(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    owner: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        completion_date=datetime.date(2022, 1, 1),
        sales__purchase_date=datetime.date(2022, 1, 1),
        sales__ownerships__owner=owner,
    )
    new_apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        completion_date=datetime.date(2022, 1, 1),
        sales=[],
    )

    assert old_apartment.is_new is False
    assert new_apartment.is_new is True

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data

    assert response_data.pop("conditions_of_sale_created", None) is True

    sales: list[ApartmentSale] = list(ApartmentSale.objects.filter(apartment=new_apartment).all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_data["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 2

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].new_ownership.apartment == new_apartment
    assert conditions_of_sale[0].old_ownership.apartment == old_apartment

    # Apartment is new after the first sale until the condition of sale created with it is fulfilled
    assert Apartment.objects.get(id=new_apartment.id).is_new is True
    conditions_of_sale[0].delete()
    assert Apartment.objects.get(id=new_apartment.id).is_new is False

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
            "uuid": response_data["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_data


@pytest.mark.django_db
def test__api__apartment_sale__create__second_sale_sets_last_latest_purchase_date(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales=[],
    )

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
        },
    )

    # First sale sets 'first_purchase_date'
    response_1 = api_client.post(url_1, data=data, format="json")
    response_data_1 = response_1.json()

    assert response_1.status_code == status.HTTP_201_CREATED, response_data_1

    assert response_data_1.pop("conditions_of_sale_created", None) is False

    sales: list[ApartmentSale] = list(ApartmentSale.objects.filter(apartment=new_apartment).all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_data_1["id"]

    new_apartment = Apartment.objects.get(id=new_apartment.id)
    assert new_apartment.first_purchase_date is not None
    assert new_apartment.latest_purchase_date is None

    data["purchase_date"] = "2023-02-01"

    # Second sale sets 'latest_purchase_date'
    response_2 = api_client.post(url_1, data=data, format="json")
    response_data_2 = response_2.json()

    assert response_2.status_code == status.HTTP_201_CREATED, response_data_2

    assert response_data_2.pop("conditions_of_sale_created", None) is False

    sales: list[ApartmentSale] = list(ApartmentSale.objects.all())
    assert len(sales) == 2
    assert sales[0].uuid.hex == response_data_2["id"]
    assert sales[1].uuid.hex == response_data_1["id"]

    new_apartment = Apartment.objects.get(id=new_apartment.id)
    assert new_apartment.first_purchase_date is not None
    assert new_apartment.latest_purchase_date is not None


@pytest.mark.django_db
def test__api__apartment_sale__create__second_sale_older_than_first(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales=[],
    )
    owner: Owner = OwnerFactory.create()

    # Latest sale, which is later than the sale we are about to create
    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=datetime.date(2023, 2, 1),
    )

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()

    # There are now two sales
    sales: list[ApartmentSale] = list(ApartmentSale.objects.all())
    assert len(sales) == 2

    # Old sale is still the only one with active ownerships
    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 1
    assert ownerships[0].sale == sale


@pytest.mark.django_db
def test__api__apartment_sale__create__cannot_sell_unregulated_apartment(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales=[],
    )
    owner: Owner = OwnerFactory.create()

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.post(url_1, data=data, format="json")
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "invalid",
        "message": "Cannot sell an unregulated apartment.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_sale__create__half_hitas__last_apartment_sold(api_client: HitasAPIClient):
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
        sales=[],
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=apartment_1.housing_company,
        sales=[],
    )

    owner: Owner = OwnerFactory.create()

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    # First apartment is sold
    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment_1.housing_company.uuid.hex,
            "apartment_uuid": apartment_1.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")

    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    # Apartment housing company is still regulated
    apartment_1.housing_company.refresh_from_db()
    assert apartment_1.housing_company.regulation_status == RegulationStatus.REGULATED

    # First apartment is sold
    url_2 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment_2.housing_company.uuid.hex,
            "apartment_uuid": apartment_2.uuid.hex,
        },
    )
    response_2 = api_client.post(url_2, data=data, format="json")

    assert response_2.status_code == status.HTTP_201_CREATED, response_2.json()

    # Apartment housing company is now released from regulation
    apartment_1.housing_company.refresh_from_db()
    assert apartment_1.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS


@pytest.mark.django_db
def test__api__apartment_sale__create__half_hitas__dont_create_condition_of_sale(api_client: HitasAPIClient):
    old_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
        completion_date=None,
        sales=[],
    )

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": old_ownership.owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": new_apartment.housing_company.uuid.hex,
            "apartment_uuid": new_apartment.uuid.hex,
        },
    )
    response = api_client.post(url_1, data=data, format="json")
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED, response_data

    # No conditions of sale are created for half hitas apartments
    assert response_data.pop("conditions_of_sale_created", None) is False
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__apartment_sale__create__half_hitas__cant_resell(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
        sales__purchase_date=datetime.date(2022, 1, 1),
    )
    owner: Owner = OwnerFactory.create()

    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2023-01-01",
        "purchase_date": "2023-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.post(url_1, data=data, format="json")
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "invalid",
        "message": "Cannot re-sell a half-hitas housing company apartment.",
        "reason": "Conflict",
        "status": 409,
    }


# Update tests


@pytest.mark.django_db
def test__api__apartment_sale__update(api_client: HitasAPIClient):
    ownership: Ownership = OwnershipFactory.create()
    sale: ApartmentSale = ApartmentSaleFactory.create(ownerships=[ownership])

    data = ApartmentSaleSerializer(sale).data
    del data["id"]
    del data["ownerships"]

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
            "uuid": sale.uuid.hex,
        },
    )
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": sale.uuid.hex,
        "ownerships": [
            {
                "owner": {
                    "id": ownership.owner.uuid.hex,
                    "name": ownership.owner.name,
                    "email": ownership.owner.email,
                    "identifier": ownership.owner.identifier,
                    "non_disclosure": ownership.owner.non_disclosure,
                },
                "percentage": float(ownership.percentage),
            }
        ],
        "notification_date": sale.notification_date.isoformat(),
        "purchase_date": sale.purchase_date.isoformat(),
        "purchase_price": float(sale.purchase_price),
        "apartment_share_of_housing_company_loans": float(sale.apartment_share_of_housing_company_loans),
        "exclude_from_statistics": sale.exclude_from_statistics,
    }


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "'Notification date' can't be null": InvalidInput(
                invalid_data={"notification_date": None},
                fields=[
                    {
                        "field": "notification_date",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Purchase date' can't be null": InvalidInput(
                invalid_data={"purchase_date": None},
                fields=[
                    {
                        "field": "purchase_date",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Purchase price' can't be null": InvalidInput(
                invalid_data={"purchase_price": None},
                fields=[
                    {
                        "field": "purchase_price",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Apartment share of housing company loans' can't be null": InvalidInput(
                invalid_data={"apartment_share_of_housing_company_loans": None},
                fields=[
                    {
                        "field": "apartment_share_of_housing_company_loans",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
            "'Exclude in statistics' can't be null": InvalidInput(
                invalid_data={"exclude_from_statistics": None},
                fields=[
                    {
                        "field": "exclude_from_statistics",
                        "message": "This field is mandatory and cannot be null.",
                    }
                ],
            ),
        }
    ),
)
@pytest.mark.django_db
def test__api__apartment_sale__update__invalid_data(api_client: HitasAPIClient, invalid_data: dict, fields: list):
    sale: ApartmentSale = ApartmentSaleFactory.create()

    data = ApartmentSaleSerializer(sale).data
    del data["id"]
    del data["ownerships"]

    data.update(invalid_data)

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
            "uuid": sale.uuid.hex,
        },
    )
    response = api_client.put(url, data=data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__apartment_sale__update__cannot_update_ownerships(api_client: HitasAPIClient):
    ownership_1: Ownership = OwnershipFactory.create()
    ownership_2: Ownership = OwnershipFactory.create()
    sale: ApartmentSale = ApartmentSaleFactory.create(ownerships=[ownership_1])

    data = ApartmentSaleSerializer(sale).data
    del data["id"]
    data["ownerships"] = [OwnershipSerializer(ownership_2).data]

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
            "uuid": sale.uuid.hex,
        },
    )
    response = api_client.put(url, data=data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "ownerships",
                "message": "Can't update ownerships.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Delete tests


@pytest.mark.django_db
def test__api__apartment_sale__delete__first_sale(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01")

    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=datetime.date(2023, 1, 1),
    )

    sale_uuid = sale.uuid.hex
    apartment = sale.apartment

    assert apartment.sales.count() == 1

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
            "uuid": sale.uuid.hex,
        },
    )
    response_1 = api_client.delete(url)
    assert response_1.status_code == status.HTTP_204_NO_CONTENT, response_1.json()

    response_2 = api_client.get(url)
    assert response_2.status_code == status.HTTP_404_NOT_FOUND, response_2.json()

    # Sale is only soft-deleted, not removed, so relationship remains intact (though also soft-deleted)
    ownerships: list[Ownership] = list(Ownership.all_objects.all())
    assert len(ownerships) == 1
    assert ownerships[0].sale is not None
    assert ownerships[0].sale.uuid.hex == sale_uuid
    assert ownerships[0].deleted is not None

    # Apartment not sold since first sale was deleted
    apartment.refresh_from_db()
    assert apartment.sales.count() == 0


@pytest.mark.django_db
def test__api__apartment_sale__delete__later_sale(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01")

    apartment: Apartment = ApartmentFactory.create(sales=[])
    latest_sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=datetime.date(2023, 1, 1),
    )
    old_sale = ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=datetime.date(2022, 1, 1),
    )
    old_sale_uuid = old_sale.uuid.hex

    assert apartment.sales.count() == 2

    # Old sale's ownerships are soft-deleted / inactive
    old_ownerships = old_sale.ownerships.all()
    old_ownership: Ownership = old_ownerships[0]
    old_ownership_id = old_ownership.id
    old_ownerships.delete()

    old_ownership.refresh_from_db()
    assert old_ownership.deleted is not None

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": latest_sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": latest_sale.apartment.uuid.hex,
            "uuid": latest_sale.uuid.hex,
        },
    )
    response_1 = api_client.delete(url)
    assert response_1.status_code == status.HTTP_204_NO_CONTENT, response_1.json()

    response_2 = api_client.get(url)
    assert response_2.status_code == status.HTTP_404_NOT_FOUND, response_2.json()

    # Old ownerships are undeleted / reactivated
    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 1
    assert ownerships[0].id == old_ownership_id
    assert ownerships[0].sale is not None
    assert ownerships[0].sale.uuid.hex == old_sale_uuid
    assert ownerships[0].deleted is None

    # Apartment not sold since first sale was deleted
    apartment.refresh_from_db()
    assert apartment.sales.count() == 1
    assert apartment.sales.first() == old_sale


@pytest.mark.django_db
def test__api__apartment_sale__delete__under_three_months(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01")

    three_months = timezone.now().date() - relativedelta(months=3)

    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=three_months,
    )

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
            "uuid": sale.uuid.hex,
        },
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


@pytest.mark.django_db
def test__api__apartment_sale__delete__over_three_months(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01")

    under_three_months = timezone.now().date() - relativedelta(months=3) - relativedelta(days=1)

    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=under_three_months,
    )

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
            "uuid": sale.uuid.hex,
        },
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    assert response.json() == {
        "error": "invalid",
        "message": "This sale can no longer be cancelled",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_sale__delete__cant_delete_sale_if_not_latest(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01")

    apartment: Apartment = ApartmentFactory.create(sales=[])
    ApartmentSaleFactory.create(  # Latest sale
        apartment=apartment,
        purchase_date=datetime.date(2023, 1, 1),
    )

    old_sale = ApartmentSaleFactory.create(  # Older sale
        apartment=apartment,
        purchase_date=datetime.date(2022, 1, 1),
    )

    url = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": old_sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": old_sale.apartment.uuid.hex,
            "uuid": old_sale.uuid.hex,
        },
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    assert response.json() == {
        "error": "invalid",
        "message": "Cannot cancel a sale that is not the latest sale",
        "reason": "Conflict",
        "status": 409,
    }
