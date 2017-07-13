# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import SP3D_Part, SP3D_Print, SP3D_Printer, SP3D_Image, SP3D_CAD, SP3D_AMF, SP3D_CONFIG
from django.contrib.auth.models import User
from .forms import UploadFileForm
from threading import Thread
from django.forms.models import model_to_dict

import os
import json
import subprocess
import requests
import MySQLdb
import time
import threading
import ntpath

# Create your views here.
TOKEN_FLASK='123456789'
DATABASE_DIRECTORY = '/home/user01/SpareParts_Database/files/'
DATABASE_DIRECTORY_TRANSITION = '/home/user01/SpareParts_Database/root/'
SLIC3R_DIRECTORY= '/home/user01/Slic3r/slic3r_dev/'

@login_required
def index(request):
    latest_part_list = SP3D_Part.objects.order_by('-creation_date')
    users = User.objects.all()
    context = {
        'latest_part_list': latest_part_list,
        'users':users,
    }
    return render(request, 'parts/index.html', context)
    # return render_to_response('parts/index.html', context, RequestContext(request))

# def part_detail(request):
#     image_url="/files/"+"IMAGES/test.png"
#     return render(request, 'parts/part-detail.html',{'image_url':image_url})

@login_required
def prints(request):
    latest_print_list = SP3D_Print.objects.order_by('-creation_date')
    context = {
        'latest_print_list': latest_print_list,
    }
    return render(request, 'parts/prints.html', context)

@login_required
def download_amf(request, id):
    filename = DATABASE_DIRECTORY + "AMF/" + id + ".amf"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_config(request, id_config):
    filename = DATABASE_DIRECTORY + "CONFIG/" + id_config + ".ini"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_gcode(request, id_gcode):
    filename = DATABASE_DIRECTORY + "GCODE/" + id_gcode + ".gcode"
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
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

@login_required
def send_to_printer(local_ip, payload, f):
    requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})

@login_required
def ajax_print(request):
    id_part=request.GET.get('part_id', None)
    id_printer=request.GET.get('printer_id',None)
    part = SP3D_Part.objects.get(id=id_part)
    printer= SP3D_Printer.objects.get(id=id_printer)

    # add print to database log
    new_print=SP3D_Print.objects.create(creation_date=time.strftime('%Y-%m-%d %H:%M:%S'), id_printer=id_printer, id_part=id_part)

    amf_file = DATABASE_DIRECTORY + "AMF/%s.amf"% part.amf
    ini_file = DATABASE_DIRECTORY + "CONFIG/%s.ini" %part.config
    gcode_file = "/home/user01/SpareParts_Database/files/GCODE/%s.gcode"%part.amf
    local_ip=printer.local_ip
    try:
        print subprocess.check_output(['perl',SLIC3R_DIRECTORY + 'slic3r.pl', '--load', ini_file, '-o', gcode_file, amf_file])
    except:
        print "An error occured while slicing..."
    filename = gcode_file
    payload = {'token': TOKEN_FLASK,'id_print':new_print.id}
    with open(filename) as f:
        requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})
        # TRYING TO use threading not to wait before sending response
        # t = Thread(target=send_to_printer, kwargs={'local_ip':local_ip, 'payload':payload, 'f':f})
        # t.setDaemon(False)
        # t.start()
    data = {
        'gcode_sent': "Gcode was sent to printer, dude"
    }
    return JsonResponse(data)

@login_required
def print_from_gcode(request, id_part, id_printer):
    part = SP3D_Part.objects.get(id=id_part)
    printer= SP3D_Printer.objects.get(id=id_printer)

    # add print to database log
    new_print=SP3D_Print.objects.create(creation_date=time.strftime('%Y-%m-%d %H:%M:%S'), id_printer=id_printer, id_part=id_part)

    amf_file = DATABASE_DIRECTORY + "AMF/%s.amf"% part.amf
    ini_file = DATABASE_DIRECTORY + "CONFIG/%s.ini" %part.config
    gcode_file = "/home/user01/SpareParts_Database/files/GCODE/%s.gcode"%part.amf
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

@login_required
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

@login_required
def part_detail(request,id_part):
    part = SP3D_Part.objects.get(id=id_part)
    image_list = SP3D_Image.objects.filter(id_part=id_part)
    cad_list=SP3D_CAD.objects.filter(id_part=id_part)
    amf_list=SP3D_AMF.objects.filter(id_part=id_part)
    config_list=SP3D_CONFIG.objects.filter(id_part=id_part)
    users = User.objects.all()
    context = {
        'part': part,
        'image_list':image_list,
        'cad_list':cad_list,
        'amf_list':amf_list,
        'users':users,
        'config_list':config_list,

    }
    return render(request, 'parts/part-detail.html', context)

@login_required
def go_local(request,id_part):
    part = SP3D_Part.objects.get(id=id_part)
    part=[part.__dict__]
    amf_list = SP3D_AMF.objects.filter(id_part=id_part)
    cad_list = SP3D_CAD.objects.filter(id_part=id_part)
    config_list = SP3D_CONFIG.objects.filter(id_part=id_part)
    # transform these django objects into readable dictionnaries to send in a POST request
    amf=[]
    cad=[]
    config=[]
    for item in amf_list:
        item=item.__dict__
        amf.append(item)
    for item in cad_list:
        item=item.__dict__
        cad.append(item)
    for item in config_list:
        item=item.__dict__
        config.append(item)

    # load all the files in these arrays:
    files=[]
    for item in amf:
        path=item["root_path"]+item["file_path"]
        files.append(('amf-%s'%item["id"],(item["name"],open(path,'rb'))))

    for item in cad:
        path=item["root_path"]+item["file_path"]
        files.append(('cad-%s'%item["id"],(item["name"],open(path,'rb'))))

    for item in config:
        path=item["root_path"]+item["file_path"]
        files.append(('config-%s'%item["id"],(item["name"],open(path,'rb'))))

    print "FILES"
    print files

    ip=get_client_ip(request)

    # files={
    #     'cad':[
    #             {
    #             'file':open('/home/user01/SpareParts_Database/root/catalogue/oem-test/part-id-292/CONFIG/401.ini','rb'),
    #             'data':"test1",
    #             },
    #             {
    #             'file': open('/home/user01/SpareParts_Database/root/catalogue/oem-test/part-id-292/CONFIG/401.ini','rb'),
    #             'data':"test",
    #             }
    #         ],
    #     'config':[],
    #     'upload_file': open('/home/user01/SpareParts_Database/root/catalogue/oem-test/part-id-292/CONFIG/401.ini','rb'),
    # }
    data = {
        'part':part,
        'amf':amf,
        'cad':cad,
        'config':config,
        'token':TOKEN_FLASK,
        # 'part': part,
        # 'image_list':image_list,
    }
    response=requests.post('http://' + ip + ':5000/create-working-dir',data=data,files = files, verify=True)

    return HttpResponseRedirect("http://localhost:5000/parts/part-detail/%s"%id_part)

@login_required
def upload_image(request,id_part):
    print "Redirection Upload Image ok"
    if request.method == 'POST':
        try:
            #  get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id
            f=request.FILES['image']
            print f.name
            subpath="catalogue/" + "oem-test/" + "part-id-%s/"%id_part + "IMAGES/"
            path = DATABASE_DIRECTORY_TRANSITION + subpath

            # Check that folder IMAGE exists
            if not os.path.exists(path):
                os.makedirs(path)

            newfile=path+f.name
            filename, file_extension = os.path.splitext(newfile)
            #Check that file extension is .amf
            if not (file_extension.lower()==".png" or file_extension.lower()==".jpg"):
                raise ValueError('Wrong file extension, we need a .png or .jpg file')
            # Check that file with same name doesn't exist and iterate on name if it does
            if os.path.exists(newfile):
                i=1
                while os.path.exists("%s-%s%s"%(filename,i,file_extension)):
                    i+=1
                newfile="%s-%s%s"%(filename,i,file_extension)

            # write in new file
            with open(newfile, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            print "New image uploaded at location " + newfile

            # create related record in database
            creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
            name=ntpath.basename(newfile)
            root_path=DATABASE_DIRECTORY_TRANSITION
            file_path=subpath+name
            new_image=SP3D_Image.objects.create(creation_date=creation_date,name=name,root_path=root_path,file_path=file_path, id_part=id_part,id_creator=userid)
            print "Image record added to sql database with id %s" % new_image.id
        except ValueError as err :
            print (err)
        else:
            print "Image Uploading Failed"
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

@login_required
def upload_cad(request,id_part):
    print "Redrection Upload CAD ok"
    if request.method == 'POST':
        try:
            # get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id

            f=request.FILES['cad']
            print f.name
            subpath="catalogue/" + "oem-test/" + "part-id-%s/"%id_part + "CAD/"
            path = DATABASE_DIRECTORY_TRANSITION + subpath

            # Check that folder CAD exists
            if not os.path.exists(path):
                os.makedirs(path)

            newfile=path+f.name
            filename, file_extension = os.path.splitext(newfile)
            #Check that file extension is .SLDASM or or .SLDDRW or .SLDPRT
            if not (file_extension.lower()==".sldasm" or file_extension.lower()==".slddrw" or file_extension.lower()==".sldprt"):
                raise ValueError('Wrong file extension, we need a .SLDASM or .SLDDRW or .SLDPRT')
            # Check that file with same name doesn't exist and iterate on name if it does
            if os.path.exists(newfile):
                i=1
                while os.path.exists("%s-%s%s"%(filename,i,file_extension)):
                    i+=1
                newfile="%s-%s%s"%(filename,i,file_extension)

            # write in new file
            with open(newfile, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            print "New CAD uploaded at location " + newfile

            # create related record in database
            creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
            name=ntpath.basename(newfile)
            root_path=DATABASE_DIRECTORY_TRANSITION
            file_path=subpath+name
            new_cad=SP3D_CAD.objects.create(creation_date=creation_date,name=name,root_path=root_path,file_path=file_path, id_part=id_part,id_creator=userid)
            print "CAD record added to sql database with id %s" % new_cad.id
        except ValueError as err :
            print (err)
        else:
            print "CAD Uploading Failed"
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

@login_required
def upload_amf(request,id_part):
    print "Redrection Upload AMF ok"
    if request.method == 'POST':
        try:
            # get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id

            f=request.FILES['amf']
            print f.name
            subpath="catalogue/" + "oem-test/" + "part-id-%s/"%id_part + "AMF/"
            path = DATABASE_DIRECTORY_TRANSITION + subpath

            # Check that folder CAD exists
            if not os.path.exists(path):
                os.makedirs(path)

            newfile=path+f.name
            filename, file_extension = os.path.splitext(newfile)
            #Check that file extension is .amf
            if not (file_extension.lower()==".amf"):
                raise ValueError('Wrong file extension, we need a .amf file')
            # Check that file with same name doesn't exist and iterate on name if it does
            if os.path.exists(newfile):
                i=1
                while os.path.exists("%s-%s%s"%(filename,i,file_extension)):
                    i+=1
                newfile="%s-%s%s"%(filename,i,file_extension)

            # write in new file
            with open(newfile, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            print "New AMF uploaded at location " + newfile

            # create related record in database
            creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
            name=ntpath.basename(newfile)
            root_path=DATABASE_DIRECTORY_TRANSITION
            file_path=subpath+name
            new_amf=SP3D_AMF.objects.create(creation_date=creation_date,name=name,root_path=root_path,file_path=file_path, id_part=id_part,id_creator=userid)
            print "AMF record added to sql database with id %s" % new_amf.id
        except ValueError as err :
            print(err)
        else:
            print "AMF Uploading Failed"
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

@login_required
def upload_config(request,id_part):
    print "Redrection Upload AMF ok"
    if request.method == 'POST':
        try:
            # get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id

            f=request.FILES['config']
            print f.name
            subpath="catalogue/" + "oem-test/" + "part-id-%s/"%id_part + "CONFIG/"
            path = DATABASE_DIRECTORY_TRANSITION + subpath

            # Check that folder CAD exists
            if not os.path.exists(path):
                os.makedirs(path)

            newfile=path+f.name
            filename, file_extension = os.path.splitext(newfile)
            #Check that file extension is .ini
            if not (file_extension.lower()==".ini"):
                raise ValueError('Wrong file extension, we need a .ini file')
            # Check that file with same name doesn't exist and iterate on name if it does
            if os.path.exists(newfile):
                i=1
                while os.path.exists("%s-%s%s"%(filename,i,file_extension)):
                    i+=1
                newfile="%s-%s%s"%(filename,i,file_extension)

            # write in new file
            with open(newfile, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            print "New CONFIG uploaded at location " + newfile

            # create related record in database
            creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
            name=ntpath.basename(newfile)
            root_path=DATABASE_DIRECTORY_TRANSITION
            file_path=subpath+name
            new_config=SP3D_CONFIG.objects.create(creation_date=creation_date,name=name,root_path=root_path,file_path=file_path, id_part=id_part,id_creator=userid)
            print "CONFIG record added to sql database with id %s" % new_config.id
        except ValueError as err :
            print (err)
        else:
            print "CONFIG Uploading Failed"
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)


# @csrf_exempt
@login_required
def add_part(request):
    part_number=request.POST.get('part-number')
    if part_number:
        print "PARt:"
        print part_number
        # try:
        #     cad_file=request.FILES['cad']
        #     is_oem_cad=request.POST.getlist('cad-oem-checkbox')
        #     oem=request.POST.get('oem')
        # permissions=request.POST.getlist('permissions')
        # notes=request.POST.get('notes')
        # part_number=request.POST.get('part-number')
        #
        #     print f.name
        #     subpath="catalogue/" + "oem-test/" + "part-id-%s/"%id_part + "IMAGES/"
        #     path = DATABASE_DIRECTORY_TRANSITION + subpath
        #
        #     # Check that folder IMAGE exists
        #     if not os.path.exists(path):
        #         os.makedirs(path)
        #
        #     newfile=path+f.name
        #     # Check that file with same name doesn't exist and iterate on name if it does
        #     if os.path.exists(newfile):
        #         filename, file_extension = os.path.splitext(newfile)
        #         i=1
        #         while os.path.exists("%s-%s%s"%(filename,i,file_extension)):
        #             i+=1
        #         newfile="%s-%s%s"%(filename,i,file_extension)
        #
        #     # write in new file
        #     with open(newfile, 'wb+') as destination:
        #         for chunk in f.chunks():
        #             destination.write(chunk)
        #     print "New image uploaded at location " + newfile
        #
        #     # create related record in database
        #     creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        #     name=ntpath.basename(newfile)
        #     root_path=DATABASE_DIRECTORY_TRANSITION
        #     file_path=subpath+name
        #     new_image=SP3D_Image.objects.create(creation_date=creation_date,name=name,root_path=root_path,file_path=file_path, id_part=id_part)
        #     print "Image record added to sql database with id %s" % new_image.id
        # except :
        #     print "Image Uploading Failed"
    return HttpResponseRedirect('/parts/')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
