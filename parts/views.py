# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import SP3D_Part, SP3D_Print, SP3D_Printer

import os
import subprocess
import requests
import MySQLdb
import time

# Create your views here.
TOKEN_FLASK='123456789'
DATABASE_DIRECTORY = '/home/user01/SpareParts_Database/files/'
SLIC3R_DIRECTORY= '/home/user01/Slic3r/slic3r_dev/'

def index(request):
    latest_part_list = SP3D_Part.objects.order_by('-creation_date')
    context = {
        'latest_part_list': latest_part_list,
    }
    return render(request, 'parts/index.html', context)

def part_detail(request):

    return render(request, 'parts/part-detail.html')


def prints(request):
    latest_print_list = SP3D_Print.objects.order_by('-creation_date')
    context = {
        'latest_print_list': latest_print_list,
    }
    return render(request, 'parts/prints.html', context)

def download_amf(request, id):
    filename = DATABASE_DIRECTORY + "AMF/" + id + ".amf"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def download_config(request, id_config):
    filename = DATABASE_DIRECTORY + "CONFIG/" + id_config + ".ini"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def download_gcode(request, id_gcode):
    filename = DATABASE_DIRECTORY + "GCODE/" + id_gcode + ".gcode"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def slice_and_download(request,id):
    part = SP3D_Part.objects.get(id=id)
    amf_file = DATABASE_DIRECTORY + "AMF/" + part.amf + ".amf"
    ini_file = DATABASE_DIRECTORY + "CONFIG/" + part.config + ".ini"
    gcode_file = DATABASE_DIRECTORY + "GCODE/" + part.amf+ ".gcode"
    try:
        print subprocess.check_output(['perl',SLIC3R_DIRECTORY + 'slic3r.pl', '--load', ini_file, '-o', gcode_file, amf_file])
    except:
        print "An error occured while slicing..."
    filename = gcode_file
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    # if we want to remove gcode created in database after:
    # if os.path.isfile(gcode_file):
    #     os.remove(gcode_file)

    return response

def print_from_gcode(request, id_part, id_printer):
    part = SP3D_Part.objects.get(id=id_part)
    printer= SP3D_Printer.objects.get(id=id_printer)

    # add print to database log
    new_print=SP3D_Print.objects.create(creation_date=time.strftime('%Y-%m-%d %H:%M:%S'), id_printer=id_printer, id_part=id_part)

    amf_file = DATABASE_DIRECTORY + "AMF/" + part.amf + ".amf"
    ini_file = DATABASE_DIRECTORY + "CONFIG/" + part.config + ".ini"
    gcode_file = "/home/user01/SpareParts_Database/files/GCODE/" + part.amf + ".gcode"
    local_ip=printer.local_ip
    try:
        print subprocess.check_output(['perl',SLIC3R_DIRECTORY + 'slic3r.pl', '--load', ini_file, '-o', gcode_file, amf_file])
    except:
        print "An error occured while slicing..."
    filename = gcode_file
    payload = {'token': TOKEN_FLASK,'id_print':new_print.id}
    with open(filename) as f:
        requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def slice_and_print(request, id_part, id_printer):
    part = SP3D_Part.objects.get(id=id_part)
    printer= SP3D_Printer.objects.get(id=id_printer)

    # add print to database log
    new_print=SP3D_Print.objects.create(creation_date=time.strftime('%Y-%m-%d %H:%M:%S'), id_printer=id_printer, id_part=id_part)

    amf_file = DATABASE_DIRECTORY + "AMF/" + part.amf + ".amf"
    ini_file = DATABASE_DIRECTORY + "CONFIG/" + part.config + ".ini"
    gcode_file = DATABASE_DIRECTORY + "GCODE/" + part.amf + ".gcode"
    try:
        print subprocess.check_output(['perl',SLIC3R_DIRECTORY + 'slic3r.pl', '--load', ini_file, '-o', gcode_file, amf_file])
    except:
        print "An error occured while slicing..."
    filename = gcode_file
    payload = {'token': TOKEN_FLASK,'id_print':new_print.id}
    with open(filename) as f:
        requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response
