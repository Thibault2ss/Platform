from django import template
from datetime import date, timedelta
from digital.models import PartImage, Part
from django.core import serializers
import json


register = template.Library()

@register.filter(name='get_due_date_string')
def get_due_date_string(value):
    delta = value.date() - date.today()

    if delta.days == 0:
        return "Today!"
    elif delta.days < 1:
        return "%s %s ago!" % (abs(delta.days),
            ("day" if abs(delta.days) == 1 else "days"))
    elif delta.days == 1:
        return "Tomorrow"
    elif delta.days > 1:
        return "In %s days" % delta.days

@register.filter(name='seconds_to_duration')
def seconds_to_duration(value):
    hours = value//3600
    minutes = (value % 3600)//60
    print "MINUTE: %s"%minutes

    return "%s h %s m"%(hours, minutes)

@register.filter(name='created_recently')
def created_recently(value):
    delta = value.date() - date.today()
    if delta.days > -2:
        return "list-group-item-success"
    else:
        return ""

@register.filter(name='extension_gcode')
def extension_gcode(value):
    extension = value.rsplit(".",1)[1].lower()
    if extension == "gcode":
        return True
    else:
        return False

@register.filter(name='model_to_dict')
def model_to_dict(instance):
    return serializers.serialize("json", [instance],  use_natural_foreign_keys=True)[1:-1]

@register.filter(name='url_list')
def url_list(image_instance_list):
    url_list=[]
    for image in image_instance_list:
        if image.image.url:
            url_list.append(image.image.url)
    return json.dumps(url_list)

@register.filter(name='dict_list')
def dict_list(file_instance_list):
    dict_list=[]
    for file in file_instance_list:
        dict_list.append({"id":file.id,"type":file.type, "url":file.file.url,"name":(file.file.name).rsplit("/",1)[1]})
    return json.dumps(dict_list)
