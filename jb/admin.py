# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import Part, Material


@admin.register(Material)
class Model_Admin(admin.ModelAdmin):
    fields = ['name','family']
    list_display = ('id', 'name','family')
