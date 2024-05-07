# fmt: off
# ruff: noqa: E501, I001
from django.test import override_settings

from hitas.tests.apis.test_api_apartment import test__api__apartment__retrieve as _test__api__apartment__retrieve
from hitas.tests.apis.test_api_apartment import test__api__apartment__retrieve__2011_onwards__indices_set as _test__api__apartment__retrieve__2011_onwards__indices_set
from hitas.tests.apis.test_api_apartment import test__api__apartment__retrieve__pre_2011__indices_set as _test__api__apartment__retrieve__pre_2011__indices_set
from hitas.tests.apis.test_api_apartment import test__api__apartment__retrieve__pre_2011__old_hitas_ruleset as _test__api__apartment__retrieve__pre_2011__old_hitas_ruleset
from hitas.tests.apis.test_api_apartment import test__api__apartment__retrieve__pre_2005__old_hitas_ruleset as _test__api__apartment__retrieve__pre_2005__old_hitas_ruleset
from hitas.tests.apis.test_api_apartment import test__api__apartment__retrieve__unconfirmed_prices_use_housing_company_completion_date as _test__api__apartment__retrieve__unconfirmed_prices_use_housing_company_completion_date
from hitas.tests.apis.test_api_housing_company import test__api__housing_company__retrieve as _test__api__housing_company__retrieve
from hitas.tests.apis.test_api_housing_company import test__api__housing_company__retrieve_rounding as _test__api__housing_company__retrieve_rounding
from hitas.tests.apis.test_api_indices import test__api__indices__create__surface_area_price_ceiling__single as _test__api__indices__create__surface_area_price_ceiling__single
from hitas.tests.apis.test_api_indices import test__api__indices__create__surface_area_price_ceiling__multiple as _test__api__indices__create__surface_area_price_ceiling__multiple
from hitas.tests.apis.test_api_reports import test__api__regulated_housing_companies_report__single_housing_company as _test__api__regulated_housing_companies_report__single_housing_company
from hitas.tests.apis.test_api_reports import test__api__regulated_housing_companies_report__multiple_housing_companies as _test__api__regulated_housing_companies_report__multiple_housing_companies
from hitas.tests.apis.test_api_reports import test__api__regulated_housing_companies_report__unregulated_not_included as _test__api__regulated_housing_companies_report__unregulated_not_included
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_calc_examples import test__api__apartment_max_price__construction_price_index__2011_onwards as _test__api__apartment_max_price__construction_price_index__2011_onwards
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_calc_examples import test__api__apartment_max_price__market_price_index__2011_onwards as _test__api__apartment_max_price__market_price_index__2011_onwards
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_calc_examples import test__api__apartment_max_price__market_price_index__pre_2011 as _test__api__apartment_max_price__market_price_index__pre_2011
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_calc_examples import test__api__apartment_max_price__construction_price_index__pre_2011 as _test__api__apartment_max_price__construction_price_index__pre_2011
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_calc_examples import test__api__apartment_max_price__pre_2011__no_improvements as _test__api__apartment_max_price__pre_2011__no_improvements
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_calc_examples import test__api__apartment_max_price__surface_area_price_ceiling as _test__api__apartment_max_price__surface_area_price_ceiling
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_calc_examples import test__api__apartment_max_price__missing_property_manager as _test__api__apartment_max_price__missing_property_manager
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_retrieve_for_date import test__api__apartment_unconfirmed_max_price__retrieve_for_date as _test__api__apartment_unconfirmed_max_price__retrieve_for_date
from hitas.tests.apis.apartment_max_price.test_api_apartment_max_price_retrieve_for_date import test__api__apartment_unconfirmed_max_price__retrieve_for_date__rr as _test__api__apartment_unconfirmed_max_price__retrieve_for_date__rr
from hitas.tests.apis.apartment_max_price.test_api_unconfirmed_max_price_pdf import test__api__unconfirmed_max_price_pdf as _test__api__unconfirmed_max_price_pdf
from hitas.tests.apis.apartment_max_price.test_api_unconfirmed_max_price_pdf import test__api__unconfirmed_max_price_pdf__old_hitas_ruleset as _test__api__unconfirmed_max_price_pdf__old_hitas_ruleset
from hitas.tests.apis.apartment_max_price.test_api_unconfirmed_max_price_pdf import test__api__unconfirmed_max_price_pdf__past_date as _test__api__unconfirmed_max_price_pdf__past_date
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__stays_regulated as _test__api__regulation__stays_regulated
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__released_from_regulation as _test__api__regulation__released_from_regulation
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__comparison_is_equal as _test__api__regulation__comparison_is_equal
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__automatically_release__all as _test__api__regulation__automatically_release__all
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__automatically_release__partial as _test__api__regulation__automatically_release__partial
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__only_external_sales_data as _test__api__regulation__only_external_sales_data
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__both_hitas_and_external_sales_data as _test__api__regulation__both_hitas_and_external_sales_data
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__use_catalog_prices as _test__api__regulation__use_catalog_prices
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation import test__api__regulation__housing_company_regulation_status as _test__api__regulation__housing_company_regulation_status
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_conditions_of_sale import test__api__regulation__conditions_of_sale_fulfilled as _test__api__regulation__conditions_of_sale_fulfilled
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_errors import test__api__regulation__catalog_price_zero as _test__api__regulation__catalog_price_zero
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_exclude import test__api__regulation__exclude_from_statistics__housing_company as _test__api__regulation__exclude_from_statistics__housing_company
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_exclude import test__api__regulation__exclude_from_statistics__sale__all as _test__api__regulation__exclude_from_statistics__sale__all
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_exclude import test__api__regulation__exclude_from_statistics__sale__partial as _test__api__regulation__exclude_from_statistics__sale__partial
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_half_hitas import test__api__regulation__owner_still_owns_half_hitas_apartment as _test__api__regulation__owner_still_owns_half_hitas_apartment
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_half_hitas import test__api__regulation__owner_still_owns_half_hitas_apartment__over_2_years as _test__api__regulation__owner_still_owns_half_hitas_apartment__over_2_years
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_no_sales_data_for_postal_code import test__api__regulation__no_sales_data_for_postal_code as _test__api__regulation__no_sales_data_for_postal_code
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_no_sales_data_for_postal_code import test__api__regulation__no_sales_data_for_postal_code__use_replacements as _test__api__regulation__no_sales_data_for_postal_code__use_replacements
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_no_sales_data_for_postal_code import test__api__regulation__no_sales_data_for_postal_code__half_hitas as _test__api__regulation__no_sales_data_for_postal_code__half_hitas
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_no_sales_data_for_postal_code import test__api__regulation__no_sales_data_for_postal_code__sale_previous_year as _test__api__regulation__no_sales_data_for_postal_code__sale_previous_year
from hitas.tests.apis.thirty_year_regulation.test_api_thirty_year_regulation_no_sales_data_for_postal_code import test__api__regulation__no_sales_data_for_postal_code__other_not_regulated as _test__api__regulation__no_sales_data_for_postal_code__other_not_regulated


# Re-run specific tests with updated_acquisition_price set,
# so that calculations are tested to work with updated_acquisition_price override.
patched = override_settings(TESTS_SHOULD_SET_UPDATED_ACQUISITION_PRICE=True)


test__api__apartment__retrieve__updated_acquisition_price = patched(_test__api__apartment__retrieve)
test__api__apartment__retrieve__2011_onwards__indices_set__updated_acquisition_price = patched(_test__api__apartment__retrieve__2011_onwards__indices_set)
test__api__apartment__retrieve__pre_2011__indices_set__updated_acquisition_price = patched(_test__api__apartment__retrieve__pre_2011__indices_set)
test__api__apartment__retrieve__pre_2011__old_hitas_ruleset__updated_acquisition_price = patched(_test__api__apartment__retrieve__pre_2011__old_hitas_ruleset)
test__api__apartment__retrieve__pre_2005__old_hitas_ruleset__updated_acquisition_price = patched(_test__api__apartment__retrieve__pre_2005__old_hitas_ruleset)
test__api__apartment__retrieve__unconfirmed_prices_use_housing_company_completion_date__updated_acquisition_price = patched(_test__api__apartment__retrieve__unconfirmed_prices_use_housing_company_completion_date)
test__api__housing_company__retrieve__updated_acquisition_price = patched(_test__api__housing_company__retrieve)
test__api__housing_company__retrieve__updated_acquisition_price = patched(_test__api__housing_company__retrieve)
test__api__housing_company__retrieve_rounding__updated_acquisition_price = patched(_test__api__housing_company__retrieve_rounding)
test__api__indices__create__surface_area_price_ceiling__single__updated_acquisition_price = patched(_test__api__indices__create__surface_area_price_ceiling__single)
test__api__indices__create__surface_area_price_ceiling__multiple__updated_acquisition_price = patched(_test__api__indices__create__surface_area_price_ceiling__multiple)
test__api__regulated_housing_companies_report__single_housing_company__updated_acquisition_price = patched(_test__api__regulated_housing_companies_report__single_housing_company)
test__api__regulated_housing_companies_report__multiple_housing_companies__updated_acquisition_price = patched(_test__api__regulated_housing_companies_report__multiple_housing_companies)
test__api__regulated_housing_companies_report__unregulated_not_included__updated_acquisition_price = patched(_test__api__regulated_housing_companies_report__unregulated_not_included)
test__api__apartment_max_price__construction_price_index__2011_onwards__updated_acquisition_price = patched(_test__api__apartment_max_price__construction_price_index__2011_onwards)
test__api__apartment_max_price__market_price_index__2011_onwards__updated_acquisition_price = patched(_test__api__apartment_max_price__market_price_index__2011_onwards)
test__api__apartment_max_price__market_price_index__pre_2011__updated_acquisition_price = patched(_test__api__apartment_max_price__market_price_index__pre_2011)
test__api__apartment_max_price__construction_price_index__pre_2011__updated_acquisition_price = patched(_test__api__apartment_max_price__construction_price_index__pre_2011)
test__api__apartment_max_price__pre_2011__no_improvements__updated_acquisition_price = patched(_test__api__apartment_max_price__pre_2011__no_improvements)
test__api__apartment_max_price__pre_2011__no_improvements__updated_acquisition_price = patched(_test__api__apartment_max_price__pre_2011__no_improvements)
test__api__apartment_max_price__surface_area_price_ceiling__updated_acquisition_price = patched(_test__api__apartment_max_price__surface_area_price_ceiling)
test__api__apartment_max_price__missing_property_manager__updated_acquisition_price = patched(_test__api__apartment_max_price__missing_property_manager)
test__api__apartment_unconfirmed_max_price__retrieve_for_date__updated_acquisition_price = patched(_test__api__apartment_unconfirmed_max_price__retrieve_for_date)
test__api__apartment_unconfirmed_max_price__retrieve_for_date__rr__updated_acquisition_price = patched(_test__api__apartment_unconfirmed_max_price__retrieve_for_date__rr)
test__api__unconfirmed_max_price_pdf__updated_acquisition_price = patched(_test__api__unconfirmed_max_price_pdf)
test__api__unconfirmed_max_price_pdf__updated_acquisition_price = patched(_test__api__unconfirmed_max_price_pdf)
test__api__unconfirmed_max_price_pdf__old_hitas_ruleset__updated_acquisition_price = patched(_test__api__unconfirmed_max_price_pdf__old_hitas_ruleset)
test__api__unconfirmed_max_price_pdf__past_date__updated_acquisition_price = patched(_test__api__unconfirmed_max_price_pdf__past_date)
test__api__regulation__stays_regulated__updated_acquisition_price = patched(_test__api__regulation__stays_regulated)
test__api__regulation__stays_regulated__updated_acquisition_price = patched(_test__api__regulation__stays_regulated)
test__api__regulation__released_from_regulation__updated_acquisition_price = patched(_test__api__regulation__released_from_regulation)
test__api__regulation__comparison_is_equal__updated_acquisition_price = patched(_test__api__regulation__comparison_is_equal)
test__api__regulation__automatically_release__all__updated_acquisition_price = patched(_test__api__regulation__automatically_release__all)
test__api__regulation__automatically_release__partial__updated_acquisition_price = patched(_test__api__regulation__automatically_release__partial)
test__api__regulation__only_external_sales_data__updated_acquisition_price = patched(_test__api__regulation__only_external_sales_data)
test__api__regulation__both_hitas_and_external_sales_data__updated_acquisition_price = patched(_test__api__regulation__both_hitas_and_external_sales_data)
test__api__regulation__use_catalog_prices__updated_acquisition_price = patched(_test__api__regulation__use_catalog_prices)
test__api__regulation__housing_company_regulation_status__updated_acquisition_price = patched(_test__api__regulation__housing_company_regulation_status)
test__api__regulation__conditions_of_sale_fulfilled__updated_acquisition_price = patched(_test__api__regulation__conditions_of_sale_fulfilled)
test__api__regulation__catalog_price_zero__updated_acquisition_price = patched(_test__api__regulation__catalog_price_zero)
test__api__regulation__exclude_from_statistics__housing_company__updated_acquisition_price = patched(_test__api__regulation__exclude_from_statistics__housing_company)
test__api__regulation__exclude_from_statistics__sale__all__updated_acquisition_price = patched(_test__api__regulation__exclude_from_statistics__sale__all)
test__api__regulation__exclude_from_statistics__sale__partial__updated_acquisition_price = patched(_test__api__regulation__exclude_from_statistics__sale__partial)
test__api__regulation__owner_still_owns_half_hitas_apartment__updated_acquisition_price = patched(_test__api__regulation__owner_still_owns_half_hitas_apartment)
test__api__regulation__owner_still_owns_half_hitas_apartment__over_2_years__updated_acquisition_price = patched(_test__api__regulation__owner_still_owns_half_hitas_apartment__over_2_years)
test__api__regulation__no_sales_data_for_postal_code__updated_acquisition_price = patched(_test__api__regulation__no_sales_data_for_postal_code)
test__api__regulation__no_sales_data_for_postal_code__use_replacements__updated_acquisition_price = patched(_test__api__regulation__no_sales_data_for_postal_code__use_replacements)
test__api__regulation__no_sales_data_for_postal_code__half_hitas__updated_acquisition_price = patched(_test__api__regulation__no_sales_data_for_postal_code__half_hitas)
test__api__regulation__no_sales_data_for_postal_code__sale_previous_year__updated_acquisition_price = patched(_test__api__regulation__no_sales_data_for_postal_code__sale_previous_year)
test__api__regulation__no_sales_data_for_postal_code__other_not_regulated__updated_acquisition_price = patched(_test__api__regulation__no_sales_data_for_postal_code__other_not_regulated)