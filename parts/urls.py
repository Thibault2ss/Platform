from django.conf.urls import url

from . import views

app_name = 'parts'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^catalogue/$', views.index, name='catalogue'),
    url(r'^prints/$', views.prints, name='prints'),
    url(r'^(?P<id>[0-9]+)/download_amf/$', views.download_amf, name='download_amf'),
    url(r'^(?P<id>[0-9]+)/download_config/$', views.download_config, name='download_config'),
    url(r'^(?P<id>[0-9]+)/slice_and_download/$', views.slice_and_download, name='slice_and_download'),
    url(r'^(?P<id>[0-9]+)/slice_and_print/$', views.slice_and_print, name='slice_and_print'),
]
