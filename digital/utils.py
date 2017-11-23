
from __future__ import unicode_literals
from digital.models import Part, PartImage, PartBulkFile
from digital.decorators import postpone
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from digital.models import Part, PartImage, PartBulkFile
from django.db.models import Case, IntegerField, Sum, When, Q
import tempfile
from stl import mesh
import numpy
import os
import json
dir_path = os.path.dirname(os.path.realpath(__file__))
def getPartsClean(organisation):
    parts = Part.objects.filter(organisation = organisation).order_by('-date_created')
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

    return parts

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
        os.unlink(temp.name)
        # print("Volume                                  = {0}".format(volume))
        # print("Position of the center of gravity (COG) = {0}".format(cog))
        # print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
        # print("                                          {0}".format(inertia[1,:]))
        # print("                                          {0}".format(inertia[2,:]))

        data = {
            'volume': volume,
            'cog': cog.tolist(),
            'inertia': inertia.tolist(),
        }

    return type, json.dumps(data)
