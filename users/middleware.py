from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

class RestrictionMiddleware(object):
    """
    Middleware to limit access to the user groups to certain apps.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated():
            usertype = request.user.usertype.name
            restriction_list = settings.RESTRICTION_LIST[usertype]
            for url in restriction_list:
                if request.path.startswith(url):
                    # raise PermissionDenied
                    return HttpResponseRedirect('/account/login/')
        return self.get_response(request)