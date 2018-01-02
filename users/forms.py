from allauth.account.forms import SignupForm as OriginalSignupForm, LoginForm as OriginalLoginForm
from allauth.socialaccount.forms import SignupForm as OriginalSocialSignupForm
from django.contrib.auth.models import Group
from allauth.account.adapter import get_adapter as get_account_adapter
from django import forms
from users.models import CustomUser
from django.utils.translation import pgettext, ugettext, ugettext_lazy as _
from allauth.utils import (
    build_absolute_uri,
    get_username_max_length,
    set_form_field_order,
)
from .models import Organisation
from address.forms import AddressField


class LoginForm(OriginalLoginForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.pop('autofocus')

class SignupForm(OriginalSignupForm):

    CHOICES=[('CLIENT','Client'),('HUB', 'Hub')]

    usertype = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(
        attrs={'type': 'radio',}
        ))

    first_name = forms.CharField(label=_("first_name"),
                               min_length = 1,
                               max_length = 50,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          _('First Name'),
                                          }))

    last_name = forms.CharField(label=_("last_name"),
                               min_length = 1,
                               max_length = 100,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          _('Last Name'),
                                          }))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        field_order = [
            'first_name',
            'last_name',
            'email',
            'email2',  # ignored when not present
            'username',
            'password1',
            'password2', # ignored when not present
            'usertype',
        ]
        self.fields['usertype'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        set_form_field_order(self,field_order)

    def clean_usertype(self):
        value = self.cleaned_data["usertype"]
        value = get_account_adapter().clean_usertype(value)
        return value

    def clean_first_name(self):
        value = self.cleaned_data["first_name"]
        value = get_account_adapter().clean_first_name(value)
        return value

    def clean_last_name(self):
        value = self.cleaned_data["last_name"]
        value = get_account_adapter().clean_last_name(value)
        return value


# FORM for choosing which user category after social login
class SocialSignupForm(OriginalSocialSignupForm):

    CHOICES=[('CLIENT','Client'),('HUB', 'Hub')]
    usertype = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(
        attrs={'type': 'radio',}
        ))

    def __init__(self, *args, **kwargs):
        super(SocialSignupForm, self).__init__(*args, **kwargs)
        field_order = [
            'email',
            'email2',  # ignored when not present
            'username',
            'password1',
            'password2', # ignored when not present
            'usertype',
        ]
        self.fields['usertype'].required = True
        # self.fields['email'].widget.attrs.pop('autofocus')
        set_form_field_order(self,field_order)

    def clean_usertype(self):
        value = self.cleaned_data["usertype"]
        value = get_account_adapter().clean_usertype(value)
        return value

class OrganisationForm(forms.ModelForm):
    address = AddressField()
    class Meta:
        model = Organisation
        fields = ['address']


class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_pic']

class OrganisationLogoForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ['logo']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'title']
