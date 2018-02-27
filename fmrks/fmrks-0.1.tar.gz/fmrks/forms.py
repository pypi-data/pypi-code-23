from django import forms
from .models import Fmrk


class MarkerModelForm(forms.ModelForm):

    class Meta:
        model = Fmrk
        exclude = ['create_by', 'content_type', 'object_id']


class MarkerHiddenModelForm(MarkerModelForm):
    def __init__(self, *args, **kwargs):
        super(MarkerHiddenModelForm, self).__init__(*args, **kwargs)
        self.fields['lat'].widget = forms.HiddenInput()
        self.fields['lng'].widget = forms.HiddenInput()
