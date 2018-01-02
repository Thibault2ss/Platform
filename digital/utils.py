# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from digital.models import Part, PartImage, PartBulkFile
from digital.decorators import postpone
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from digital.models import Part, PartImage, PartBulkFile, Characteristics, PartType, ApplianceFamily, BulkPartUpload
from jb.models import CoupleTechnoMaterial, Technology, Material, FinalCard
from django.db.models import Case, IntegerField, Sum, When, Q, Count, Max
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
import re, math
from collections import Counter
from os.path import join
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

def getBulkUploadSumUp(organisation):
    parts_sumup = None
    parttype_distrib = []
    appliance_fam_distrib = []
    techno_material_distrib = []
    latest_bulk_upload_part = Part.objects.filter(organisation = organisation, bulk_upload__isnull = False).order_by('-id').first()
    if latest_bulk_upload_part:
        latest_bulk_upload = latest_bulk_upload_part.bulk_upload
        parts_sumup = Part.objects.filter(organisation = organisation, bulk_upload = latest_bulk_upload).aggregate(
            parts_total = Sum(Case(When(~Q(pk=None), then=1),default = 0, output_field=IntegerField())),
            parts_with_type = Sum(Case(When(type__isnull=False, then=1), default = 0, output_field=IntegerField())),
            parts_with_final_card = Sum(Case(When(final_card__isnull=False, then=1), default = 0, output_field=IntegerField())),
        )
        appliance_fam_distrib =  Part.objects.filter(organisation = organisation, bulk_upload = latest_bulk_upload, type__isnull=False, type__appliance_family__isnull=False).values('type__appliance_family__name').annotate(count=Count('type__appliance_family__name')).order_by('-count')
        parttype_distrib =  Part.objects.filter(organisation = organisation, bulk_upload = latest_bulk_upload, type__isnull=False).values('type__name').annotate(count=Count('type__name')).order_by('-count')
        techno_material_distrib =  Part.objects.filter(organisation = organisation, bulk_upload = latest_bulk_upload, final_card__isnull=False, final_card__techno_material__isnull=False).values('final_card__techno_material__technology__name', 'final_card__techno_material__material__name').annotate(count=Count('pk')).order_by('-count')

    return parts_sumup, parttype_distrib, appliance_fam_distrib, techno_material_distrib



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

def getApplianceFamilyDistribution(organisation):
    distribution =  Part.objects.filter(organisation = organisation).values('type__appliance_family__name').annotate(count=Count('type__appliance_family__name')).order_by('-count')
    return distribution

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






def upload_bulk_parts(file, user):
    error_list=[]
    warning_list=[]
    fieldnames = ['reference', 'name', 'type', 'appliance_family', 'weight', 'x', 'y', 'z']
    filename, file_extension = os.path.splitext('%s'%file)

    # check file extension
    if not file_extension.lower() == '.csv':
        error_list.append("WRONG FILE EXTENSION")
        return error_list, warning_list

    # create temporary file
    temp = tempfile.NamedTemporaryFile(delete = False)
    for chunk in file.chunks():
        temp.write(chunk)
    temp.close()

    # create a instance of Bulk PartUpload
    bulk_upload = BulkPartUpload(created_by = user)
    bulk_upload.file = file
    bulk_upload.save()

    # treat temporary file to populate database
    with open(temp.name, 'rb+') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames = fieldnames)
        for index, row in enumerate(reader, start=1):
            if index == 1:continue
            print index
            if row.get('reference',None):
                part, error_dic, warning_dic = processPartRow(row, bulk_upload, user)
                if error_dic:
                    error_dic["row_index"] = index
                    error_list.append(error_dic)
                if warning_dic:
                    warning_dic["row_index"] = index
                    warning_list.append(warning_dic)

    bulk_upload.errors = "%s"%error_list
    bulk_upload.warnings = "%s"%warning_list
    bulk_upload.save()
    os.unlink(temp.name)
    return error_list, warning_list

def processPartRow(row, bulk_upload, user):
    part= None
    error_dic={}
    warning_dic={}

    # extract all row values
    _reference = row.get('reference',None)
    _name = row.get('name',None)
    _appliance_family = row.get('appliance_family',None)
    _type = row.get('type',None)
    _weight = row.get('weight',None)
    _x = row.get('x',None)
    _y = row.get('y',None)
    _z = row.get('z',None)

    # check errors on fields
    # MANDATORY FIELD  - reference
    if _reference:
        _reference = _reference.upper()
    else:
        error_dic["reference"] = "Part Reference is missing"
    # MANDATORY FIELD  - name
    if _name:
        _name = unicode(_name.decode('latin'))
    else:
        error_dic["name"] = "Part Name is missing"
    #  MANDATORY FIELD  - appliance family
    if not _appliance_family:
        appl_fams = ApplianceFamily.objects.all()
        for appl_fam in appl_fams:
            if appl_fam.name.lower() in _name.lower():
                _appliance_family = appl_fam.name
                break

    if not _appliance_family:
        error_dic["appliance_family"] = "Appliance Family is missing and no match was found from name"

    #  MANDATORY FIELD  - weight
    if _weight:
        try:
            _weight = float(_weight)
        except ValueError:
            error_dic["weight"] = "Part Weight is not a float"
    else:
        error_dic["weight"] = "Part Weight is missing"
    #  OPTIONAL FIELD  - Part type
    if not _type:
        warning_dic["type"] = "No Part Type specified"
    #  OPTIONAL FIELDS  - Dimensions
    if _x and _y and _z:
        try:
            _x = float(_x)
            _y = float(_y)
            _z = float(_z)
        except ValueError:
            error_dic["x_y_z"] = "Part Dimensions are not floats"
    else:
        warning_dic["x_y_z"] = "Part Dimensions are missing"


    # if no errors, find or create the part
    if not error_dic:
        try:
            part = Part.objects.get(organisation = user.organisation, reference = _reference)
        except Part.DoesNotExist:
            part = Part(created_by = user, organisation=user.organisation, reference=_reference)

        part.bulk_upload = bulk_upload
        part.name = _name
        part.weight = _weight
        if _x and _y and _z:
            part.length = _x
            part.width = _y
            part.height = _z

        # find part type
        temp_type = None
        if _type and _appliance_family:
            temp_type = PartType.objects.filter(name__icontains = _type, appliance_family__name__icontains = _appliance_family).first()
        if not temp_type:
            type_prediction = part_type_from_name_1(_name, _appliance_family)
            temp_type = type_prediction.get('part_type', None)
        part.type = temp_type
        if not temp_type:
            warning_dic["part_type"] = "Part Type not found"

        # save part
        part.save()

        if part.type:
            if part.type.characteristics:
                new_charac = part.type.characteristics
                new_charac.pk = part.characteristics.pk if part.characteristics else None
                new_charac.part_type = None
                new_charac.part = part
                new_charac.save()
            else:
                warning_dic["characteristics"] = "Part Type %s - %s - %s has No characteristics attached"%(part.type.id, part.type.name, part.type.appliance_family)



        # find couple techno_material match
        list_couple_techno_material, perfect_match, errors, discarded_criterias = findTechnoMaterial(part, fallback_mode=False)
        if errors:
            error_dic["find_techno_material"] = errors
        if perfect_match and list_couple_techno_material:
            if part.final_card:
                final_card = part.final_card
            else:
                final_card = FinalCard(part = part)
            final_card.techno_material = list_couple_techno_material.first()
            final_card.save()
        elif part.final_card:
            part.final_card.delete()

        # refresh instance of part
        part.refresh_from_db()

    return part, error_dic, warning_dic








def part_type_prevision(file):
    error_list=[]
    warning_list=[]
    filename, file_extension = os.path.splitext('%s'%file)

    # check file extension
    if not file_extension.lower() == '.csv':
        error_list.append("WRONG FILE EXTENSION")
        return error_list, warning_list

    fieldnames = ['name_eng','hierarchy']

    temp = tempfile.NamedTemporaryFile(delete = False)
    for chunk in file.chunks():
        temp.write(chunk)
    temp.close()

    # copy csv in temporary file
    final_file = open(join(dir_path, "part_type_prevision.csv"),'wb+')



    # treat temporary file to populate database
    with open(temp.name, 'rb+') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames = fieldnames)
        for index, row in enumerate(reader, start=1):
            if index == 1:continue
            print index
            if row.get('name_eng',None):
                # yolo = part_type_from_name(row['name_eng'])
                try:
                    family_code = row['hierarchy'].split('-')[1]
                except IndexError:
                    family_code = ""
                yolo = part_type_from_name_1(row['name_eng'], family_code )

                part_type_name = yolo['part_type'].name if yolo['part_type'] else "Unknown"
                appliance_family = yolo['appliance_family'].name if yolo['appliance_family'] else "Unknown"
                intersection = yolo['intersection']
                line = '%s\t%s\t%s\t%s\t%s\n'%(index, row['name_eng'].decode('latin'),part_type_name, appliance_family, intersection)
                line = line.encode('utf-8')
                final_file.write(line)

    final_file.close()
    os.unlink(temp.name)
    return None, None






def translate_matrix(file):
    error_list=[]
    warning_list=[]
    filename, file_extension = os.path.splitext('%s'%file)

    # check file extension
    if not file_extension.lower() == '.csv':
        error_list.append("WRONG FILE EXTENSION")
        return error_list, warning_list


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
        fieldnames = ['part_type','appliance_family', 'keywords','d','e','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    else:
        error_list.append("WRONG FILE NAME")
        return error_list, warning_list


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

def RepresentsFloat(s):
    try:
        _float = float(s)
        return _float
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
            cleaned_dic['technology'] = Technology.objects.get(name__iexact=dic['technology'])
        except Technology.DoesNotExist:
            error['technology'] = 'Technology %s does not match a technology in database'%dic['technology']


    # check if material exists
    if dic.get('material', None):
        try:
            cleaned_dic['material'] = Material.objects.get(name__iexact=dic['material'])
        except Material.DoesNotExist:
            error['material'] = 'Material %s does not match a material in database'%dic['material']


    # check if part_type exists
    if dic.get('part_type', None) and dic.get('appliance_family', None):
        try:
            print "appliance family:%s"%dic['appliance_family']
            print "part type:%s"%dic['part_type']
            temp_appliance_family = ApplianceFamily.objects.get(name__iexact = dic['appliance_family'])
            print temp_appliance_family
            cleaned_dic['part_type'] = PartType.objects.get(name = dic['part_type'], appliance_family = temp_appliance_family)
            cleaned_dic['part_type'].keywords = dic['keywords']
            cleaned_dic['part_type'].save()
        except ApplianceFamily.DoesNotExist:
            error['appliance_family'] = 'No match on appliance family %s'%dic['appliance_family']
        except PartType.DoesNotExist:
            part_type = PartType(name= dic['part_type'], appliance_family = temp_appliance_family, keywords = dic['keywords'])
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





def findTechnoMaterial(part, fallback_mode=True):
    errors = []
    list_couple_techno_material = None
    args = []
    kwargs = {}
    perfect_match = False
    discarded_criterias = {}

    # check if part has characteristics attached
    if not part.characteristics:
        errors.append("No prevision Possible, Part has no characteristics attached !")
        return list_couple_techno_material, perfect_match, errors, discarded_criterias


    # set up first filters as args for Q and kwargs for rest
    characs = part.characteristics
    # discriminant criterias:
    kwargs['characteristics__is_rubbery'] = characs.is_rubbery
    kwargs['characteristics__is_transparent'] = characs.is_transparent
    # non discriminant criterias:
    kwargs['characteristics__is_visual'] = characs.is_visual
    kwargs['characteristics__is_water_resistant'] = characs.is_water_resistant
    kwargs['characteristics__is_chemical_resistant'] = characs.is_chemical_resistant
    kwargs['material__characteristics__is_flame_retardant'] = characs.is_flame_retardant
    kwargs['characteristics__is_food_grade'] = characs.is_food_grade
    if characs.flame_retardancy == 'NA':higher_ret_list = ['NA', 'HB', 'V2', 'V1', 'V0']
    elif characs.flame_retardancy == 'HB':higher_ret_list = ['HB', 'V2', 'V1', 'V0']
    elif characs.flame_retardancy == 'V2':higher_ret_list = ['V2', 'V1', 'V0']
    elif characs.flame_retardancy == 'V1':higher_ret_list = ['V1', 'V0']
    elif characs.flame_retardancy == 'V0':higher_ret_list = ['V0']
    kwargs['material__characteristics__flame_retardancy__in'] = higher_ret_list

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
    # if characs.is_water_resistant:
    #     kwargs['characteristics__is_water_resistant'] = characs.is_water_resistant
    # else:
    #     discarded_criterias['water resistant'] = characs.is_water_resistant
    # if characs.is_water_resistant:
    #     kwargs['characteristics__is_chemical_resistant'] = characs.is_chemical_resistant
    # else:
    #     discarded_criterias['chemical resistant'] = characs.is_chemical_resistant
    # if characs.is_flame_retardant:
    #     kwargs['material__characteristics__is_flame_retardant'] = characs.is_flame_retardant
    # else:
    #     discarded_criterias['flame retardant'] = characs.is_flame_retardant
    # if characs.is_food_grade:
    #     kwargs['characteristics__is_food_grade'] = characs.is_food_grade
    # else:
    #     discarded_criterias['food grade'] = characs.is_food_grade
    # if characs.is_flame_retardant:
    #     if characs.flame_retardancy == 'NA':higher_ret_list = ['NA', 'HB', 'V2', 'V1', 'V0']
    #     if characs.flame_retardancy == 'HB':higher_ret_list = ['HB', 'V2', 'V1', 'V0']
    #     if characs.flame_retardancy == 'V2':higher_ret_list = ['V2', 'V1', 'V0']
    #     if characs.flame_retardancy == 'V1':higher_ret_list = ['V1', 'V0']
    #     if characs.flame_retardancy == 'V0':higher_ret_list = ['V0']
    #     kwargs['material__characteristics__flame_retardancy__in'] = higher_ret_list


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

    # if no perfect match remove non discriminant characteristics and query again
    if not list_couple_techno_material:
        if not characs.is_visual:
            discarded_criterias['visual part'] = kwargs.pop('characteristics__is_visual')
        if not characs.is_water_resistant:
            discarded_criterias['water resistant'] = kwargs.pop('characteristics__is_water_resistant')
        if not characs.is_water_resistant:
            discarded_criterias['chemical resistant'] = kwargs.pop('characteristics__is_chemical_resistant')
        if not characs.is_flame_retardant:
            discarded_criterias['flame retardant'] = kwargs.pop('material__characteristics__is_flame_retardant')
        if not characs.is_food_grade:
            discarded_criterias['food grade'] = kwargs.pop('characteristics__is_food_grade')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs)
        if list_couple_techno_material:perfect_match=True
        print "QUERY 2"
        print kwargs

    if fallback_mode:
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




def part_type_from_name_1(name, family_code):
    if not name:return None
    result = {'intersection':0, 'intersection_f':0, 'part_type': None, 'appliance_family':None}
    name_vector = text_to_vector(name)

    # match with appliance type first
    if family_code:
        result['appliance_family'] = ApplianceFamily.objects.filter(name__icontains = family_code).first()
    if not result['appliance_family']:
        appliances_f = ApplianceFamily.objects.all()
        for appliance_f in appliances_f:
            intersection = get_intersection(text_to_vector(appliance_f.name), name_vector)
            if intersection and intersection > result['intersection_f']:
                result['appliance_family'] = appliance_f
                result['intersection_f'] = intersection


    if result['appliance_family']:
        part_types = PartType.objects.filter(appliance_family = result['appliance_family'])
        for part_type in part_types:
            intersection = get_intersection(text_to_vector(part_type.name + part_type.keywords), name_vector)
            if intersection and intersection > result['intersection']:
                result['part_type'] = part_type
                result['intersection'] = intersection

    # if no match or no appliance family, check in category Other
    if (not result['appliance_family']) or (not result['part_type']):
        part_types = PartType.objects.filter(appliance_family__name__iexact = "Other")
        for part_type in part_types:
            intersection = get_intersection(text_to_vector(part_type.name + part_type.keywords), name_vector)
            if intersection and intersection > result['intersection']:
                result['part_type'] = part_type
                result['intersection'] = intersection

    return result





def part_type_from_name(name):
    if not name:return None
    result = {'cosine':0.0}
    name_vector = text_to_vector(name)
    appliance_family = None


    # match with appliance type first
    appliance_f_cos = 0
    appliances_f = ApplianceFamily.objects.all()
    for appliance_f in appliances_f:
        cosine = get_cosine(text_to_vector(appliance_f.name), name_vector)
        if cosine and cosine > appliance_f_cos:
            appliance_family = appliance_f
            appliance_f_cos = cosine



    if appliance_family:
        part_types = PartType.objects.filter(appliance_family = appliance_family)
    else:
        part_types = PartType.objects.all()

    for part_type in part_types:
        cosine = get_cosine(text_to_vector(part_type.name + part_type.keywords), name_vector)
        if cosine and cosine > result['cosine']:
            result = {'part_type':part_type, 'appliance_family':appliance_family, 'cosine':cosine}

    if not 'part_type' in result:result = None
    return result


WORD = re.compile(r'\w+')

def get_intersection(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    return len(intersection)


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text):
    words = WORD.findall(text.lower())
    return Counter(words)
