
from __future__ import unicode_literals
from digital.models import Part, PartImage, PartBulkFile
from digital.decorators import postpone
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from digital.models import Part, PartImage, PartBulkFile, Characteristics, PartType, ApplianceFamily
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
    error_list=[]
    warning_list=[]
    filename, file_extension = os.path.splitext('%s'%file)

    # check file extension
    if not file_extension.lower() == '.csv':
        error_list.append("WRONG FILE EXTENSION")
        return error_list


    # check file name
    if filename.lower() == 'techno_materials':
        fieldnames = ['technology','material', 'c','d','e','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    elif filename.lower() == 'materials':
        fieldnames = ['material','description', 'type','d','e','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    elif filename.lower() == 'technologies':
        fieldnames = ['technology','max_X', 'max_Y','max_Z','description','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    elif filename.lower() == 'part_types':
        fieldnames = ['part_type','appliance_family', 'c','d','e','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    else:
        error_list.append("WRONG FILE NAME")
        return error_list


    # copy csv in temporary file
    temp = tempfile.NamedTemporaryFile(delete = False)
    for chunk in file.chunks():
        temp.write(chunk)
    temp.close()
    print "temp file name: %s"%temp.name


    # treat temporary file to populate database
    with open(temp.name, 'rb+') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames = fieldnames)
        for index, row in enumerate(reader, start=1):
            if index == 1:continue
            if row.get('material',None) or row.get('technology',None) or row.get('part_type',None) :
                error, warning, cleaned_dic = CleanCSV(row)
                if error:
                    error['row_number'] = index
                    error_list.append(error)
                    print "ERROR: %s"%error
                else:
                    # add warnings to list
                    if warning:
                        warning['row_number'] = index
                        warning_list.append(warning)


                    # remove all fields not related
                    if 'techno_material' in cleaned_dic:
                        cleaned_dic.pop('material', None)
                        cleaned_dic.pop('technology', None)
                        cleaned_dic.pop('part_type', None)
                        cleaned_dic.pop('part', None)
                    elif 'material' in cleaned_dic:
                        cleaned_dic.pop('techno_material', None)
                        cleaned_dic.pop('technology', None)
                        cleaned_dic.pop('part_type', None)
                        cleaned_dic.pop('part', None)
                    elif 'technology' in cleaned_dic:
                        cleaned_dic.pop('techno_material', None)
                        cleaned_dic.pop('material', None)
                        cleaned_dic.pop('part_type', None)
                        cleaned_dic.pop('part', None)
                    elif 'part_type' in cleaned_dic:
                        cleaned_dic.pop('techno_material', None)
                        cleaned_dic.pop('material', None)
                        cleaned_dic.pop('technology', None)
                        cleaned_dic.pop('part', None)


                    # check if characteristic card already exists, update, otherwise create new card
                    if cleaned_dic.get('techno_material',None) and cleaned_dic['techno_material'].characteristics:
                        techno_material = cleaned_dic.pop('techno_material')
                        Characteristics.objects.filter(id=techno_material.characteristics.id).update(**cleaned_dic)
                    elif cleaned_dic.get('material',None) and cleaned_dic['material'].characteristics:
                        material = cleaned_dic.pop('material')
                        Characteristics.objects.filter(id=material.characteristics.id).update(**cleaned_dic)
                    elif cleaned_dic.get('technology',None) and cleaned_dic['technology'].characteristics:
                        technology = cleaned_dic.pop('technology')
                        Characteristics.objects.filter(id=technology.characteristics.id).update(**cleaned_dic)
                    elif cleaned_dic.get('part_type',None) and cleaned_dic['part_type'].characteristics:
                        part_type = cleaned_dic.pop('part_type')
                        Characteristics.objects.filter(id=part_type.characteristics.id).update(**cleaned_dic)
                    else:
                        new_card = Characteristics(**cleaned_dic)
                        new_card.save()

    os.unlink(temp.name) #delete temp file

    return error_list, warning_list


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def CleanCSV(dic):
    error={}
    warning={}
    positive_match = ['true', 'yes', 'y']
    cleaned_dic = {}
    cleaned_dic['is_transparent'] = dic['is_transparent'].lower() in positive_match
    cleaned_dic['is_food_grade'] = dic['is_food_grade'].lower() in positive_match
    cleaned_dic['is_rubbery'] = dic['is_rubbery'].lower() in positive_match
    cleaned_dic['is_visual'] = dic['is_visual'].lower() in positive_match
    cleaned_dic['is_water_resistant'] = dic['is_water_resistant'].lower() in positive_match
    cleaned_dic['is_chemical_resistant'] = dic['is_chemical_resistant'].lower() in positive_match
    cleaned_dic['is_flame_retardant'] = dic['is_flame_retardant'].lower() in positive_match

    if RepresentsInt(dic.get('max_temp',None)):
        cleaned_dic['max_temp'] = dic['max_temp']
    else:
        warning["max_temp"]="max Temp is not an Integer"

    if RepresentsInt(dic.get('min_temp',None)):
        cleaned_dic['min_temp'] = dic['min_temp']
    else:
        warning["min_temp"]="min Temp is not an Integer"


    # if is_flame_retardant, look up level:
    if cleaned_dic.get('is_flame_retardant',None) and dic.get('flame_retardancy',None):
        temp_error, flame_retardancy = Characteristics().get_retardant_choice(dic['flame_retardancy'])
        if temp_error:
            error['flame_retardancy'] = temp_error
        cleaned_dic['flame_retardancy'] = flame_retardancy


    # check if technology exists
    if dic.get('technology',None):
        try:
            cleaned_dic['technology'] = Technology.objects.get(name=dic['technology'])
        except Technology.DoesNotExist:
            error['technology'] = 'Technology %s does not match a technology in database'%dic['technology']


    # check if material exists
    if dic.get('material', None):
        try:
            cleaned_dic['material'] = Material.objects.get(name=dic['material'])
        except Material.DoesNotExist:
            error['material'] = 'Material %s does not match a material in database'%dic['material']


    # check if part_type exists
    if dic.get('part_type', None) and dic.get('appliance_family', None):
        try:
            temp_appliance_family = ApplianceFamily.objects.get(name=dic['appliance_family'])
            cleaned_dic['part_type'] = PartType.objects.get(name=dic['part_type'], appliance_family = temp_appliance_family)
        except ApplianceFamily.DoesNotExist:
            error['appliance_family'] = 'No match on appliance family %s'%dic['appliance_family']
        except PartType.DoesNotExist:
            part_type = PartType(name= dic['part_type'], appliance_family = temp_appliance_family)
            part_type.save()
            cleaned_dic['part_type'] = part_type


    # check if techno_material exists
    if cleaned_dic.get('material', None) and cleaned_dic.get('technology',None):
        try:
            techno_material = CoupleTechnoMaterial.objects.get(material= cleaned_dic['material'], technology = cleaned_dic['technology'])
        except CoupleTechnoMaterial.DoesNotExist:
            techno_material = CoupleTechnoMaterial(material= cleaned_dic['material'], technology = cleaned_dic['technology'])
            techno_material.save()
        cleaned_dic['techno_material'] = techno_material

    return error, warning, cleaned_dic

def findTechnoMaterial(part):
    errors = []
    list_couple_techno_material = None
    args = []
    kwargs = {}
    perfect_match = False
    discarded_criterias = {}

    # check if part has characteristics attached
    if not part.characteristics:
        errors.append("No prevision Possible, Part has no characteristics attached !")
        return None, errors, None


    # set up first filters as args for Q and kwargs for rest
    characs = part.characteristics
    # discriminant criterias:
    kwargs['characteristics__is_rubbery'] = characs.is_rubbery
    kwargs['characteristics__is_visual'] = characs.is_visual
    kwargs['characteristics__is_transparent'] = characs.is_transparent
    if part.length and part.width and part.height:
        args.append(
            (Q(technology__max_X__gte=part.length) & Q(technology__max_Y__gte=part.width) & Q(technology__max_Z__gte=part.height)) |
            (Q(technology__max_X__gte=part.length) & Q(technology__max_Y__gte=part.height) & Q(technology__max_Z__gte=part.width)) |
            (Q(technology__max_X__gte=part.width) & Q(technology__max_Y__gte=part.length) & Q(technology__max_Z__gte=part.height)) |
            (Q(technology__max_X__gte=part.width) & Q(technology__max_Y__gte=part.height) & Q(technology__max_Z__gte=part.length)) |
            (Q(technology__max_X__gte=part.height) & Q(technology__max_Y__gte=part.length) & Q(technology__max_Z__gte=part.width)) |
            (Q(technology__max_X__gte=part.height) & Q(technology__max_Y__gte=part.width) & Q(technology__max_Z__gte=part.length))
        )
    # non discriminant criterias:
    if characs.is_water_resistant:
        kwargs['characteristics__is_water_resistant'] = characs.is_water_resistant
    else:
        discarded_criterias['water resistant'] = characs.is_water_resistant
    if characs.is_water_resistant:
        kwargs['characteristics__is_chemical_resistant'] = characs.is_chemical_resistant
    else:
        discarded_criterias['chemical resistant'] = characs.is_chemical_resistant
    if characs.is_flame_retardant:
        kwargs['material__characteristics__is_flame_retardant'] = characs.is_flame_retardant
    else:
        discarded_criterias['flame retardant'] = characs.is_flame_retardant
    if characs.is_food_grade:
        kwargs['characteristics__is_food_grade'] = characs.is_food_grade
    else:
        discarded_criterias['food grade'] = characs.is_food_grade
    if characs.is_flame_retardant:
        if characs.flame_retardancy == 'NA':higher_ret_list = ['NA', 'HB', 'V2', 'V1', 'V0']
        if characs.flame_retardancy == 'HB':higher_ret_list = ['HB', 'V2', 'V1', 'V0']
        if characs.flame_retardancy == 'V2':higher_ret_list = ['V2', 'V1', 'V0']
        if characs.flame_retardancy == 'V1':higher_ret_list = ['V1', 'V0']
        if characs.flame_retardancy == 'V0':higher_ret_list = ['V0']
        kwargs['material__characteristics__flame_retardancy__in'] = higher_ret_list
    # nullable criterias:
    if (characs.min_temp is not None) and (characs.max_temp is not None):
        kwargs['material__characteristics__min_temp__lte'] = characs.min_temp
        kwargs['material__characteristics__max_temp__gte'] = characs.max_temp


    # QUERIES
    # first query filter
    list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
    if list_couple_techno_material:perfect_match=True
    print "QUERY 1"
    print kwargs

    # 2 query filter if 1 had no match
    if (not list_couple_techno_material) and ('material__characteristics__min_temp__lte' in kwargs) and ('material__characteristics__max_temp__gte' in kwargs):
        discarded_criterias['min temp'] = kwargs.pop('material__characteristics__min_temp__lte')
        discarded_criterias['max temp'] = kwargs.pop('material__characteristics__max_temp__gte')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 2"
        print kwargs

    # 3 query filter if 2 had no match
    if (not list_couple_techno_material) and ('characteristics__is_transparent' in kwargs):
        discarded_criterias['transparent'] = kwargs.pop('characteristics__is_transparent')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 3"
        print kwargs

    # 4 query filter if 3 had no match
    if (not list_couple_techno_material) and ('material__characteristics__is_flame_retardant' in kwargs):
        discarded_criterias['flame retardant'] = kwargs.pop('material__characteristics__is_flame_retardant')
        if 'material__characteristics__flame_retardancy__in' in kwargs: kwargs.pop('material__characteristics__flame_retardancy__in')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 4"
        print kwargs

    # 5 query filter if 4 had no match
    if (not list_couple_techno_material) and ('characteristics__is_chemical_resistant' in kwargs):
        discarded_criterias['chemical resistant'] = kwargs.pop('characteristics__is_chemical_resistant')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 5"
        print kwargs

    # 6 query filter if 5 had no match
    if (not list_couple_techno_material) and ('characteristics__is_water_resistant' in kwargs):
        discarded_criterias['water resistant'] = kwargs.pop('characteristics__is_water_resistant')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 6"
        print kwargs

    # 7 query filter if 6 had no match
    if (not list_couple_techno_material) and ('characteristics__is_visual' in kwargs):
        discarded_criterias['visual part'] = kwargs.pop('characteristics__is_visual')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 7"
        print kwargs

    # 8 query filter if 7 had no match
    if (not list_couple_techno_material) and ('characteristics__is_food_grade' in kwargs):
        discarded_criterias['food grade'] = kwargs.pop('characteristics__is_food_grade')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 8"
        print kwargs

    # 9 query filter if 8 had no match
    if (not list_couple_techno_material) and ('characteristics__is_rubbery' in kwargs):
        discarded_criterias['rubbery'] = kwargs.pop('characteristics__is_rubbery')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        print "QUERY 9"
        print kwargs

    return list_couple_techno_material, perfect_match, errors, discarded_criterias


def part_type_from_name(name):
    
    return None
