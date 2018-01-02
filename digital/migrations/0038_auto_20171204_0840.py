# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-04 08:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0037_auto_20171204_0738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characteristics',
            name='color',
            field=models.CharField(choices=[('NA', 'n/a'), ('GREEN', 'Green'), ('WHITE', 'White'), ('BLACK', 'Black'), ('GREY', 'Grey'), ('SILVER', 'Silver')], default='NA', max_length=20),
        ),
        migrations.AlterField(
            model_name='part',
            name='weight_unit',
            field=models.CharField(choices=[('gr', 'gr')], default='gr', max_length=5),
        ),
    ]
