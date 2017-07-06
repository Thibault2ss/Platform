from django.conf.urls import url, include

from . import views

app_name = 'parts'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^part-detail/$', views.part_detail, name='part_detail'),
    url(r'^catalogue/$', views.index, name='catalogue'),
    url(r'^prints/$', views.prints, name='prints'),
    url(r'^(?P<id>[0-9]+)/download_amf/$', views.download_amf, name='download_amf'),
    url(r'^(?P<id_config>[0-9]+)/download_config/$', views.download_config, name='download_config'),
    url(r'^(?P<id_gcode>[0-9]+)/download_gcode/$', views.download_gcode, name='download_gcode'),
    url(r'^(?P<id>[0-9]+)/slice_and_download/$', views.slice_and_download, name='slice_and_download'),
    url(r'^(?P<id_part>[0-9]+)/(?P<id_printer>[0-9]+)/slice_and_print/$', views.slice_and_print, name='slice_and_print'),
    url(r'^(?P<id_part>[0-9]+)/(?P<id_printer>[0-9]+)/print_from_gcode/$', views.print_from_gcode, name='print_from_gcode'),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
