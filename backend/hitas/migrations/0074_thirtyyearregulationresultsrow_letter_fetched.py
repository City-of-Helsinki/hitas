# Generated by Django 3.2.18 on 2023-05-04 12:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0073_change_base_managers"),
    ]

    operations = [
        migrations.AddField(
            model_name="thirtyyearregulationresultsrow",
            name="letter_fetched",
            field=models.BooleanField(default=False),
        ),
    ]