
from __future__ import unicode_literals
from digital.models import Part, PartImage, PartBulkFile
from digital.decorators import postpone
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from digital.models import Part, PartImage, PartBulkFile
from django.db.models import Case, IntegerField, Sum, When, Q

def getPartsClean(organisation):
    parts = Part.objects.filter(organisation = organisation)
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
        parts_pending_indus = Sum(Case(When(status__id=2, then=1), default = 0, output_field=IntegerField())),
        parts_disqualified = Sum(Case(When(status__id=3, then=1),default = 0,output_field=IntegerField())),
        parts_industrialized = Sum(Case(When(status__id=4, then=1),default = 0,output_field=IntegerField())),
        parts_metal = Sum(Case(When(material__family="metal", then=1),default = 0,output_field=IntegerField())),
        parts_plastic = Sum(Case(When(material__family="plastic", then=1),default = 0,output_field=IntegerField())),
    )
    return parts_sumup

def getOrganisationCapacity(organisation):
    images = PartImage.objects.filter
