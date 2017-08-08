# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 09:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0034_sp3d_part_part_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='sp3d_part',
            name='status',
            field=models.CharField(choices=[('opened', 'opened'), ('geometry', 'geometry'), ('indus', 'indus'), ('qc', 'qc'), ('closed', 'closed')], default='opened', max_length=200),
        ),
    ]
