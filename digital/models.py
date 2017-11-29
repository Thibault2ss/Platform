# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from sp3d.storage_backends import PrivateMediaStorage
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.core import serializers
# Create your models here.

class Characteristics(models.Model):
    COLOR_CHOICES = (("NA", "n/a"),("GREEN", "Green"),("WHITE", "White"),("BLACK", "Black"))
    FLAME_RETARDANT_CHOICES = (("NA", "n/a"),("HB", "HB"),("V0", "V0"),("V1", "V1"),("V2", "V2"))
    TEMPERATURE_UNIT_CHOICES = (("°C", "°C"),("°F", "°F"))
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default="NA")
    is_visual = models.BooleanField("Visual part", default=False, blank=True)
    is_transparent = models.BooleanField("Transparent", default=False, blank=True)
    is_elastic = models.BooleanField("Elastic", default=False, blank=True)
    is_water_resistant = models.BooleanField("Water Resistant", default=False, blank=True)
    is_chemical_resistant = models.BooleanField("Chemical Resistant", default=False, blank=True)
    is_flame_retardant = models.BooleanField("Flame Retardant", default=False, blank=True)
    is_food_grade = models.BooleanField("Food Grade", default=False, blank=True)
    flame_retardancy =  models.CharField(max_length=10, choices=FLAME_RETARDANT_CHOICES, default="NA")
    min_temp =  models.IntegerField(default=0)
    max_temp =  models.IntegerField(default=60)
    temp_unit = models.CharField(max_length=5, choices=TEMPERATURE_UNIT_CHOICES, default="°C")
    techno_material = models.ForeignKey('jb.CoupleTechnoMaterial', on_delete=models.CASCADE, null=True, blank=True, verbose_name = "Couple Techno-Material (Only if this card is not attached to a part already)")
    max_X = models.IntegerField("Maximum X (for Couple Techno-Mat only)", null=True, blank=True)
    max_Y = models.IntegerField("Maximum Y (for Couple Techno-Mat only)", null=True, blank=True)
    max_Z = models.IntegerField("Maximum Z (for Couple Techno-Mat only)", null=True, blank=True)
    def __str__(self):
        return "Characteristics card %s" % (self.id,)

    def natural_key(self):
        return {
            'id':self.id,
            'color':self.color,
            'is_visual':self.is_visual,
            'is_transparent':self.is_transparent,
            'is_elastic':self.is_elastic,
            'is_water_resistant':self.is_water_resistant,
            'is_chemical_resistant':self.is_chemical_resistant,
            'is_flame_retardant':self.is_flame_retardant,
            'is_food_grade':self.is_food_grade,
            'flame_retardancy':self.flame_retardancy,
            'min_temp':self.min_temp,
            'max_temp':self.max_temp,
            'temp_unit':self.temp_unit,
            }
    def get_retardant_choice(self, string):
        error = ''
        choices = [choice[0] for choice in self.FLAME_RETARDANT_CHOICES]
        if string.upper() in choices:
            return error, string.upper()
        else:
            error = 'Wrong Retardancy Level: %s. Instead, assigned HB'%string
            return error, "HB"

class PartType(models.Model):
    name = models.CharField(max_length=100, default = '')
    industry = models.ForeignKey('users.Industry', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'id':self.id,'name':self.name, 'industry':self.industry.name}
    class Meta:
        unique_together = (('name', 'industry'),)

class ApplianceFamily(models.Model):
    name = models.CharField(max_length=100, default = '', unique = True)
    industry = models.ForeignKey('users.Industry', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'name':self.name, 'industry':self.industry.name}


class Appliance(models.Model):
    name = models.CharField(max_length=200, default = '')
    reference = models.CharField(max_length=200, null = True, unique = True)
    organisation = models.ForeignKey('users.Organisation', on_delete=models.CASCADE, null=True)
    family = models.ForeignKey('ApplianceFamily', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'id':self.id, 'name':self.name, 'reference':self.reference, 'family':self.family.name}

    class Meta:
        unique_together = (('name', 'reference','family'),)

class Grade(models.Model):
    name = models.CharField(max_length=50, default = '')
    short_description = models.CharField(max_length=200, default = '')

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'name':self.name, 'short_description':self.short_description}

    class Meta:
        unique_together = (('name', 'short_description'),)

class ClientPartStatus(models.Model):
    name = models.CharField(max_length=50, default = '', unique=True)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'id':self.id,'name':self.name}

class PartEvent(models.Model):
    EVENT_TYPE_CHOICES = (
        ("INFO", "info"),
        ("REQUEST", "request"),
        ("STATUS_CHANGE", "status change"),
    )
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True)
    part = models.ForeignKey('Part', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default="INFO")
    status = models.ForeignKey('ClientPartStatus', on_delete=models.CASCADE, null=True)
    short_description = models.CharField(max_length=100, default = '')
    long_description = models.TextField(default = '')

    def __str__(self):
        return "%s" % (self.short_description,)

    def natural_key(self):
        return {'id':self.id, 'type':type, 'short_description':short_description}


class Environment(models.Model):
    name = models.CharField(max_length=50, default = '')
    short_description = models.CharField(max_length=200, default = '')

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'name':self.name, 'short_description':self.short_description}

    class Meta:
        unique_together = (('name', 'short_description'),)

class Part(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True)
    type = models.ForeignKey('PartType', on_delete=models.CASCADE, null=True, blank=True)
    characteristics = models.OneToOneField('Characteristics', on_delete=models.CASCADE, null=True)
    organisation = models.ForeignKey('users.Organisation', on_delete=models.CASCADE, null=True)
    appliance = models.ManyToManyField(Appliance, blank=True)
    reference = models.CharField(max_length=200, null = True, unique = True)
    name = models.CharField(max_length=200, default = '')
    material = models.ForeignKey('jb.Material', on_delete=models.CASCADE, null=True, blank=True)
    length = models.FloatField(max_length=10, null=True, blank=True)
    width = models.FloatField(max_length=10, null=True, blank=True)
    height = models.FloatField(max_length=10, null=True, blank=True)
    weight = models.FloatField(max_length=10, null=True, blank=True)
    dimension_unit = models.CharField(max_length=5, default="mm", choices=[('mm','mm'), ('inch','inch')])
    weight_unit = models.CharField(max_length=5, null=True, choices=[('gr','gr')], blank=True)
    status = models.ForeignKey('ClientPartStatus', on_delete=models.CASCADE, default=1)
    final_card = models.OneToOneField('jb.FinalCard', on_delete=models.CASCADE, null=True, blank=True)
    notify_status_to_client = models.BooleanField("Notify Part Status to Client", default=False, blank=True)

    def __str__(self):
        return "%s" % (self.name,)

def get_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/parts/{1}/images/{2}'.format(instance.part.organisation.name, instance.part.reference, filename)


class PartImage(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True)
    part = models.ForeignKey('Part', on_delete=models.CASCADE, null=True)
    image = models.ImageField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_image_path, blank=True)
    thumbnail = models.ImageField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_image_path, blank=True, null=True)

    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.image:
            return

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (200, 200)

        DJANGO_TYPE = self.image.file.content_type

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(StringIO(self.image.read()))

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.image.name)[-1],
                temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.thumbnail.save(
            '%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )

    def save(self, *args, **kwargs):
        self.create_thumbnail()
        force_update = False
        # If the instance already has been saved, it has an id and we set
        # force_update to True
        if self.id:
            force_update = True
        # Force an UPDATE SQL query if we're editing the image to avoid integrity exception
        super(PartImage, self).save(force_update=force_update)

    def __str__(self):
        return "%s" % (self.image.name,)

    def natural_key(self):
        return self.image.url

# delete image file on bucket on delete instance if not in  production:
@receiver(pre_delete, sender=PartImage)
def partimage_delete(sender, instance, **kwargs):
    if settings.DEBUG:
        # Pass false so FileField doesn't save the model.
        instance.image.delete(False)
        instance.thumbnail.delete(False)


def get_bulk_path(instance, filename):
    path = '{0}/parts/{1}/'.format(instance.part.organisation.name, instance.part.reference)
    if instance.type == "BULK":
        path = path + 'bulk_files/{0}'.format(filename)
    elif instance.type == "MATERIAL":
        path = path + 'bulk_files/{0}'.format(filename)
    elif instance.type == "2D":
        path = path + '2d_files/{0}'.format(filename)
    elif instance.type == "3D" or instance.type == "STL":
        path = path + '3d_files/{0}'.format(filename)
    else:
        path = path + '{0}'.format(filename)
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return path

class PartBulkFile(models.Model):
    FILE_TYPE_CHOICES = (
        ("BULK", "bulk files"),
        ("MATERIAL", "material files"),
        ("3D", "3d model"),
        ("2D", "2d drawings"),
        ("STL", "STL file"),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True)
    part = models.ForeignKey('Part', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default="BULK")
    file = models.FileField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_bulk_path, blank=True)
    data = models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "%s" % (self.file.name,)

    def getTypeChoices(self):
        return self.FILE_TYPE_CHOICES

    def natural_key(self):
        return {"name":self.file.name.rsplit("/",1)[1], "url":self.file.url, 'id':self.id, 'type':self.type, 'data':self.data}

# delete image file on bucket on delete instance if not in  production:
@receiver(pre_delete, sender=PartBulkFile)
def partbulkfile_delete(sender, instance, **kwargs):
    if settings.DEBUG:
        # Pass false so FileField doesn't save the model.
        instance.file.delete(False)
