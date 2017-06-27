from django.conf.urls import url

from . import views

app_name = 'parts'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<id>[0-9]+)/download/$', views.download, name='download'),
]
