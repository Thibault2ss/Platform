from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from users.models import CustomUser
from address.models import AddressField


class Hub(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, default = '')
    address = AddressField()

    def __str__(self):
        return "Adress id %s" % (self.id,)
