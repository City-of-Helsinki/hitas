# Generated by Django 3.2.14 on 2022-07-14 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import enumfields.fields
import hitas.models.housing_company
import hitas.models.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildingType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True)),
                ('in_use', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, unique=True, validators=[hitas.models.utils.validate_code_number])),
                ('legacy_start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('legacy_end_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Building type',
                'verbose_name_plural': 'Building types',
                'ordering': ['order', 'id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True)),
                ('in_use', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, unique=True, validators=[hitas.models.utils.validate_code_number])),
                ('legacy_start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('legacy_end_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Developer',
                'verbose_name_plural': 'Developers',
                'ordering': ['order', 'id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FinancingMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True)),
                ('in_use', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, unique=True, validators=[hitas.models.utils.validate_code_number])),
                ('legacy_start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('legacy_end_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Financing methods',
                'verbose_name_plural': 'Financing methods',
                'ordering': ['order', 'id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HousingCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('official_name', models.CharField(max_length=1024)),
                ('display_name', models.CharField(max_length=1024)),
                ('state', enumfields.fields.EnumField(default='not_ready', enum=hitas.models.housing_company.HousingCompanyState, max_length=40)),
                ('business_id', models.CharField(help_text='Format: 1234567-8', max_length=9, validators=[hitas.models.utils.validate_business_id])),
                ('street_address', models.CharField(max_length=1024)),
                ('acquisition_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('realized_acquisition_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('primary_loan', models.DecimalField(decimal_places=2, max_digits=15)),
                ('sales_price_catalogue_confirmation_date', models.DateField(blank=True, null=True)),
                ('notification_date', models.DateField(blank=True, null=True)),
                ('legacy_id', models.CharField(blank=True, max_length=10, null=True)),
                ('notes', models.TextField(blank=True)),
                ('last_modified_datetime', models.DateTimeField(auto_now=True)),
                ('building_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.buildingtype')),
                ('developer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.developer')),
                ('financing_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.financingmethod')),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Housing company',
                'verbose_name_plural': 'Housing companies',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PostalCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True)),
                ('in_use', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, unique=True, validators=[hitas.models.utils.validate_code_number])),
                ('legacy_start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('legacy_end_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Postal code',
                'verbose_name_plural': 'Postal codes',
                'ordering': ['order', 'id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RealEstate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('property_identifier', models.CharField(help_text='Format: 1234-1234-1234-1234', max_length=19, validators=[hitas.models.utils.validate_property_id])),
                ('street_address', models.CharField(max_length=1024)),
                ('housing_company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='real_estates', to='hitas.housingcompany')),
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.postalcode')),
            ],
            options={
                'verbose_name': 'Real estate',
                'verbose_name_plural': 'Real estates',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PropertyManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=1024)),
                ('email', models.EmailField(max_length=254)),
                ('street_address', models.CharField(max_length=1024)),
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.postalcode')),
            ],
            options={
                'verbose_name': 'Property manager',
                'verbose_name_plural': 'Property managers',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='housingcompany',
            name='postal_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.postalcode'),
        ),
        migrations.AddField(
            model_name='housingcompany',
            name='property_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.propertymanager'),
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('completion_date', models.DateField(null=True)),
                ('street_address', models.CharField(max_length=1024)),
                ('building_identifier', models.CharField(blank=True, help_text='Format: 100012345A or 91-17-16-1 S 001', max_length=25, null=True, validators=[hitas.models.utils.validate_building_id])),
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hitas.postalcode')),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='buildings', to='hitas.realestate')),
            ],
            options={
                'verbose_name': 'Building',
                'verbose_name_plural': 'Buildings',
                'ordering': ['id'],
            },
        ),
        migrations.AddConstraint(
            model_name='housingcompany',
            constraint=models.CheckConstraint(check=models.Q(('acquisition_price__gte', 0)), name='acquisition_price_positive'),
        ),
        migrations.AddConstraint(
            model_name='housingcompany',
            constraint=models.CheckConstraint(check=models.Q(('realized_acquisition_price__gte', 0)), name='realized_acquisition_price_positive'),
        ),
    ]
