# Generated by Django 3.2.19 on 2023-08-21 22:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0010_interest_migration"),
    ]

    operations = [
        migrations.RenameField(
            model_name="apartment",
            old_name="interest_during_construction_14",
            new_name="interest_during_construction_cpi",
        ),
        migrations.RenameField(
            model_name="apartment",
            old_name="interest_during_construction_6",
            new_name="interest_during_construction_mpi",
        ),
    ]
