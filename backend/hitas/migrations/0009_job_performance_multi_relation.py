# Generated by Django 3.2.19 on 2023-06-20 07:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("hitas", "0008_remove_property_manager_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobperformance",
            name="object_id",
            field=models.PositiveBigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="jobperformance",
            name="object_type",
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
    ]
