# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-05 03:53
from __future__ import unicode_literals

from django.db import migrations
from digital.models import Part


def populate_onetoone(apps, schema_editor):
    for part in Part.objects.all():
        if part.final_card is not None:
            part.final_card.part = part
            part.final_card.save()

class Migration(migrations.Migration):

    dependencies = [
        ('jb', '0017_finalcard_part'),
    ]

    operations = [
        migrations.RunPython(populate_onetoone),
    ]
