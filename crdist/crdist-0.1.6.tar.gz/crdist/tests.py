#-*- coding: utf-8

from django.test import TestCase
from crdist.models import District
from django import forms
from django.shortcuts import render
# Create your tests here.
from crdist.widgets import DistrictSelect
import json


class WidgetTestCase(TestCase):
    def setUp(self):
        pass

    def test_province(self):
        widget = DistrictSelect()
        result = widget.render("province", None)
        self.assertNotEqual(result.find( 'for="id_province_province"'), -1) 
        self.assertNotEqual(result.find('select id="id_province_province"'), -1 )
        self.assertNotEqual(result.find('div href="/crdist/canton?name=province"'), -1 )
        self.assertNotEqual(result.find('div href="/crdist/district?name=province"'), -1 )

    def test_canton(self):
        response = self.client.get("/crdist/canton?name=province&province=4")
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content.decode('utf-8'))
        self.assertEqual('div_canton_province', obj['id'])
        for x in [  'value=\"8\"',  # Heredia Central
                    'value=\"9\"',  # Barva
                    'value=\"10\"', # Santo Domingo
                    'value=\"11\"', # Santa Barbara
                    'value=\"12\"', # San Rafael
                    'value=\"13\"', # San Isidro
                    'value=\"14\"', # Belen
                    'value=\"21\"', # Flores
                    'value=\"22\"', # San Pablo
                    'value=\"23\"'  # Sarapiqui
                 ]:
            self.assertNotEqual(obj['content'].find(x), -1)
        


    def test_distric(self):
        response = self.client.get("/crdist/district?name=province&canton=9")
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content.decode('utf-8'))
        self.assertEqual('div_district_province', obj['id'])
        for x in [  'value=\"715\"',    # San Pedro
                    'value=\"716\"',    # San Pablo
                    'value=\"717\"',    # San Roque
                    'value=\"718\"',    # Santa Lucida
                    'value=\"719\"',    # San Jos\u00e9 de la Montania
                    'value=\"828\"',    # Barva 
                 ]:
            self.assertNotEqual(obj['content'].find(x), -1)

    def test_attrs(self):
        widget = DistrictSelect({'class': "crdist"})
        result = widget.render("province", None)
        self.assertNotEqual(result.find('select class="crdist"'), -1)
        response = self.client.get("/crdist/canton?name=province&province=4&attrs=7b22636c617373223a2022637264697374227d")
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content.decode('utf-8'))
        self.assertNotEqual(obj['content'].find('select  class=\"crdist\"'), -1)        
        

    def test_crdist_onerror(self):
        widget = DistrictSelect({'class': "crdist"})
        result = widget.render("province", 828) # Barva
        self.assertNotEqual(result.find('class="crdist_onerror" value="4"'), -1)
        self.assertNotEqual(result.find('class="crdist_onerror" value="9"'), -1)

class CRForm(forms.Form):
    district = forms.ModelChoiceField(queryset=District.objects.all(),
                                  widget=DistrictSelect(),
                                  label="Localización ")


def view_test_form(request):
    form = CRForm()
    return render(request, 'form_ejemplo.html', {'form': form})


