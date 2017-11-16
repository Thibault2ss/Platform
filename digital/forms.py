from django import forms
from digital.models import PartBulkFile, Part

class PartBulkFileForm(forms.ModelForm):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'required':True}))
    part = forms.ModelChoiceField(queryset=Part.objects.none(),widget=forms.HiddenInput(attrs={'required': True}))
    type = forms.ChoiceField(choices=PartBulkFile().getTypeChoices,widget=forms.HiddenInput(attrs={'required': True}))
    class Meta:
        model = PartBulkFile
        fields = ['part', 'file', 'type']

    def __init__(self, *args, **kwargs):
        created_by = None
        if 'created_by' in kwargs:
            created_by = kwargs.pop('created_by')
        super(PartBulkFileForm, self).__init__(*args, **kwargs)
        # allow change only for a part of your organisation:
        if created_by:
            self.created_by = created_by
            self.fields['part'].queryset = Part.objects.filter(organisation__id = created_by.organisation.id)

    def save(self):
        partBulkFile = super(PartBulkFileForm, self).save(commit=False)
        partBulkFile.created_by = self.created_by
        partBulkFile.save()
        return partBulkFile
