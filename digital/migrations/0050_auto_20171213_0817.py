# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-13 08:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0049_auto_20171213_0403'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkpartupload',
            name='errors',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bulkpartupload',
            name='warnings',
            field=models.TextField(blank=True, null=True),
        ),
    ]
