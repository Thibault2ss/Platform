# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-04 07:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0032_auto_20171204_0206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characteristics',
            name='max_X',
        ),
        migrations.RemoveField(
            model_name='characteristics',
            name='max_Y',
        ),
        migrations.RemoveField(
            model_name='characteristics',
            name='max_Z',
        ),
        migrations.AddField(
            model_name='parttype',
            name='appliance_family',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='digital.ApplianceFamily', verbose_name='Appliance Family'),
        ),
        migrations.AlterField(
            model_name='characteristics',
            name='max_temp',
            field=models.IntegerField(default=70, verbose_name='Maximum Operating Temperature'),
        ),
        migrations.AlterField(
            model_name='characteristics',
            name='min_temp',
            field=models.IntegerField(default=0, verbose_name='Minimum Operating Temperature'),
        ),
        migrations.AlterUniqueTogether(
            name='parttype',
            unique_together=set([]),
        ),
    ]
