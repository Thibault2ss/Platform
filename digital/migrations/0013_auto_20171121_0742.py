# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-21 07:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0012_model_organisation'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Model',
            new_name='Appliance',
        ),
    ]
