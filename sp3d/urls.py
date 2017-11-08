"""part_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
import notifications.urls
from users.views import JointLoginSignupView
from django.views.generic import RedirectView


urlpatterns = [
    # url(r'^login/$', auth_views.login, name='login'),
    # url(r'^logout/$', auth_views.logout,{'next_page': '/jb'}, name='logout'),
    url(r'^jb/', include('jb.urls')),
    url(r'^account/login/$', JointLoginSignupView.as_view(), name='login_page'),
    url(r'^account/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^hub/', include('hub.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^', RedirectView.as_view(pattern_name='login_page', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)