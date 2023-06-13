# Generated by Django 3.2.19 on 2023-06-13 07:44

import enumfields.fields
from django.db import migrations, models

import hitas.models.email_template


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0005_emailtemplate"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailtemplate",
            name="type",
            field=enumfields.fields.EnumField(
                default="confirmed_max_price_calculation",
                enum=hitas.models.email_template.EmailTemplateType,
                max_length=33,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="emailtemplate",
            name="name",
            field=models.CharField(max_length=256),
        ),
        migrations.AddConstraint(
            model_name="emailtemplate",
            constraint=models.UniqueConstraint(
                fields=("name", "type"),
                name="hitas_emailtemplate_unique_name_type",
            ),
        ),
    ]
