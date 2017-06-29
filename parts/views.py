# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import SP3D_Part
import os
import subprocess
import requests
# Create your views here.

def index(request):
    latest_part_list = SP3D_Part.objects.order_by('id')
    context = {
        'latest_part_list': latest_part_list,
    }
    return render(request, 'parts/index.html', context)

def download_amf(request, id):
    filename = "/home/user01/SpareParts_Database/files/AMF/" + id + ".amf"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def download_config(request, id):
    filename = "/home/user01/SpareParts_Database/files/CONFIG/" + id + ".ini"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def slice_and_download(request,id):
    part = SP3D_Part.objects.get(id=id)
    amf_file = "/home/user01/SpareParts_Database/files/AMF/" + part.amf + ".amf"
    ini_file = "/home/user01/SpareParts_Database/files/CONFIG/" + part.config + ".ini"
    gcode_file = "/home/user01/SpareParts_Database/files/GCODE/" + part.amf + ".gcode"
    try:
        print subprocess.check_output(['perl','/home/user01/Slic3r/slic3r_dev/slic3r.pl', '--load', ini_file, '-o', gcode_file, amf_file])
    except:
        print "An error occured while slicing..."
    filename = gcode_file
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    if os.path.isfile(gcode_file): 
        os.remove(gcode_file)
        
    return response
    
def slice_and_print(request, id):
    part = SP3D_Part.objects.get(id=id)
    amf_file = "/home/user01/SpareParts_Database/files/AMF/" + part.amf + ".amf"
    ini_file = "/home/user01/SpareParts_Database/files/CONFIG/" + part.config + ".ini"
    gcode_file = "/home/user01/SpareParts_Database/files/GCODE/" + part.amf + ".gcode"
    try:
        print subprocess.check_output(['perl','/home/user01/Slic3r/slic3r_dev/slic3r.pl', '--load', ini_file, '-o', gcode_file, amf_file])
    except:
        print "An error occured while slicing..."
    filename = gcode_file
    payload = {'token', '123456789'}
    with open(filename) as f:
        requests.post('http://192.168.0.213:5000/print', data=payload, files={'gcode_file':f})
    if os.path.isfile(gcode_file): 
        os.remove(gcode_file)
    
    return None
