# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class SP3D_Part(models.Model):

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

class SP3D_Order(models.Model):

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

class SP3D_Client(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    code = models.CharField(max_length=10, default = '')
    address = models.CharField(max_length=200, default = '')
    activity = models.CharField(max_length=200, default = '')
    notes = models.CharField(max_length=200, default = '')

    def __str__(self):
        return "Client number " + str(self.id)

class SP3D_Contact(models.Model):

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


class SP3D_Iteration(models.Model):
    iteration_id = models.IntegerField(default=0)
    creation_date = models.DateTimeField('date published')
    part = models.ForeignKey(SP3D_Part)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Iteration number " + str(self.iteration_id)

class SP3D_Status_Eng(models.Model):
    name = models.CharField(max_length=200, default = '')
    def __str__(self):
        return "Status id is " + str(self.id)

class SP3D_Status_Ord(models.Model):
    name = models.CharField(max_length=200, default = '')
    def __str__(self):
        return "Status id is " + str(self.id)

class SP3D_Status_Eng_History(models.Model):
    part_id = models.IntegerField(default=0)
    date = models.DateTimeField('date published')
    id_status = models.IntegerField(default=1)
    id_creator = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Engineering Status Change Event id " + str(self.id)

class SP3D_Status_Ord_History(models.Model):
    id_order = models.IntegerField(default=0)
    date = models.DateTimeField('date published')
    id_status = models.IntegerField(default=0)
    id_creator = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "Order Status Change Event id " + str(self.id)

class SP3D_Print(models.Model):

    creation_date = models.DateTimeField('date published')
    id_part = models.IntegerField(default=0)
    id_cad = models.IntegerField(default=0)
    id_3mf = models.IntegerField(default=0)
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

class SP3D_Printer(models.Model):

    name = models.CharField(max_length=200, default = 'Printer001')
    location = models.CharField(max_length=200, default = 'SP3D Office Singapore')
    local_ip=models.CharField(max_length=200, default = '')
    z_offset=models.FloatField(default = 0.1)
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
    first_config = models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "CAD file Id " + str(self.id)

class SP3D_STL(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_cad = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "STL file Id " + str(self.id)

class SP3D_CAD2D(models.Model):

    creation_date = models.DateTimeField('date published')
    name = models.CharField(max_length=200, default = '')
    root_path = models.CharField(max_length=200, default = '/home/user01/SpareParts_Database/root/')
    file_path = models.CharField(max_length=200, default = '')
    id_cad = models.IntegerField(default=0)
    id_creator=models.IntegerField(default=0)
    notes=models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "2d drawing file Id " + str(self.id)

class SP3D_3MF(models.Model):
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

class SP3D_Bulk_Files(models.Model):

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

class SP3D_Po_Revision(models.Model):

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

class SP3D_Quote_Revision(models.Model):

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

class SP3D_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slack_name = models.TextField(max_length=200, default='')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        SP3D_Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.sp3d_profile.save()
