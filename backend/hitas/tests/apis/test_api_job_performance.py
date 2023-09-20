import datetime

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models.job_performance import JobPerformance, JobPerformanceSource
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import UserFactory


@pytest.mark.parametrize(
    "viewname",
    [
        "hitas:job-performance-confirmed-maximum-price",
        "hitas:job-performance-unconfirmed-maximum-price",
    ],
)
@pytest.mark.django_db
def test__api__job_performance__no_entries(api_client: HitasAPIClient, viewname):
    date_params = {"start_date": "2021-01-01", "end_date": "2021-01-31"}
    response = api_client.get(reverse(viewname) + "?" + urlencode(date_params))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totals": {
            "count": 0,
            "average_days": 0,
            "maximum_days": 0,
        },
        "per_user": [],
    }


@pytest.mark.parametrize(
    "viewname,source",
    [
        ("hitas:job-performance-confirmed-maximum-price", JobPerformanceSource.CONFIRMED_MAX_PRICE),
        ("hitas:job-performance-unconfirmed-maximum-price", JobPerformanceSource.UNCONFIRMED_MAX_PRICE),
    ],
)
@pytest.mark.django_db
def test__api__job_performance__multiple_users(api_client: HitasAPIClient, viewname, source):
    user1 = UserFactory.create(first_name="John", last_name="Doe")
    # Included in the results, days between request and delivery is 4
    # but it contains saturday and sunday so the actual value used in calculation is 2
    JobPerformance.objects.create(
        user=user1,
        request_date=datetime.date(2021, 1, 1),
        delivery_date=datetime.date(2021, 1, 5),
        source=source,
    )
    # Included in the results, days between request and delivery is 25
    # but it contains 7 weekend days so the actual value used in calculations is 18
    JobPerformance.objects.create(
        user=user1,
        request_date=datetime.date(2021, 1, 5),
        delivery_date=datetime.date(2021, 1, 30),
        source=source,
    )
    # Excluded from the results
    JobPerformance.objects.create(
        user=user1,
        request_date=datetime.date(2020, 1, 1),
        delivery_date=datetime.date(2022, 1, 1),
        source=source,
    )

    user2 = UserFactory.create(first_name="Jane", last_name="Doe")
    # Included in the results, days between request and delivery is 1
    # but 09012021 is a saturday so 0 days which is a special case that is converted to 0.5
    JobPerformance.objects.create(
        user=user2,
        request_date=datetime.date(2021, 1, 8),
        delivery_date=datetime.date(2021, 1, 9),
        source=source,
    )

    date_params = {"start_date": "2021-01-01", "end_date": "2021-01-31"}
    response = api_client.get(reverse(viewname) + "?" + urlencode(date_params))

    # 3 cases combined handling times is 2+18+0.5 = 20.5

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totals": {
            "count": 3,
            "average_days": 6.83,
            "maximum_days": 18,
        },
        "per_user": [
            {
                "full_name": "John Doe",
                "job_performance_count": 2,
            },
            {
                "full_name": "Jane Doe",
                "job_performance_count": 1,
            },
        ],
    }


@pytest.mark.parametrize(
    "viewname,date_params",
    [
        ("hitas:job-performance-confirmed-maximum-price", {"strt_date": "2021-01-01"}),
        ("hitas:job-performance-confirmed-maximum-price", {"end_date": "2021-01-31"}),
        ("hitas:job-performance-unconfirmed-maximum-price", {"start_date": "2021-01-01"}),
        ("hitas:job-performance-unconfirmed-maximum-price", {"end_date": "2021-01-31"}),
        ("hitas:job-performance-confirmed-maximum-price", {"start_date": "2021-02-01", "end_date": "2021-01-31"}),
        ("hitas:job-performance-unconfirmed-maximum-price", {"start_date": "2021-02-01", "end_date": "2021-01-31"}),
    ],
)
@pytest.mark.django_db
def test__api__job_performance__bad_params(api_client: HitasAPIClient, viewname, date_params):
    response = api_client.get(
        reverse(viewname) + "?" + urlencode(date_params),
        openapi_validate_request=False,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
