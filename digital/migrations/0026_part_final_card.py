# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-24 01:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jb', '0007_finalcard'),
        ('digital', '0025_auto_20171123_0722'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='final_card',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='jb.FinalCard'),
        ),
    ]
