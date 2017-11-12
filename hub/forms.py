from django import forms
from address.forms import AddressField

class HubForm(forms.Form):
    name = forms.CharField(max_length=100)
    address = AddressField()
