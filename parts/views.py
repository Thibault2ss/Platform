# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import SP3D_Part
# Create your views here.

def index(request):
    latest_part_list = SP3D_Part.objects.order_by('id')
    context = {
        'latest_part_list': latest_part_list,
    }
    return render(request, 'parts/index.html', context)

def download(request):
    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % "/home/user01/SpareParts_Database/files/AMF/1.amf"
    return response
