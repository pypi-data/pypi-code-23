from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import ManyToOneRel

from .models import City, State, Country, CountryCode, Location
from .widgets import MapWidget


class CityForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), initial='')

    class Meta:
        model = City
        fields = '__all__'


class StateForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), initial='')

    class Meta:
        model = State
        fields = '__all__'


class CountryForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), initial='')

    class Meta:
        model = Country
        fields = '__all__'


class CountryCodeForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), initial='')

    class Meta:
        model = CountryCode
        fields = '__all__'


class LocationForm(forms.ModelForm):
    map = forms.CharField(widget=MapWidget, required=False)
    slug = forms.CharField(widget=forms.HiddenInput(), initial='', required=False)
    latitude = forms.CharField(widget=forms.HiddenInput(), initial='')
    longitude = forms.CharField(widget=forms.HiddenInput(), initial='')
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)
    states = forms.ModelChoiceField(queryset=State.objects.all(), required=False)

    class Meta:
        model = Location
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)

        rel = ManyToOneRel('states', State, 'id')
        self.fields['states'].widget = RelatedFieldWidgetWrapper(self.fields['states'].widget, rel, self.admin_site)

        if self.instance.pk:
            self.fields['map'].widget.latitude = self.instance.latitude
            self.fields['map'].widget.longitude = self.instance.longitude
            self.fields['country'].initial = self.instance.city.state.country.pk
            self.fields['states'].choices = [(0, '---------')] + [(state.pk, state.name) for state in State.objects.filter(country_id=self.instance.city.state.country.pk).all()]
            self.fields['states'].inital = self.instance.city.state.pk
