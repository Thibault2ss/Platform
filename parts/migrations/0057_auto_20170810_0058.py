# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-10 00:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0056_remove_sp3d_order_quantities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sp3d_order',
            name='parts',
            field=models.CharField(default='{}', max_length=200),
        ),
    ]
