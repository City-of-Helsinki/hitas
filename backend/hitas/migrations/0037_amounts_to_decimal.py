# Generated by Django 3.2.16 on 2022-11-11 07:22

from decimal import Decimal
import django.core.validators
from django.db import migrations
import hitas.models._base


class Migration(migrations.Migration):

    dependencies = [
        ('hitas', '0036_update_max_price_calc_json_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='additional_work_during_construction',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='debt_free_purchase_price',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='debt_free_purchase_price_during_construction',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='interest_during_construction',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='loans_during_construction',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='primary_loan_amount',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, default=0, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='apartmentconstructionpriceimprovement',
            name='value',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='apartmentmarketpriceimprovement',
            name='value',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='apartmentmaximumpricecalculation',
            name='maximum_price',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='housingcompanyconstructionpriceimprovement',
            name='value',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='housingcompanymarketpriceimprovement',
            name='value',
            field=hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
