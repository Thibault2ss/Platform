# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-30 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20171130_0229'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Position Title'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(default=b'', max_length=60),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
