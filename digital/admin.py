# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Characteristics, PartType, ApplianceFamily, Appliance, Part, PartImage, PartBulkFile, Grade, Environment, ClientPartStatus
# Register your models here.
@admin.register(PartType)
class PartType_Admin(admin.ModelAdmin):
    fields = ['name', 'industry']
    list_display = ('id','name','industry')

@admin.register(ApplianceFamily)
class ApplianceFamily_Admin(admin.ModelAdmin):
    fields = ['name', 'industry']
    list_display = ('id','name','industry')

@admin.register(Appliance)
class Appliance_Admin(admin.ModelAdmin):
    fields = ['name','organisation', 'reference','family']
    list_display = ('id', 'name', 'organisation', 'reference','family')

@admin.register(ClientPartStatus)
class ClientPartStatus_Admin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id', 'name')

@admin.register(Grade)
class Grade_Admin(admin.ModelAdmin):
    fields = ['name','short_description']
    list_display = ('id', 'name','short_description')

@admin.register(Environment)
class Environment_Admin(admin.ModelAdmin):
    fields = ['name','short_description']
    list_display = ('id', 'name','short_description')

@admin.register(Characteristics)
class Characteristics_Admin(admin.ModelAdmin):
    fields = ['color', 'is_visual']
    list_display = ('id','is_visual', 'color')

class PartImage_Inline(admin.TabularInline):
    model = PartImage
    fields = ['created_by','part','image']
    list_display = ('id','image','thumbnail', 'created_by')

class PartBulkFile_Inline(admin.TabularInline):
    model = PartBulkFile
    fields = ['created_by','part','file']
    list_display = ('id','file', 'created_by')

class Characteristics_Inline(admin.TabularInline):
    model = Characteristics
    fields = ['color', 'is_visual']
    list_display = ('id','is_visual', 'color')

@admin.register(Part)
class Part_Admin(admin.ModelAdmin):
    # fields = ['created_by','organisation','appliance', 'reference', 'name']
    list_display = ('id', 'reference', 'name', 'created_by','organisation')
    fieldsets = (
        (None, {'fields': ('created_by','organisation','appliance', 'type', 'reference', 'name')}),
        ('Dimensions & Weight', {'fields': ('material','length', 'width', 'height','dimension_unit', 'weight','weight_unit')}),
        ('Other Characteristics', {'fields': ('characteristics',)}),
    )
    inlines=[PartImage_Inline, PartBulkFile_Inline]


# @admin.register(PartImage)
# class PartImage_Admin(admin.ModelAdmin):
#     fields = ['created_by','part','image']
#     list_display = ('id','image','thumbnail', 'created_by')
