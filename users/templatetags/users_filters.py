from django import template
from datetime import date, timedelta
from digital.models import PartImage, Part
from django.core import serializers
import json
import random
from copy import copy
import types

register = template.Library()

@register.simple_tag
def random_int():
    return random.randint(1, 5000)
