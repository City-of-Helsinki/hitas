# Generated by Django 3.2.16 on 2023-01-16 14:19

import uuid
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import hitas.models._base


class Migration(migrations.Migration):

    dependencies = [
        ("hitas", "0048_bump_json_version_to_5"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApartmentSale",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("deleted", models.DateTimeField(db_index=True, editable=False, null=True)),
                ("deleted_by_cascade", models.BooleanField(default=False, editable=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("notification_date", models.DateField()),
                ("purchase_date", models.DateField()),
                (
                    "purchase_price",
                    hitas.models._base.HitasModelDecimalField(
                        decimal_places=2,
                        max_digits=15,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "apartment_share_of_housing_company_loans",
                    hitas.models._base.HitasModelDecimalField(
                        decimal_places=2,
                        max_digits=15,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                ("include_in_statistics", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Apartment sale",
                "verbose_name_plural": "Apartment sales",
                "ordering": ["id"],
            },
        ),
        migrations.AlterField(
            model_name="ownership",
            name="apartment",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ownerships",
                to="hitas.apartment",
            ),
        ),
        migrations.AlterField(
            model_name="ownership",
            name="owner",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ownerships",
                to="hitas.owner",
            ),
        ),
        migrations.AlterField(
            model_name="ownership",
            name="percentage",
            field=hitas.models._base.HitasModelDecimalField(
                decimal_places=2,
                editable=False,
                max_digits=15,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0")),
                    django.core.validators.MaxValueValidator(Decimal("100")),
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="ownership",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted__isnull", True)),
                fields=("apartment", "owner"),
                name="hitas_ownership_single_ownership_for_apartment_per_owner",
            ),
        ),
        migrations.AddField(
            model_name="apartmentsale",
            name="apartment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sales",
                to="hitas.apartment",
            ),
        ),
        migrations.AddField(
            model_name="ownership",
            name="sale",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="ownerships",
                to="hitas.apartmentsale",
            ),
        ),
    ]
