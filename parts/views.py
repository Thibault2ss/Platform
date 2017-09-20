# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.core.urlresolvers import reverse
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import SP3D_Part, SP3D_Print, SP3D_Printer, SP3D_Image, SP3D_CAD, SP3D_AMF, SP3D_CONFIG, SP3D_Oem, SP3D_3MF, SP3D_STL, SP3D_CAD2D, SP3D_Status_Eng, SP3D_Status_Ord, SP3D_Status_Eng_History, SP3D_Status_Ord_History, SP3D_Bulk_Files, SP3D_Client, SP3D_Order, SP3D_Po_Revision, SP3D_Quote_Revision, SP3D_Contact
from django.contrib.auth.models import User
from .forms import UploadFileForm
from threading import Thread
from django.forms.models import model_to_dict
from random import randint
from datetime import datetime, timedelta
from tzlocal import get_localzone
from configbundle import ConfigBundle


import os
import json
import subprocess
import requests
import MySQLdb
import time
import threading
import ntpath
import ast
import shutil
import pytz
import collections
# Create your views here.
TOKEN_FLASK='123456789'

SLACK_WEBHOOK_PRINTER = 'https://hooks.slack.com/services/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'

DATABASE_DIRECTORY = '/home/user01/SpareParts_Database/files/'
DATABASE_DIRECTORY_TRANSITION = '/home/user01/SpareParts_Database/root/'
SLIC3R_DIRECTORY= '/home/user01/Slic3r/slic3r_dev/'
LOCAL_APP = "http://localhost:5000"


@login_required
def index(request, error=""):
    print "TESTTTTT: %s"%error
    latest_part_list = SP3D_Part.objects.order_by('-creation_date')
    p=[]
    for part in latest_part_list:
        p.append(part.id)


    test1 = SP3D_Part.objects.get(id = 421 )
    test2 = SP3D_Part.objects.get(id = 420 )
    print "PART 421 CREATION DATE: %s"%type(test1.creation_date)
    print "PART 420 CREATION DATE: %s"%type(test2.creation_date)
    print "COMPARISON: %s"%(test2.creation_date>test1.creation_date)
    print "LIST: %s"%p

    users = User.objects.all()
    oems=SP3D_Oem.objects.all()
    status_eng_list = SP3D_Status_Eng.objects.all()
    oem_list = SP3D_Oem.objects.all()
    printers = SP3D_Printer.objects.all().order_by("name")
    nb_opened = SP3D_Part.objects.filter(status_eng = 1 ).count()
    nb_geometry = SP3D_Part.objects.filter(status_eng = 2 ).count()
    nb_indus = SP3D_Part.objects.filter(status_eng = 3 ).count()
    nb_qc = SP3D_Part.objects.filter(status_eng = 4 ).count()
    nb_closed = SP3D_Part.objects.filter(status_eng = 5 ).count()
    nb_rework = SP3D_Part.objects.filter(status_eng = 6 ).count()
    context = {
        'latest_part_list': latest_part_list,
        'users':users,
        'oems':oems,
        'error':error,
        'oem_list':oem_list,
        'printers':printers,
        'status_eng_list':status_eng_list,
        'nb_opened':nb_opened,
        'nb_geometry':nb_geometry,
        'nb_indus':nb_indus,
        'nb_qc':nb_qc,
        'nb_closed':nb_closed,
        'nb_rework':nb_rework,
    }
    print "COOKIES"
    print request.COOKIES
    return render(request, 'parts/index.html', context)

@login_required
def orders(request):
    # if (request.user.id == 2):
    #     return HttpResponseRedirect("/parts/")

    filter_status = request.GET.get("status","")
    if filter_status:
        try:
            filter_status = int(filter_status)
        except:
            return redirect('/parts/orders/?status=1')
    else:
        filter_status = 1

    clients = SP3D_Client.objects.all().order_by('name')
    users = User.objects.all()
    print "FILTER STATUS IS: %s"%filter_status
    orders = SP3D_Order.objects.filter(status_ord = filter_status).order_by("due_date")

    status_ord_list= SP3D_Status_Ord.objects.all()
    context = {
        'clients' :clients,
        'orders':orders,
        'users':users,
        'filter_status':filter_status,
        'status_ord_list':status_ord_list,
    }
    return render(request, 'parts/orders.html', context)

@login_required
def order_detail(request, id_order, error=""):
    # if not request.user.id==1:
    #     return HttpResponseRedirect("/parts/")
    print "TESTTTTT: %s"%error
    # clients = SP3D_Client.objects.all().order_by('name')
    oems = SP3D_Oem.objects.all().order_by('name')
    status_eng_list = SP3D_Status_Eng.objects.all()
    bulk_files = SP3D_Bulk_Files.objects.filter(id_order=int(id_order))
    latest_part_list = {}
    for oem in oems:
        latest_part_list[oem.id] = SP3D_Part.objects.filter(id_oem = oem.id).order_by('-creation_date')
    users = User.objects.all()
    order = SP3D_Order.objects.get(id=id_order)
    print "ORDER STATUS IS: %s "%order.status_ord
    client = SP3D_Client.objects.get(id=order.id_client)
    status_ord_list = SP3D_Status_Ord.objects.all()
    contacts = SP3D_Contact.objects.filter(id_client=order.id_client)
    permissions = map(int, filter( None , order.permissions.split("-")))
    if request.user.id in permissions:
        permission = 1
    else:
        permission=0
    parts_qtty = ast.literal_eval(order.parts)
    part_id_list = list(parts_qtty.keys())

    parts = SP3D_Part.objects.filter(id__in = part_id_list).order_by("id")
    context = {
        'client' :client,
        'contacts':contacts,
        'order':order,
        'latest_part_list': latest_part_list,
        'users':users,
        'permission':permission,
        'oems':oems,
        'parts':parts,
        'parts_qtty':parts_qtty,
        'status_eng_list':status_eng_list,
        'status_ord_list':status_ord_list,
        'bulk_files':bulk_files,
        # 'error':error,
        # 'oem_list':oem_list,
        # 'nb_opened':nb_opened,
        # 'nb_geometry':nb_geometry,
        # 'nb_indus':nb_indus,
        # 'nb_qc':nb_qc,
        # 'nb_closed':nb_closed,
        # 'nb_rework':nb_rework,
    }
    # print "COOKIES"
    # print request.COOKIES
    return render(request, 'parts/order-detail.html', context)

@login_required
def prints(request):
    latest_print_list = SP3D_Print.objects.order_by('-creation_date')
    # list of all parts id related
    part_id_list = []
    for pr in latest_print_list:
        if not pr.id_part in part_id_list:
            part = SP3D_Part.objects.get(id = pr.id_part)
            part_id_list.append(pr.id_part)
    parts = SP3D_Part.objects.filter(id__in=part_id_list)
    # get all printers
    printers = SP3D_Printer.objects.all()
    # get all printers
    users = User.objects.all()

    context = {
        'latest_print_list': latest_print_list,
        'parts':parts,
        'printers':printers,
        'users':users,
    }
    return render(request, 'parts/prints.html', context)

@login_required
def download_cad(request, id_part, id_cad):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    cad = SP3D_CAD.objects.get(id = id_cad)
    filename = cad.root_path + cad.file_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_bulk(request, id_bulk):
    bulk = SP3D_Bulk_Files.objects.get(id = id_bulk)
    filename = bulk.root_path + bulk.file_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_amf(request, id_part, id_3mf):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    _3mf = SP3D_3MF.objects.get(id = id_3mf)
    filename = _3mf.root_path + _3mf.amf_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_config(request, id_part, id_3mf):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    _3mf = SP3D_3MF.objects.get(id = id_3mf)
    filename = _3mf.root_path + _3mf.config_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_configb(request, id_part, id_3mf):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    _3mf = SP3D_3MF.objects.get(id = id_3mf)
    filename = _3mf.root_path + _3mf.configb_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_gcode(request, id_part, id_3mf):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    _3mf = SP3D_3MF.objects.get(id = id_3mf)
    filename = _3mf.root_path + _3mf.gcode_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_cad2d(request, id_part, id_cad2d):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    cad2d = SP3D_CAD2D.objects.get(id = id_cad2d)
    filename = cad2d.root_path + cad2d.file_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_stl(request, id_part, id_stl):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    stl = SP3D_STL.objects.get(id = id_stl)
    filename = stl.root_path + stl.file_path
    response = HttpResponse(file(filename), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def download_log(request, id_print):
    # part= SP3D_Part.objects.get(id = id_part)
    # oem = SP3D_Oem.objects.get(id = part.id_oem)
    _print = SP3D_Print.objects.get(id = id_print)
    if not _print.done:
        print "Print is not finished, cannot download log for print %s"%id_print
        return HttpResponseRedirect("/parts/prints/")
    filename = DATABASE_DIRECTORY_TRANSITION + "Print_Logs/print-%s/log-%s.txt"%(id_print, id_print)
    if not os.path.isfile(filename):
         print "Print Log log-%s.txt is not in folder, cannot download" %id_print
         return HttpResponseRedirect("/parts/prints/")
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
def new_part_number(request):
    try:
        parts = SP3D_Part.objects.filter(part_number__startswith = "pn-").order_by('-part_number')
        count = parts.count()
        if count==0:
            part_number = "pn-%06d" % 1
            print "PART NUMBER: %s"%part_number
        else:
            index = 0
            while index < count:
                part_number = parts[index].part_number
                print "LAST PART NUMBER: %s"%part_number
                try:
                    part_number = int(part_number.split("-")[1])
                    part_number = part_number + 1
                    part_number = "pn-%06d" % part_number
                    break
                except:
                    index = index + 1
                    print "NOT THIS PART: %s"%part_number

        data = {
            "part_number": part_number
        }
    except ValueError as err:
        data = {
            "part_number": 555,
            "result": err
        }
    except:
        data = {
            "part_number": 777,
            "result": "Problem happened during image deletion, check records"
        }
    return JsonResponse(data)

@login_required
def update_notes(request):
    try:
        print "Notes entered "
        print "request form: %s"%request.POST
        _id = request.POST.get("pk")
        id_type = request.POST.get("type")
        new_note = request.POST.get("value")
        if id_type == '3mf':
            obj = SP3D_3MF.objects.get(id=int(_id))
        elif id_type == 'stl':
            obj = SP3D_STL.objects.get(id=int(_id))
        elif id_type == 'cad2d':
            obj = SP3D_CAD2D.objects.get(id=int(_id))
        elif id_type == 'stl':
            obj = SP3D_Bulk_Files.objects.get(id=int(_id))
        elif id_type == 'part':
            obj = SP3D_Part.objects.get(id=int(_id))
        elif id_type == 'order':
            obj = SP3D_Order.objects.get(id=int(_id))
        elif id_type == 'bulk':
            obj = SP3D_Bulk_Files.objects.get(id=int(_id))
        else:
            raise ValueError("this type of notes not supported")
        obj.notes = new_note
        obj.save()
        data = {
            "result": "Note editing updated successfully"
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
def ajax_save_quantity(request):
    try:
        id_part = request.GET.get('id_part', None)
        id_order = request.GET.get('id_order', None)
        quantity = request.GET.get('quantity', None)
        order = SP3D_Order.objects.get(id=int(id_order))
        # test if quantity is not a string
        try:
            int(quantity)
        except:
            raise ValueError("Quantity is not numeric")
        if not (int(quantity)==quantity or quantity>=0):
            raise ValueError("Quantity is not integer or positive")
        # add to dictionnary
        parts_qtty = ast.literal_eval(order.parts)
        if id_part in parts_qtty:
            if int(quantity)==0:
                del parts_qtty[id_part]
            else:
                parts_qtty[id_part]=int(quantity)
        else:
            parts_qtty[id_part] = int(quantity)

        # sort dictionnary
        parts_qtty = collections.OrderedDict(sorted(parts_qtty.items()))
        parts_qtty = json.dumps(parts_qtty)
        order.parts = "%s"%parts_qtty
        order.save()
        data = {
            "result": "Part Quantity was changed successfully"
        }
    except ValueError as err:
        data = {
            "error": err
        }
    except:
        data = {
            "error": "Problem happened quantity change"
        }
    return JsonResponse(data)

@login_required
def ajax_generate_po_nb(request):
    try:
        id_client = request.GET.get('id_client', None)
        client = SP3D_Client.objects.get(id=int(id_client))
        client_code = client.code
        now = datetime.now()
        print now.year, now.month, now.day, now.hour, now.minute, now.second
        id_client = request.GET.get('id_client', None)

        po_number = "PO-%s-%s%02d%02d"%(client.code, now.year, now.month, now.day )
        data = {
            "result": po_number,
        }
    except ValueError as err:
        data = {
            "error": err
        }
    except:
        data = {
            "error": "Problem happened quantity change"
        }
    return JsonResponse(data)


@login_required
def ajax_generate_quote_nb(request):
    try:
        id_client = request.GET.get('id_client', None)
        client = SP3D_Client.objects.get(id=int(id_client))
        client_code = client.code
        now = datetime.now()
        print now.year, now.month, now.day, now.hour, now.minute, now.second
        id_client = request.GET.get('id_client', None)

        quote_number = "QUO-%s%02d%02d-%s"%(now.year, now.month, now.day, client.code )
        data = {
            "result": quote_number,
        }
    except ValueError as err:
        data = {
            "error": err
        }
    except:
        data = {
            "error": "Problem happened quantity change"
        }
    return JsonResponse(data)

@login_required
def delete_image(request):
    try:
        image_id = request.GET.get('image_id', None)
        if not image_id : raise ValueError('image_id not found in ajax request')
        img = SP3D_Image.objects.get(id=image_id)
        if not img : raise ValueError('image not found in mysql records')
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
def delete_part(request ):
    try:
        id_part = request.GET.get('id_part', None)
        if not id_part : raise ValueError('id_part not found in ajax request')
        part = SP3D_Part.objects.get(id=id_part)
        oem = SP3D_Oem.objects.get(id=part.id_oem)
        if not part : raise ValueError('part not found in mysql records')
        partid = part.id

        # remove status change records:
        status_history = SP3D_Status_Eng_History.objects.filter(part_id=part.id)
        for record in status_history:
            record.delete()

        shutil.rmtree(DATABASE_DIRECTORY_TRANSITION + "catalogue/oem-%s/part-id-%s"%(oem.code, part.id))
        part.delete()
        print "PART folder deleted: %s"%partid
        data = {
            "result": "deleted part successfully :%s"%partid
        }
    except:
        print "PART folder NOT deleted: %s"%partid
        data = {
            "result": " part deletion ISSUE  :%s"%partid
        }

    return JsonResponse(data)

@login_required
def delete_order(request):
    try:
        id_order = request.GET.get('id_order', None)
        if not id_order : raise ValueError('id_order not found in ajax request')
        order = SP3D_Order.objects.get(id=id_order)
        if not order : raise ValueError('order not found in mysql records')
        orderid = order.id
        pos = SP3D_Po_Revision.objects.filter(id_order=order.id)
        quotes = SP3D_Quote_Revision.objects.filter(id_order=order.id)
        bulk_files = SP3D_Bulk_Files.objects.filter(id_order = order.id)
        status_history = SP3D_Status_Ord_History.objects.filter(id_order=order.id)
        shutil.rmtree(DATABASE_DIRECTORY_TRANSITION + "Orders/order-%s"%order.id)
        order.delete()
        for bulk in bulk_files:
            bulk.delete()
        for quote in quotes:
            quote.delete()
        for po in pos:
            po.delete()
        for record in status_history:
            record.delete()
        print "ORDER folder deleted: %s"%orderid
        data = {
            "result": "deleted order successfully :%s"%orderid
        }
    except ValueError as err:
        print "ORDER %s deletion issue: %s"%(orderid,err)
        data = {
            "error": "ORDER %s deletion issue: %s"%(orderid,err)
        }
    except:
        print "ORDER folder NOT deleted: %s"%orderid
        data = {
            "error": " order deletion ISSUE on order:%s, ORDER FOLDER NOT DELETED"%orderid
        }

    return JsonResponse(data)

@login_required
def delete_3mf(request):
    try:
        id_3mf = request.GET.get('id_3mf', None)
        if not id_3mf : raise ValueError('id_3mf not found in ajax request')
        _3mf = SP3D_3MF.objects.get(id=id_3mf)
        if not _3mf : raise ValueError('3mf not found in mysql records')
        os.remove(_3mf.root_path + _3mf.amf_path)
        os.remove(_3mf.root_path + _3mf.config_path)
        os.remove(_3mf.root_path + _3mf.configb_path)
        os.remove(_3mf.root_path + _3mf.gcode_path)
        print "3mf file deleted : %s"%_3mf.id
        _3mf.delete()
        print "3mf record deleted"
        data = {
            "result": "3mf was deleted successfully"
        }
    except ValueError as err:
        data = {
            "result": err
        }
    except:
        data = {
            "result": "Problem happened during 3mf deletion, check records"
        }
    return JsonResponse(data)

@login_required
def delete_cad2d(request):
    try:
        id_cad2d = request.GET.get('id_cad2d', None)
        if not id_cad2d : raise ValueError('id_cad2d not found in ajax request')
        cad2d = SP3D_CAD2D.objects.get(id=id_cad2d)
        if not cad2d : raise ValueError('cad2d not found in mysql records')
        os.remove(cad2d.root_path + cad2d.file_path)
        print "CAD2D file deleted: %s"%cad2d.id
        cad2d.delete()
        print "CAD2D record deleted"
        data = {
            "result": "CAD2D was deleted successfully"
        }
    except ValueError as err:
        data = {
            "result": err
        }
    except:
        data = {
            "result": "Problem happened during CAD2D deletion, check records"
        }
    return JsonResponse(data)

@login_required
def delete_stl(request):
    try:
        id_stl = request.GET.get('id_stl', None)
        if not id_stl : raise ValueError('id_stl not found in ajax request')
        stl = SP3D_STL.objects.get(id=id_stl)
        if not stl : raise ValueError('stl not found in mysql records')
        os.remove(stl.root_path + stl.file_path)
        print "STL file deleted: %s"%stl.id
        stl.delete()
        print "STL record deleted"
        data = {
            "result": "STL was deleted successfully"
        }
    except ValueError as err:
        data = {
            "result": err
        }
    except:
        data = {
            "result": "Problem happened during STL deletion, check records"
        }
    return JsonResponse(data)

@login_required
def delete_bulk(request):
    try:
        print "REQUEST GET: %s"%request.GET
        id_bulk = request.GET.get('id_bulk', None)
        if not id_bulk : raise ValueError('id_bulk not found in ajax request')
        bulk = SP3D_Bulk_Files.objects.get(id=id_bulk)
        if not bulk : raise ValueError('bulk not found in mysql records')
        os.remove(bulk.root_path + bulk.file_path)
        print "BULK file deleted: %s"%bulk.id
        bulk.delete()
        print "bulk record deleted"
        data = {
            "result": "bulk was deleted successfully"
        }
    except ValueError as err:
        data = {
            "result": err
        }
    except:
        data = {
            "result": "Problem happened during bulk deletion, check records"
        }
    return JsonResponse(data)

@login_required
def delete_cad(request):
    try:
        id_cad = request.GET.get('id_cad', None)
        if not id_cad : raise ValueError('id_cad not found in ajax request')
        cad = SP3D_CAD.objects.get(id=id_cad)
        if not cad : raise ValueError('cad not found in mysql records')
        os.remove(cad.root_path + cad.file_path)
        print "CAD file deleted: %s"%cad.id
        cad.delete()
        print "CAD record deleted"
        data = {
            "result": "CAD was deleted successfully"
        }
    except ValueError as err:
        data = {
            "result": err
        }
    except:
        data = {
            "result": "Problem happened during CAD deletion, check records"
        }
    return JsonResponse(data)

@login_required
def change_status_eng(request):
    try:
        userid = request.user.id
        part_id = request.GET.get('id_part', None)
        if not part_id : raise ValueError('id_part not found in ajax request')
        status_id = request.GET.get('id_status', None)
        if not status_id : raise ValueError('id_status not found in ajax request')
        part = SP3D_Part.objects.get(id=part_id)
        if not part : raise ValueError('part not found in mysql records')
        part.status_eng = int(status_id)
        part.save()

        # add change to the history
        new_record = SP3D_Status_Eng_History.objects.create(part_id=part.id, date=time.strftime('%Y-%m-%d %H:%M:%S'), id_status = int(status_id), id_creator = userid )
        print "new record saved in status history"
        print "Changed part %s status to : %s"%(part_id,status_id)
        data = {
            "result": "Status of part %s was updated successfully"%part_id
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
def change_status_order(request):
    try:
        userid = request.user.id
        id_order = request.GET.get('id_order', None)
        if not id_order : raise ValueError('id_order not found in ajax request')
        id_status = request.GET.get('id_status', None)
        if not id_status : raise ValueError('id_status not found in ajax request')
        order = SP3D_Order.objects.get(id=int(id_order))
        if not order : raise ValueError('order not found in mysql records')
        order.status_ord = int(id_status)
        if int(id_status) == 3:
            order.completion_date = datetime.now()
            order.closed_by = userid
        order.save()

        # add change to the history
        new_record = SP3D_Status_Ord_History.objects.create(id_order=order.id, date=time.strftime('%Y-%m-%d %H:%M:%S'), id_status = int(id_status), id_creator = userid )
        print "new record saved in status history"
        print "Changed order %s status to : %s"%(id_order,id_status)
        data = {
            "result": "Status of order %s was updated successfully"%id_order
        }
    except ValueError as err:
        data = {
            "result": err
        }
    except ValueError as err:
        data = {
            "error": err
        }
    except:
        data = {
            "error": "Problem happened during image deletion, check records"
        }
    return JsonResponse(data)

@login_required
def test(request):
    prints = SP3D_Print.objects.all()
    for pr in prints:
        td = pr.finished_date - pr.creation_date
        pr.printing_time = int(td.days*86400 + td.seconds)
        pr.save()
    print "FINISHED"
    # print"T1 is: %s"%t1
    # print"T1 type: %s"%type(t1)
    # t2 = pytz.utc.localize(datetime.now())
    # print"T2 is: %s"%t2
    # print"T2 type: %s"%type(t2)
    # d=t2-t1
    # print"D is: %s"%d
    # print"D type: %s"%type(d)

    return HttpResponseRedirect("/parts/")


@login_required
def ajax_print(request):
    # get user who printed

    userid = request.user.id
    user = User.objects.get(id=userid)
    # get all info
    print "RAKESH: %s"%request.GET
    id_3mf=request.GET.get('id_3mf', None)
    z_offset=request.GET.get('z_offset', None)
    try:
        z_offset = float(z_offset)
        if (z_offset>0.5 or z_offset<-0.2):
            raise ValueError("z_offset not in allowed range: -0.2 to 0.5")
    except ValueError as err:
        data = {'error': "%s"%err}
        print "%s"%err
        return JsonResponse(data)
    except:
        data = {'error': "Z offset is not a float number:%s"%z_offset}
        print "Z offset is wrong"
        return JsonResponse(data)

    print "3MF ID IS: %s"%id_3mf
    id_printer=request.GET.get('printer_id',None)
    _3mf = SP3D_3MF.objects.get(id=id_3mf)
    id_cad = _3mf.id_cad
    print "ID CAD FOR RAKESH IS : %s"%id_cad
    cad = SP3D_CAD.objects.get(id=id_cad)
    id_part = cad.id_part
    part = SP3D_Part.objects.get(id=id_part)
    id_oem = part.id_oem
    oem = SP3D_Oem.objects.get(id=id_oem)
    printer= SP3D_Printer.objects.get(id=id_printer)

    # check if printer is already printing or not:
    # response = requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})

    # add print to database log
    new_print=SP3D_Print.objects.create(creation_date=time.strftime('%Y-%m-%d %H:%M:%S'), id_printer=id_printer, id_3mf=id_3mf, id_cad=id_cad, id_part=id_part, id_creator=userid)
    print_log_path = DATABASE_DIRECTORY_TRANSITION + "Print_Logs/print-%s/" % new_print.id
    if not os.path.isdir(print_log_path):
        os.makedirs(print_log_path)

    # get necessary files
    amf_file = DATABASE_DIRECTORY_TRANSITION + "catalogue/oem-%s/part-id-%s/AMF/%s"%(oem.code, part.id, _3mf.name_amf)
    config_file = DATABASE_DIRECTORY_TRANSITION + "catalogue/oem-%s/part-id-%s/CONFIG/%s"%(oem.code, part.id, _3mf.name_config)
    gcode_file = print_log_path + "gcode-%s.gcode"%new_print.id
    local_ip=printer.local_ip

    # modify config file:
    configb = ConfigBundle(config_file)
    config_file = configb.change_config_param("post_process", '"/usr/bin/perl /home/user01/Slic3r/slic3r_dev/offset_z_post_process.pl %s"'%z_offset, print_log_path + "config-%s.ini"%new_print.id)
    print "changed config with z_offset equal to: %s"%z_offset
    try:
        print subprocess.check_output(['perl',SLIC3R_DIRECTORY + 'slic3r.pl', '--load', config_file, '-o', gcode_file, amf_file])
    except:
        print "An error occured while slicing..."
        remove_print(new_print.id)
        data = {'error': "an error occured during slicing"}
        return JsonResponse(data)

    payload = {
        'token': TOKEN_FLASK,
        'id_print':new_print.id,
        'id_3mf':_3mf.id,
        'id_cad' : cad.id,
        'id_part':part.id,
        'username':user.first_name,
        'id_printer':printer.id,
        'printer_name':printer.name,
        'printer_location':printer.location,
        'printer_ip':printer.local_ip,

            }
    with open(gcode_file) as f:
        response = requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})
        # TRYING TO use threading not to wait before sending response
        # t = Thread(target=send_to_printer, kwargs={'local_ip':local_ip, 'payload':payload, 'f':f})
        # t.setDaemon(False)
        # t.start()
    print "ABOUT TO SEND AJAX ANSWER TO CLIENT"
    if response.status_code == 350:
        message = "print %s, part %s, 3mf %s: Printer is already printing something"%(new_print.id, part.id, _3mf.id)
        print message
        data = {'error': message}
        remove_print(new_print.id)
    elif response.status_code == 360:
        header = "%s: An error happened during print  :cry:"%printer.name
        message = "Something happened during print, was it stopped manually ?\n print %s, part %s - %s, 3mf %s: \n%s" % (new_print.id, part.id, part.part_name, _3mf.id, user.sp3d_profile.slack_name)
        print message
        data = {'error': message}
        # slack_message(header, message, "#f44242")
    elif response.status_code == 200:
        header = "%s: A print finished successfully :muscle:"%printer.name
        message = "gcode successfully printed, dude\nprint %s, part %s - %s, 3mf %s\n%s"%(new_print.id, part.id, part.part_name, _3mf.id, user.sp3d_profile.slack_name)
        print "AJAX CONTAINS: 200"
        data = {'gcode_sent': message}
        # slack_message(header, message, "#e33a3a")
    else:
        message = "print %s, part %s - %s, 3mf %s: something unknown happened on printer server"%(new_print.id, part.id, part.part_name, _3mf.id)
        print message
        data = {'error': message}
    print "AJAX PRINT OVER"
    return JsonResponse(data)

@login_required
def ajax_print_direct_gcode(request):
    # get user who printed

    userid = request.user.id
    user = User.objects.get(id=userid)
    # get all info
    print "RAKESH: %s"%request.GET
    id_bulk_gcode=request.GET.get('id_bulk_gcode', None)
    try:
        id_bulk_gcode = int(id_bulk_gcode)
    except:
        return JsonResponse({'error': "ID BULK GCODE is wrong integer"})

    print "GCODE BULK ID IS: %s"%id_bulk_gcode
    id_printer=request.GET.get('printer_id',None)
    _gcode = SP3D_Bulk_Files.objects.get(id=id_bulk_gcode)
    id_part = _gcode.id_part
    part = SP3D_Part.objects.get(id=id_part)
    id_oem = part.id_oem
    oem = SP3D_Oem.objects.get(id=id_oem)
    printer= SP3D_Printer.objects.get(id=id_printer)

    # check if printer is already printing or not:
    # response = requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})

    # add print to database log
    new_print=SP3D_Print.objects.create(creation_date=time.strftime('%Y-%m-%d %H:%M:%S'), id_printer=id_printer, id_bulk=id_bulk_gcode, id_part=id_part, id_creator=userid)
    print_log_path = DATABASE_DIRECTORY_TRANSITION + "Print_Logs/print-%s/" % new_print.id
    if not os.path.isdir(print_log_path):
        os.makedirs(print_log_path)

    # get necessary files
    gcode_file = print_log_path + "gcode-%s.gcode"%new_print.id
    with open(gcode_file, "wb+") as f:
        for line in open(_gcode.root_path + _gcode.file_path,"rb"):
            f.write(line)

    local_ip=printer.local_ip

    payload = {
        'token': TOKEN_FLASK,
        'id_print':new_print.id,
        'id_3mf':0,
        'id_cad' : 0,
        'id_part':part.id,
        'username':user.first_name,
        'id_printer':printer.id,
        'printer_name':printer.name,
        'printer_location':printer.location,
        'printer_ip':printer.local_ip,

            }
    with open(gcode_file) as f:
        response = requests.post('http://'+local_ip+':5000/print', data=payload, files={'gcode_file':f})
        # TRYING TO use threading not to wait before sending response
        # t = Thread(target=send_to_printer, kwargs={'local_ip':local_ip, 'payload':payload, 'f':f})
        # t.setDaemon(False)
        # t.start()
    print "ABOUT TO SEND AJAX ANSWER TO CLIENT"
    if response.status_code == 350:
        message = "print %s, part %s, 3mf %s: Printer is already printing something"%(new_print.id, part.id, _3mf.id)
        print message
        data = {'error': message}
        remove_print(new_print.id)
    elif response.status_code == 360:
        header = "%s: An error happened during print  :cry:"%printer.name
        message = "Something happened during print, was it stopped manually ?\n print %s, part %s - %s, 3mf %s: \n%s" % (new_print.id, part.id, part.part_name, _3mf.id, user.sp3d_profile.slack_name)
        print message
        data = {'error': message}
        # slack_message(header, message, "#f44242")
    elif response.status_code == 200:
        header = "%s: A print finished successfully :muscle:"%printer.name
        message = "gcode successfully printed, dude\nprint %s, part %s - %s, 3mf %s\n%s"%(new_print.id, part.id, part.part_name, _3mf.id, user.sp3d_profile.slack_name)
        print "AJAX CONTAINS: 200"
        data = {'gcode_sent': message}
        # slack_message(header, message, "#e33a3a")
    else:
        message = "print %s, part %s - %s, 3mf %s: something unknown happened on printer server"%(new_print.id, part.id, part.part_name, _3mf.id)
        print message
        data = {'error': message}
    print "AJAX PRINT OVER"
    return JsonResponse(data)

def remove_print(id_print):
    global DATABASE_DIRECTORY_TRANSITION
    _print = SP3D_Print.objects.get(id=id_print)
    print_logs = DATABASE_DIRECTORY_TRANSITION + "Print_Logs/print-%s" % _print.id
    shutil.rmtree(print_logs)
    _print.delete()
    return True

def slack_message(header, message, color):
    global SLACK_WEBHOOK_PRINTER
    slack_data = {
                        "text": header,
                        "attachments": [
                            {
                                "text": message,
                                "color": color,
                                "attachment_type": "default"
                            }
                        ]
                    }
    print "SENDING SLACK MESSAGE"
    slack_res = requests.post(SLACK_WEBHOOK_PRINTER, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
    print "SLACK MESSAGE SENT"
    return True


@login_required
def part_detail(request,id_part):
    part = SP3D_Part.objects.get(id=id_part)
    image_list = SP3D_Image.objects.filter(id_part=id_part)
    cad_list=SP3D_CAD.objects.filter(id_part=id_part).order_by('creation_date')
    users = User.objects.all()
    status_eng_list = SP3D_Status_Eng.objects.all()
    printers=SP3D_Printer.objects.all().order_by("name")
    permissions = map(int, filter( None , part.permissions.split("-")))
    if request.user.is_authenticated():
        username = request.user.username
        userid = request.user.id
    if userid in permissions:
        permission = 1
    else:
        permission = 0
    if userid == 1:
        superpermission = 1
    else:
        superpermission = 0

    _3mf_per_cad={} #dictionnary of 3mf like:{'idcad' : _3mf_object, ...}
    for cad in cad_list:
        _3mf_list = SP3D_3MF.objects.filter(id_cad=cad.id).order_by('creation_date')
        _3mf_per_cad[cad.id]=[]
        for _3mf in _3mf_list:
            _3mf_per_cad[cad.id].append(_3mf)

    cad2d_per_cad={} #dictionnary of 2d drawings files like:{'idcad' : cad2d_object, ...}
    for cad in cad_list:
        cad2d_list = SP3D_CAD2D.objects.filter(id_cad=cad.id).order_by('creation_date')
        cad2d_per_cad[cad.id]=[]
        for cad2d in cad2d_list:
            cad2d_per_cad[cad.id].append(cad2d)

    stl_per_cad={} #dictionnary of stl files like:{'idcad' : stl_object, ...}
    for cad in cad_list:
        stl_list = SP3D_STL.objects.filter(id_cad=cad.id).order_by('creation_date')
        stl_per_cad[cad.id]=[]
        for stl in stl_list:
            stl_per_cad[cad.id].append(stl)


    # amf_list=SP3D_AMF.objects.filter(id_part=id_part)
    # config_list=SP3D_CONFIG.objects.filter(id_part=id_part)
    bulk_files = SP3D_Bulk_Files.objects.filter(id_part=id_part)

    oem_list = SP3D_Oem.objects.all()

    print "tmf per cad: %s"%_3mf_per_cad
    context = {
        'part': part,
        'image_list':image_list,
        'cad_list':cad_list,
        'printers':printers,
        # 'amf_list':amf_list,
        # 'config_list':config_list,
        'bulk_files':bulk_files,
        'users':users,
        'oem_list':oem_list,
        'tmf_per_cad':_3mf_per_cad,
        'cad2d_per_cad':cad2d_per_cad,
        'stl_per_cad':stl_per_cad,
        'permission':permission,
        'superpermission':superpermission,
        'status_eng_list':status_eng_list,

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

# deprecated
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

# deprecated
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
    cad2d_list = SP3D_CAD2D.objects.filter(id_cad=id_cad)
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
    for item in stl_list:
        item=model_to_dict(item)
        data["stl-%s"%item["id"]] = [item]
    for item in cad2d_list:
        item=model_to_dict(item)
        data["2dcad-%s"%item["id"]] = [item]
    for item in _3mf_list:
        item=model_to_dict(item)
        data["_3mf-%s"%item["id"]] = [item]

    # load all the files in these arrays:
    files=[]
    for key in data:
        if key.startswith("cad"):
            path=data[key][0]["root_path"]+data[key][0]["file_path"]
            files.append((key,(data[key][0]["name"],open(path,'rb'))))
        if key.startswith("stl"):
            path=data[key][0]["root_path"]+data[key][0]["file_path"]
            files.append((key,(data[key][0]["name"],open(path,'rb'))))
        if key.startswith("2dcad"):
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
def print_finished(request):
    if request.method == 'POST':
        token = request.POST.get("token")
        error = request.POST.get("error")
        print "ERRROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOR IS: %s"%error
        print_id = request.POST.get('print_id')
        _print = SP3D_Print.objects.get(id=print_id)
        part = SP3D_Part.objects.get(id=_print.id_part)
        printer = SP3D_Printer.objects.get(id= _print.id_printer)
        _3mf = SP3D_3MF.objects.get(id = _print.id_3mf)
        user = User.objects.get(id=_print.id_creator)
        print "USER"
        print "USER SLACK NAME: %s"%user.sp3d_profile.slack_name
        log_file = request.FILES.get('log_file')
        try:
            # copy log that is sent into db
            new_log = DATABASE_DIRECTORY_TRANSITION + "Print_Logs/print-%s/log-%s.txt" %(print_id, print_id)
            with open(new_log, "w+") as f:
                for line in log_file:
                    f.write(line)
            # update print record
            _print.done = 1
            _print.log_id = print_id
            _print.finished_date = time.strftime('%Y-%m-%d %H:%M:%S')
            if not error :
                _print.completed = 1
            else:
                _print.completed = 0
            _print.save()
            # I import it again to make sure that I get the date times converted
            _print = SP3D_Print.objects.get(id=print_id)
            print "FINISHED DATE: %s"%_print.finished_date
            print "FINISHED DATE TYPE: %s"%type(_print.finished_date)
            print "CREATION DATE: %s"%_print.creation_date
            print "CREATION DATE TYPE: %s"%type(_print.creation_date)

            td = _print.finished_date - _print.creation_date
            print "timedelta type:%s, and its value is: %s"%(type(td),td)
            print "DEBUG235: %s"%int(td.days*86400 + td.seconds)
            _print.printing_time = int(td.days*86400 + td.seconds)
            print "printing time is :%s"%_print.printing_time
            _print.save()

            # handle slack messages
            if error:
                header = "%s: An error happened during print  :cry::cry::cry::cry::cry::cry:"%printer.name
                message = "from SP3D Cloud: %s\nSomething happened during print, was it stopped manually ?\n print %s, part %s - %s, 3mf %s: \n%s" % (error, _print.id, part.id, part.part_name, _3mf.id, user.sp3d_profile.slack_name)
                print "GOTO SLACK MESSAGE"
                slack_message(header, message, "#f44242")
            else:
                header = "%s: A print finished successfully :muscle::muscle:"%printer.name
                message = "from SP3D cloud: \ngcode successfully printed, dude\nprint %s, part %s - %s, 3mf %s\n%s"%(_print.id, part.id, part.part_name, _3mf.id, user.sp3d_profile.slack_name)
                print "GOTO SLACK MESSAGE"
                slack_message(header, message, "#43db7b")

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
        print "NOTES ARE: %s"%request.POST.get('notes')
        notes_dic = ast.literal_eval(request.POST.get('notes'))
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
                if key.startswith("cad2d"):
                    error , new_cad2d_id = upload_cad2d(files[key], int(id_part), int(cad_id), int(userid))
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
                            if (filename1.startswith("amf") or filename1.startswith("config") or filename1.startswith("gcode")):
                                filetype = filename1.rsplit('.',1)[0].split('-')[0]
                                file3mfid = filename1.rsplit('.',1)[0].split('-')[1]
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
                        note = notes_dic[_3mf_id] #add the note
                        error = upload_3mf(amf_file, config_file, configb_file, gcode_file, int(cad_id), int(userid), note)
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
            userid = 0
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
    oem_part_number=request.POST.get('oem-part-number')
    part_name=request.POST.get('part-name')
    oem_name=request.POST.get('oem')
    oem=SP3D_Oem.objects.get(name=oem_name)

    permission_list=request.POST.getlist('permissions')
    permissions="1-"
    for index in permission_list:
        permissions= permissions + "%s-" % index

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
        new_part=SP3D_Part.objects.create(creation_date=creation_date,part_number=part_number, oem_part_number=oem_part_number, id_oem=oem.id,oem_name=oem.name,id_creator=user.id, permissions=permissions, part_name=part_name, notes=notes)

        new_part_path = DATABASE_DIRECTORY_TRANSITION + "catalogue/oem-%s/part-id-%s/"%(oem.code, new_part.id)
        sub_directories=["CAD/","AMF/","CONFIG/","GCODE/","IMAGES/","STL/", "CAD2D/", "BULK/"]

        # Check that folder exists
        if not os.path.exists(new_part_path):
            os.makedirs(new_part_path)
            for subpath in sub_directories:
                os.makedirs(new_part_path + subpath)
        else:
            raise ValueError("Error: part folder already exists")

        print "NEW PART ADDED TO DB: %s"%new_part.part_number

        # if order exist, attach part created to order
        id_order=request.POST.get('id_order')
        if id_order or (id_order is not None):
            add_parts_to_order(id_order, {"%s"%new_part.id:1})
            return HttpResponseRedirect('/parts/orders/order-detail/%s'%id_order)

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
        userid = request.user.id
        files = request.FILES
        form = request.POST

        id_part = request.POST.get("part_id")
        id_cad = request.POST.get("cad_id")
        notes = request.POST.get("notes")

        amf_file = request.FILES.get('amf')
        config_file = request.FILES.get('config')
        configb_file = request.FILES.get('configb')
        gcode_file = request.FILES.get('gcode')

        upload_3mf(amf_file, config_file, configb_file, gcode_file, id_cad, userid, notes)

        print "FILES: %s"%files
        print "form is: %s"%form
        context={}
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

# add new client
@login_required
def add_client(request):
    if request.method == 'POST':
        userid = request.user.id
        files = request.FILES

        client_name = request.POST.get("client-name")
        activity = request.POST.get("activity")
        address = request.POST.get("address")
        notes = request.POST.get("notes")
        code = request.POST.get("client-code").upper()

        nb_sim_client = SP3D_Client.objects.filter(name = client_name).count()
        if nb_sim_client:
            return HttpResponseRedirect('/parts/orders/')

        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        new_client = SP3D_Client.objects.create(creation_date=creation_date, name=client_name, code=code, address= address, activity=activity, notes=notes)
        print "NEW CLIENT CREATED WITH ID: %s"%new_client.id
        context={}
    return HttpResponseRedirect('/parts/orders/')

# add new contact
@login_required
def add_contact(request):
    if request.method == 'POST':
        userid = request.user.id
        prefix = request.POST.get("contact-prefix")
        id_order = request.POST.get("order-id")
        id_client = request.POST.get("client-id")

        first_name = request.POST.get("contact-first-name")
        last_name = request.POST.get("contact-last-name")
        email = request.POST.get("contact-email")
        position = request.POST.get("contact-position")
        phone_perso = request.POST.get("contact-phone-perso")
        phone_office = request.POST.get("contact-phone-office")
        notes = request.POST.get("notes")

        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        new_contact = SP3D_Contact.objects.create(creation_date=creation_date, prefix=prefix, first_name=first_name, last_name=last_name, email=email, position= position, phone_perso= phone_perso, phone_office=phone_office, notes=notes, id_client=id_client)
        print "NEW CLIENT CREATED WITH ID: %s"%new_contact.id
        # attach contact to order
        order=SP3D_Order.objects.get(id=id_order)
        order.id_contact = int(new_contact.id)
        order.save()

        context={}
    return HttpResponseRedirect('/parts/orders/order-detail/%s/'%id_order)

# add new contact
@login_required
def change_order_contact(request):
    if request.method == 'POST':
        userid = request.user.id
        id_order = request.POST.get("id-order")
        id_contact = request.POST.get("id-contact")

        order = SP3D_Order.objects.get(id=id_order)
        order.id_contact = int(id_contact)
        order.save()
        context={}
    return HttpResponseRedirect('/parts/orders/order-detail/%s/'%id_order)

# add new order
@login_required
def add_order(request):
    if request.method == 'POST':
        userid = request.user.id
        files = request.FILES

        order_type = request.POST.get("type")
        client_id = request.POST.get("client")
        due_date = pytz.timezone("Asia/Singapore").localize(datetime.strptime(request.POST.get("date"), '%d-%m-%Y'))
        quote_number = request.POST.get("quote-number")
        po_number = request.POST.get("po-number")
        assigned_to = request.POST.get("assign-to")
        order_name = request.POST.get("name")
        notes = request.POST.get("notes")
        permission_list=request.POST.getlist('permissions')
        permissions="1-"
        for index in permission_list:
            permissions= permissions + "%s-" % index

        root_path = DATABASE_DIRECTORY_TRANSITION + "Orders/"
        # create record in DB
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        new_order = SP3D_Order.objects.create(creation_date=creation_date, root_path=root_path, name=order_name, type=order_type, id_client= client_id, quote_number= quote_number, po_number=po_number, due_date=due_date, assigned_to=assigned_to, notes=notes, id_creator=userid, permissions = permissions)

        # create folder in SERVER
        # create folder containing files
        new_order_path = root_path + "order-%s/"%new_order.id
        sub_directories=["BULK/"]
        # Check that folder exists
        if not os.path.exists(new_order_path):
            os.makedirs(new_order_path)
            for subpath in sub_directories:
                os.makedirs(new_order_path + subpath)
        else:
            raise ValueError("Error: Order folder already exists")

    return HttpResponseRedirect('/parts/orders/')

# update new order
@login_required
def update_order(request):
    if request.method == 'POST':
        userid = request.user.id
        id_order = request.POST.get("order_id")
        order_type = request.POST.get("type")
        due_date = pytz.timezone("Asia/Singapore").localize(datetime.strptime(request.POST.get("date"), '%d-%m-%Y'))
        quote_number = request.POST.get("quote-number")
        po_number = request.POST.get("po-number")
        assigned_to = request.POST.get("assign-to")
        order_name = request.POST.get("name")
        notes = request.POST.get("notes")

        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        old_order = SP3D_Order.objects.get(id=id_order)
        old_order.type = order_type
        old_order.due_date = due_date
        old_order.name = order_name
        old_order.quote_number = quote_number
        old_order.po_number = po_number
        old_order.assigned_to = assigned_to
        old_order.notes = notes
        old_order.save()

    return HttpResponseRedirect('/parts/orders/order-detail/%s'%id_order)

# update new order
@login_required
def part_to_order(request):
    if request.method == 'POST':
        userid = request.user.id
        id_order = request.POST.get("order_id")
        order = SP3D_Order.objects.get(id=id_order)

        parts_added = request.POST.getlist("parts")
        print "PARTS SELECTED ARE: %s"%parts_added
        print "POST IS: %s"%request.POST
        new_parts_qtty={}
        for key, value in request.POST.iteritems():
            if key.startswith("qtty") and value:
                id_part = key.split("-")[1]
                new_parts_qtty[id_part]=value

        add_parts_to_order(id_order, new_parts_qtty)

        # due_date = pytz.timezone("Asia/Singapore").localize(datetime.strptime(request.POST.get("date"), '%d-%m-%Y'))
        # quote_number = request.POST.get("quote-number")
        # po_number = request.POST.get("po-number")
        # assigned_to = request.POST.get("assign-to")
        # order_name = request.POST.get("name")
        # notes = request.POST.get("notes")
        #
        # creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        # old_order = SP3D_Order.objects.get(id=id_order)
        # old_order.type = order_type
        # old_order.due_date = due_date
        # old_order.name = order_name
        # old_order.quote_number = quote_number
        # old_order.po_number = po_number
        # old_order.assigned_to = assigned_to
        # old_order.notes = notes
        # old_order.save()

    return HttpResponseRedirect('/parts/orders/order-detail/%s'%id_order)

def add_parts_to_order(id_order , new_parts_dict):
    order = SP3D_Order.objects.get(id = int(id_order))
    part_dict = ast.literal_eval(order.parts)
    for key, value in new_parts_dict.iteritems():
        if key in part_dict:
            part_dict[key] = int(part_dict[key]) + int(value)
        else:
            part_dict[key] = int(value)

    # sort dictionnary
    part_dict = collections.OrderedDict(sorted(part_dict.items()))
    part_dict = json.dumps(part_dict)

    order.parts = "%s"%part_dict
    order.save()
    return True

# add new 2d drawing
@login_required
def add_cad2d(request):
    if request.method == 'POST':
        userid = request.user.id
        files = request.FILES
        form = request.POST

        id_part = request.POST.get("part_id")
        id_cad = request.POST.get("cad_id")
        notes = request.POST.get("notes")
        cad2d_file = request.FILES.get('cad2d')

        upload_cad2d(cad2d_file, id_part, id_cad, userid, notes)

        print "FILES: %s"%files
        print "form is: %s"%form
        context={}
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

# add new stl
@login_required
def add_stl(request):
    if request.method == 'POST':
        userid = request.user.id
        files = request.FILES
        form = request.POST

        id_part = request.POST.get("part_id")
        id_cad = request.POST.get("cad_id")
        notes = request.POST.get("notes")
        stl_file = request.FILES.get('stl')

        upload_stl(stl_file, id_part, id_cad, userid, notes)

        print "FILES: %s"%files
        print "form is: %s"%form
        context={}
    return HttpResponseRedirect('/parts/part-detail/%s'%id_part)

# add new bulk
@csrf_exempt
@login_required
def add_bulk(request):
    if request.method == 'POST':
        userid = request.user.id
        print "userid is: %s"%userid
        files = request.FILES
        bulk_file = request.FILES.get('bulk')
        notes = request.POST.get("notes")
        bulk_type = request.POST.get("bulk_type")
        form = request.POST
        print "BULK FORM: %s"%form
        if  bulk_type== "part":
            id_link = request.POST.get("part_id")
        elif bulk_type == "order":
            id_link = request.POST.get("order_id")

        upload_bulk(bulk_file, id_link, userid, notes, bulk_type)

        print "FILES: %s"%files
        print "form is: %s"%form
        context={}

        if bulk_type== "part":
            return HttpResponseRedirect('/parts/part-detail/%s'%id_link)
        elif bulk_type == "order":
            return HttpResponseRedirect('/parts/orders/order-detail/%s'%id_link)


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

# upload new stl file
def upload_stl(file , id_part , id_cad, userid, notes=""):
    error=""
    try:
        print "DEBUG 6000"
        part = SP3D_Part.objects.get(id = id_part)
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)

        # kepep subpath separated from path, because used later
        subpath="catalogue/oem-%s/part-id-%s/STL/"%(oem.code,id_part)
        path = DATABASE_DIRECTORY_TRANSITION + subpath
        print "DEBUG 6010"
        # Check that folder exists
        if not os.path.exists(path):
            os.makedirs(path)

        newfile=path+"%s"%file
        filename, file_extension = os.path.splitext(newfile)
        #Check that file extension is .amf
        if not file_extension.lower()==".stl":
            raise ValueError('Wrong file extension, we need a .stl')
        # Check that file with same name doesn't exist and iterate on name if it does
        if os.path.exists(newfile):
            i=1
            while os.path.exists("%s-iteration-%s%s"%(filename,i,file_extension)):
                i+=1
            newfile = "%s-iteration-%s%s"%(filename,i,file_extension)
        print "DEBUG 6030"
        # write in new file
        with open(newfile, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        print "New STL uploaded at location " + newfile
        print "DEBUG 6040"
        # create related record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        name=ntpath.basename(newfile)
        root_path=DATABASE_DIRECTORY_TRANSITION
        file_path=subpath+name
        new_stl=SP3D_STL.objects.create(creation_date=creation_date, name=name, root_path=root_path, file_path=file_path, id_cad=int(id_cad), id_creator=userid, notes=notes)
        print "STL record added to sql database with id %s" % new_stl.id
        print "DEBUG 6080"
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

# upload new stl file
def upload_bulk(file , id_link , userid, notes="", bulk_type = "part"):
    error=""
    try:
        print "DEBUG 6000"
        print "ID LINK %s"%id_link
        print "NOTES %s"%notes

        if bulk_type == "part":
            part = SP3D_Part.objects.get(id = id_link)
            oem_id=part.id_oem
            oem=SP3D_Oem.objects.get(id=oem_id)
            # keep subpath separated from path, because used later
            subpath="catalogue/oem-%s/part-id-%s/BULK/"%(oem.code,id_link)
            path = DATABASE_DIRECTORY_TRANSITION + subpath
            id_part = id_link
            id_order = 0
        elif bulk_type == "order":
            subpath="Orders/order-%s/BULK/"%id_link
            path = DATABASE_DIRECTORY_TRANSITION + subpath
            id_part = 0
            id_order = id_link
        # Check that folder exists
        if not os.path.exists(path):
            os.makedirs(path)

        newfile=path+"%s"%file
        filename, file_extension = os.path.splitext(newfile)
        # Check that file with same name doesn't exist and iterate on name if it does
        if os.path.exists(newfile):
            i=1
            while os.path.exists("%s-%s%s"%(filename,i,file_extension)):
                i+=1
            newfile = "%s-%s%s"%(filename,i,file_extension)
        print "DEBUG 6030"
        # write in new file
        with open(newfile, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        print "New BULK uploaded at location " + newfile
        print "DEBUG 6040"
        # create related record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        name=ntpath.basename(newfile)
        root_path=DATABASE_DIRECTORY_TRANSITION
        file_path=subpath+name
        new_bulk=SP3D_Bulk_Files.objects.create(creation_date=creation_date, name=name, root_path=root_path, file_path=file_path, id_part=int(id_part), id_order=int(id_order), id_creator=userid, notes=notes)
        print "Bulk record added to sql database with id %s" % new_bulk.id
        print "DEBUG 6080"
        print "DEBUG50:"
    except ValueError as err :
        print (err)
        error=error + "%s"%err
    except:
        print "BULK Uploading Failed"
        error = error + "BULK Uploading failed"

    result=[error, new_bulk.id]
    print "DEBUG51:"
    return result


# upload new 2d drawing
def upload_cad2d(file , id_part , id_cad, userid, notes=""):
    error=""
    try:
        print "DEBUG 6000"
        part = SP3D_Part.objects.get(id = id_part)
        oem_id=part.id_oem
        oem=SP3D_Oem.objects.get(id=oem_id)

        # kepep subpath separated from path, because used later
        subpath="catalogue/oem-%s/part-id-%s/CAD2D/"%(oem.code,id_part)
        path = DATABASE_DIRECTORY_TRANSITION + subpath
        print "DEBUG 6010"
        # Check that folder exists
        if not os.path.exists(path):
            os.makedirs(path)

        newfile=path+"%s"%file
        filename, file_extension = os.path.splitext(newfile)
        #Check that file extension is .amf
        if not (file_extension.lower()==".slddrw" or file_extension.lower()==".pdf"):
            raise ValueError('Wrong file extension, we need a .slddrw or .pdf')
        # Check that file with same name doesn't exist and iterate on name if it does
        if os.path.exists(newfile):
            i=1
            while os.path.exists("%s-iteration-%s%s"%(filename,i,file_extension)):
                i+=1
            newfile = "%s-iteration-%s%s"%(filename,i,file_extension)
        print "DEBUG 6030"
        # write in new file
        with open(newfile, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        print "New 2D Drawing uploaded at location " + newfile
        print "DEBUG 6040"
        # create related record in database
        creation_date=time.strftime('%Y-%m-%d %H:%M:%S')
        name=ntpath.basename(newfile)
        root_path=DATABASE_DIRECTORY_TRANSITION
        file_path=subpath+name
        new_cad2d=SP3D_CAD2D.objects.create(creation_date=creation_date, name=name, root_path=root_path, file_path=file_path, id_cad=int(id_cad), id_creator=userid, notes=notes)
        print "STL record added to sql database with id %s" % new_cad2d.id
        print "DEBUG 6080"
        print "DEBUG50:"
    except ValueError as err :
        print (err)
        error=error + "%s"%err
    except:
        print "CAD2D Uploading Failed"
        error = error + "CAD2D Uploading failed"

    result=[error, new_cad2d.id]
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
def upload_3mf(amf_file, config_file, configb_file, gcode_file, id_cad, userid, notes):
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
        new_3mf=SP3D_3MF.objects.create(creation_date=creation_date,root_path=root_path, id_cad=int(id_cad),id_creator=userid, notes=notes)
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
