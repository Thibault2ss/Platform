# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class SP3D_Part(models.Model):

    creation_date = models.DateTimeField('date published')
    oem_number = models.CharField(max_length=200, default = '')
    part_number=models.CharField(max_length=200, default = '')
    id_oem=models.IntegerField(default=0)
    amf = models.IntegerField(default=0)
    config = models.IntegerField(default=0)
    gcode = models.IntegerField(default=0)
    id_creator = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Part number " + str(self.id)

class SP3D_Iteration(models.Model):
    iteration_id = models.IntegerField(default=0)
    creation_date = models.DateTimeField('date published')
    part = models.ForeignKey(SP3D_Part)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Iteration number " + str(self.iteration_id)

class SP3D_Print(models.Model):

    creation_date = models.DateTimeField('date published')
    id_part = models.IntegerField(default=0)
    id_printer=models.IntegerField(default=0)
    log_id = models.IntegerField(default=0)
    done = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Print number " + str(self.id)

class SP3D_Printer(models.Model):

    name = models.CharField(max_length=200, default = 'Printer001')
    location = models.CharField(max_length=200, default = 'SP3D Office Singapore')
    local_ip=models.CharField(max_length=200, default = '')
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
         return "Printer Number " + str(self.id)

class SP3D_Image(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Image Id " + str(self.id)

class SP3D_CAD(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    is_oem_cad=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "CAD file Id " + str(self.id)

class SP3D_AMF(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "AMF file Id " + str(self.id)

class SP3D_CONFIG(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "CONFIG file Id " + str(self.id)

class SP3D_Oem(models.Model):

    name = models.CharField(max_length=200, default = 'Spare Parts 3D')
    code=models.CharField(max_length=100, default = 'SP3D')
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "OEM id :" + str(self.id)
