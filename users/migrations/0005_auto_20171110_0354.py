# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-10 03:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20171109_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.CharField(default=b'', max_length=100, unique=True),
        ),
    ]
