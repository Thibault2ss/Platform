# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import os
from os.path import join
import numpy
from stl import mesh
from django.core import serializers
from digital.forms import PartBulkFileForm, PartForm, CharacteristicsForm, PartImageForm
from users.forms import ProfilePicForm, OrganisationForm, ProfileForm
from jb.forms import FinalCardForm
from django.core.files.uploadedfile import UploadedFile
from digital.utils import getPartsClean, send_email, getPartSumUp, getfiledata, translate_matrix, findTechnoMaterial, part_type_from_name
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json

from digital.models import Part, PartImage, PartBulkFile, ClientPartStatus, PartEvent, Characteristics, PartType
from users.models import CustomUser
from jb.models import FinalCard
dir_path = os.path.dirname(os.path.realpath(__file__))

# Create your views here.
@login_required
def dashboard(request):
    parts_sumup = getPartSumUp(request.user.organisation)
    print parts_sumup
    context = {
        'page':"dashboard",
        'parts_sumup':parts_sumup,
    }
    # total_parts_indus = Parts.objects.filter()
    return render(request, 'digital/dashboard.html', context)
@login_required
def account(request):
    team_members = CustomUser.objects.filter(organisation = request.user.organisation).exclude(pk = request.user.pk)
    context = {
        'page':"account",
        'team_members':team_members,
        'formOrganisation':OrganisationForm(),
    }
    return render(request, 'digital/account.html', context)
@login_required
def printers(request):
    context = {
        'page':"printers",
    }
    return render(request, 'digital/printers.html', context)
@login_required
def parts(request):
    # query parts, and add all images to a _image attribute in Part object for more query efficiency in template
    parts, page_number, pagination_range, nb_per_page, id_status = getPartsClean(request)
    parts_sumup = getPartSumUp(request.user.organisation)
    stl_mesh = mesh.Mesh.from_file(join(dir_path, 'static', 'digital', 'stl', 'assemb6.STL'))
    volume, cog, inertia = stl_mesh.get_mass_properties()
    # print("Volume                                  = {0}".format(volume))
    # print("Position of the center of gravity (COG) = {0}".format(cog))
    # print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
    # print("                                          {0}".format(inertia[1,:]))
    # print("                                          {0}".format(inertia[2,:]))
    print pagination_range
    context = {
        'page':"parts",
        'parts':parts,
        'id_status':id_status,
        'page_number':page_number,
        'pagination_range':pagination_range,
        'nb_per_page':nb_per_page,
        'parts_sumup':parts_sumup,
        'formPartBulkFile': PartBulkFileForm(),
        'PartImageForm': PartImageForm(),
        'formPart': PartForm(created_by=request.user),
        'formCharacteristics': CharacteristicsForm(initial={'min_temp':0,'max_temp':70}),
        'formFinalCard':FinalCardForm(),
        'clientPartStatuses':ClientPartStatus.objects.all().order_by('id'),
        'search_string':request.GET.get('search', '')
    }
    return render(request, 'digital/parts.html', context)
@login_required
def billing(request):
    context = {
        'page':"billing",
    }
    print "YES"
    return render(request, 'digital/billing.html', context)
@login_required
def table(request):
    context = {
        'page':"table",
    }
    return render(request, 'digital/table.html', context)
@login_required
def typography(request):
    context = {
        'page':"typography",
    }
    return render(request, 'digital/typography.html', context)
@login_required
def icons(request):
    context = {
        'page':"icons",
    }
    return render(request, 'digital/icons.html', context)
@login_required
def maps(request):
    context = {
        'page':"maps",
    }
    return render(request, 'digital/maps.html', context)
@login_required
def notifications(request):
    context = {
        'page':"notifications",
    }
    return render(request, 'digital/notifications.html', context)
@login_required
def qualification(request):
    context = {
        'page':"qualification",
    }
    return render(request, 'digital/qualification.html', context)


@login_required
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
                    type, data = getfiledata(_file)
                    print 'debug3'
                    _new_file = form.save(type= type, data = data)
                    files_success.append({"name":(_new_file.file.name).rsplit("/",1)[1], "url":_new_file.file.url, 'id':_new_file.id, 'type':_new_file.type, 'data':_new_file.data})
                    print 'debug4'
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
        print 'debug5'
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")




@login_required
def upload_part_image(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        images_success=[]
        images_failure=[]
        print request.POST
        print request.FILES
        if request.FILES == None:
            success = False
            errors.append("No files attached")
        else:
            for _image in request.FILES.getlist('image'):
                request.FILES['file'] = _image
                form = PartImageForm(request.POST, request.FILES, created_by=request.user)
                if form.is_valid():
                    print "FORM IS VALID"
                    _new_image = form.save()
                    images_success.append({"name":(_new_image.image.name).rsplit("/",1)[1], "url":_new_image.image.url, 'id':_new_image.id})
                else:
                    print "FORM IS NOT VALID"
                    images_failure.append({"name":_image})
                    success = False
                    errors.append("form with file %s is not valid"%_image)
        data={
            "success":success,
            "errors":errors,
            "images_success":images_success,
            "images_failure":images_failure,
            "id_part": request.POST["part"],
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")






@login_required
def upload_profile_pic(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        thumbnail=''
        print request.POST
        print request.FILES
        _file = request.FILES.get('profile_pic', False)
        if request.FILES == None and _file:
            success = False
            errors.append("No files attached")
        else:
            form = ProfilePicForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                print "FORM IS VALID"
                _user = form.save()
                thumbnail = _user.profile_thumb.url
            else:
                print "FORM IS NOT VALID"
                success = False
                errors.append("form with file %s is not valid"%_image)
        data={
            "success":success,
            "errors":errors,
            "thumbnail":thumbnail,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/account/")





@login_required
def delete_bulk_file(request):
        success=True
        errors=[]
        id_file = request.GET.get("id_file")
        file = PartBulkFile.objects.get(id=id_file)
        if file.part.organisation == request.user.organisation:
            file.delete()
        else:
            success=False
            errors.append("this file does not belong to your organisation")
        data={
            "success":success,
            "errors":errors,
            }
        return JsonResponse(data)

@login_required
def request_for_indus(request):
    success=True
    errors=[]
    id_part = request.GET.get("id_part")
    part = Part.objects.get(id=id_part)
    if part.organisation == request.user.organisation:
        pendingStatus = ClientPartStatus.objects.get(id=2)
        part.status = pendingStatus
        part.save()
        if not settings.DEBUG:
            send_email(
                'digital/mail_templates/rfi.html',
                { 'user': request.user, 'part':part },
                'SP3D: New Industrialisation Request',
                'contact@sp3d.co',
                ['paul.de-misouard@sp3d.co','thibault.de-saint-sernin@sp3d.co'],
                )
        new_event = PartEvent.objects.create(
            part=part,
            created_by = request.user,
            type="STATUS_CHANGE",
            status = part.status,
            short_description = "status changed to %s"%part.status.name,
            long_description = "The part has been changed to status: %s, and will be reviewed by our team. We will get back to you ASAP"%part.status.name
        )
    else:
        success=False
        errors.append("this part does not belong to your organisation")
    data={
        "success":success,
        "errors":errors,
        }
    return JsonResponse(data)

@login_required
def change_part_status(request):
    success=True
    errors=[]
    id_part = request.GET.get("id_part")
    id_status = request.GET.get("id_status")
    part = Part.objects.get(id=id_part)
    new_status = ClientPartStatus.objects.get(id=id_status)
    if part.organisation == request.user.organisation:
        if not part.status == new_status:
            if new_status == 3 or new_status == 4:
                part.notify_status_to_client = True
            part.status = new_status
            part.save()
            if not settings.DEBUG:
                send_email(
                    'digital/mail_templates/status_change.html',
                    { 'user': request.user, 'part':part },
                    'SP3D: Client Part - Status Change',
                    'contact@sp3d.co',
                    ['paul.de-misouard@sp3d.co','thibault.de-saint-sernin@sp3d.co'],
                    )
            new_event = PartEvent.objects.create(
                part=part,
                created_by = request.user,
                type="STATUS_CHANGE",
                status = part.status,
                short_description = "status changed to %s"%part.status.name,
                long_description = "The part has been changed to status: %s, and will be reviewed by our team. We will get back to you ASAP"%part.status.name
            )
    else:
        success=False
        errors.append("this part does not belong to your organisation")
    data={
        "success":success,
        "errors":errors,
        }
    return JsonResponse(data)

@login_required
def send_recap_mail(request):
    success=True
    errors=[]
    parts = Part.objects.filter(organisation = request.user.organisation, notify_status_to_client = True).order_by('date')
    email_list = CustomUser.objects.filter(organisation = request.user.organisation).values_list('email', flat=True)
    send_email(
        'digital/mail_templates/client_update_status.html',
        { 'user': request.user, 'parts':parts },
        'Update on your Parts',
        'contact@sp3d.co',
        list(email_list),
        )
    parts.update(notify_status_to_client = False)
    data={
        "success":success,
        "errors":errors,
        }
    return JsonResponse(data)

@login_required
def get_part_history(request):
    success=True
    errors=[]
    id_part = request.GET.get("id_part")
    part = Part.objects.get(id=id_part)
    if part.organisation == request.user.organisation:
        events = PartEvent.objects.filter(part = part).order_by('date')
    else:
        success=False
        errors.append("this part does not belong to your organisation")
    data={
        "success":success,
        "errors":errors,
        "events":serializers.serialize('json', events, use_natural_foreign_keys=True),
        }
    return JsonResponse(data)

@login_required
def new_part(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        part=None
        print request.POST
        form = PartForm(request.POST, created_by=request.user)
        form_charac = CharacteristicsForm(request.POST)
        if not form.is_valid():
            print "Part form is not valid"
        if not form_charac.is_valid():
            print "Charac form is not valid"
        if all((form.is_valid(), form_charac.is_valid())):
            _characteristics = form_charac.save()
            print "ALL FORMS ARE VALID"
            _new_part = form.save(characteristics = _characteristics)
            part = serializers.serialize("json", [_new_part],  use_natural_foreign_keys=True)[1:-1]
        else:
            print "FORM IS NOT VALID"
            success = False
            errors.append("form is not valid")
        data={
            "success":success,
            "errors":errors,
            "part":part,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")

@login_required
def update_part_card(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        new_part = None
        part = Part.objects.get(id=request.POST.get("id_part"))
        if part.organisation == request.user.organisation:
            print request.POST
            form = PartForm(request.POST, created_by = request.user, instance = part)
            if part.characteristics is None:
                form_charac = CharacteristicsForm(request.POST)
            else:
                form_charac = CharacteristicsForm(request.POST, instance=part.characteristics)
            if all((form.is_valid(), form_charac.is_valid())):
                _characteristics = form_charac.save()
                print "ALL FORMS ARE VALID"
                _new_part = form.save(characteristics = _characteristics)
                new_part = serializers.serialize("json", [_new_part],  use_natural_foreign_keys=True)[1:-1]
            else:
                print "FORM IS NOT VALID"
                success = False
                errors.append("form is not valid")
        else:
            print "NOT RIGHT ORGANISATION OR PART"
            success = False
            errors.append("Part doesn't belong to Organisation")

        data={
            "success":success,
            "errors":errors,
            "part":new_part,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")

@login_required
def update_final_card(request):
    if request.method == 'POST':
        success = True
        errors = []
        print request.POST
        print request.POST["id_part"]
        part = Part.objects.get(id=request.POST.get("id_part"))
        if part.organisation == request.user.organisation:
            if part.final_card is None:
                form = FinalCardForm(request.POST)
                if form.is_valid():
                    _final_card = form.save()
                    part.final_card = _final_card
                    part.save()
                else:
                    success = False
                    errors.append("Form is not Valid Step 1")
            else:
                form = FinalCardForm(request.POST, instance=part.final_card)
                if form.is_valid():
                    _final_card= form.save()
                else:
                    success = False
                    errors.append("Form is not Valid Step 2")
            final_card = serializers.serialize("json", [_final_card],  use_natural_foreign_keys=True)[1:-1]
        else:
            print "NOT RIGHT ORGANISATION OR PART"
            success = False
            errors.append("Part doesn't belong to Organisation")

        data={
            "success":success,
            "errors":errors,
            "final_card":final_card,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")



@login_required
def update_profile(request):
    if request.method == 'POST':
        success = True
        errors = []
        print request.POST
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            success = False
            errors.append("Form not valid")
        data={
            "success":success,
            "errors":errors,
            }
        return JsonResponse(data)
    return HttpResponseRedirect("/digital/account/")


@login_required
def update_organisation(request):
    if request.method == 'POST':
        success = True
        errors = []
        print request.POST
        form = OrganisationForm(request.POST, instance=request.user.organisation)
        if form.is_valid():
            form.save()
        else:
            success = False
            errors.append("Form not valid")
        data={
            "success":success,
            "errors":errors,
            }
        return JsonResponse(data)
    return HttpResponseRedirect("/digital/account/")



@login_required
def upload_solution_matrix(request):
    if request.method == 'POST' and request.user.is_staff:
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
            errors, warnings = translate_matrix(request.FILES.get('file'))
            print errors
        data={
            "success":success,
            "errors":errors,
            "warnings":warnings,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")

@login_required
def get_best_solution(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        techno_material_list=[]
        discarded_criterias={}
        perfect_match=False
        print request.POST
        if request.POST.get('id_part', None):
            part = get_object_or_404(Part, id = request.POST.get('id_part'))
            techno_materials, perfect_match, error_list, discarded_criterias = findTechnoMaterial(part)
            errors += error_list
            if techno_materials:
                techno_material_list=techno_materials
            else:
                success = False
                errors.append("NO MATCH FOUND")
        else:
            success=False
            errors.append("NO ID_PART IN REQUEST")

        data={
            "success":success,
            "errors":errors,
            'techno_material_list':serializers.serialize("json", techno_material_list,  use_natural_foreign_keys=True),
            'perfect_match':perfect_match,
            'discarded_criterias':discarded_criterias,
        }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")



@login_required
def get_characteristics(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        characteristics = None
        if request.POST.get('id_type', None):
            part_type = get_object_or_404(PartType, id = request.POST.get('id_type'))
            if part_type.characteristics:
                characteristics = part_type.characteristics.natural_key()
            else:
                success = False
                errors.append("NO CHARACTERISTICS ATTACHED TO PART TYPE")
        else:
            success=False
            errors.append("NO ID_TYPE IN REQUEST")

        data={
            "success":success,
            "errors":errors,
            'characteristics':characteristics,
        }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")



def get_part_type(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        id_part_type = None
        id_appliance_family = None
        characteristics = None
        if request.POST.get('part_name', None):
            part_type = part_type_from_name(request.POST.get('part_name'))
            if part_type:
                id_part_type = part_type['part_type'].id
                id_appliance_family = part_type['part_type'].appliance_family.id
                characteristics = part_type['part_type'].characteristics.natural_key()
            else:
                success=False
                errors.append("PAR NAME DID NOT MATCH ANY PART")
        else:
            success=False
            errors.append("NO PART_NAME IN REQUEST")

        data={
            "success":success,
            "errors":errors,
            'id_part_type':id_part_type,
            'id_appliance_family':id_appliance_family,
            'characteristics':characteristics,
        }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")
