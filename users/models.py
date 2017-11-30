from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch.dispatcher import receiver
from datetime import datetime
from django.contrib.auth.models import Group
from sp3d.storage_backends import PrivateMediaStorage
from address.models import AddressField
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3StorageFile

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.usertype = Group.objects.get(name="STAFF")
        user.save(using=self._db)
        return user


def get_profile_pic_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/members/pictures/{1}'.format(instance.organisation.name, filename)

class CustomUser(AbstractBaseUser):
    type_choices = (
        ('STAFF', 'Staff User'),
        ('HUB', 'Hub User'),
        ('CLIENT', 'Client User'),
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    usertype = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=60, default='')
    last_name = models.CharField(max_length=100, default='')
    date_joined = models.DateTimeField(auto_now_add=True)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE, null=True)
    permissions = models.ManyToManyField('auth.Permission', blank=True)
    profile_pic = models.ImageField(storage = PrivateMediaStorage(bucket='sp3d-users'), upload_to = get_profile_pic_path, null=True, blank=True)
    profile_thumb = models.ImageField(storage = PrivateMediaStorage(bucket='sp3d-users'), upload_to = get_profile_pic_path, blank=True, null=True)
    title = models.CharField("Position Title", max_length=100, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['first_name', 'last_name']
    # class Meta:
    #     permissions = (
    #         ("add_part", "Can Add Part"),
    #     )

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        if self.is_admin:
            return True
        permission = self.permissions.filter(codename = perm)
        if permission:
            return True
        else:
            return False


    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return self.first_name + self.last_name

    def natural_key(self):
        return {"first_name":self.first_name, "last_name":self.last_name}

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_types(self):
        return self.type_choices

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        if self.usertype.name == 'STAFF':
            return True
        else:
            return False

    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.profile_pic:
            return
        # if the image is not a new image, but is already a S3 file, do not create thumbnail
        if isinstance(self.profile_pic.file, S3Boto3StorageFile):
            return

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (130, 130)

        DJANGO_TYPE = self.profile_pic.file.content_type

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        profile_pic = Image.open(StringIO(self.profile_pic.read()))

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        profile_pic.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        profile_pic.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.profile_pic.name)[-1],
                temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.profile_thumb.save(
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
        super(CustomUser, self).save(force_update=force_update)

@receiver(models.signals.pre_save, sender=CustomUser)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    In Dev Mode Deletes old profile pics from filesystem
    when corresponding `CustomUser` object is updated
    with new pics.
    """
    if settings.DEBUG:
        if not instance.pk:
            return False

        try:
            old_user = CustomUser.objects.get(pk=instance.pk)
            old_profile_pic = old_user.profile_pic
            old_profile_thumb = old_user.profile_thumb
        except CustomUser.DoesNotExist:
            return False

        new_profile_pic = instance.profile_pic
        if not old_profile_pic == new_profile_pic:
            old_profile_pic.delete(False)
            old_profile_thumb.delete(False)

class Industry(models.Model):
    name = models.CharField(max_length=100, default = '', unique = True)

    def __str__(self):
        return "%s" % (self.name,)

    def get_short_name(self):
        return self.name

    def natural_key(self):
        return self.name

def get_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/logo/{1}'.format(instance.name, filename)


class Organisation(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, default = '', unique = True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, default=1)
    logo = models.ImageField(storage = PrivateMediaStorage(bucket='sp3d-users'), upload_to = get_logo_path, null=True, blank=True)
    address = AddressField(blank=True, null=True)

    def __str__(self):
        return "%s" % (self.name,)

    def get_short_name(self):
        return self.name

    def natural_key(self):
        return self.name
