# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import PartFamily, Model, Part, PartImage, PartBulkFile, Grade, Environment, ClientPartStatus
# Register your models here.
@admin.register(PartFamily)
class PartFamily_Admin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name',)

@admin.register(Model)
class Model_Admin(admin.ModelAdmin):
    fields = ['name','reference','family']
    list_display = ('id', 'name','reference','family')

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

class PartImage_Inline(admin.TabularInline):
    model = PartImage
    fields = ['created_by','part','image']
    list_display = ('id','image','thumbnail', 'created_by')

class PartBulkFile_Inline(admin.TabularInline):
    model = PartBulkFile
    fields = ['created_by','part','file']
    list_display = ('id','file', 'created_by')

@admin.register(Part)
class Part_Admin(admin.ModelAdmin):
    # fields = ['created_by','organisation','model', 'reference', 'name']
    list_display = ('id', 'reference', 'name', 'model', 'created_by','organisation')
    fieldsets = (
        (None, {'fields': ('created_by','organisation','model', 'reference', 'name')}),
        ('Dimensions & Weight', {'fields': ('material','length', 'width', 'height','dimension_unit', 'weight','weight_unit')}),
        ('Other Characteristics', {'fields': ('color','grade', 'environment')}),
    )
    inlines=[PartImage_Inline, PartBulkFile_Inline]


# @admin.register(PartImage)
# class PartImage_Admin(admin.ModelAdmin):
#     fields = ['created_by','part','image']
#     list_display = ('id','image','thumbnail', 'created_by')
