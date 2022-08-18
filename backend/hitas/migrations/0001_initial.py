# Generated by Django 3.2.14 on 2022-07-26 19:52

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import enumfields.fields
import hitas.models._base
import hitas.models.apartment
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
            name='Apartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('state', enumfields.fields.EnumField(default='free', enum=hitas.models.apartment.ApartmentState, max_length=10)),
                ('surface_area', hitas.models._base.HitasModelDecimalField(decimal_places=2, help_text='Measured in m^2', max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('share_number_start', models.PositiveIntegerField(null=True)),
                ('share_number_end', models.PositiveIntegerField(null=True)),
                ('street_address', models.CharField(max_length=128)),
                ('apartment_number', models.PositiveSmallIntegerField()),
                ('floor', models.PositiveSmallIntegerField(default=1)),
                ('stair', models.CharField(max_length=16)),
                ('debt_free_purchase_price', hitas.models._base.HitasModelDecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('purchase_price', hitas.models._base.HitasModelDecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('acquisition_price', hitas.models._base.HitasModelDecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('primary_loan_amount', hitas.models._base.HitasModelDecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('loans_during_construction', hitas.models._base.HitasModelDecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('interest_during_construction', hitas.models._base.HitasModelDecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Apartment',
                'verbose_name_plural': 'Apartments',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ApartmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True)),
                ('in_use', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, null=True)),
                ('legacy_start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('legacy_end_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Apartment type',
                'verbose_name_plural': 'Apartment types',
                'ordering': ['order', 'id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BuildingType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True)),
                ('in_use', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, null=True)),
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
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, null=True)),
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
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, null=True)),
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
                ('acquisition_price', hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('realized_acquisition_price', hitas.models._base.HitasModelDecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('primary_loan', hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('sales_price_catalogue_confirmation_date', models.DateField(blank=True, null=True)),
                ('notification_date', models.DateField(blank=True, null=True)),
                ('legacy_id', models.CharField(blank=True, max_length=10, null=True)),
                ('notes', models.TextField(blank=True)),
                ('last_modified_datetime', models.DateTimeField(auto_now=True)),
                ('building_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='housing_companies', to='hitas.buildingtype')),
                ('developer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='housing_companies', to='hitas.developer')),
                ('financing_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='housing_companies', to='hitas.financingmethod')),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='housing_companies', to=settings.AUTH_USER_MODEL)),
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
                ('legacy_code_number', models.CharField(help_text='Format: 000', max_length=3, null=True)),
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
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='real_estates', to='hitas.postalcode')),
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
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='property_managers', to='hitas.postalcode')),
            ],
            options={
                'verbose_name': 'Property manager',
                'verbose_name_plural': 'Property managers',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('social_security_number', models.CharField(blank=True, max_length=128, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('street_address', models.CharField(max_length=128)),
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='persons', to='hitas.postalcode')),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'Persons',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ownership_percentage', hitas.models._base.HitasModelDecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))])),
                ('ownership_start_date', models.DateField(blank=True, null=True)),
                ('ownership_end_date', models.DateField(blank=True, null=True)),
                ('apartment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='owners', to='hitas.apartment')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='owners', to='hitas.person')),
            ],
            options={
                'verbose_name': 'Owner',
                'verbose_name_plural': 'Owners',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='housingcompany',
            name='postal_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='housing_companies', to='hitas.postalcode'),
        ),
        migrations.AddField(
            model_name='housingcompany',
            name='property_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='housing_companies', to='hitas.propertymanager'),
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('completion_date', models.DateField(null=True)),
                ('street_address', models.CharField(max_length=1024)),
                ('building_identifier', models.CharField(blank=True, help_text='Format: 100012345A or 91-17-16-1 S 001', max_length=25, null=True, validators=[hitas.models.utils.validate_building_id])),
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='buildings', to='hitas.postalcode')),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='buildings', to='hitas.realestate')),
            ],
            options={
                'verbose_name': 'Building',
                'verbose_name_plural': 'Buildings',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='apartment',
            name='apartment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='apartments', to='hitas.apartmenttype'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='apartments', to='hitas.building'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='postal_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='apartments', to='hitas.postalcode'),
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
