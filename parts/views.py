# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import SP3D_Part, SP3D_Print, SP3D_Printer, SP3D_Image, SP3D_CAD, SP3D_AMF, SP3D_CONFIG, SP3D_Oem
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
LOCAL_APP = "http://localhost:5000"

@login_required
def index(request, error=""):
    print "TESTTTTT: %s"%error
    latest_part_list = SP3D_Part.objects.order_by('-creation_date')
    users = User.objects.all()
    oems=SP3D_Oem.objects.all()
    oem_list = SP3D_Oem.objects.all()
    context = {
        'latest_part_list': latest_part_list,
        'users':users,
        'oems':oems,
        'error':error,
        'oem_list':oem_list,
    }
    print "COOKIES"
    print request.COOKIES
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
    oem_list = SP3D_Oem.objects.all()
    users = User.objects.all()
    context = {
        'part': part,
        'image_list':image_list,
        'cad_list':cad_list,
        'amf_list':amf_list,
        'users':users,
        'config_list':config_list,
        'oem_list':oem_list,

    }
    return render(request, 'parts/part-detail.html', context)

def model_to_dict(model):
    model=model.__dict__
    if '_state' in model:
        # del model['_state']
        model['_state']=str(model['_state'])
    if 'creation_date'in model:
        model['creation_date']=str(model['creation_date'])
        # del model['creation_date']
    return model


@login_required
def checkout_part(request,id_part):
    part = SP3D_Part.objects.get(id=id_part)
    part=model_to_dict(part)

    amf_list = SP3D_AMF.objects.filter(id_part=id_part)
    cad_list = SP3D_CAD.objects.filter(id_part=id_part)
    config_list = SP3D_CONFIG.objects.filter(id_part=id_part)
    # transform these django objects into readable dictionnaries to send in a POST request
    data={}
    for item in amf_list:
        item=model_to_dict(item)
        data["amf-%s"%item["id"]] = [item]
        print "done0"
    for item in cad_list:
        item=model_to_dict(item)
        data["cad-%s"%item["id"]] = [item]
        print "done1"
    for item in config_list:
        item=model_to_dict(item)
        data["config-%s"%item["id"]] = [item]
        print "done2"

    # load all the files in these arrays:
    files=[]
    for key in data:
         path=data[key][0]["root_path"]+data[key][0]["file_path"]
         files.append((key,(data[key][0]["name"],open(path,'rb'))))

    ip=get_client_ip(request)
    # only now, should we add the part and the token to the data

    data.update({'part':"%s"%part,'token':TOKEN_FLASK, 'userid':request.user.id, 'username':request.user.username})

    print "DATA"
    print data
    response=requests.post('http://' + ip + ':5000/create-working-dir',data=data, files=files, verify=True)

    return HttpResponseRedirect(LOCAL_APP + "/parts/part-detail/%s"%id_part)


@csrf_exempt
def push(request,id_part):
    if request.method == 'POST':
        token=request.POST.get("token")
        print "TOKEN %s"%token

        userid = request.POST.get('userid')
        username = request.POST.get('username')
        print "USERID %s"%userid
        print "USERNAME %s"%username
        files=request.FILES
        print "FILES RECEIVED ARE: %s"%files

        try:
            for key in files:
                if key.startswith("cad"):
                    error=upload_cad(files[key], id_part, int(userid))
                    print "BEACON1: went to upload_cad with file %s"%files[key]
                    if error:raise ValueError(error)
                elif key.startswith("amf"):
                    error=upload_amf(files[key], id_part, int(userid))
                    if error:raise ValueError(error)
                elif key.startswith("config"):
                    error=upload_config(files[key], id_part, int(userid))
                    if error:raise ValueError(error)
        except ValueError as err:
            print (err)
            return HttpResponse(status=500)
        except:
            return HttpResponse(status=500)

    return HttpResponse()



@login_required
def upload_image(request,id_part):
    print "Redirection Upload Image ok"
    if request.method == 'POST':
        try:
            #  get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id
            part=SP3D_Part.objects.get(id=id_part)
            oem=SP3D_Oem.objects.get(id=part.id_oem)
            f=request.FILES['image']
            print "IMAGE: %s"%f
            print "filename: " + f.name
            print "file type: %s"%type(f)
            subpath="catalogue/oem-%s/part-id-%s/IMAGES/"%(oem.code,id_part)
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
def upload_cad_direct(request,id_part):
    print "Redirection Upload CAD ok"
    if request.method == 'POST':
        try:
            # get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id
            # process upload
            error=upload_cad(request.FILES['cad'], id_part, userid)
            if error: raise ValueError(error)
        except ValueError as err :
            print (err)
        except:
            print "CAD Uploading Failed1"
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

@login_required
def upload_amf_direct(request,id_part):
    print "Redirection Upload AMF ok"
    if request.method == 'POST':
        try:
            # get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id
            # process upload
            error=upload_amf(request.FILES['amf'], id_part, userid)
            if error: raise ValueError(error)
        except ValueError as err :
            print (err)
        except:
            print "AMF Uploading Failed1"
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

@login_required
def upload_config_direct(request,id_part):
    print "Redirection Upload Config ok"
    if request.method == 'POST':
        try:
            # get user name
            userid = None
            if request.user.is_authenticated():
                userid = request.user.id
            # process upload
            error=upload_config(request.FILES['config'], id_part, userid)
            if error: raise ValueError(error)
        except ValueError as err :
            print (err)
        except:
            print "CONFIG Uploading Failed1"
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)


# @csrf_exempt
@login_required
def add_part(request):
    userid = request.user.id
    user = User.objects.get(id=userid)
    print "USER id : %s"% userid
    print "USERNAME : %s"% user.username

    part_number=request.POST.get('part-number')
    oem_name=request.POST.get('oem')
    oem=SP3D_Oem.objects.get(name=oem_name)

    permission_list=request.POST.getlist('permissions')
    permissions=""
    for index in permission_list:
        permissions=permissions+"%s-"%index

    notes=request.POST.get('notes')
    cad=request.FILES.get('cad')
    is_oem=request.POST.get('is_oem')
    existing_part=SP3D_Part.objects.filter(part_number=part_number).count()

    try:
        if not (oem and part_number):
            raise ValueError("Error: no part number or corresponding oem")
        if not existing_part==0:
            raise ValueError("Error: part Number already rexists")

        # create new record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        new_part=SP3D_Part.objects.create(creation_date=creation_date,part_number=part_number, id_oem=oem.id,oem_name=oem.name,id_creator=user.id, permissions=permissions)


        new_part_path = DATABASE_DIRECTORY_TRANSITION + "catalogue/oem-%s/part-id-%s/"%(oem.code, new_part.id)
        sub_directories=["CAD/","AMF/","CONFIG/","GCODE/","IMAGES/","STL/"]

        # Check that folder exists
        if not os.path.exists(new_part_path):
            os.makedirs(new_part_path)
            for subpath in sub_directories:
                os.makedirs(new_part_path + subpath)
        else:
            raise ValueError("Error: part folder already exists")

        print "NEW PART ADDED TO DB: %s"%new_part.part_number

        # print "PARt:"
        # print part_number
        # print "OEM NAME: %s"%oem_name
        # print "PERMISSIONS: %s"%permissions
        # print "NOTES: %s"%notes
        # print "CAD: %s"%cad
        # print "IS OEM: %s"%is_oem
        # print "EXISTING PARTS: %s"%existing_part



        # try:
        #     cad_file=request.FILES['cad']
        #     is_oem_cad=request.POST.getlist('cad-oem-checkbox')
        #     oem=request.POST.get('oem')
        # permissions=request.POST.getlist('permissions')
        # notes=request.POST.get('notes')
        # part_number=request.POST.get('part-number')
        #
        #     print f.name
        #     subpath="catalogue/" + "oem-SP3D/" + "part-id-%s/"%id_part + "IMAGES/"
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
    except ValueError as err:
        print err
        return redirect('/parts', error=err)
    return HttpResponseRedirect('/parts/part-detail/%s'%new_part.id)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# upload new ca
def upload_cad(file,id_part,userid):
    error=None
    try:

        part=SP3D_Part.objects.get(id=id_part)
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)

        # kepep subpath separated from path, because used later
        subpath="catalogue/oem-%s/part-id-%s/CAD/"%(oem.code,id_part)
        path = DATABASE_DIRECTORY_TRANSITION + subpath

        # Check that folder exists
        if not os.path.exists(path):
            os.makedirs(path)

        newfile=path+"%s"%file
        filename, file_extension = os.path.splitext(newfile)
        #Check that file extension is .amf
        if not (file_extension.lower()==".sldasm" or file_extension.lower()==".slddrw" or file_extension.lower()==".sldprt"):
            raise ValueError('Wrong file extension, we need a .SLDASM or .SLDDRW or .SLDPRT')
        # Check that file with same name doesn't exist and iterate on name if it does
        if os.path.exists(newfile):
            i=1
            while os.path.exists("%s-iteration-%s%s"%(filename,i,file_extension)):
                i+=1
            newfile="%s-iteration-%s%s"%(filename,i,file_extension)

        # write in new file
        with open(newfile, 'wb+') as destination:
            for chunk in file.chunks():
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
        error=error + "%s"%err
    except:
        print "CAD Uploading Failed"
        error = error + "CAD Uploading failed"
    return error

# upload amf
def upload_amf(file,id_part,userid):
    error=None
    try:
        part=SP3D_Part.objects.get(id=id_part)
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)

        # kepep subpath separated from path, because used later
        subpath="catalogue/oem-%s/part-id-%s/AMF/"%(oem.code,id_part)
        path = DATABASE_DIRECTORY_TRANSITION + subpath

        # Check that folder exists
        if not os.path.exists(path):
            os.makedirs(path)

        newfile=path+"%s"%file
        filename, file_extension = os.path.splitext(newfile)
        #Check that file extension is .amf
        if not file_extension.lower()==".amf":
            raise ValueError('Wrong file extension, we need a .AMF')
        # Check that file with same name doesn't exist and iterate on name if it does
        if os.path.exists(newfile):
            i=1
            while os.path.exists("%s-iteration-%s%s"%(filename,i,file_extension)):
                i+=1
            newfile="%s-iteration-%s%s"%(filename,i,file_extension)

        # write in new file
        with open(newfile, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        print "New AMF uploaded at location " + newfile

        # create related record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        name=ntpath.basename(newfile)
        root_path=DATABASE_DIRECTORY_TRANSITION
        file_path=subpath+name
        print "USERID IS %s" % userid
        print "TYPE: %s"%type(userid)
        print "CREATION DATE IS %s" % creation_date
        print "TYPE: %s"%type(creation_date)
        print "NAME IS  %s" % name
        print "TYPE: %s"%type(name)
        print "ROOTPATH IS %s" % root_path
        print "TYPE: %s"%type(root_path)
        print "FILEPATH IS %s" % file_path
        print "TYPE: %s"%type(file_path)
        print "IDPART IS %s" % userid
        print "TYPE: %s"%type(userid)


        new_amf=SP3D_AMF.objects.create(creation_date=creation_date,name=name,root_path=root_path,file_path=file_path, id_part=id_part,id_creator=userid)
        print "AMF record added to sql database with id %s" % new_amf.id
    except ValueError as err :
        print (err)
        error= error +"%s"%err
    except:
        print "AMF Uploading Failed"
        error = error + "AMF Uploading failed"
    return error

# upload config
def upload_config(file,id_part,userid):
    error=None
    try:
        print "BALISE100"
        part=SP3D_Part.objects.get(id=id_part)
        print "BALISE101"
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)
        # kepep subpath separated from path, because used later
        subpath="catalogue/oem-%s/part-id-%s/CONFIG/"%(oem.code,id_part)
        path = DATABASE_DIRECTORY_TRANSITION + subpath
        print "BALISE1"
        # Check that folder exists
        if not os.path.exists(path):
            os.makedirs(path)
        print "BALISE2"
        newfile=path+"%s"%file
        filename, file_extension = os.path.splitext(newfile)
        #Check that file extension is .config
        if not file_extension.lower()==".ini":
            raise ValueError('Wrong file extension, we need a .INI')
        print "BALISE3"
        # Check that file with same name doesn't exist and iterate on name if it does
        if os.path.exists(newfile):
            i=1
            while os.path.exists("%s-iteration-%s%s"%(filename,i,file_extension)):
                i+=1
            newfile="%s-iteration-%s%s"%(filename,i,file_extension)

        # write in new file
        with open(newfile, 'wb+') as destination:
            for chunk in file.chunks():
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
        error=error +"%s"%err
    except:
        print "CONFIG Uploading Failed"
        error = error + "CONFIG Uploading failed"
    return error
