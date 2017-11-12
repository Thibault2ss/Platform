# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
import os
from os.path import join
import numpy
from stl import mesh
from digital.models import Part, PartImage, PartBulkFile, ClientPartStatus
from django.core import serializers
from digital.forms import PartBulkFileForm
from django.core.files.uploadedfile import UploadedFile
from digital.utils import getPartsClean, send_email


dir_path = os.path.dirname(os.path.realpath(__file__))
# Create your views here.
def index(request):
    context = {
        'page':"index",
    }
    return render(request, 'digital/dashboard.html', context)
def account(request):
    context = {
        'page':"account",
    }
    return render(request, 'digital/account.html', context)
def printers(request):
    context = {
        'page':"printers",
    }
    return render(request, 'digital/printers.html', context)
def parts(request):
    # query parts, and add all images to a _image attribute in Part object for more query efficiency in template
    parts = getPartsClean(request)
    print serializers.serialize("json", parts, use_natural_foreign_keys=True)
    stl_mesh = mesh.Mesh.from_file(join(dir_path, 'static', 'digital', 'stl', 'assemb6.STL'))
    volume, cog, inertia = stl_mesh.get_mass_properties()
    # print("Volume                                  = {0}".format(volume))
    # print("Position of the center of gravity (COG) = {0}".format(cog))
    # print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
    # print("                                          {0}".format(inertia[1,:]))
    # print("                                          {0}".format(inertia[2,:]))
    context = {
        'page':"parts",
        'parts':parts,
        'formPartBulkFile': PartBulkFileForm(),
    }
    return render(request, 'digital/parts.html', context)
def billing(request):
    context = {
        'page':"billing",
    }
    print "YES"
    return render(request, 'digital/billing.html', context)
def table(request):
    context = {
        'page':"table",
    }
    return render(request, 'digital/table.html', context)
def typography(request):
    context = {
        'page':"typography",
    }
    return render(request, 'digital/typography.html', context)
def icons(request):
    context = {
        'page':"icons",
    }
    return render(request, 'digital/icons.html', context)
def maps(request):
    context = {
        'page':"maps",
    }
    return render(request, 'digital/maps.html', context)
def notifications(request):
    context = {
        'page':"notifications",
    }
    return render(request, 'digital/notifications.html', context)
def qualification(request):
    context = {
        'page':"qualification",
    }
    return render(request, 'digital/qualification.html', context)

def upload_part_bulk_file(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        files_success=[]
        files_failure=[]
        print request.POST
        print request.FILES
        if request.FILES == None:
            success = False
            errors.append("No files attached")
        else:
            for _file in request.FILES.getlist('file'):
                request.FILES['file'] = _file
                form = PartBulkFileForm(request.POST, request.FILES, created_by=request.user)
                if form.is_valid():
                    print "FORM IS VALID"
                    _new_file = form.save()
                    files_success.append({"name":(_new_file.file.name).rsplit("/",1)[1], "url":_new_file.file.url})
                else:
                    print "FORM IS NOT VALID"
                    files_failure.append({"name":_file})
                    success = False
                    errors.append("form with file %s is not valid"%_file)
        data={
            "success":success,
            "errors":errors,
            "files_success":files_success,
            "files_failure":files_failure,
            "id_part": request.POST["part"],
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")

def request_for_indus(request):
    success=True
    errors=[]
    id_part = request.GET.get("id_part")
    part = Part.objects.get(id=id_part)
    if part.organisation == request.user.organisation:
        pendingStatus = ClientPartStatus.objects.get(id=2)
        part.status = pendingStatus
        part.save()
        send_email(
            'digital/mail_templates/rfi.html',
            { 'user': request.user, 'part':part },
            'SP3D: New Industrialisation Request',
            'contact@sp3d.co',
            ['thibault.de-saint-sernin@sp3d.co'],
            )
    else:
        success=False
    data={
        "success":success,
        "errors":errors,
        }
    return JsonResponse(data)
