from django import forms
from digital.models import PartBulkFile, Part, Appliance, PartType, Characteristics

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

    def save(self, type="BULK", data={}):
        partBulkFile = super(PartBulkFileForm, self).save(commit=False)
        partBulkFile.created_by = self.created_by
        partBulkFile.data = "%s"%data
        partBulkFile.type = "%s"%type
        partBulkFile.save()
        return partBulkFile

class PartForm(forms.ModelForm):
    # file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'required':True}))
    appliance = forms.ModelMultipleChoiceField(queryset=Appliance.objects.none())
    type = forms.ModelChoiceField(queryset=PartType.objects.none())
    class Meta:
        model = Part
        exclude = ['date_created', 'created_by', 'organisation', 'characteristics', 'status', 'final_card']

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
            self.fields['appliance'].queryset = Appliance.objects.filter(organisation = created_by.organisation)
            self.fields['type'].queryset = PartType.objects.filter(industry = created_by.organisation.industry)

    def save(self, characteristics = None):
        part = super(PartForm, self).save(commit=False)
        part.created_by = self.created_by
        part.organisation = self.organisation
        if characteristics:
            part.characteristics = characteristics
        part.save()
        self.save_m2m()
        return part

class CharacteristicsForm(forms.ModelForm):
    class Meta:
        model = Characteristics
        exclude = ['max_X','max_Y','max_Z']
