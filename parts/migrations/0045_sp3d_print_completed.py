# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 07:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0044_sp3d_print_finished_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='sp3d_print',
            name='completed',
            field=models.IntegerField(default=0),
        ),
    ]
