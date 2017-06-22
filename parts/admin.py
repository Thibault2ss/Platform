# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import SP3D_Part, SP3D_Iteration
# Register your models here.

class SP3D_Part_Admin(admin.ModelAdmin):
    fields = ['part_id', 'creation_date']
    list_display = ('id', 'creation_date')
    

class SP3D_Iteration_Admin(admin.ModelAdmin):
    fields = ['iteration_id', 'creation_date', 'part']
    list_display = ('iteration_id', 'creation_date', 'part')
    
    
admin.site.register(SP3D_Part, SP3D_Part_Admin)
admin.site.register(SP3D_Iteration, SP3D_Iteration_Admin)
