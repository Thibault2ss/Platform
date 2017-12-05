
from __future__ import unicode_literals
from digital.models import Part, PartImage, PartBulkFile
from digital.decorators import postpone
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from digital.models import Part, PartImage, PartBulkFile, Characteristics
from jb.models import CoupleTechnoMaterial, Technology, Material
from django.db.models import Case, IntegerField, Sum, When, Q
from django.shortcuts import get_object_or_404
import tempfile
from stl import mesh
import numpy
import os
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from digital.models import ClientPartStatus
import csv
from django.db.models import Q
dir_path = os.path.dirname(os.path.realpath(__file__))

DEFAULT_NB_PER_PAGE = 20
DEFAULT_PAGE_RANGE = 10

def getPartsClean(request):
    # FILTERS:
    filters ={}
    id_status = request.GET.get('status', '')
    filters['organisation'] = request.user.organisation
    if id_status:
        filters['status'] = get_object_or_404(ClientPartStatus, pk=id_status)

    # search
    search_string = request.GET.get('search', '')
    search_q  = Q(name__icontains=search_string) | Q(reference__icontains=search_string)

    all_parts = Part.objects.filter(search_q, **filters).order_by('date_created')


    # PAGINATION
    page = request.GET.get('page', '')
    nb_per_page = request.GET.get('nb-per-page', '')
    if not page:
        page = 1
    if not nb_per_page:
        nb_per_page = DEFAULT_NB_PER_PAGE
    paginator = Paginator(all_parts, nb_per_page) #show nb_per_page elements per page
    try:
        parts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = 1
        parts = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.num_pages
        parts = paginator.page(page)

    first_pagination_number = (int(page)/DEFAULT_PAGE_RANGE)*DEFAULT_PAGE_RANGE + 1
    pagination_range=[]
    for i in range(DEFAULT_PAGE_RANGE):
        # print paginator.num_pages
        if first_pagination_number + i > paginator.num_pages:
            break
        pagination_range.append(first_pagination_number + i)
        print(first_pagination_number + i)



    # CONCATENATION
    parts_dict = dict([(part.id, part) for part in parts])

    # inject pictures directly in
    pictures = PartImage.objects.filter(part__in=parts)
    relation_dict = {}
    for pic in pictures:
        relation_dict.setdefault(pic.part.id, []).append(pic)
    for id, images in relation_dict.items():
        parts_dict[id].images = images


    # inject files directly in
    bulk_files = PartBulkFile.objects.filter(part__in=parts)
    relation_dict = {}
    for file in bulk_files:
        relation_dict.setdefault(file.part.id, []).append(file)
    for id, files in relation_dict.items():
        parts_dict[id].bulk_files = files


    return parts, page, pagination_range, nb_per_page, id_status




@postpone
def send_email(html_path, context, subject, from_email, to):
    html = get_template(html_path)
    html_content = html.render(context)
    msg = EmailMessage(subject, html_content, from_email, to=to)
    msg.content_subtype = 'html'
    msg.send()
    return True


def getPartSumUp(organisation):
    parts_sumup = Part.objects.filter(organisation = organisation).aggregate(
        parts_total = Sum(Case(When(~Q(pk=None), then=1),default = 0, output_field=IntegerField())),
        parts_new = Sum(Case(When(status__id=1, then=1), default = 0, output_field=IntegerField())),
        parts_pending_indus = Sum(Case(When(status__id=2, then=1), default = 0, output_field=IntegerField())),
        parts_disqualified = Sum(Case(When(status__id=3, then=1),default = 0,output_field=IntegerField())),
        parts_industrialized = Sum(Case(When(status__id=4, then=1),default = 0,output_field=IntegerField())),
        parts_metal = Sum(Case(When(material__family="metal", then=1),default = 0,output_field=IntegerField())),
        parts_plastic = Sum(Case(When(material__family="plastic", then=1),default = 0,output_field=IntegerField())),
    )
    for key, item in parts_sumup.iteritems():
        if item is None:
            parts_sumup[key]=0
    return parts_sumup

def getOrganisationCapacity(organisation):
    images = PartImage.objects.filter

def getfiledata(file):
    data=''
    type="BULK"
    filename, file_extension = os.path.splitext('%s'%file)

    if file_extension.lower() == '.stl':
        type="STL"
        temp = tempfile.NamedTemporaryFile(delete = False)
        # temp = open(dir_path + "/test.stl", 'wb+')
        for chunk in file.chunks():
            temp.write(chunk)
        temp.close()
        print "temp file name: %s"%temp.name
        # stl_mesh = mesh.Mesh.from_file(os.path.join(dir_path, 'test.stl'))
        stl_mesh = mesh.Mesh.from_file(temp.name)
        volume, cog, inertia = stl_mesh.get_mass_properties()

        print("Volume                                  = {0}".format(volume))
        print("Position of the center of gravity (COG) = {0}".format(cog))
        print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
        print("                                          {0}".format(inertia[1,:]))
        print("                                          {0}".format(inertia[2,:]))
        os.unlink(temp.name)
        data = {
            'volume': volume,
            'cog': cog.tolist(),
            'inertia': inertia.tolist(),
        }
        print 'DEBUG 1'

    if file_extension.lower() in ['.sldprt','.sldasm','.step','.iges','.gcode']:
        type="3D"
    if file_extension.lower() in ['.dwg', '.dxf']:
        type='2D'
        print 'DEBUG 2'
    return type, json.dumps(data)


def translate_matrix(file):
    filename, file_extension = os.path.splitext('%s'%file)

    if file_extension.lower() == '.csv':
        temp = tempfile.NamedTemporaryFile(delete = False)
        # copy file in temporary file
        for chunk in file.chunks():
            temp.write(chunk)
        temp.close()
        print "temp file name: %s"%temp.name


        # remove all old characteristics card attached to couple techno-material
        techno_material_couples = CoupleTechnoMaterial.objects.all()
        charac_card = Characteristics.objects.filter(techno_material__in = techno_material_couples).delete()

        fieldnames = [
            'solution_id',
            'is_transparent',
            'is_food_grade',
            'is_flame_retardant',
            'is_rubbery',
            'is_visual',
            'is_chemical_resistant',
            'is_water_resistant',
            # 'max_X',
            # 'max_Y',
            # 'max_Z',
            'min_temp',
            'max_temp',
            'technology',
            'material'
        ]
        error_list=[]
        with open(temp.name, 'rb+') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames = fieldnames)
            for row in reader:
                if row['solution_id'] and row['material'] and row['technology'] and RepresentsInt(row['solution_id']) :
                    error, cleaned_dic = CleanCSV(row)
                    if error:
                        error['solution_id'] = row['solution_id']
                        error_list.append(error)
                        print "ERROR: %s"%error
                    else:
                        new_card = Characteristics(**cleaned_dic)
                        new_card.save()

        os.unlink(temp.name) #delete temp file

    return error_list


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def CleanCSV(dic):
    error={}
    false_match = ['false', 'no', 'n']
    cleaned_dic = {}
    cleaned_dic['is_transparent'] = not dic['is_transparent'].lower() in false_match
    cleaned_dic['is_food_grade'] = not dic['is_food_grade'].lower() in false_match
    cleaned_dic['is_rubbery'] = not dic['is_rubbery'].lower() in false_match
    cleaned_dic['is_visual'] = not dic['is_visual'].lower() in false_match
    cleaned_dic['is_water_resistant'] = not dic['is_visual'].lower() in false_match
    cleaned_dic['is_chemical_resistant'] = not dic['is_chemical_resistant'].lower() in false_match
    cleaned_dic['is_flame_retardant'] = not dic['is_flame_retardant'].lower() in false_match

    # if is_flame_retardant, look up level:
    if cleaned_dic['is_flame_retardant']:
        temp_error, flame_retardancy = Characteristics().get_retardant_choice(dic['is_flame_retardant'])
        if temp_error:
            error['flame_retardancy'] = temp_error
        cleaned_dic['flame_retardancy'] = flame_retardancy

    # check if technology exists
    try:
        cleaned_dic['technology'] = Technology.objects.get(name=dic['technology'])
    except Technology.DoesNotExist:
        cleaned_dic['technology'] = None
        error['technology'] = 'Technology %s does not match a technology in database'%dic['technology']

    # check if material exists
    try:
        cleaned_dic['material'] = Material.objects.get(name=dic['material'])
    except Material.DoesNotExist:
        cleaned_dic['material'] = None
        error['material'] = 'Material %s does not match a material in database'%dic['material']

    if (not (cleaned_dic['material'] is None)) and (not (cleaned_dic['technology'] is None)):
        try:
            techno_material = CoupleTechnoMaterial.objects.get(material= cleaned_dic['material'], technology = cleaned_dic['technology'])
        except CoupleTechnoMaterial.DoesNotExist:
            techno_material = CoupleTechnoMaterial(material= cleaned_dic['material'], technology = cleaned_dic['technology'])
            techno_material.save()
        cleaned_dic.pop('material', None)
        cleaned_dic.pop('technology', None)
        # cleaned_dic['techno_material'] = techno_material

    # Max X, Y, Z, Min Temp, Max_temp:
    # if RepresentsInt(dic['max_X']):
    #     cleaned_dic['max_X'] = dic['max_X']
    # else:
    #     error["max_X"]="max X is not an Integer"
    #
    # if RepresentsInt(dic['max_Y']):
    #     cleaned_dic['max_Y'] = dic['max_Y']
    # else:
    #     error["max_Y"]="max Y is not an Integer"
    #
    # if RepresentsInt(dic['max_Z']):
    #     cleaned_dic['max_Z'] = dic['max_Z']
    # else:
    #     error["max_Z"]="max Z is not an Integer"

    if RepresentsInt(dic['max_temp']):
        cleaned_dic['max_temp'] = dic['max_temp']
    else:
        error["max_temp"]="max Temp is not an Integer"

    if RepresentsInt(dic['min_temp']):
        cleaned_dic['min_temp'] = dic['min_temp']
    else:
        error["min_temp"]="min Temp is not an Integer"

    return error, cleaned_dic

def findTechnoMaterial(part):
    errors = []
    list_couple_techno_material = None
    args = []
    kwargs = {}

    # check if part has characteristics attached
    if not part.characteristics:
        errors.append("No prevision Possible, Part has no characteristics attached !")
        return None, errors, None


    # set up first filters as args for Q and kwargs for rest
    characs = part.characteristics
    kwargs['characteristics__is_visual'] = characs.is_visual
    kwargs['characteristics__is_transparent'] = characs.is_transparent
    kwargs['characteristics__is_water_resistant'] = characs.is_water_resistant
    kwargs['characteristics__is_rubbery'] = characs.is_rubbery
    kwargs['characteristics__is_chemical_resistant'] = characs.is_chemical_resistant
    kwargs['material__characteristics__is_flame_retardant'] = characs.is_flame_retardant
    kwargs['characteristics__is_food_grade'] = characs.is_food_grade
    if characs.is_flame_retardant:
        if characs.flame_retardancy == 'NA':higher_ret_list = ['NA', 'HB', 'V2', 'V1', 'V0']
        if characs.flame_retardancy == 'HB':higher_ret_list = ['HB', 'V2', 'V1', 'V0']
        if characs.flame_retardancy == 'V2':higher_ret_list = ['V2', 'V1', 'V0']
        if characs.flame_retardancy == 'V1':higher_ret_list = ['V1', 'V0']
        if characs.flame_retardancy == 'V0':higher_ret_list = ['V0']
        kwargs['material__characteristics__flame_retardancy__in'] = higher_ret_list
    if characs.min_temp and characs.max_temp:
        kwargs['characteristics__min_temp__lte'] = characs.min_temp
        kwargs['characteristics__max_temp__gte'] = characs.max_temp
    if part.length and part.width and part.height:
        args.append(
            (Q(technology__max_X__gte=part.length) & Q(technology__max_Y__gte=part.width) & Q(technology__max_Z__gte=part.height)) |
            (Q(technology__max_X__gte=part.length) & Q(technology__max_Y__gte=part.height) & Q(technology__max_Z__gte=part.width)) |
            (Q(technology__max_X__gte=part.width) & Q(technology__max_Y__gte=part.length) & Q(technology__max_Z__gte=part.height)) |
            (Q(technology__max_X__gte=part.width) & Q(technology__max_Y__gte=part.height) & Q(technology__max_Z__gte=part.length)) |
            (Q(technology__max_X__gte=part.height) & Q(technology__max_Y__gte=part.length) & Q(technology__max_Z__gte=part.width)) |
            (Q(technology__max_X__gte=part.height) & Q(technology__max_Y__gte=part.width) & Q(technology__max_Z__gte=part.length))
        )


    # first query filter
    list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
    print "QUERY 1"
    print kwargs

    # 2 query filter if 1 had no match
    if (not list_couple_techno_material) and ('characteristics__min_temp__lte' in kwargs) and ('characteristics__max_temp__gte' in kwargs):
        if ('characteristics__min_temp__lte' in kwargs) and ('characteristics__max_temp__gte' in kwargs):
            kwargs.pop('characteristics__min_temp__lte')
            kwargs.pop('characteristics__max_temp__gte')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
            print "QUERY 2"
            print kwargs

    # 3 query filter if 2 had no match
    if (not list_couple_techno_material) and ('characteristics__is_transparent' in kwargs):
        kwargs.pop('characteristics__is_transparent')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 3"
        print kwargs

    # 4 query filter if 3 had no match
    if (not list_couple_techno_material) and ('material__characteristics__is_flame_retardant' in kwargs):
        kwargs.pop('material__characteristics__is_flame_retardant')
        if 'material__characteristics__flame_retardancy__in' in kwargs: kwargs.pop('material__characteristics__flame_retardancy__in')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 4"
        print kwargs

    # 5 query filter if 4 had no match
    if (not list_couple_techno_material) and ('characteristics__is_chemical_resistant' in kwargs):
        kwargs.pop('characteristics__is_chemical_resistant')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 5"
        print kwargs

    # 6 query filter if 5 had no match
    if (not list_couple_techno_material) and ('characteristics__is_water_resistant' in kwargs):
        kwargs.pop('characteristics__is_water_resistant')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 6"
        print kwargs

    # 7 query filter if 6 had no match
    if (not list_couple_techno_material) and ('characteristics__is_visual' in kwargs):
        kwargs.pop('characteristics__is_visual')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 7"
        print kwargs

    # 8 query filter if 7 had no match
    if (not list_couple_techno_material) and ('characteristics__is_food_grade' in kwargs):
        kwargs.pop('characteristics__is_food_grade')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 8"
        print kwargs

    # 9 query filter if 8 had no match
    if (not list_couple_techno_material) and ('characteristics__is_rubbery' in kwargs):
        kwargs.pop('characteristics__is_rubbery')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 9"
        print kwargs

    return list_couple_techno_material, errors, kwargs
