from django import forms
from digital.models import PartBulkFile, Part, Model

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

class PartForm(forms.ModelForm):
    # file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'required':True}))
    # part = forms.ModelChoiceField(queryset=Part.objects.none(),widget=forms.HiddenInput(attrs={'required': True}))
    # type = forms.ChoiceField(choices=PartBulkFile().getTypeChoices,widget=forms.HiddenInput(attrs={'required': True}))
    model = forms.ModelMultipleChoiceField(queryset=Model.objects.none())
    class Meta:
        model = Part
        fields = ['reference', 'model', 'name', 'material', 'length', 'width','height', 'dimension_unit', 'weight', 'weight_unit', 'color', 'grade', 'environment']

    def __init__(self, *args, **kwargs):
        created_by = None
        if 'created_by' in kwargs:
            created_by = kwargs.pop('created_by')
        super(PartForm, self).__init__(*args, **kwargs)
        # allow change only for a part of your organisation:
        if created_by:
            self.created_by = created_by
            self.organisation = created_by.organisation
            # parts_qs = Parts.objects.filter(organisation = created_by.organisation)
            # self.fields['model'].queryset = Model.objects.filter(model_set__in = parts_qs)
            self.fields['model'].queryset = Model.objects.filter(organisation = created_by.organisation)

    def save(self):
        part = super(PartForm, self).save(commit=False)
        part.created_by = self.created_by
        part.organisation = self.organisation
        part.save()
        self.save_m2m()
        return part
