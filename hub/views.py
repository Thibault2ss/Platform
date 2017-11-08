# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import os
from os.path import join
import numpy
from stl import mesh

dir_path = os.path.dirname(os.path.realpath(__file__))
# Create your views here.
def index(request):
    context = {
        'page':"index",
    }
    return render(request, 'hub/dashboard.html', context)
def account(request):
    context = {
        'page':"account",
    }
    return render(request, 'hub/account.html', context)
def printers(request):
    context = {
        'page':"printers",
    }
    return render(request, 'hub/printers.html', context)
def orders(request):
    stl_mesh = mesh.Mesh.from_file(join(dir_path, 'static', 'hub', 'stl', 'assemb6.STL'))
    volume, cog, inertia = stl_mesh.get_mass_properties()
    print("Volume                                  = {0}".format(volume))
    print("Position of the center of gravity (COG) = {0}".format(cog))
    print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
    print("                                          {0}".format(inertia[1,:]))
    print("                                          {0}".format(inertia[2,:]))
    context = {
        'page':"orders",
    }
    return render(request, 'hub/orders.html', context)
def billing(request):
    context = {
        'page':"billing",
    }
    print "YES"
    return render(request, 'hub/billing.html', context)
def table(request):
    context = {
        'page':"table",
    }
    return render(request, 'hub/table.html', context)
def typography(request):
    context = {
        'page':"typography",
    }
    return render(request, 'hub/typography.html', context)
def icons(request):
    context = {
        'page':"icons",
    }
    return render(request, 'hub/icons.html', context)
def maps(request):
    context = {
        'page':"maps",
    }
    return render(request, 'hub/maps.html', context)
def notifications(request):
    context = {
        'page':"notifications",
    }
    return render(request, 'hub/notifications.html', context)
def qualification(request):
    context = {
        'page':"qualification",
    }
    return render(request, 'hub/qualification.html', context)
