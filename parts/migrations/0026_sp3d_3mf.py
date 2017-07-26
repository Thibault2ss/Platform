# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 01:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0025_sp3d_part_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='SP3D_3MF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(verbose_name='date published')),
                ('id_cad', models.IntegerField(default=0)),
                ('name_amf', models.CharField(default='', max_length=200)),
                ('name_config', models.CharField(default='', max_length=200)),
                ('name_configb', models.CharField(default='', max_length=200)),
                ('root_path', models.CharField(default='/home/user01/SpareParts_Database/root/', max_length=200)),
                ('amf_path', models.CharField(default='', max_length=200)),
                ('config_path', models.CharField(default='', max_length=200)),
                ('configb_path', models.CharField(default='', max_length=200)),
                ('id_creator', models.IntegerField(default=0)),
                ('notes', models.CharField(default='', max_length=1000)),
            ],
        ),
    ]
