# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
    }
    return render(request, 'hub/dashboard.html', context)
def user(request):
    context = {
    }
    return render(request, 'hub/user.html', context)
def table(request):
    context = {
    }
    return render(request, 'hub/table.html', context)
def typography(request):
    context = {
    }
    return render(request, 'hub/typography.html', context)
def icons(request):
    context = {
    }
    return render(request, 'hub/icons.html', context)
def maps(request):
    context = {
    }
    return render(request, 'hub/maps.html', context)
def notifications(request):
    context = {
    }
    return render(request, 'hub/notifications.html', context)
