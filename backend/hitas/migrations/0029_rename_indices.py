# Generated by Django 3.2.16 on 2022-10-11 06:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hitas', '0028_housing_company_remove_realized_acquisition_price'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MarketPriceIndexPre2005',
            new_name='ConstructionPriceIndex2005Equal100',
        ),
        migrations.RenameModel(
            old_name='ConstructionPriceIndexPre2005',
            new_name='MarketPriceIndex2005Equal100',
        ),
        migrations.AlterModelOptions(
            name='constructionpriceindex',
            options={'verbose_name': 'Construction price index for apartments constructed before January 2011', 'verbose_name_plural': 'Construction price indices for apartments constructed before January 2011'},
        ),
        migrations.AlterModelOptions(
            name='constructionpriceindex2005equal100',
            options={'verbose_name': 'Construction price index year for apartments constructed in January 2005 onwards', 'verbose_name_plural': 'Construction price indices for apartments constructed in January 2005 onwards'},
        ),
        migrations.AlterModelOptions(
            name='marketpriceindex',
            options={'verbose_name': 'Market price index for apartments constructed before January 2011', 'verbose_name_plural': 'Market price indices for apartment constructed before January 2011'},
        ),
        migrations.AlterModelOptions(
            name='marketpriceindex2005equal100',
            options={'verbose_name': 'Market price index for apartments constructed in January 2011 onwards', 'verbose_name_plural': 'Market price indices for apartment constructed in January 2011 onwards'},
        ),
    ]
