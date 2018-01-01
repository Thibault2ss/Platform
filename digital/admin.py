# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Characteristics, PartType, ApplianceFamily, Appliance, Part, PartImage, PartBulkFile, Grade, Environment, ClientPartStatus, FinancialCard
from jb.models import FinalCard

class FinalCard_Inline(admin.TabularInline):
    model = FinalCard
    fields = ['techno_material', 'lead_time','unit_price', 'currency']
    list_display = ('id','techno_material', 'lead_time','unit_price', 'currency')

class Characteristics_Inline(admin.TabularInline):
    model = Characteristics
    fields = ['is_visual', 'is_transparent','is_rubbery', 'is_water_resistant', 'is_chemical_resistant','is_flame_retardant','flame_retardancy', 'is_food_grade','min_temp', 'max_temp', 'temp_unit', 'color']
    list_display = ('id','is_visual', 'is_transparent','is_rubbery','is_water_resistant', 'is_chemical_resistant','is_flame_retardant','is_food_grade','flame_retardancy')

class FinancialCard_Inline(admin.TabularInline):
    model = FinancialCard
    fields = ['stock', 'selling_price','selling_volumes']
    list_display = ('id','stock', 'selling_price','selling_volumes')

# Register your models here.
@admin.register(PartType)
class PartType_Admin(admin.ModelAdmin):
    fields = ['name', 'appliance_family']
    list_display = ('id','name','appliance_family')
    inlines=[Characteristics_Inline]
    search_fields = ['name', 'appliance_family__name']

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
    # fields = ['color', 'is_visual', 'is_transparent','is_rubbery', 'is_water_resistant', 'is_chemical_resistant','is_flame_retardant','is_food_grade','flame_retardancy','min_temp', 'max_temp', 'temp_unit','techno_material']
    list_display = ('id','is_visual', 'is_transparent','is_rubbery','is_water_resistant', 'is_chemical_resistant','is_flame_retardant','is_food_grade','flame_retardancy')
    fieldsets = (
        (None, {'fields': ('is_visual', 'is_transparent','is_rubbery', 'is_water_resistant', 'is_chemical_resistant','is_flame_retardant','flame_retardancy', 'is_food_grade','min_temp', 'max_temp', 'temp_unit', 'color')}),
        # ('FILL ONLY IF CHARACTERISTIC CARD IS LINKED TO A COUPLE TECHNO-MATERIAL', {'fields': ('techno_material',)}),
    )

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
    # fields = ['created_by','organisation','appliance', 'reference', 'name']
    list_display = ('id', 'reference', 'name', 'created_by','organisation')
    fieldsets = (
        (None, {'fields': ('created_by','organisation','appliance', 'type', 'reference', 'name')}),
        ('Dimensions & Weight', {'fields': ('material','length', 'width', 'height','dimension_unit', 'weight','weight_unit')}),
        ('Final Card', {'fields': ('final_card',)}),
    )
    inlines=[PartImage_Inline, PartBulkFile_Inline, Characteristics_Inline, FinancialCard_Inline, FinalCard_Inline]


# @admin.register(PartImage)
# class PartImage_Admin(admin.ModelAdmin):
#     fields = ['created_by','part','image']
#     list_display = ('id','image','thumbnail', 'created_by')
