# Generated by Django 4.2.4 on 2024-04-30 10:36

from decimal import Decimal

import django.core.validators
from django.db import migrations

import hitas.models._base


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0013_format_real_estate_property_identifiers"),
    ]

    operations = [
        migrations.AddField(
            model_name="apartment",
            name="updated_acquisition_price",
            field=hitas.models._base.HitasModelDecimalField(
                decimal_places=2,
                max_digits=15,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0"))],
            ),
        ),
    ]
