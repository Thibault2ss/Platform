# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-29 08:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0030_characteristics_is_elastic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='digital.PartType'),
        ),
    ]
