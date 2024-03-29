# Generated by Django 3.2.18 on 2023-06-12 10:17

import enumfields.fields
from django.db import migrations, models
from enumfields import Enum

import hitas.models._base
import hitas.models.email_template


class EmailTemplateName(Enum):
    CONFIRMED_MAX_PRICE_CALCULATION = "confirmed_max_price_calculation"
    UNCONFIRMED_MAX_PRICE_CALCULATION = "unconfirmed_max_price_calculation"

    class Labels:
        CONFIRMED_MAX_PRICE_CALCULATION = "Enimmäishintalaskelma"
        UNCONFIRMED_MAX_PRICE_CALCULATION = "Hinta-arvio"


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0004_remove_apartment_state"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailTemplate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    enumfields.fields.EnumField(
                        enum=EmailTemplateName,
                        max_length=33,
                        unique=True,
                    ),
                ),
                ("text", models.TextField(max_length=10000)),
            ],
            options={
                "verbose_name": "Email template",
                "verbose_name_plural": "Email templates",
            },
            bases=(
                hitas.models._base.PostFetchModelMixin,
                hitas.models._base.AuditLogAdditionalDataMixin,
                models.Model,
            ),
        ),
    ]
