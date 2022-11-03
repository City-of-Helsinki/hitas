# Generated by Django 3.2.16 on 2022-11-02 08:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import rest_framework.utils.encoders
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hitas', '0031_apartment_required_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApartmentMaxPriceCalculation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('confirmed_at', models.DateTimeField(null=True)),
                ('calculation_date', models.DateField()),
                ('valid_until', models.DateField()),
                ('max_price', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('json', models.JSONField(encoder=rest_framework.utils.encoders.JSONEncoder)),
                ('json_version', models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('apartment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='max_price_calculations', to='hitas.apartment')),
            ],
            options={
                'verbose_name': 'Apartment maximum price calculation',
                'verbose_name_plural': 'Apartment maximum price calculations',
            },
        ),
    ]
