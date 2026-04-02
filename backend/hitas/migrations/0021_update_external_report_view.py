from django.db import migrations

UPDATE_SQL = """
CREATE OR REPLACE VIEW hitas_apartment_external_report_view AS
    SELECT
        id,
        deleted,
        deleted_by_cascade,
        uuid,
        share_number_start,
        share_number_end,
        completion_date,
        street_address,
        stair,
        apartment_number,
        floor,
        surface_area,
        rooms,
        catalog_purchase_price,
        catalog_primary_loan_amount,
        additional_work_during_construction,
        loans_during_construction,
        interest_during_construction_mpi,
        interest_during_construction_cpi,
        debt_free_purchase_price_during_construction,
        apartment_type_id,
        building_id,
        updated_acquisition_price
    FROM hitas_apartment
    WHERE deleted IS NULL;
COMMENT ON VIEW hitas_apartment_external_report_view IS
    'hitas_apartment view for external report usage, excluding the notes column because notes may contain sensitive information.';
"""  # noqa: E501

REVERSE_SQL = """
CREATE OR REPLACE VIEW hitas_apartment_external_report_view AS
    SELECT
        id,
        deleted,
        deleted_by_cascade,
        uuid,
        share_number_start,
        share_number_end,
        completion_date,
        street_address,
        stair,
        apartment_number,
        floor,
        surface_area,
        rooms,
        catalog_purchase_price,
        catalog_primary_loan_amount,
        additional_work_during_construction,
        loans_during_construction,
        interest_during_construction_mpi,
        interest_during_construction_cpi,
        debt_free_purchase_price_during_construction,
        apartment_type_id,
        building_id,
        updated_acquisition_price
    FROM hitas_apartment;
COMMENT ON VIEW hitas_apartment_external_report_view IS
    'hitas_apartment view for external report usage, excluding the notes column because notes may contain sensitive information.';
"""  # noqa: E501


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0020_add_apartment_number_integer"),
    ]

    operations = [
        migrations.RunSQL(
            sql=UPDATE_SQL,
            reverse_sql=REVERSE_SQL,
        ),
    ]
