# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 06:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0047_sp3d_print_printing_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='sp3d_part',
            name='oem_part_number',
            field=models.CharField(default='', max_length=200),
        ),
    ]
