# Generated by Django 2.1.7 on 2019-02-14 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20190214_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='coin',
            name='code',
            field=models.CharField(db_index=True, default='', max_length=255, verbose_name='Код'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coin',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Валюта'),
        ),
    ]
