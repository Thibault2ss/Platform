from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'digital_'
urlpatterns = [

    url(r'^$', views.index, name=app_name + 'index'),
    url(r'^account/$', views.account, name=app_name+'account'),
    url(r'^qualification/$', views.qualification, name=app_name+'qualification'),
    url(r'^printers/$', views.printers, name=app_name+'printers'),
    url(r'^parts/$', views.parts, name=app_name+'parts'),
    url(r'^parts/upload-part-bulk-file/$', views.upload_part_bulk_file, name=app_name+'upload_part_bulk_file'),
    url(r'^parts/request-for-indus/$', views.request_for_indus, name=app_name+'request_for_indus'),
    url(r'^billing/$', views.billing, name=app_name+'billing'),
    url(r'^table/$', views.table, name=app_name+'table'),
    url(r'^notifications/$', views.notifications, name=app_name+'notifications'),
    url(r'^typography/$', views.typography, name=app_name+'typography'),
    url(r'^icons/$', views.icons, name=app_name+'icons'),
    url(r'^maps/$', views.maps, name=app_name+'maps'),

]
