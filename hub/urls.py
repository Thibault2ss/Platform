from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'hub'
urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^user/$', views.user, name='user'),
    url(r'^table/$', views.table, name='table'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^typography/$', views.typography, name='typography'),
    url(r'^icons/$', views.icons, name='icons'),
    url(r'^maps/$', views.maps, name='maps'),

]


urlpatterns += staticfiles_urlpatterns()
