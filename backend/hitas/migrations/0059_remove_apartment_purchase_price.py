# Generated by Django 3.2.16 on 2023-02-10 15:33


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hitas", "0058_add_sales_catalog_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="apartment",
            name="purchase_price",
        ),
    ]