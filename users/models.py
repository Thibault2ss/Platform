from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.contrib.auth.models import Group
from sp3d.storage_backends import PrivateMediaStorage
from address.models import AddressField

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
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    date_joined = models.DateTimeField(auto_now_add=True)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

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
        # Simplest possible answer: All admins are staff
        # return self.is_admin

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
