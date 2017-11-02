# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from allauth.account.views import *
from django.shortcuts import render

# Create your views here.


class JointLoginSignupView(LoginView):
    form_class = LoginForm
    signup_form  = SignupForm
    def __init__(self, **kwargs):
        super(JointLoginSignupView, self).__init__(*kwargs)

    def get_context_data(self, **kwargs):
        ret = super(JointLoginSignupView, self).get_context_data(**kwargs)
        ret['signupform'] = get_form_class(app_settings.FORMS, 'signup', self.signup_form)
        return ret

login = JointLoginSignupView.as_view()
