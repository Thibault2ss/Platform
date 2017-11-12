# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-12 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0003_auto_20171112_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('short_description', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='environment',
            unique_together=set([('name', 'short_description')]),
        ),
    ]