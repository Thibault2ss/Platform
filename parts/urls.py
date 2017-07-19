from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'parts'
urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^part-detail/(?P<id_part>[0-9]+)$', views.part_detail, name='part_detail'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/local$', views.checkout_part, name='checkout_part'),
    url(r'^catalogue/$', views.index, name='catalogue'),
    url(r'^add-part/$', views.add_part, name='add_part'),
    url(r'^prints/$', views.prints, name='prints'),
    url(r'^ajax/print/$', views.ajax_print, name='ajax_print'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/push/$', views.push, name='push'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/upload-image/$', views.upload_image, name='upload_image'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/upload-cad/$', views.upload_cad_direct, name='upload_cad_direct'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/upload-amf/$', views.upload_amf_direct, name='upload_amf_direct'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/upload-config/$', views.upload_config_direct, name='upload_config_direct'),
    url(r'^(?P<id>[0-9]+)/download_amf/$', views.download_amf, name='download_amf'),
    url(r'^(?P<id_config>[0-9]+)/download_config/$', views.download_config, name='download_config'),
    url(r'^(?P<id_gcode>[0-9]+)/download_gcode/$', views.download_gcode, name='download_gcode'),
    url(r'^(?P<id>[0-9]+)/slice_and_download/$', views.slice_and_download, name='slice_and_download'),
    url(r'^(?P<id_part>[0-9]+)/(?P<id_printer>[0-9]+)/slice_and_print/$', views.slice_and_print, name='slice_and_print'),
    url(r'^(?P<id_part>[0-9]+)/(?P<id_printer>[0-9]+)/print_from_gcode/$', views.print_from_gcode, name='print_from_gcode'),
]


urlpatterns += staticfiles_urlpatterns()
