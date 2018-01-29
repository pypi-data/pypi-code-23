#encoding:utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
# user autentication
from .models import *
from .forms import PreferenciasManageForm, SelectDBForm
import os, datetime
from datetime import timedelta
from .core import get_facturasmes_liquidacion, get_indices, set_indices
from django.http import HttpResponse, HttpResponseRedirect
from microsip_api.apps.cfdi.certificador.core import CertificadorSAT, create_ini_file, save_xml_in_document, create_ini_file_33_ve,save_xml_in_document_33_ve
from microsip_api.comun.comun_functions import split_seq
from microsip_api.comun.sic_db import first_or_none
from django.db import connections, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db import router
from django.core import management

class InitialConfiguration(object):
    def __init__(self, using):
        self.errors = []
        self.using = using

    def is_valid(self):
        self.errors= []
        valid = True
        
        try:
            Registry.objects.get(nombre='SIC_EnlaceLiquida_ConfigFormLleno').get_value()
        except ObjectDoesNotExist:
            self.errors.append('''Por favor inicializa la configuracion de la aplicacion dando  <a href="/enlace_liquida/preferencias/inicializar_configuracion/">click aqui</a>''')
        else:
            from_lleno = False
            try:
                from_lleno = Registry.objects.get(nombre='SIC_EnlaceLiquida_ConfigFormLleno').get_value() == u'1'
            except ObjectDoesNotExist:
                self.errors.append('''Por favor inicializa la configuracion de la aplicacion dando  <a href="/enlace_liquida/preferencias/inicializar_configuracion/">click aqui</a>''')
            
            if not from_lleno:
                self.errors.append("Es nesesario configurar la aplicacion en [ Herramientas > Preferencias. ] ")
                
        if not self.errors == []:
            valid = False
        
        return valid

def agregar_empresa_a_ignorar(empresa):
    ''' Para agregar una empresa a ignorar al registro. Se agrega en el momento que ya se certifico '''

    actual_year = datetime.datetime.now().year
    actual_month = datetime.datetime.now().month
    str_actual = u"%s%s"%(str(actual_year),str(actual_month))

    # Obtenemos los valores de el registro
    empresas_a_ignorar_obj = RegistryLong.objects.get(nombre='SIC_EnlaceLiquida_EmpresasFacturaCertificada')
    valor = empresas_a_ignorar_obj.valor
    referencia = empresas_a_ignorar_obj.referencia.strip(' ')

    # Si la referencia es  igual a la referencia actual creada
    #---------------------------------------------------------
    # REFERENCIA: es para si se esta ravisando empresas de otro mes diferente 
    # a la actual entonces se resetea valor del registro para tomar en cuenta 
    # todas las empresas desde el principio

    # si la referencia es igual agregamos empresa a ignorar
    if referencia == str_actual:
        valor = empresas_a_ignorar_obj.valor
        empresas_a_ignorar_obj.valor = "%s,%s"% (valor, empresa)
        empresas_a_ignorar_obj.save()

    #si no es igual inicializamos el registro con la nueva referencia y la primera empresa a ignorar
    else:
        empresas_a_ignorar_obj.referencia = str_actual
        empresas_a_ignorar_obj.valor = empresa
        empresas_a_ignorar_obj.save()

def obtener_empresas_a_ignorar():
    ''' Para obtener una lista de las empresas a ignorar. '''
    
    empresas_a_ignorar = []

    empresas_a_ignorar_obj = RegistryLong.objects.get(nombre='SIC_EnlaceLiquida_EmpresasFacturaCertificada')
    actual_year = datetime.datetime.now().year
    actual_month = datetime.datetime.now().month
    str_actual = u"%s%s"%(str(actual_year),str(actual_month))

    # si no tenemos ningun valor en referencia no hay empresas a ignorar
    if empresas_a_ignorar_obj.referencia:

        referencia = empresas_a_ignorar_obj.referencia.strip(' ')
        # Si la referencia es  igual a la referencia actual creada
        # --------------------------------------------------------
        # REFERENCIA: es para si se esta ravisando empresas de otro mes diferente 
        # a la actual entonces se resetea valor del registro para tomar en cuenta 
        # todas las empresas desde el principio

        # si la referencia es igual sacamos las empresas a ignorar
        if str_actual ==  referencia:
            if empresas_a_ignorar_obj.valor:
                empresas_a_ignorar = empresas_a_ignorar_obj.valor.split(',')

        #si no es igual inicializamos el registro con la nueva referencia y con empresa a ignorar vacio
        else:
            empresas_a_ignorar_obj.valor = ""
            empresas_a_ignorar_obj.referencia = str_actual
            empresas_a_ignorar_obj.save()

    return empresas_a_ignorar

@login_required( login_url = '/login/' )
def index( request, template_name = 'django-microsip-liquida/index.html' ):
    modo_servidor = settings.MODO_SERVIDOR
    
    using = router.db_for_write(Registry)
    actual_year = datetime.datetime.now().year
    actual_month = datetime.datetime.now().month
    initial_configuration = InitialConfiguration(using)
    c= {}

    if not initial_configuration.is_valid():
        c['errors'] = initial_configuration.errors
    else:
        #Para ignorar las empresas que ya se certificaron
        empresas_a_ignorar = obtener_empresas_a_ignorar()
        databases = settings.MICROSIP_DATABASES.keys()
        for empresa_a_ignorar in empresas_a_ignorar:
            if str(empresa_a_ignorar) in databases:
                databases.remove(empresa_a_ignorar)
                    
        facturas_dic = []
        fecha_actual = datetime.date.today()
        errores = []

        # Para poner un numero como ultimo si quedan menos de 50 facturas por checar
        ultimo = 50
        if len(databases) < ultimo:
            ultimo = len(databases)
        
        for using in databases[0:ultimo]:

            try:
                # Sacamos todas las facturas de la epmpresa (using) pendientes por facturar
                facturas = VentasDocumento.objects.using(using).filter(tipo='F', fecha= datetime.datetime.now(), estado='N', modalidad_facturacion='CFDI',cfd_certificado='N', ).values_list('id','folio','importe_neto','impuestos_total','retenciones_total','fecha',)

                # Si no encomntramos facturas pendientes por facturar 
                # agregamos la empresa (using) a empresas a ignorar
                if not facturas:
                    agregar_empresa_a_ignorar(using)

                for factura in facturas:
                    importe_neto = factura[2]
                    impuestos_total = factura[3]
                    retenciones_total = factura[4]
                    fecha = factura[5]
                    importe_total = importe_neto+ impuestos_total- retenciones_total
                    facturas_dic.append({
                        'id': "%s;%s"%(using, factura[0]),
                        'folio': factura[1],
                        'fecha': fecha,
                        'empresa': using,
                        'importe_total': importe_total,
                        })  
            except:
                errores.append(using)
        fc=facturas_dic[0:ultimo]

        c = {'facturas':facturas_dic[0:ultimo], 'today':fecha_actual, 'errores': errores, 'modo_servidor':modo_servidor,}

    return render_to_response( template_name, c, context_instance = RequestContext( request ) )
    
from django.core import serializers
import json
from django.views.generic import TemplateView
@login_required(login_url='/login/')
def PrepararEmpresasView(request, template_name='django-microsip-liquida/preparar_empresas.html'):
    msg = ''
    form = SelectDBForm(request.POST or None)
    if form.is_valid():
        #Datos de origen
        articulo_clave = Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ArticuloClave').get_value()
        origen_articulo_clave = ArticuloClave.objects.get(clave=articulo_clave)
        origen_articulo =  origen_articulo_clave.articulo

        origen_impuesto_articulo = first_or_none(ImpuestosArticulo.objects.filter(articulo=origen_articulo))
        origen_impuesto = origen_impuesto_articulo.impuesto

        #Datos de destino
        database_to_clone = form.cleaned_data['conexion']

        destino_articulo = first_or_none(Articulo.objects.using(database_to_clone).filter(nombre=origen_articulo.nombre))
        
        #Si no existe articulo crea el articulo
        if destino_articulo:
            destino_articulo.nombre = origen_articulo.nombre
            destino_articulo.es_almacenable = origen_articulo.es_almacenable
            destino_articulo.estatus = origen_articulo.estatus
            destino_articulo.seguimiento = origen_articulo.seguimiento
            destino_articulo.cuenta_ventas = origen_articulo.cuenta_ventas
            destino_articulo.nota_ventas = origen_articulo.nota_ventas
            destino_articulo.unidad_venta = origen_articulo.unidad_venta
            destino_articulo.unidad_compra = origen_articulo.unidad_compra
            destino_articulo.costo_ultima_compra = origen_articulo.costo_ultima_compra
            destino_articulo.usuario_ult_modif = origen_articulo.usuario_ult_modif
            destino_articulo.save(using=database_to_clone)
        else:
            destino_articulo = Articulo.objects.using(database_to_clone).create(
                    nombre = origen_articulo.nombre,
                    es_almacenable = origen_articulo.es_almacenable,
                    estatus = origen_articulo.estatus,
                    seguimiento = origen_articulo.seguimiento,
                    cuenta_ventas = origen_articulo.cuenta_ventas,
                    nota_ventas = origen_articulo.nota_ventas,
                    unidad_venta = origen_articulo.unidad_venta,
                    unidad_compra = origen_articulo.unidad_compra,
                    costo_ultima_compra = origen_articulo.costo_ultima_compra,
                    usuario_ult_modif = origen_articulo.usuario_ult_modif,
                )

        #CLAVE DE ARTICULO
        destino_articulo_clave = first_or_none(ArticuloClave.objects.using(database_to_clone).filter(articulo=destino_articulo, rol__es_ppal='S'))
        rol_principal = ArticuloClaveRol.objects.using(database_to_clone).get(es_ppal='S')
        if not destino_articulo_clave:
            ArticuloClave.objects.using(database_to_clone).create(
                clave = articulo_clave,
                articulo = destino_articulo,
                rol = rol_principal,
            )

        #IMPUESTO DE ARTICULO
        destino_impuesto = first_or_none(Impuesto.objects.using(database_to_clone).filter(nombre=origen_impuesto.nombre))

        if not destino_impuesto:
            tipo_impuesto = first_or_none(ImpuestoTipo.objects.using(database_to_clone).filter(nombre=origen_impuesto.tipoImpuesto.nombre))
            destino_impuesto = Impuesto.objects.using(database_to_clone).create(
                nombre= origen_impuesto.nombre,
                tipoImpuesto = tipo_impuesto,
                tipo_iva = origen_impuesto.tipo_iva,
                porcentaje = origen_impuesto.porcentaje
            )
        
        destino_impuesto_articulo = first_or_none(ImpuestosArticulo.objects.using(database_to_clone).filter(articulo=destino_articulo, impuesto = destino_impuesto))
        if not destino_impuesto_articulo:
            ImpuestosArticulo.objects.using(database_to_clone).create(
                articulo = destino_articulo,
                impuesto = destino_impuesto,
            )

        #Origen Cliente
        origen_cliente =  first_or_none(Cliente.objects.filter(nombre=Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ClienteNombre').get_value()))
        origen_condicion_pago = origen_cliente.condicion_de_pago
        origen_primer_plazo = first_or_none(CondicionPagoPlazo.objects.filter(condicion_de_pago= origen_condicion_pago))
        origen_direccion = first_or_none(ClienteDireccion.objects.filter(cliente=origen_cliente))

        #Condicion de pago
        destino_condicion_pago = first_or_none(CondicionPago.objects.using(database_to_clone).filter(nombre=origen_condicion_pago.nombre))
        if not destino_condicion_pago:
            destino_condicion_pago = CondicionPago.objects.using(database_to_clone).create(
                nombre= origen_condicion_pago.nombre,
                dias_ppag= origen_condicion_pago.dias_ppag,
                porcentaje_descuento_ppago= origen_condicion_pago.porcentaje_descuento_ppago,
                es_predet= origen_condicion_pago.es_predet,
                usuario_creador= origen_condicion_pago.usuario_creador,
                usuario_ult_modif= origen_condicion_pago.usuario_creador
            )

        destino_primer_plazo = first_or_none(CondicionPagoPlazo.objects.using(database_to_clone).filter(condicion_de_pago= destino_condicion_pago))
        if not destino_primer_plazo:
            CondicionPagoPlazo.objects.using(database_to_clone).create(
                condicion_de_pago = destino_condicion_pago,
                dias = origen_primer_plazo.dias,
                porcentaje_de_venta = origen_primer_plazo.porcentaje_de_venta
            )
        destino_cliente =  first_or_none(Cliente.objects.using(database_to_clone).filter(nombre=origen_cliente.nombre))
        if not destino_cliente:
            destino_cliente = Cliente.objects.using(database_to_clone).create(
                nombre = origen_cliente.nombre,
                condicion_de_pago = destino_condicion_pago,
                moneda = origen_cliente.moneda,
                cobrar_impuestos = origen_cliente.cobrar_impuestos,
                generar_interereses = origen_cliente.generar_interereses,
                emir_estado_cuenta = origen_cliente.emir_estado_cuenta,
            )
        else:
            destino_cliente.nombre = origen_cliente.nombre    
            destino_cliente.condicion_de_pago = destino_condicion_pago
            destino_cliente.moneda = origen_cliente.moneda
            destino_cliente.cobrar_impuestos = origen_cliente.cobrar_impuestos
            destino_cliente.generar_interereses = origen_cliente.generar_interereses
            destino_cliente.emir_estado_cuenta = origen_cliente.emir_estado_cuenta
        
            destino_cliente.save(using=database_to_clone)

        origen_pais = None
        origen_estado = None
        origen_ciudad = None
        if origen_direccion:
            origen_ciudad = origen_direccion.ciudad
            if origen_ciudad:
                origen_estado = origen_ciudad.estado
                origen_pais = origen_estado.pais
                
        destino_pais = None
        destino_estado = None
        destino_ciudad = None
        
        if origen_ciudad:        
            destino_pais = first_or_none(Pais.objects.using(database_to_clone).filter(nombre=origen_pais.nombre))
            destino_estado = first_or_none(Estado.objects.using(database_to_clone).filter(nombre=origen_estado.nombre))
            destino_ciudad = first_or_none(Ciudad.objects.using(database_to_clone).filter(nombre=origen_ciudad.nombre))
            
        if not destino_pais:
            destino_pais = Pais.objects.using(database_to_clone).create(
                nombre= origen_pais.nombre,
                es_predet = origen_pais.es_predet,
                nombre_abreviado = origen_pais.nombre_abreviado
            )

        if not destino_estado:
            destino_estado = Estado.objects.using(database_to_clone).create(
                nombre= origen_estado.nombre,
                nombre_abreviado = origen_estado.nombre_abreviado,
                es_predet= origen_estado.es_predet,
                pais = destino_pais
            )
        
        if not destino_ciudad:
            destino_ciudad = Ciudad.objects.using(database_to_clone).create(
                nombre= origen_ciudad.nombre,
                es_predet= origen_ciudad.es_predet,
                estado = destino_estado
            )
            
        destino_direccion = first_or_none(ClienteDireccion.objects.using(database_to_clone).filter(cliente=destino_cliente))

        if not destino_direccion:
            destino_direccion = ClienteDireccion.objects.using(database_to_clone).create(
                cliente= destino_cliente,
                rfc_curp= origen_direccion.rfc_curp,
                ciudad= destino_ciudad,
                estado= destino_estado,
                pais= destino_pais,
                colonia= origen_direccion.colonia,
                nombre_consignatario= origen_direccion.nombre_consignatario,
                calle= origen_direccion.calle,
                es_ppal= origen_direccion.es_ppal,
                referencia= origen_direccion.referencia,
                codigo_postal= origen_direccion.codigo_postal,
                calle_nombre= origen_direccion.calle_nombre,
                numero_exterior= origen_direccion.numero_exterior,
                numero_interior= origen_direccion.numero_interior,
                email= origen_direccion.email,
            )
        else:
            destino_direccion.rfc_curp = origen_direccion.rfc_curp
            destino_direccion.ciudad = destino_ciudad
            destino_direccion.colonia = origen_direccion.colonia
            destino_direccion.nombre_consignatario = origen_direccion.nombre_consignatario
            destino_direccion.calle = origen_direccion.calle
            destino_direccion.es_ppal = origen_direccion.es_ppal
            if settings.MICROSIP_VERSION >= 2013:
                destino_direccion.poblacion = origen_direccion.poblacion
            destino_direccion.referencia = origen_direccion.referencia

            destino_direccion.codigo_postal = origen_direccion.codigo_postal
            destino_direccion.calle_nombre = origen_direccion.calle_nombre
            destino_direccion.numero_exterior = origen_direccion.numero_exterior
            destino_direccion.numero_interior = origen_direccion.numero_interior
            destino_direccion.email = origen_direccion.email

            destino_direccion.save(using=database_to_clone)
            


    c = { 'msg':msg, 'form':form, }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def PreferenciasManageView(request, template_name='django-microsip-liquida/herramientas/preferencias.html'):
    msg = ''
    
    form_initial = {
        'facturaa_cliente': first_or_none(Cliente.objects.filter(nombre=Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ClienteNombre').get_value())),
        'facturaa_articulo_clave': Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ArticuloClave').get_value(),
        'ruta_liquidacion': Registry.objects.get(nombre='SIC_EnlaceLiquida_RutaLiquidacion').get_value(),
        'empresas_a_ignorar': Registry.objects.get(nombre='SIC_EnlaceLiquida_EmpresasAIgnorar').get_value(),
        'carpeta_facturacion_sat': Registry.objects.get( nombre = 'SIC_CarpetaFacturacionSAT').get_value(),
    }

    form  = PreferenciasManageForm(request.POST or None, initial=form_initial)
    warrning = ''

    if form.is_valid():
        formulario_valido = Registry.objects.get( nombre = 'SIC_EnlaceLiquida_ConfigFormLleno' )
        formulario_valido.valor = 1
        formulario_valido.save()
        form.save()
        msg = 'Datos guardados correctamente'

    c = { 'form':form, 'msg':msg,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required( login_url = '/login/' )
def UpdateConfigurationDatabase(request):
    """ Agrega campos nuevos en tablas de base de datos. """
    padre = first_or_none(Registry.objects.filter(nombre='PreferenciasEmpresa'))
    if request.user.is_superuser and padre:
        
        using = router.db_for_write(Registry)
        c = connections[using].cursor()
        c.execute('''
            CREATE OR ALTER PROCEDURE SIC_CREA_REGISTRY 
            as
            begin
                if (not exists(
                select 1 from rdb$relations where rdb$relation_name = 'SIC_REGISTRY')) then
                    execute statement 'create table SIC_REGISTRY (id int not null primary key, nombre char(100) not null, referencia char(100), valor memo)';
            end
        ''')
        c.execute('EXECUTE PROCEDURE SIC_CREA_REGISTRY;')
        c.execute('DROP PROCEDURE SIC_CREA_REGISTRY;')
        c.close()
        management.call_command( 'syncdb', database = using, interactive= False)

        if not RegistryLong.objects.filter( nombre = 'SIC_EnlaceLiquida_EmpresasFacturaCertificada' ).exists():
            RegistryLong.objects.create(
                id = 1,
                nombre = 'SIC_EnlaceLiquida_EmpresasFacturaCertificada',
                referencia = '',
                valor = '',
            )

        if not Registry.objects.filter( nombre = 'SIC_EnlaceLiquida_EmpresasAIgnorar' ).exists():
            Registry.objects.create(
                nombre = 'SIC_EnlaceLiquida_EmpresasAIgnorar',
                tipo = 'V',
                padre = padre,
                valor= '',
            )

        if not Registry.objects.filter( nombre = 'SIC_EnlaceLiquida_FacturarA_ClienteNombre' ).exists():
            Registry.objects.create(
                nombre = 'SIC_EnlaceLiquida_FacturarA_ClienteNombre',
                tipo = 'V',
                padre = padre,
                valor= '',
            )

        if not Registry.objects.filter( nombre = 'SIC_EnlaceLiquida_FacturarA_ArticuloClave' ).exists():
            Registry.objects.create(
                nombre = 'SIC_EnlaceLiquida_FacturarA_ArticuloClave',
                tipo = 'V',
                padre = padre,
                valor= '',
            )

        if not Registry.objects.filter( nombre = 'SIC_EnlaceLiquida_RutaLiquidacion' ).exists():
            Registry.objects.create(
                nombre = 'SIC_EnlaceLiquida_RutaLiquidacion',
                tipo = 'V',
                padre = padre,
                valor= 'C:\Liquida',
            )

        if not Registry.objects.filter( nombre = 'SIC_INDICE_BASES_DATOS_SYN' ).exists():
            Registry.objects.create(
                nombre = 'SIC_INDICE_BASES_DATOS_SYN',
                tipo = 'V',
                padre = padre,
                valor= '',
            )
        if not Registry.objects.filter( nombre = 'SIC_EnlaceLiquida_ConfigFormLleno' ).exists():
            Registry.objects.create(
                nombre = 'SIC_EnlaceLiquida_ConfigFormLleno',
                tipo = 'V',
                padre = padre,
                valor= '0',
            )

        if not Registry.objects.filter( nombre = 'SIC_CarpetaFacturacionSAT' ).exists():
            Registry.objects.create(
                nombre = 'SIC_CarpetaFacturacionSAT',
                tipo = 'V',
                padre = padre,
                valor= '',
            )
        
    return HttpResponseRedirect('/enlace_liquida/')

@login_required( login_url = '/login/' )
def CertificarFacturasTests(request):
    errors = []
    using = request.GET['using']

    errors.append('error en %s'%using)
    data = { 'errors': errors, 'using':using, }
    return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required( login_url = '/login/' )
def CertificarFacturas(request):
    factura_id = request.GET['factura_id']
    using = request.GET['using']
    # PROD, PRUEBAS
    carpeta_facturacion_sat = Registry.objects.get(nombre='SIC_CarpetaFacturacionSAT').get_value()  
    facturar_a_cliente_nombre = Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ClienteNombre').get_value()
    facturaa_articulo_clave = Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ArticuloClave').get_value()
    certificador_sat = CertificadorSAT(carpeta_facturacion_sat, modo=settings.MODO_SERVIDOR)
    datos_empresa = Registry.objects.using(using).get(nombre='DatosEmpresa')
    datos_empresa = Registry.objects.using(using).filter(padre=datos_empresa)
    rfc = datos_empresa.get(nombre='Rfc').get_value().replace('-','').replace(' ','')

    documento = VentasDocumento.objects.using(using).get(pk=factura_id)
    # #Se crear archivo ini
    create_ini_file_33_ve(documento.id, carpeta_facturacion_sat, using)
    
    #Se certifica con archivo ini
    ini_file_path = "%s\\facturas\\%s.ini"%(carpeta_facturacion_sat, documento.folio)

    errors = certificador_sat.certificar_33(ini_file_path=ini_file_path,rfc=rfc)
    if not errors:
        #Se guarda archivo xml en documento
        save_xml_in_document_33_ve(ini_file_path, using, documento.id)
        agregar_empresa_a_ignorar(using)

    if errors:
        errors="%s:%s"%(using,errors)
    data = { 'errors': errors }
    return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required( login_url = '/login/' )
def actualiza_nombes_de_carpetas_sellos( request ):
    carpeta_facturacion_sat = Registry.objects.get(nombre='SIC_CarpetaFacturacionSAT').get_value()  
    ruta_sellos = os.path.join(carpeta_facturacion_sat,'sellos')

    registro =  Registry.objects.get(nombre='SIC_INDICE_BASES_DATOS_SYN').valor
    registro_split = registro.split(';')
    if len(registro_split)== 2:
        registro_tipo = registro_split[0]
        valor = int(registro_split[1])
        if registro_tipo != 'CARPETAS_UPDATE':
            valor = 0
    else:
        valor = 0

    data_bases = split_seq(settings.MICROSIP_DATABASES.keys(),70)

    for data_base in data_bases[valor]:
        data_base_rfc = Registry.objects.using(data_base).filter(padre__nombre='DatosEmpresa').get(nombre='Rfc').get_value().replace('-','').replace(' ','')
        data_base_name = data_base[3:]
        sellos_empresa_nombre_path = os.path.join(ruta_sellos,data_base_name)
        
        sellos_empresa_rfc_path = os.path.join(ruta_sellos,data_base_rfc)
        
        if os.path.exists(sellos_empresa_nombre_path):
            if not os.path.exists(sellos_empresa_rfc_path):
                os.rename(sellos_empresa_nombre_path,sellos_empresa_rfc_path)
            else:
                os.rename(sellos_empresa_nombre_path,sellos_empresa_nombre_path+"DUPLICADO")

    registro =  Registry.objects.get(nombre='SIC_INDICE_BASES_DATOS_SYN')
    valor = valor +1
    #Si el indice del split de facturs es el ultimo se inicia en 0
    if valor == len(data_bases):
        valor = 0
        print 'SE TERMINO CON TODAS LAS CARPETAS'
    registro.valor ="CARPETAS_UPDATE;%s"% str(valor)
    registro.save()

    return HttpResponseRedirect('/enlace_liquida/')

@login_required( login_url = '/login/' )
def DescargarFacturasDelMes(request):
    errors = []
    facturar_a_cliente_nombre = Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ClienteNombre').get_value()
    facturaa_articulo_clave = Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ArticuloClave').get_value()

    conexion_activa  = request.session['conexion_activa']
    fecha_actual = datetime.datetime.today()
    facturas, errors = get_facturasmes_liquidacion()
    empresa_clave = ''
    progress =0
    indice_siguiente =0

    cliente_no_existe = ''
    documento_ya_existe = ''
    consecutivo_folio_no_definido = ''

    if not errors:
        facturas_len = len(facturas)
        descripcion_documentos = 'LIQUIDACIONES-%s-%s'%(fecha_actual.month, fecha_actual.year)
        indice, indice_siguiente = get_indices(facturas_len, 1, 'DESCARGAR_FACTURAS_MES')
        
        factura = facturas[indice]
        empresa_clave = factura['empresa_clave']
        using = '%02d-%s'% (conexion_activa,factura['empresa_clave'])
        
        if using in settings.MICROSIP_DATABASES:
            documento_sin_generar = not VentasDocumento.objects.using(using).filter(descripcion=descripcion_documentos).exists()
            consecutivo_folio_definido = FolioVenta.objects.using(using).filter(tipo_doc = 'F', modalidad_facturacion = 'CFDI').count() > 0
            cliente_existe = Cliente.objects.using(using).filter(nombre=facturar_a_cliente_nombre).count() > 0


            if not consecutivo_folio_definido or not cliente_existe or not documento_sin_generar:
                if not consecutivo_folio_definido:
                    consecutivo_folio_no_definido = factura['empresa_clave']
                if not cliente_existe:
                    cliente_no_existe = factura['empresa_clave']
                if not documento_sin_generar:
                    documento_ya_existe = factura['empresa_clave']

            if documento_sin_generar and consecutivo_folio_definido and cliente_existe:
                
                datos_empresa = Registry.objects.using(using).get(nombre='DatosEmpresa')
                datos_empresa = Registry.objects.using(using).filter(padre=datos_empresa)
                rfc = datos_empresa.get(nombre='Rfc').get_value().replace('-','').replace(' ','')
                cliente        = Cliente.objects.using(using).filter(nombre=facturar_a_cliente_nombre).values_list('condicion_de_pago', 'moneda',)[0]
                condicion_pago = CondicionPago.objects.using(using).get(pk=cliente[0])
                moneda         = Moneda.objects.using(using).get(pk=cliente[1])
                cliente        = Cliente.objects.using(using).get(nombre=facturar_a_cliente_nombre)
                almacen        = Almacen.objects.using(using).get(es_predet='S')

                direccion = first_or_none(ClienteDireccion.objects.using(using).filter(cliente= cliente))
                documento = VentasDocumento.objects.using(using).create(
                        tipo                    = 'F',
                        subtipo                 ='N', 
                        fecha                   = datetime.datetime.now(),
                        cliente                 = cliente,
                        descripcion             = descripcion_documentos,
                        cliente_clave           = '',
                        cliente_direccion       = direccion,
                        direccion_consignatario = direccion,
                        almacen                 = almacen,
                        moneda                  = moneda,
                        estado                  = 'N',
                        aplicado                = 'N',
                        importe_neto            = factura['importe_neto'],
                        sistema_origen          = 'VE',
                        condicion_pago          = condicion_pago,
                        es_cfd                  = 'S',
                        modalidad_facturacion   = 'CFDI',
                        uso_cfdi                = 'G03',
                        metodo_pago_sat         = 'PPD',
                        envio_fechahora         = None,
                        creacion_usuario        = request.user.username,
                    )

                #plazos de pagos
                plazos = CondicionPagoPlazo.objects.using(using).filter(condicion_de_pago=condicion_pago)
                for plazo in plazos:
                    fecha_vencimiento = documento.fecha + timedelta(days=plazo.dias)
                    c = connections[using].cursor()
                    query =  '''INSERT INTO "VENCIMIENTOS_CARGOS_VE" ("DOCTO_VE_ID", "FECHA_VENCIMIENTO", "PCTJE_VEN") \
                        VALUES (%s, %s, %s)'''
                    c.execute(query,[documento.id,  fecha_vencimiento, plazo.porcentaje_de_venta])
                    c.close()

                articulo_id = ArticuloClave.objects.using(using).filter(clave=facturaa_articulo_clave).values_list('articulo')[0][0]
                articulo = Articulo.objects.using(using).get(pk=articulo_id)
               
                for detalle in factura['detalles']:
                    unidades = detalle[1]
                    precio = detalle[2]
                    importe_neto =  detalle[3]
                    VentasDocumentoDetalle.objects.using(using).create(
                        documento         = documento,
                        articulo_clave    = facturaa_articulo_clave,
                        articulo          = articulo,
                        unidades          = unidades,
                        precio_unitario   = precio,
                        precio_total_neto = importe_neto
                        )

        progress = indice_siguiente * 100 / facturas_len;
        set_indices(indice_siguiente, facturas_len, 'DESCARGAR_FACTURAS_MES')
        
    data = { 
        'progress': progress,
        'basedatos_no':empresa_clave, 
        'errors':errors, 
        'cliente_no_existe':cliente_no_existe,
        'documento_ya_existe':documento_ya_existe,
        'consecutivo_folio_no_definido':consecutivo_folio_no_definido,
    }
    data = json.dumps(data)
    registry = RegistryLong.objects.get(nombre='SIC_EnlaceLiquida_EmpresasFacturaCertificada')
    registry.valor = ''
    registry.save()
    return HttpResponse(data, mimetype='application/json')

@login_required( login_url = '/login/' )
def GetEmpresasList(request):
    empresas_a_ignorar = Registry.objects.get(nombre='SIC_EnlaceLiquida_EmpresasAIgnorar').get_value()
    using = router.db_for_write(Registry)
    conexion_no = using.split('-')[0]
    if empresas_a_ignorar:
        
        empresas_a_ignorar = empresas_a_ignorar.split(',')
        empresas_a_ignorar = [ conexion_no + '-' + empresa for empresa in empresas_a_ignorar ]
    else:
        empresas_a_ignorar = []

    databases = settings.MICROSIP_DATABASES.keys()
    databases.remove(using)
    for empresa_a_ignorar in empresas_a_ignorar:
        if str(empresa_a_ignorar) in databases:
            databases.remove(empresa_a_ignorar)
    
    cliente_nombre = Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ClienteNombre').get_value()
    articulo_clave = Registry.objects.get(nombre='SIC_EnlaceLiquida_FacturarA_ArticuloClave').get_value()
    articulo_nombre = ArticuloClave.objects.get(clave=articulo_clave).articulo.nombre

    data = { 
        'empresas': databases,
        'cliente_nombre':cliente_nombre,
        'articulo_nombre':articulo_nombre,
    }

    data = json.dumps(data)

    return HttpResponse(data, mimetype='application/json')

@login_required( login_url = '/login/' )
def ValidarEmpresa(request):
    empresa_id = request.GET['empresa_id']
    cliente_nombre = request.GET['cliente_nombre']
    articulo_nombre = request.GET['articulo_nombre']
    is_valid = False
    cliente =  first_or_none(Cliente.objects.using(empresa_id).filter(nombre=cliente_nombre))
    articulo = first_or_none(Articulo.objects.using(empresa_id).filter(nombre=articulo_nombre))

    if cliente and articulo:
        is_valid = True


        
    data = { 
        'is_valid': is_valid,
    }

    data = json.dumps(data)

    return HttpResponse(data, mimetype='application/json')