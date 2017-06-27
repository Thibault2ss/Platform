from django.conf.urls import url

from . import views

app_name = 'parts'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<id>[0-9]+)/download_amf/$', views.download_amf, name='download_amf'),
    url(r'^(?P<id>[0-9]+)/download_config/$', views.download_config, name='download_config'),
]
