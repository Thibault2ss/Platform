# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-31 05:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20171031_0500'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='user_type',
            new_name='usertype',
        ),
    ]