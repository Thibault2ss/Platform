from django import forms
from jb.models import FinalCard

class FinalCardForm(forms.ModelForm):
    class Meta:
        model = FinalCard
        exclude = []
