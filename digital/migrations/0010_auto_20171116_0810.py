# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-16 08:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0009_partevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='partbulkfile',
            name='type',
            field=models.CharField(choices=[('BULK', 'bulk files'), ('MATERIAL', 'material files'), ('3D', '3d model'), ('2D', '2d drawings')], default='BULK', max_length=20),
        ),
        migrations.AlterField(
            model_name='partevent',
            name='type',
            field=models.CharField(choices=[('INFO', 'info'), ('REQUEST', 'request'), ('STATUS_CHANGE', 'status change')], default='INFO', max_length=20),
        ),
    ]
