# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

class Technology(models.Model):
    characteristics = models.OneToOneField('digital.Characteristics', on_delete=models.SET_NULL, null=True, blank=True, related_name = 'technology_characteristics')
    name = models.CharField("Short Technology Name",max_length=100, default = '', unique=True)
    description = models.TextField("Technology Description", default = '', blank=True)
    max_X = models.IntegerField("Maximum Part X (mm)", null=True)
    max_Y = models.IntegerField("Maximum Part Y (mm)", null=True)
    max_Z = models.IntegerField("Maximum Part Z (mm)", null=True)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'id':self.id,'name':self.name}

class Material(models.Model):
    characteristics = models.OneToOneField('digital.Characteristics', on_delete=models.SET_NULL, null=True, blank=True, related_name = 'material_characteristics')
    MATERIAL_FAMILY_CHOICES = [('metal','metal'), ('plastic','plastic')]
    family= models.CharField("Material Family", max_length=20, choices = MATERIAL_FAMILY_CHOICES, null=True)
    name = models.CharField("Short Material Name",max_length=20, default = '', unique=True)
    description = models.TextField("Material Description", default = '', blank=True)
    technology = models.ManyToManyField(Technology, through='CoupleTechnoMaterial')

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'id':self.id,'family':self.family, 'name':self.name}


class CoupleTechnoMaterial(models.Model):
    characteristics = models.OneToOneField('digital.Characteristics', on_delete=models.SET_NULL, null=True, blank=True, related_name = 'techno_material_characteristics')
    material= models.ForeignKey(Material, on_delete=models.CASCADE)
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)

    def __str__(self):
        return "%s + %s" % (self.technology.name, self.material.name,)

    def natural_key(self):
        return {'id':self.id, 'material':self.material.id, 'technology':self.technology.id}

    class Meta:
        unique_together = (('material', 'technology'),)

class FinalCard(models.Model):
    CURRENCY_CHOICE = [('USD','$US'), ('SGD','$SG'), ('EUR','€'), ('BTC','Bitcoin'), ('ETH','Euthereum')]
    part = models.OneToOneField('digital.Part', on_delete=models.CASCADE, null=True, blank=True, related_name = 'material_final_card')

    unit_price = models.FloatField("Unit Price",max_length=20, default = 0.0)
    currency = models.CharField("Currency", max_length=10, choices = CURRENCY_CHOICE, default="USD")
    lead_time = models.IntegerField("Lead time (days)", default=10)
    techno_material = models.ForeignKey(CoupleTechnoMaterial, on_delete=models.CASCADE, verbose_name = 'Couple Techno-Material', null=True, blank=True)

    def __str__(self):
        return "%s" % (self.id,)

    def natural_key(self):
        return {
            'id':self.id,
            'unit_price':self.unit_price,
            'currency':self.currency,
            'techno_material':self.techno_material.natural_key(),
            'lead_time':self.lead_time
            }
# save opposite one to one key
@receiver(post_save, sender=FinalCard)
def save_reverse_onetoones_finalcard(sender, created, instance, **kwargs):
    if instance.part:
        instance.part.final_card = instance
        instance.part.save()

class Part(models.Model):

    creation_date = models.DateTimeField('date published')
    oem_name = models.CharField(max_length=200, default = '')
    part_number=models.CharField(max_length=200, default = '')
    part_name = models.CharField(max_length=200, default = '')
    id_oem=models.IntegerField(default=0)
    oem_part_number = models.CharField(max_length=200, default = '')
    amf = models.IntegerField(default=0)
    config = models.IntegerField(default=0)
    gcode = models.IntegerField(default=0)
    id_creator = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')
    permissions=models.CharField(max_length=200, default = '')
    checked_out=models.IntegerField(default=0)
    checked_out_by = models.IntegerField(default=0)
    status_eng = models.IntegerField(default=1)

    def __str__(self):
        return "Part number " + str(self.id)

class Order(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    type = models.CharField(max_length=200, default = '')
    id_client = models.IntegerField(default=0)
    quote_number = models.CharField(max_length=200, default = '')
    po_number = models.CharField(max_length=200, default = '')
    due_date = models.DateTimeField('date published', null=True)
    assigned_to = models.IntegerField(default=0)
    root_path = models.CharField(max_length=200, default = '')
    parts = models.CharField(max_length=200, default = '{}')
    id_creator = models.IntegerField(default=0)
    id_contact = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')
    permissions=models.CharField(max_length=200, default = '')
    status_ord = models.IntegerField(default=1)
    completion_date = models.DateTimeField('date published', null=True)
    closed_by = models.IntegerField(default=0)

    def __str__(self):
        return "Order number " + str(self.id)

class Client(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    code = models.CharField(max_length=10, default = '')
    address = models.CharField(max_length=200, default = '')
    activity = models.CharField(max_length=200, default = '')
    notes = models.CharField(max_length=200, default = '')

    def __str__(self):
        return "Client number " + str(self.id)

class Contact(models.Model):

    creation_date = models.DateTimeField('date published')
    prefix = models.CharField(max_length=20, default = '')
    first_name = models.CharField(max_length=200, default = '')
    last_name = models.CharField(max_length=200, default = '')
    email = models.CharField(max_length=200, default = '')
    phone_perso = models.CharField(max_length=200, default = '')
    phone_office = models.CharField(max_length=200, default = '')
    position = models.CharField(max_length=200, default = '')
    id_client = models.IntegerField(default=0)
    notes = models.CharField(max_length=200, default = '')

    def __str__(self):
        return "Contact number " + str(self.id)

class Status_Eng(models.Model):
    name = models.CharField(max_length=200, default = '')
    def __str__(self):
        return "Status id is " + str(self.id)

class Status_Ord(models.Model):
    name = models.CharField(max_length=200, default = '')
    def __str__(self):
        return "Status id is " + str(self.id)

class Status_Eng_History(models.Model):
    part_id = models.IntegerField(default=0)
    date = models.DateTimeField('date published')
    id_status = models.IntegerField(default=1)
    id_creator = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Engineering Status Change Event id " + str(self.id)

class Status_Ord_History(models.Model):
    id_order = models.IntegerField(default=0)
    date = models.DateTimeField('date published')
    id_status = models.IntegerField(default=0)
    id_creator = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Order Status Change Event id " + str(self.id)

class Print(models.Model):

    creation_date = models.DateTimeField('date published')
    id_part = models.IntegerField(default=0)
    id_cad = models.IntegerField(default=0)
    id_3mf = models.IntegerField(default=0)
    id_bulk = models.IntegerField(default=0)
    id_printer=models.IntegerField(default=0)
    log_id = models.IntegerField(default=0)
    done = models.IntegerField(default=0)
    finished_date = models.DateTimeField('date published', null=True)
    completed = models.IntegerField(default=0)
    printing_time = models.IntegerField(null=True)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Print number " + str(self.id)

class Printer(models.Model):

    name = models.CharField(max_length=200, default = 'Printer001')
    location = models.CharField(max_length=200, default = 'SP3D Office Singapore')
    local_ip=models.CharField(max_length=200, default = '')
    z_offset=models.FloatField(default = 0.1)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
         return "Printer Number " + str(self.id)

class Image(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Image Id " + str(self.id)

class CAD(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    is_oem_cad=models.IntegerField(default=0)
    first_config = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "CAD file Id " + str(self.id)

class STL(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_cad = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "STL file Id " + str(self.id)

class CAD2D(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_cad = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "2d drawing file Id " + str(self.id)

class ThreeMF(models.Model):
    creation_date = models.DateTimeField('date published')
    id_cad = models.IntegerField(default=0)

    name_amf = models.CharField(max_length=200, default = '')
    name_config = models.CharField(max_length=200, default = '')
    name_configb = models.CharField(max_length=200, default = '')
    name_gcode = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    amf_path = models.CharField(max_length=200, default = '')
    config_path = models.CharField(max_length=200, default = '')
    configb_path = models.CharField(max_length=200, default = '')
    gcode_path = models.CharField(max_length=200, default = '')

    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "3MF Id " + str(self.id)

class Bulk_Files(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_order = models.IntegerField(default=0, null=True)
    id_creator=models.IntegerField(default=0, null=True)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Bulk File Id " + str(self.id)

class Po_Revision(models.Model):

    creation_date = models.DateTimeField('date published')
    id_client = models.CharField(max_length=200, default = '')
    id_order = models.IntegerField(default=0, null=True)
    client_contact = models.IntegerField(null=True)
    revision = models.IntegerField(default=0)
    po_number = models.CharField(max_length=200, default = '')
    parts = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_creator=models.IntegerField(default=0, null=True)
    notes=models.CharField(max_length=1000, default = '')
    value = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    currency = models.CharField(max_length=20, default = '')
    lead_time = models.IntegerField(default=0)

    def __str__(self):
        return "Po Revision Id " + str(self.id)

class Quote_Revision(models.Model):

    creation_date = models.DateTimeField('date published')
    id_client = models.CharField(max_length=200, default = '')
    id_order = models.IntegerField(default=0, null=True)
    client_contact = models.IntegerField(null=True)
    revision = models.IntegerField(default=0)
    quote_number = models.CharField(max_length=200, default = '')
    parts = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_creator=models.IntegerField(default=0, null=True)
    notes=models.CharField(max_length=1000, default = '')
    value = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    currency = models.CharField(max_length=20, default = '')
    lead_time = models.IntegerField(default=0)

    def __str__(self):
        return "Quote Revision Id " + str(self.id)

class AMF(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "AMF file Id " + str(self.id)

class CONFIG(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_part = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "CONFIG file Id " + str(self.id)

class Oem(models.Model):

    name = models.CharField(max_length=200, default = 'Spare Parts 3D')
    code=models.CharField(max_length=100, default = 'SP3D')
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "OEM id :" + str(self.id)
