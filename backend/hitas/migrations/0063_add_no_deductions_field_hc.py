# Generated by Django 3.2.18 on 2023-02-28 15:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0062_rename_exclude_in_statistics_apartmentsale_exclude_from_statistics"),
    ]

    operations = [
        migrations.AddField(
            model_name="housingcompanymarketpriceimprovement",
            name="no_deductions",
            field=models.BooleanField(default=False),
        ),
    ]