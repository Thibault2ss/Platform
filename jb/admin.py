# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from jb.models import Part
# Register your models here.
@admin.register(Part)
class Part_Admin(admin.ModelAdmin):
    fields = ['part_id', 'creation_date']
    list_display = ('id', 'creation_date')
