# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from sp3d.storage_backends import PrivateMediaStorage
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.core import serializers
# Create your models here.

class PartFamily(models.Model):
    name = models.CharField(max_length=100, default = '', unique = True)
    industry = models.ForeignKey('users.Industry', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'name':self.name, 'industry':self.industry}


class Model(models.Model):
    name = models.CharField(max_length=200, default = '')
    reference = models.CharField(max_length=200, null = True, unique = True)
    organisation = models.ForeignKey('users.Organisation', on_delete=models.CASCADE, null=True)
    family = models.ForeignKey('PartFamily', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'name':self.name, 'reference':self.reference, 'family':self.family.name}

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
    organisation = models.ForeignKey('users.Organisation', on_delete=models.CASCADE, null=True)
    model = models.ManyToManyField(Model, blank=True)
    reference = models.CharField(max_length=200, null = True, unique = True)
    name = models.CharField(max_length=200, default = '')
    material = models.ForeignKey('jb.Material', on_delete=models.CASCADE, null=True, blank=True)
    length = models.FloatField(max_length=10, null=True, blank=True)
    width = models.FloatField(max_length=10, null=True, blank=True)
    height = models.FloatField(max_length=10, null=True, blank=True)
    weight = models.FloatField(max_length=10, null=True, blank=True)
    dimension_unit = models.CharField(max_length=5, null=True, choices=[('mm','mm'), ('inch','inch')], blank=True)
    weight_unit = models.CharField(max_length=5, null=True, choices=[('gr','gr')], blank=True)
    color = models.CharField(max_length=20, default = '')
    grade = models.ManyToManyField(Grade)
    environment = models.ManyToManyField(Environment)
    status = models.ForeignKey('ClientPartStatus', on_delete=models.CASCADE, default=1)

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
    elif instance.type == "3D":
        path = path + '3d_files/{0}'.format(filename)
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return path

class PartBulkFile(models.Model):
    FILE_TYPE_CHOICES = (
        ("BULK", "bulk files"),
        ("MATERIAL", "material files"),
        ("3D", "3d model"),
        ("2D", "2d drawings"),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True)
    part = models.ForeignKey('Part', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default="BULK")
    file = models.FileField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_bulk_path, blank=True)

    def __str__(self):
        return "%s" % (self.file.name,)

    def getTypeChoices(self):
        return self.FILE_TYPE_CHOICES

    def natural_key(self):
        return {"name":self.file.name, "url":self.file.url, 'id':self.id, 'type':self.type}

# delete image file on bucket on delete instance if not in  production:
@receiver(pre_delete, sender=PartBulkFile)
def partbulkfile_delete(sender, instance, **kwargs):
    if settings.DEBUG:
        # Pass false so FileField doesn't save the model.
        instance.file.delete(False)
