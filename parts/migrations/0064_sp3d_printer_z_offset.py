# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-14 08:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0063_sp3d_status_ord_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='sp3d_printer',
            name='z_offset',
            field=models.FloatField(default=0.0),
        ),
    ]
