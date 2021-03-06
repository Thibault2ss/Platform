# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-05 01:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jb', '0014_auto_20171204_0223'),
        ('digital', '0042_auto_20171204_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='characteristics',
            name='material',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='material_characteristics', to='jb.Material'),
        ),
        migrations.AddField(
            model_name='characteristics',
            name='techno_material',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='techno_material_characteristics', to='jb.CoupleTechnoMaterial'),
        ),
        migrations.AddField(
            model_name='characteristics',
            name='technology',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='technology_characteristics', to='jb.Technology'),
        ),
    ]
