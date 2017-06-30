# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class SP3D_Part(models.Model):
    
    creation_date = models.DateTimeField('date published')
    oem_number = models.CharField(max_length=200, default = '')
    amf = models.CharField(max_length=200, default = '')
    config = models.CharField(max_length=200, default = '')
    done = models.IntegerField(default=0)
    
    def __str__(self):
        return "Part number " + str(self.oem_number)

class SP3D_Iteration(models.Model):
    iteration_id = models.IntegerField(default=0)
    creation_date = models.DateTimeField('date published')
    part = models.ForeignKey(SP3D_Part)
    
    def __str__(self):
        return "Iteration number " + str(self.iteration_id)

class SP3D_Print(models.Model):
    
    creation_date = models.DateTimeField('date published')
    printer_id=models.IntegerField(default=0)
    printer_name=models.CharField(max_length=200, default = 'Printer001')
    oem_number = models.CharField(max_length=200, default = '')
    amf = models.CharField(max_length=200, default = '')
    log_id = models.IntegerField(default=0)
    done = models.IntegerField(default=0)
    
    def __str__(self):
        return "Part number " + str(self.oem_number)
