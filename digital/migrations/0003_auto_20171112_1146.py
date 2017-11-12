# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-12 11:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0002_auto_20171111_0139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('short_description', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='part',
            name='color',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='part',
            name='dimension_unit',
            field=models.CharField(blank=True, choices=[('mm', 'mm'), ('inch', 'inch')], max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='height',
            field=models.FloatField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='length',
            field=models.FloatField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jb.Material'),
        ),
        migrations.AlterField(
            model_name='part',
            name='weight',
            field=models.FloatField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='weight_unit',
            field=models.CharField(blank=True, choices=[('gr', 'gr')], max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='width',
            field=models.FloatField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='model',
            unique_together=set([('name', 'reference', 'family')]),
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together=set([('name', 'short_description')]),
        ),
        migrations.AddField(
            model_name='part',
            name='grade',
            field=models.ManyToManyField(to='digital.Grade'),
        ),
    ]
