import datetime

import pytest
from django.template.loader import get_template

from hitas.models import Apartment
from hitas.tests.factories import ApartmentFactory, UserFactory
from hitas.views.apartment import ApartmentDetailSerializer


def get_unconfirmed_prices():
    return {
        "construction_price_index": {"value": 100, "maximum": False},
        "market_price_index": {"value": 150, "maximum": False},
        "surface_area_price_ceiling": {"value": 200, "maximum": False},
    }


@pytest.mark.parametrize(
    "maximum_index", ["construction_price_index", "market_price_index", "surface_area_price_ceiling"]
)
@pytest.mark.django_db
def test__render_unconfirmed_max_price__surface_area_price_ceiling(maximum_index):
    api_user = UserFactory.create()
    ap: Apartment = ApartmentFactory.create(completion_date=datetime.date(2011, 1, 1))
    apartment_data = ApartmentDetailSerializer(ap).data

    unconfirmed_prices = get_unconfirmed_prices()
    unconfirmed_prices.update({maximum_index: {"value": 1000, "maximum": True}})
    apartment_data["prices"]["maximum_prices"]["unconfirmed"]["onwards_2011"] = unconfirmed_prices
    texts = ["||foo||", "||bar||", "||baz||"]

    context = {
        "apartment": apartment_data,
        "user": api_user,
        "body_parts": texts,
    }

    html = get_template("unconfirmed_maximum_price.jinja").render(context)
    if maximum_index == "construction_price_index":
        assert "euroa rakennuskustannusindeksillä laskettuna" in html
    elif maximum_index == "market_price_index":
        assert "euroa markkinahintaindeksillä laskettuna" in html
    elif maximum_index == "surface_area_price_ceiling":
        assert "laskettu voimassaolevan rajahinnan perusteella" in html

    assert api_user.first_name in html
    assert api_user.last_name in html
    assert api_user.title in html

    assert "||foo||" in html
    if maximum_index == "surface_area_price_ceiling":
        assert "||bar||" in html
        assert "||baz||" in html


@pytest.mark.parametrize("additional_info", [None, "", "Pesukarhujen salaliittoteoria"])
@pytest.mark.django_db
def test__render_unconfirmed_max_price__additional_info(additional_info):
    api_user = UserFactory.create()
    ap: Apartment = ApartmentFactory.create(completion_date=datetime.date(2011, 1, 1))
    apartment_data = ApartmentDetailSerializer(ap).data
    apartment_data["prices"]["maximum_prices"]["unconfirmed"]["onwards_2011"] = get_unconfirmed_prices()
    texts = ["||foo||", "||bar||", "||baz||"]

    context = {
        "apartment": apartment_data,
        "additional_info": additional_info,
        "user": api_user,
        "body_parts": texts,
    }

    html = get_template("unconfirmed_maximum_price.jinja").render(context)
    if additional_info:
        assert additional_info in html
    else:
        pass  # Template should still render without errors

    assert api_user.first_name in html
    assert api_user.last_name in html
    assert api_user.title in html

    assert "||foo||" in html
    assert "||bar||" not in html
    assert "||baz||" not in html
