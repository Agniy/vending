# Generated by Django 2.1.7 on 2019-02-14 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20190214_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sort',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Номинал'),
        ),
    ]
