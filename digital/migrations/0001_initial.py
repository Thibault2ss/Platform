# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-10 07:46
from __future__ import unicode_literals

import digital.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sp3d.storage_backends


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0005_auto_20171110_0354'),
    ]

    operations = [
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('reference', models.CharField(max_length=200, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('reference', models.CharField(max_length=200, null=True, unique=True)),
                ('name', models.CharField(default='', max_length=200)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('model', models.ManyToManyField(to='digital.Model')),
                ('organisation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Organisation')),
            ],
        ),
        migrations.CreateModel(
            name='PartBulkFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, storage=sp3d.storage_backends.PrivateMediaStorage(bucket='sp3d-clients'), upload_to=digital.models.get_bulk_path)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('part', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='digital.Part')),
            ],
        ),
        migrations.CreateModel(
            name='PartFamily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PartImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(blank=True, storage=sp3d.storage_backends.PrivateMediaStorage(bucket='sp3d-clients'), upload_to=digital.models.get_image_path)),
                ('thumbnail', models.ImageField(blank=True, null=True, storage=sp3d.storage_backends.PrivateMediaStorage(bucket='sp3d-clients'), upload_to=digital.models.get_image_path)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('part', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='digital.Part')),
            ],
        ),
        migrations.AddField(
            model_name='model',
            name='family',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='digital.PartFamily'),
        ),
    ]
