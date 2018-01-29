from django.conf.urls import patterns, url
from .views import index, actualiza_nombes_de_carpetas_sellos, UpdateConfigurationDatabase, PreferenciasManageView, DescargarFacturasDelMes, CertificarFacturas, PrepararEmpresasView, ValidarEmpresa, GetEmpresasList

urlpatterns = patterns('',
	(r'^$', index),
	
	url(r'^certificar_factura/', CertificarFacturas),
	url(r'^validar_empresa/', ValidarEmpresa),
	url(r'^get_empresas_list/', GetEmpresasList),
	
	url(r'^descargar_facturas/', DescargarFacturasDelMes),
	url(r'^actualiza_nombre_carpetas_sellos/', actualiza_nombes_de_carpetas_sellos),	
	url(r'^preferencias/inicializar_configuracion/$', UpdateConfigurationDatabase),
	url(r'^herramientas/preferencias/$', PreferenciasManageView),
	url(r'^transferir_datos/$', PrepararEmpresasView),
	
	
)