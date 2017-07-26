# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import SP3D_Part, SP3D_Print, SP3D_Printer, SP3D_Image, SP3D_CAD, SP3D_AMF, SP3D_CONFIG, SP3D_Oem, SP3D_3MF, SP3D_STL
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
import ast

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
def delete_image(request):
    try:
        image_id = request.GET.get('image_id', None)
        if not image_id : raise ValueError('image_id not found in ajax request')
        img = SP3D_Image.objects.get(id=image_id)
        if not img : raise ValueError('image_id not found in mysql records')
        os.remove(img.root_path + img.file_path)
        print "Image file deleted: %s"%img.name
        img.delete()
        print "Image record deleted"
        data = {
            "result": "Image was deleted successfully"
        }
    except ValueError as err:
        data = {
            "result": err
        }
    except:
        data = {
            "result": "Problem happened during image deletion, check records"
        }
    return JsonResponse(data)


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
    cad_list=SP3D_CAD.objects.filter(id_part=id_part).order_by('creation_date')
    users = User.objects.all()
    permissions = map(int, filter( None , part.permissions.split("-")))
    if request.user.is_authenticated():
        username = request.user.username
        userid = request.user.id
    if userid in permissions:
        permission = 1
    else:
        permission = 0

    id_cad_list=[]
    _3mf_per_cad={} #dictionnary of 3mf like:{'idcad' : _3mf_object, ...}
    for cad in cad_list:
        _3mf_list = SP3D_3MF.objects.filter(id_cad=cad.id).order_by('creation_date')
        _3mf_per_cad[cad.id]=[]
        for _3mf in _3mf_list:
            _3mf_per_cad[cad.id].append(_3mf)


    amf_list=SP3D_AMF.objects.filter(id_part=id_part)
    config_list=SP3D_CONFIG.objects.filter(id_part=id_part)

    oem_list = SP3D_Oem.objects.all()

    print "tmf per cad: %s"%_3mf_per_cad
    context = {
        'part': part,
        'image_list':image_list,
        'cad_list':cad_list,
        'amf_list':amf_list,
        'users':users,
        'config_list':config_list,
        'oem_list':oem_list,
        'tmf_per_cad':_3mf_per_cad,
        'permission':permission,

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

@login_required
def checkout_part1(request,id_part):
    part = SP3D_Part.objects.get(id=id_part)
    part=model_to_dict(part)
    cad_list = SP3D_CAD.objects.filter(id_part=id_part)
    configb0 = SP3D_3MF.objects.get(id=0)
    permissions = part.permissions.split('-')
    checked_out = part.checked_out

    if request.user.is_authenticated():
        username = request.user.username
        userid = request.user.id

    if checked_out:
        return HttpResponseRedirect(LOCAL_APP + "/parts/part-detail/%s"%id_part)


    cad_id_list=[]
    for cad in cad_list:
        cad_id_list = cad_id_list + [cad.id]
    _3mf_list = SP3D_3MF.objects.filter(id_cad__in=cad_id_list)


    # transform these django objects into readable dictionnaries to send in a POST request
    data={}
    for item in cad_list:
        item=model_to_dict(item)
        data["cad-%s"%item["id"]] = [item]
        print "done0"
    for item in _3mf_list:
        item=model_to_dict(item)
        data["_3mf-%s"%item["id"]] = [item]
        print "done1"

    # load all the files in these arrays:
    files=[]
    for key in data:
        if key.startswith("cad"):
            path=data[key][0]["root_path"]+data[key][0]["file_path"]
            files.append((key,(data[key][0]["name"],open(path,'rb'))))
        if key.startswith("_3mf"):
            path_amf=data[key][0]["root_path"]+data[key][0]["amf_path"]
            path_config=data[key][0]["root_path"]+data[key][0]["config_path"]
            path_configb=data[key][0]["root_path"]+data[key][0]["configb_path"]
            files.append((key+"-amf",(data[key][0]["name_amf"],open(path_amf,'rb'))))
            files.append((key+"-config",(data[key][0]["name_config"],open(path_config,'rb'))))
            files.append((key+"-configb",(data[key][0]["name_configb"],open(path_configb,'rb'))))

    ip=get_client_ip(request)
    # only now, should we add the part and the token to the data

    data.update({'part':"%s"%part,'token':TOKEN_FLASK, 'userid':request.user.id, 'username':request.user.username})

    print "DATA"
    print data
    response=requests.post('http://' + ip + ':5000/create-working-dir1',data=data, files=files, verify=True)
    if response.status_code==302:
        return HttpResponseRedirect("/parts/part-detail/%s"%id_part)

    return HttpResponseRedirect(LOCAL_APP + "/parts/part-detail/%s"%id_part)

@login_required
def checkout_cad(request, id_part, id_cad):
    part = SP3D_Part.objects.get(id=id_part)
    # part=model_to_dict(part)
    print "id part : %s"%id_part
    print "part : %s"%part
    print "part checkout: %s"%part.checked_out
    # we look for a cad list, even though only one will show up, because of how it was built before
    cad_list = SP3D_CAD.objects.filter(id=id_cad)
    stl_list = SP3D_STL.objects.filter(id_cad=id_cad)
    configb0 = SP3D_3MF.objects.get(id=cad_list[0].first_config)
    permissions = part.permissions.split('-')
    checked_out = part.checked_out


    if request.user.is_authenticated():
        username = request.user.username
        userid = request.user.id

    if checked_out:
        print "PART IS ALREADY CHECKED OUT"
        return HttpResponseRedirect(LOCAL_APP + "/parts/part-detail/%s"%id_part)

    cad_id_list=[]
    for cad in cad_list:
        cad_id_list = cad_id_list + [cad.id]
    _3mf_list = SP3D_3MF.objects.filter(id_cad__in=cad_id_list)


    # transform these django objects into readable dictionnaries to send in a POST request
    data={}
    for item in cad_list:
        item=model_to_dict(item)
        data["cad-%s"%item["id"]] = [item]
        print "done0"
    for item in stl_list:
        item=model_to_dict(item)
        data["stl-%s"%item["id"]] = [item]
        print "done01"
    for item in _3mf_list:
        item=model_to_dict(item)
        data["_3mf-%s"%item["id"]] = [item]
        print "done1"

    # load all the files in these arrays:
    files=[]
    for key in data:
        if key.startswith("cad"):
            path=data[key][0]["root_path"]+data[key][0]["file_path"]
            files.append((key,(data[key][0]["name"],open(path,'rb'))))
        if key.startswith("stl"):
            path=data[key][0]["root_path"]+data[key][0]["file_path"]
            files.append((key,(data[key][0]["name"],open(path,'rb'))))
        if key.startswith("_3mf"):
            path_amf=data[key][0]["root_path"]+data[key][0]["amf_path"]
            path_config=data[key][0]["root_path"]+data[key][0]["config_path"]
            path_configb=data[key][0]["root_path"]+data[key][0]["configb_path"]
            path_gcode=data[key][0]["root_path"]+data[key][0]["gcode_path"]
            files.append((key+"-amf",(data[key][0]["name_amf"],open(path_amf,'rb'))))
            files.append((key+"-config",(data[key][0]["name_config"],open(path_config,'rb'))))
            files.append((key+"-configb",(data[key][0]["name_configb"],open(path_configb,'rb'))))
            files.append((key+"-gcode",(data[key][0]["name_gcode"],open(path_gcode,'rb'))))

    # also add the template config bundle configb-0.ini
    path_configb0 = configb0.root_path + configb0.configb_path
    files.append(("configb-0",("configb-0.ini", open(path_configb0, 'rb'))))

    ip=get_client_ip(request)

    # only now, should we add the part and the token to the data

    data.update({'part':"%s"%model_to_dict(part),'token':TOKEN_FLASK, 'userid':request.user.id, 'username':request.user.username, 'cad_id':cad_id_list[0]})

    print "DATA"
    print data
    response=requests.post('http://' + ip + ':5000/create-working-dir2',data=data, files=files, verify=True)
    if response.status_code==306:
        return HttpResponseRedirect(LOCAL_APP + "/local/existing")
    if not response.status_code==200:
        return HttpResponseRedirect("/parts/part-detail/%s"%id_part)
        
    # search the part again, and check it out. Leave it searched again, otherwise error
    part = SP3D_Part.objects.get(id=id_part)
    part.checked_out = 1
    part.checked_out_by = int(userid)
    part.save()
    return HttpResponseRedirect(LOCAL_APP + "/local/%s"%id_part)

@csrf_exempt
def push(request,id_part):
    if request.method == 'POST':
        token=request.POST.get("token")

        userid = request.POST.get('userid')
        username = request.POST.get('username')
        files=request.FILES
        print "FILES RECEIVED ARE: %s"%files
        print "DATA RECEIVED IS: %s"%request.POST
        print "DEBUG1: %s"%request.POST.get('cad_correspondance')
        print "DEBUG1 TYPE: %s"%type(request.POST.get('cad_correspondance'))

        old_cad_correspondance=ast.literal_eval(request.POST.get('cad_correspondance'))  #list of tuples like: ((cad_name , old_cad_id),...)
        print 'DEBUG 1000'
        new_cad_correspondance = [] #list of tuples like: ((cad_name , new_id_cad),...)
        _3mf_cad_correspondance = [] #list of tuples like: ((id_3mf , id_cad),...)
        oldid_newid=[]
        print 'DEBUG 1001'
        print type(_3mf_cad_correspondance)
        try:
            for key in request.POST:
                print "REQUEST ISS: %s"%request.POST
                if key.startswith("cad_3mf"):
                    print 'DEBUG 1018: %s'%key
                    print 'DEBUG 1019: %s'%key.rsplit('_',1)[1]
                    print 'DEBUG 1019 TYPE: %s'%type(key.rsplit('_',1)[1])
                    print 'DEBUG 1019b: %s'%request.POST.get(key)
                    print 'DEBUG 1019b TYPE: %s'%type(request.POST.get(key))
                    print "DEBUG 1050 TYPE: %s"%type(_3mf_cad_correspondance)

                    _3mf_cad_correspondance.append((key.rsplit('_',1)[1] , request.POST.get(key)))
                    print 'DEBUG 10199: %s'%_3mf_cad_correspondance
                    print 'DEBUG 10199: %s'%type(_3mf_cad_correspondance)
            _3mf_cad_correspondance=dict(_3mf_cad_correspondance)
            print 'DEBUG 1020: %s' % _3mf_cad_correspondance
            print 'DEBUG 1020 TYPE: %s' %type(_3mf_cad_correspondance)

            for key in files:
                if key.startswith("cad"):
                    error,new_cad_id = upload_cad(files[key], id_part, int(userid))
                    print "DEBUG99:"
                    new_cad_correspondance.append(("%s"%files[key],new_cad_id))
                    print "DEBUG100:"
                    print old_cad_correspondance
                    old_cad_correspondance=dict([old_cad_correspondance])
                    print type(old_cad_correspondance)
                    print "%s"%files[key]
                    old_cad_id = old_cad_correspondance["%s"%files[key]]
                    print "DEBUG101: %s"%old_cad_id
                    oldid_newid.append((old_cad_id,new_cad_id))
                    print "DEBUG101b: %s"%oldid_newid
                    if error:raise ValueError(error)
            oldid_newid=dict(oldid_newid)
            _3mf_finished=[]
            for key in files:
                print "DEBUG102:"
                if (key.startswith("amf") or key.startswith("config") or key.startswith("configb")):
                    print "DEBUG103:"
                    filename = "%s"%files[key]
                    _3mf_id = filename.rsplit('.',1)[0].split('-',1)[1]
                    print "DEBUG104:"
                    print _3mf_cad_correspondance
                    print _3mf_id
                    old_cad_id=_3mf_cad_correspondance[_3mf_id]
                    print "DEBUG105:"
                    if not _3mf_id in _3mf_finished:
                        print "DEBUG106:"
                        print "DEBUG106b: %s"%oldid_newid
                        for key1 in oldid_newid:
                            print "DEBUG107:%s" % key1
                            print "DEBUG107b:%s" % old_cad_id
                            if key1 == old_cad_id:
                                print "DEBUG108:"
                                final_cad_id = oldid_newid[key1]
                                print "DEBUG109:"
                            else:
                                print "DEBUG110:"
                                final_cad_id = old_cad_id
                                print "DEBUG111:"
                        amf_file, config_file, configb_file = None, None, None
                        print "DEBUG112:"
                        for key1 in files:
                            if (("%s"%files[key1]).startswith("amf") or ("%s"%files[key1]).startswith("config")):
                                print "DEBUG113:"
                                print ("%s"%files[key1])
                                print (("%s"%files[key1]).rsplit('.',1)[0].split('-')[1])
                                if (("%s"%files[key1]).rsplit('.',1)[0].split('-')[1]) == _3mf_id and (("%s"%files[key1]).rsplit('.',1)[0].split('-')[0]=="amf"):
                                    print "DEBUG114:"
                                    amf_file = files[key1]
                                elif (("%s"%files[key1]).rsplit('.',1)[0].split('-')[1]) == _3mf_id and (("%s"%files[key1]).rsplit('.',1)[0].split('-')[0]=="config"):
                                    print "DEBUG115:"
                                    config_file = files[key1]
                                elif (("%s"%files[key1]).rsplit('.',1)[0].split('-')[1]) == _3mf_id and (("%s"%files[key1]).rsplit('.',1)[0].split('-')[0]=="configb"):
                                    print "DEBUG116:"
                                    configb_file = files[key1]
                        if not (amf_file and config_file and configb_file):
                            print "DEBUG117:"
                            raise ValueError("Not All three files are there: amf, config and configb")
                        print "DEBUG118:"
                        error=upload_3mf(amf_file, config_file, configb_file, final_cad_id, int(userid))
                    print "DEBUG119:"
                    if error:raise ValueError(error)
                    _3mf_finished.append(_3mf_id)
        except ValueError as err:
            print "DEBUG122:"
            print (err)
            return HttpResponse(status=500)
        except:
            print "DEBUG123:"
            return HttpResponse(status=500)
        print "DEBUG124:"
    return HttpResponse()

@csrf_exempt
def push_cad(request , id_part):
    if request.method == 'POST':
        token=request.POST.get("token")
        part = SP3D_Part.objects.get(id=id_part)
        userid = request.POST.get('userid')
        username = request.POST.get('username')
        files=request.FILES
        cad_id = request.POST.get('cad_id')
        print "FILES RECEIVED ARE: %s"%files
        print "DATA RECEIVED IS: %s"%request.POST
        print "DEBUG 1000"
        try:
            for key in files:
                if key.startswith("stl"):
                    error , new_stl_id = upload_stl(files[key], int(id_part), int(cad_id), int(userid))
                    if error:raise ValueError(error)
            _3mf_finished=[]
            for key in files:
                print "DEBUG102:"
                if (key.startswith("amf") or key.startswith("config") or key.startswith("configb") or key.startswith("gcode")):
                    print "DEBUG103:"
                    filename = "%s"%files[key]
                    _3mf_id = filename.rsplit('.',1)[0].split('-',1)[1]
                    print "DEBUG104:"
                    print _3mf_id
                    print "DEBUG105:"
                    if not _3mf_id in _3mf_finished:
                        print "DEBUG106:"
                        # the following is a check to verify that all 4 files of the 3mf are present : amf, config, configb, gcode
                        amf_file, config_file, configb_file, gcode_file = None, None, None, None
                        print "DEBUG112:"
                        for key1 in files:
                            filename1 = "%s"%files[key1]
                            filetype = filename1.rsplit('.',1)[0].split('-')[0]
                            file3mfid = filename1.rsplit('.',1)[0].split('-')[1]
                            if (filename1.startswith("amf") or filename1.startswith("config") or filename1.startswith("gcode")):
                                print "DEBUG113:"
                                print filename1
                                print file3mfid
                                if file3mfid == _3mf_id and filetype=="amf":
                                    print "DEBUG114:"
                                    amf_file = files[key1]
                                elif file3mfid == _3mf_id and filetype=="config":
                                    print "DEBUG115:"
                                    config_file = files[key1]
                                elif file3mfid == _3mf_id and filetype=="configb":
                                    print "DEBUG116:"
                                    configb_file = files[key1]
                                elif file3mfid == _3mf_id and filetype=="gcode":
                                    print "DEBUG116:"
                                    gcode_file = files[key1]
                        if not (amf_file and config_file and configb_file and gcode_file):
                            print "DEBUG117:"
                            raise ValueError("Not All four files are there: amf, config, configb and gcode")
                        print "DEBUG118:"
                        error = upload_3mf_1(amf_file, config_file, configb_file, gcode_file, int(cad_id), int(userid))
                    print "DEBUG119:"
                    if error:raise ValueError(error)
                    _3mf_finished.append(_3mf_id)
        except ValueError as err:
            print "DEBUG122:"
            print (err)
            return HttpResponse(status=500)
        except:
            print "DEBUG123:"
            return HttpResponse(status=500)
        print "DEBUG124:"
    part.checked_out = 0
    part.checked_out_by = 0
    part.save()
    return HttpResponse()


@csrf_exempt
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
        except:
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
            error, new_cad_id = upload_cad(request.FILES['cad'], id_part, userid)
            if error: raise ValueError(error)

            first_config = request.POST.get('tmf')
            print "TMF id is: %s"%first_config
            cad = SP3D_CAD.objects.get(id=new_cad_id)
            "DEBUG 400: NEW CAD ID: %s"%new_cad_id
            "DEBUG 400: FIRST CONFIG: %s"%first_config
            cad.first_config = int(first_config)
            cad.save()
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
        permissions="1-" + permissions + "%s-" % index

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

# add new 3mf
@login_required
def add_3mf(request):
    if request.method == 'POST':
        files = request.FILES
        form = request.POST
        print "FILES: %s"%files
        print "form is: %s"%form
        context={}
    return HttpResponseRedirect('/parts/part-detail/297')


# upload new cad
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

        print "DEBUG50:"
    except ValueError as err :
        print (err)
        error=error + "%s"%err
    except:
        print "CAD Uploading Failed"
        error = error + "CAD Uploading failed"

    result=[error, new_cad.id]
    print "DEBUG51:"
    return result

# upload new stl
def upload_stl(file , id_part , id_cad, userid):
    error=None
    try:
        part = SP3D_Part.objects.get(id = id_part)
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)

        # kepep subpath separated from path, because used later
        subpath="catalogue/oem-%s/part-id-%s/STL/"%(oem.code,id_part)
        path = DATABASE_DIRECTORY_TRANSITION + subpath

        # Check that folder exists
        if not os.path.exists(path):
            os.makedirs(path)

        newfile=path+"%s"%file
        filename, file_extension = os.path.splitext(newfile)
        #Check that file extension is .amf
        if not (file_extension.lower()==".stl"):
            raise ValueError('Wrong file extension, we need a .stl')
        # Check that file with same name doesn't exist and iterate on name if it does
        if os.path.exists(newfile):
            i=1
            while os.path.exists("%s-iteration-%s%s"%(filename,i,file_extension)):
                i+=1
            newfile = "%s-iteration-%s%s"%(filename,i,file_extension)

        # write in new file
        with open(newfile, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        print "New STL uploaded at location " + newfile

        # create related record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        name=ntpath.basename(newfile)
        root_path=DATABASE_DIRECTORY_TRANSITION
        file_path=subpath+name
        new_stl=SP3D_STL.objects.create(creation_date=creation_date, name=name, root_path=root_path, file_path=file_path, id_cad=int(id_cad), id_creator=userid)
        print "STL record added to sql database with id %s" % new_stl.id

        print "DEBUG50:"
    except ValueError as err :
        print (err)
        error=error + "%s"%err
    except:
        print "STL Uploading Failed"
        error = error + "STL Uploading failed"

    result=[error, new_stl.id]
    print "DEBUG51:"
    return result

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

# UPLOAD 3MF
def upload_3mf(amf_file, config_file, configb_file, id_cad, userid):
    error=None
    try:
        print "BALISE 2000: %s"%id_cad
        cad=SP3D_CAD.objects.get(id=id_cad)
        id_part=cad.id_part
        part=SP3D_Part.objects.get(id=id_part)
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)
        print "BALISE200"
        extension_amf=("%s"%amf_file).rsplit('.',1)[1]
        extension_config=("%s"%config_file).rsplit('.',1)[1]
        extension_configb=("%s"%configb_file).rsplit('.',1)[1]
        if not extension_amf == "amf":
            raise ValueError("Wrong extension file, supposed to be .amf")
        if not extension_config == "ini":
            raise ValueError("Wrong extension file, supposed to be .ini")
        if not extension_configb == "ini":
            raise ValueError("Wrong extension file, supposed to be .ini")


        subpath_amf="catalogue/oem-%s/part-id-%s/AMF/"%(oem.code,part.id)
        subpath_config="catalogue/oem-%s/part-id-%s/CONFIG/"%(oem.code,part.id)

        print "BALISE201"

        path_amf = DATABASE_DIRECTORY_TRANSITION + subpath_amf
        path_config = DATABASE_DIRECTORY_TRANSITION + subpath_config
        print "BALISE1"
        # Check that folder exists
        if not os.path.exists(path_amf):
            os.makedirs(path_amf)
        if not os.path.exists(path_config):
            os.makedirs(path_config)
        print "BALISE2"

        # create related record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        if ("%s"%file).startswith("amf"):
            namestart="amf"

        root_path=DATABASE_DIRECTORY_TRANSITION
        new_3mf=SP3D_3MF.objects.create(creation_date=creation_date,root_path=root_path, id_cad=int(id_cad),id_creator=userid)
        print "3MF record added to sql database with id %s" % new_3mf.id
        new_3mf.name_amf = 'amf-%s.amf' % new_3mf.id
        new_3mf.name_config = 'config-%s.ini' % new_3mf.id
        new_3mf.name_configb = 'configb-%s.ini' % new_3mf.id
        new_3mf.amf_path = subpath_amf + 'amf-%s.amf' % new_3mf.id
        new_3mf.config_path = subpath_config + 'config-%s.ini' % new_3mf.id
        new_3mf.configb_path = subpath_config + 'configb-%s.ini' % new_3mf.id
        new_3mf.save()


        new_amf = root_path + new_3mf.amf_path
        new_config = root_path + new_3mf.config_path
        new_configb = root_path + new_3mf.configb_path

        amf_name, amf_extension = os.path.splitext(new_amf)
        config_name, config_extension = os.path.splitext(new_config)
        configb_name, configb_extension = os.path.splitext(new_configb)

        # # #Check that file extension is .config
        # if not _extension.lower()==".ini":
        #     raise ValueError('Wrong file extension, we need a .INI')
        print "BALISE3"
        # Check that file with same name doesn't exist and iterate on name if it does
        # if os.path.exists(new_amf):
        #     it=1
        #     while os.path.exists("%s-iteration-%s%s"%(filename,it,file_extension)):
        #         it+=1
        #     newfile="%s-iteration-%s%s"%(filename,it,file_extension)

        # write in new file
        with open(new_amf, 'wb+') as destination:
            for chunk in amf_file.chunks():
                destination.write(chunk)
        print "New AMF uploaded at location " + new_amf
        with open(new_config, 'wb+') as destination:
            for chunk in config_file.chunks():
                destination.write(chunk)
        print "New CONFIG uploaded at location " + new_config
        with open(new_configb, 'wb+') as destination:
            for chunk in configb_file.chunks():
                destination.write(chunk)
        print "New CONFIGB uploaded at location " + new_configb


    except ValueError as err :
        print (err)
        error=error +"%s"%err
    except:
        print "3MF Uploading Failed"
        error = error + "3MF Uploading failed"
    return error

# UPLOAD 3MF
def upload_3mf_1(amf_file, config_file, configb_file, gcode_file, id_cad, userid):
    error=None
    try:
        print "BALISE 2000: %s"%id_cad
        cad=SP3D_CAD.objects.get(id=id_cad)
        id_part=cad.id_part
        part=SP3D_Part.objects.get(id=id_part)
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)
        print "BALISE200"
        extension_amf=("%s"%amf_file).rsplit('.',1)[1]
        extension_config=("%s"%config_file).rsplit('.',1)[1]
        extension_configb=("%s"%configb_file).rsplit('.',1)[1]
        extension_gcode=("%s"%gcode_file).rsplit('.',1)[1]
        if not extension_amf == "amf":
            raise ValueError("Wrong extension file, supposed to be .amf")
        if not extension_config == "ini":
            raise ValueError("Wrong extension file, supposed to be .ini")
        if not extension_configb == "ini":
            raise ValueError("Wrong extension file, supposed to be .ini")
        if not extension_gcode == "gcode":
            raise ValueError("Wrong extension file, supposed to be .gcode")


        subpath_amf="catalogue/oem-%s/part-id-%s/AMF/"%(oem.code,part.id)
        subpath_config="catalogue/oem-%s/part-id-%s/CONFIG/"%(oem.code,part.id)
        subpath_gcode="catalogue/oem-%s/part-id-%s/GCODE/"%(oem.code,part.id)

        print "BALISE201"

        path_amf = DATABASE_DIRECTORY_TRANSITION + subpath_amf
        path_config = DATABASE_DIRECTORY_TRANSITION + subpath_config
        path_gcode = DATABASE_DIRECTORY_TRANSITION + subpath_gcode
        print "BALISE1"
        # Check that folder exists
        if not os.path.exists(path_amf):
            os.makedirs(path_amf)
        if not os.path.exists(path_config):
            os.makedirs(path_config)
        if not os.path.exists(path_gcode):
            os.makedirs(path_gcode)
        print "BALISE2"

        # create related record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')

        root_path=DATABASE_DIRECTORY_TRANSITION
        new_3mf=SP3D_3MF.objects.create(creation_date=creation_date,root_path=root_path, id_cad=int(id_cad),id_creator=userid)
        print "3MF record added to sql database with id %s" % new_3mf.id
        # names of files in 3mf
        new_3mf.name_amf = 'amf-%s.amf' % new_3mf.id
        new_3mf.name_config = 'config-%s.ini' % new_3mf.id
        new_3mf.name_configb = 'configb-%s.ini' % new_3mf.id
        new_3mf.name_gcode = 'gcode-%s.gcode' % new_3mf.id
        # path of files in 3mf
        new_3mf.amf_path = subpath_amf + 'amf-%s.amf' % new_3mf.id
        new_3mf.config_path = subpath_config + 'config-%s.ini' % new_3mf.id
        new_3mf.configb_path = subpath_config + 'configb-%s.ini' % new_3mf.id
        new_3mf.gcode_path = subpath_gcode + 'gcode-%s.gcode' % new_3mf.id

        new_3mf.save()

        new_amf = root_path + new_3mf.amf_path
        new_config = root_path + new_3mf.config_path
        new_configb = root_path + new_3mf.configb_path
        new_gcode = root_path + new_3mf.gcode_path

        amf_name, amf_extension = os.path.splitext(new_amf)
        config_name, config_extension = os.path.splitext(new_config)
        configb_name, configb_extension = os.path.splitext(new_configb)
        gcode_name, gcode_extension = os.path.splitext(new_gcode)

        print "BALISE3"

        with open(new_amf, 'wb+') as destination:
            for chunk in amf_file.chunks():
                destination.write(chunk)
        print "New AMF uploaded at location " + new_amf
        with open(new_config, 'wb+') as destination:
            for chunk in config_file.chunks():
                destination.write(chunk)
        print "New CONFIG uploaded at location " + new_config
        with open(new_configb, 'wb+') as destination:
            for chunk in configb_file.chunks():
                destination.write(chunk)
        print "New CONFIGB uploaded at location " + new_configb
        with open(new_gcode, 'wb+') as destination:
            for chunk in gcode_file.chunks():
                destination.write(chunk)
        print "New GCODE uploaded at location " + new_gcode


    except ValueError as err :
        print (err)
        error=error +"%s"%err
    except:
        print "3MF Uploading Failed"
        error = error + "3MF Uploading failed"
    return error
