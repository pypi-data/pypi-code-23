#encoding:utf-8
from django import forms
from .models import Registry, Cliente, ArticuloClave
import autocomplete_light
from django.conf import settings
from django.db import router
import os

class SelectDBForm(forms.Form):    
    try:
        using = router.db_for_write(Registry)
    except:
        databases = []
    else:
        databases = settings.MICROSIP_DATABASES.keys()
        try:
            databases.remove(using)
        except:
            pass
            
    opcions = []
    for empresa in databases:
        opcions.append([empresa, empresa])
    
    conexion = forms.ChoiceField(choices= opcions)

class PreferenciasManageForm(forms.Form):
    facturaa_cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'))
    facturaa_articulo_clave = forms.CharField()
    ruta_liquidacion = forms.CharField()
    empresas_a_ignorar = forms.CharField(required=False)
    carpeta_facturacion_sat = forms.CharField()

    def clean_ruta_liquidacion(self):
        ruta_liquidacion = self.cleaned_data['ruta_liquidacion']
        try:
            os.listdir(ruta_liquidacion)
        except WindowsError:
            raise forms.ValidationError('ruta de carpeta [%s] invalida.'% ruta_liquidacion)
        else:
            if not os.path.isfile(os.path.join(ruta_liquidacion,'lprodrec.DBF')):
                raise forms.ValidationError('ruta de carpeta [%s] no es la ruta de liquidacion.'% ruta_liquidacion)
            
        return ruta_liquidacion

    def clean_carpeta_facturacion_sat(self):
        carpeta_facturacion_sat = self.cleaned_data['carpeta_facturacion_sat']
        try:
            os.listdir(os.path.join(carpeta_facturacion_sat,'sellos'))
        except WindowsError:
            raise forms.ValidationError('ruta de la carpeta [%s] de datos de facturacion es invalida.'% carpeta_facturacion_sat)

        return carpeta_facturacion_sat

    def clean_facturaa_articulo_clave(self):
        articulo_clave = self.cleaned_data['facturaa_articulo_clave']
        if not ArticuloClave.objects.filter(clave=articulo_clave).exists():
            raise forms.ValidationError('No existe ningun articulo con la clave indicada')
        return articulo_clave

    def clean_empresas_a_ignorar(self):
        using = router.db_for_write(Registry)
        conexion_no = using.split('-')[0]
        empresas_a_ignorar_filed = self.cleaned_data['empresas_a_ignorar']
        databases = settings.MICROSIP_DATABASES.keys()
        
        if empresas_a_ignorar_filed:
            empresas_a_ignorar = empresas_a_ignorar_filed.split(',')
            empresas_a_ignorar = [ conexion_no + '-' + empresa for empresa in empresas_a_ignorar ]
            for empresa in empresas_a_ignorar:
                if not empresa in databases:
                    raise forms.ValidationError('la empresa %s no se encuentra registrada en microsip'%empresa)

        return empresas_a_ignorar_filed

    def save(self, *args, **kwargs):
        facturaa_cliente_nombre = Registry.objects.get( nombre = 'SIC_EnlaceLiquida_FacturarA_ClienteNombre')
        facturaa_cliente_nombre.valor = self.cleaned_data['facturaa_cliente'].nombre
        facturaa_cliente_nombre.save()

        facturaa_articulo_clave = Registry.objects.get( nombre = 'SIC_EnlaceLiquida_FacturarA_ArticuloClave')
        facturaa_articulo_clave.valor = self.cleaned_data['facturaa_articulo_clave']
        facturaa_articulo_clave.save()

        ruta_liquidacion = Registry.objects.get( nombre = 'SIC_EnlaceLiquida_RutaLiquidacion')
        ruta_liquidacion.valor = self.cleaned_data['ruta_liquidacion']
        ruta_liquidacion.save()

        empresas_a_ignorar = Registry.objects.get( nombre = 'SIC_EnlaceLiquida_EmpresasAIgnorar')
        empresas_a_ignorar.valor = self.cleaned_data['empresas_a_ignorar']
        empresas_a_ignorar.save()

        carpeta_facturacion_sat = Registry.objects.get( nombre = 'SIC_CarpetaFacturacionSAT')
        carpeta_facturacion_sat.valor = self.cleaned_data['carpeta_facturacion_sat']
        carpeta_facturacion_sat.save()
