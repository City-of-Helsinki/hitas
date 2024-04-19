from django.db import migrations


def format_real_estate_property_identifiers(apps, schema_editor):
    RealEstate = apps.get_model("hitas", "RealEstate")
    real_estates_missing_dashes = RealEstate.objects.exclude(property_identifier__contains="-")
    for real_estate in real_estates_missing_dashes:
        # Format `12312312341234` as `123-123-1234-1234`
        real_estate.property_identifier = (
            f"{real_estate.property_identifier[:3]}"
            "-"
            f"{real_estate.property_identifier[3:6]}"
            "-"
            f"{real_estate.property_identifier[6:10]}"
            "-"
            f"{real_estate.property_identifier[10:]}"
        )
        real_estate.save()


class Migration(migrations.Migration):
    dependencies = [
        ("hitas", "0012_nonobfuscatedowner"),
    ]

    operations = [
        migrations.RunPython(format_real_estate_property_identifiers, reverse_code=migrations.RunPython.noop),
    ]
