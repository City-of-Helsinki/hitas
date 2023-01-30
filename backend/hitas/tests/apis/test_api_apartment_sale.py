import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import Apartment, ApartmentSale, ConditionOfSale, Owner, Ownership
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
    apartment: Apartment = ApartmentFactory.create()

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
    sale: ApartmentSale = ApartmentSaleFactory.create(ownerships=[ownership])

    url = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": sale.apartment.housing_company.uuid.hex,
            "apartment_uuid": sale.apartment.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": sale.uuid.hex,
            "ownerships": [
                {
                    "owner": {
                        "id": ownership.owner.uuid.hex,
                        "name": ownership.owner.name,
                        "email": ownership.owner.email,
                        "identifier": ownership.owner.identifier,
                    },
                    "percentage": float(ownership.percentage),
                }
            ],
            "notification_date": sale.notification_date.isoformat(),
            "purchase_date": sale.purchase_date.isoformat(),
            "purchase_price": float(sale.purchase_price),
            "apartment_share_of_housing_company_loans": float(sale.apartment_share_of_housing_company_loans),
            "exclude_in_statistics": sale.exclude_in_statistics,
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
                },
                "percentage": float(ownership.percentage),
            },
        ],
        "notification_date": sale.notification_date.isoformat(),
        "purchase_date": sale.purchase_date.isoformat(),
        "purchase_price": float(sale.purchase_price),
        "apartment_share_of_housing_company_loans": float(sale.apartment_share_of_housing_company_loans),
        "exclude_in_statistics": sale.exclude_in_statistics,
    }


# Create tests


@pytest.mark.django_db
def test__api__apartment_sale__create(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create()
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
        "exclude_in_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")

    sales: list[ApartmentSale] = list(ApartmentSale.objects.all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_1.json()["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 1

    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
            "uuid": response_1.json()["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_1.json()


@pytest.mark.django_db
def test__api__apartment_sale__create__multiple_owners(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create()
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
        "exclude_in_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")

    sales: list[ApartmentSale] = list(ApartmentSale.objects.all())
    assert len(sales) == 1
    assert sales[0].uuid.hex == response_1.json()["id"]

    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 2

    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    url_2 = reverse(
        "hitas:apartment-sale-detail",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
            "uuid": response_1.json()["id"],
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json() == response_1.json()


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
                invalid_data={"exclude_in_statistics": None},
                fields=[
                    {
                        "field": "exclude_in_statistics",
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
    apartment: Apartment = ApartmentFactory.create()
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
        "exclude_in_statistics": True,
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
def test__api__apartment_sale__create__replace_old_ownerships(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory.create()
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    owner_3: Owner = OwnerFactory.create()
    ownership_1: Ownership = OwnershipFactory.create(owner=owner_1, apartment=apartment, percentage=60.0)
    ownership_2: Ownership = OwnershipFactory.create(owner=owner_2, apartment=apartment, percentage=40.0)
    ApartmentSaleFactory.create(apartment=apartment, ownerships=[ownership_1, ownership_2])

    apartment_sales_pre = list(apartment.sales.all())
    apartment_ownerships_pre = list(apartment.ownerships.all())
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
        "exclude_in_statistics": True,
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
    apartment_ownerships_post = list(apartment.ownerships.all())
    assert len(apartment_sales_post) == 2
    assert len(apartment_ownerships_post) == 1
    assert apartment_ownerships_post[0].owner.uuid.hex == owner_3.uuid.hex


@pytest.mark.django_db
def test__api__apartment_sale__create__condition_of_sale_fulfilled(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=new_apartment)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)
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
        "exclude_in_statistics": True,
    }

    url_1 = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": old_apartment.housing_company.uuid.hex,
            "apartment_uuid": old_apartment.uuid.hex,
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
                },
                "percentage": float(ownership.percentage),
            }
        ],
        "notification_date": sale.notification_date.isoformat(),
        "purchase_date": sale.purchase_date.isoformat(),
        "purchase_price": float(sale.purchase_price),
        "apartment_share_of_housing_company_loans": float(sale.apartment_share_of_housing_company_loans),
        "exclude_in_statistics": sale.exclude_in_statistics,
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
                invalid_data={"exclude_in_statistics": None},
                fields=[
                    {
                        "field": "exclude_in_statistics",
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
def test__api__apartment_sale__delete(api_client: HitasAPIClient):
    ownership: Ownership = OwnershipFactory.create()
    sale: ApartmentSale = ApartmentSaleFactory.create(ownerships=[ownership])

    sale_uuid = sale.uuid.hex

    assert ownership.sale.uuid.hex == sale_uuid

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

    # Sale is only soft-deleted, not removed, so relationship remains intact
    ownerships: list[Ownership] = list(Ownership.objects.all())
    assert len(ownerships) == 1
    assert ownerships[0].id == ownership.id
    assert ownerships[0].sale is not None
    assert ownerships[0].sale.uuid.hex == sale_uuid
