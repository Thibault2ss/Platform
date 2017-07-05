# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class SP3D_Part(models.Model):

    creation_date = models.DateTimeField('date published')
    oem_number = models.CharField(max_length=200, default = '')
    amf = models.CharField(max_length=200, default = '')
    config = models.CharField(max_length=200, default = '')
    gcode = models.IntegerField(default=0)
    done = models.IntegerField(default=0)

    def __str__(self):
        return "Part number " + str(self.id)

class SP3D_Iteration(models.Model):
    iteration_id = models.IntegerField(default=0)
    creation_date = models.DateTimeField('date published')
    part = models.ForeignKey(SP3D_Part)

    def __str__(self):
        return "Iteration number " + str(self.iteration_id)

class SP3D_Print(models.Model):

    creation_date = models.DateTimeField('date published')
    id_part = models.IntegerField(default=0)
    id_printer=models.IntegerField(default=0)
    log_id = models.IntegerField(default=0)
    done = models.IntegerField(default=0)

    def __str__(self):
        return "Print number " + str(self.id)

class SP3D_Printer(models.Model):

    name = models.CharField(max_length=200, default = 'Printer001')
    location = models.CharField(max_length=200, default = 'SP3D Office Singapore')
    local_ip=models.CharField(max_length=200, default = '')

    def __str__(self):
         return "Printer Number " + str(self.id)
