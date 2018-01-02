from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'hub_'
urlpatterns = [

    url(r'^$', views.index, name=app_name + 'index'),
    url(r'^account/$', views.account, name=app_name+'account'),
    url(r'^qualification/$', views.qualification, name=app_name+'qualification'),
    url(r'^printers/$', views.printers, name=app_name+'printers'),
    url(r'^orders/$', views.orders, name=app_name+'orders'),
    url(r'^billing/$', views.billing, name=app_name+'billing'),
    url(r'^table/$', views.table, name=app_name+'table'),
    url(r'^notifications/$', views.notifications, name=app_name+'notifications'),
    url(r'^typography/$', views.typography, name=app_name+'typography'),
    url(r'^icons/$', views.icons, name=app_name+'icons'),
    url(r'^maps/$', views.maps, name=app_name+'maps'),

]
