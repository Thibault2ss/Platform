# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-23 05:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0021_auto_20171123_0349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characteristics',
            name='color',
            field=models.CharField(choices=[('NA', 'n/a'), ('GREEN', 'Green'), ('WHITE', 'White'), ('BLACK', 'Black')], default='NA', max_length=20),
        ),
        migrations.AlterField(
            model_name='characteristics',
            name='flame_retardancy',
            field=models.CharField(choices=[('NA', 'n/a'), ('HB', 'HB'), ('V0', 'V0'), ('V1', 'V1'), ('V2', 'V2')], default='NA', max_length=10),
        ),
        migrations.AlterField(
            model_name='characteristics',
            name='max_temp',
            field=models.IntegerField(default=60),
        ),
        migrations.AlterField(
            model_name='characteristics',
            name='min_temp',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='characteristics',
            name='temp_unit',
            field=models.CharField(choices=[('\xb0C', '\xb0C'), ('\xb0F', '\xb0F')], default='\xb0C', max_length=5),
        ),
    ]
