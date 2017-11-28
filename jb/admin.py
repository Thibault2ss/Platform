# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import Part, Material, Technology, CoupleTechnoMaterial, FinalCard


@admin.register(Material)
class Model_Admin(admin.ModelAdmin):
    fields = ['name','family', 'description']
    list_display = ('id', 'name','family')

@admin.register(Technology)
class Technology_Admin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ('id', 'name')

@admin.register(CoupleTechnoMaterial)
class CoupleTechnoMaterial_Admin(admin.ModelAdmin):
    fields = ['technology', 'material']
    list_display = ('id', 'technology', 'material')

@admin.register(FinalCard)
class FinalCard_Admin(admin.ModelAdmin):
    fields = ['techno_material', 'lead_time', 'unit_price', 'currency']
    list_display = ('id', 'techno_material', 'lead_time', 'unit_price', 'currency')
