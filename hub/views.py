# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

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
    context = {
        'page':"orders",
    }
    return render(request, 'hub/orders.html', context)
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
