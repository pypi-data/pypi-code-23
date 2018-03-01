# -*- coding: utf-8 -*-
from daylifact.entidades import *
import xml.etree.cElementTree as ETXML
from daylifact.logica import Crear_XML
import datetime
import os

# Ruta en donde se van a guardar los archivos generados
ruta_archivos = os.path.abspath("E:/test")

# Retorna una lista de entidades del tipo Impuesto
def Formato_Total_Con_Impuestos():
    # ETIQUETA XML: <totalConImpuestos>
    # Apartado Total con impuestos (Por toda la factura)

    # Simulación de los impuestos en la factura
    total_con_impuestos = []

    # 'codigo': Nombre del impuesto: iva (IVA 0% e IVA 12%) | ice (ICE %) | irbpnr
    # 'codigo_porcentaje': Porcentaje de IVA únicamente (0, 12, 14...) ** la tarifa ICE tiene sus propios códigos (VER TABLA 19 SRI) *** la tarifa IRBPNR tiene sus propios códigos
    # 'descuento_adicional': -1,  # Opcional solo aplica para codigo iva

    imp1 = Impuesto()
    imp1.codigo = 'iva'
    imp1.codigo_porcentaje = 'noiva' #Puede ser int o str
    imp1.descuento_adicional = -1 # Opcional solo aplica para código iva. Poner -1 si este campo está vacío
    imp1.base_imponible = 15
    imp1.valor = 0

    imp2 = Impuesto()
    imp2.codigo = 'iva'
    imp2.codigo_porcentaje = 'excento' #Puede ser int o str
    imp2.descuento_adicional = -1  # Opcional solo aplica para código iva. Poner -1 si este campo está vacío
    imp2.base_imponible = 4
    imp2.valor = 0

    imp3 = Impuesto()
    imp3.codigo = 'ice'
    imp3.codigo_porcentaje = 3011 #Puede ser int o str
    imp3.base_imponible = 14
    imp3.valor = 5

    imp4 = Impuesto()
    imp4.codigo = 'irbpnr'
    imp4.codigo_porcentaje = 5001 #Puede ser int o str
    imp4.base_imponible = 0
    imp4.valor = 4

    total_con_impuestos.append(imp1)
    total_con_impuestos.append(imp2)
    total_con_impuestos.append(imp3)
    total_con_impuestos.append(imp4)

    return total_con_impuestos

# Retorna una lista de entidades del tipo Detalle_Adicional
def Formato_Info_Adicional():
    # ETIQUETA XML: <infoAdicional>
    # Apartado info adicional (OPCIONAL)

    # Simulación de la info adicional
    info_adicional = []

    inf1 = Detalle_Adicional('Direccion', 'NADA')
    inf2 = Detalle_Adicional('Email', 'asdas@gmail.com')

    info_adicional.append(inf1)
    info_adicional.append(inf2)

    return info_adicional

# Retorna una lista de entidades del tipo Detalle_Adicional
def Detalle_Adicional_Prod1():
    # ETIQUETA XML: <detallesAdicionales>
    # Apartado detalles adicionales del producto(OPCIONAL)

    # Simulación de los detalles adicionales (En caso de tenerlos)
    detalles_adicionales_prod1 = []

    det_prod1_1 = Detalle_Adicional('Marca Chevrolet', 'Chevrolet')
    det_prod1_2 = Detalle_Adicional('Modelo', '2012')

    detalles_adicionales_prod1.append(det_prod1_1)
    detalles_adicionales_prod1.append(det_prod1_2)

    return  detalles_adicionales_prod1

# Retorna una lista de entidades del tipo Impuesto
def Impuestos_Prod1():
    # ETIQUETA XML: <impuestos>
    # Apartado impuestos (Por cada producto en el detalle de la factura)

    # Simulación de los impuestos en el detalle
    impuestos = []

    # 'codigo': Nombre del impuesto: iva (IVA 0% e IVA 12%) | ice (ICE %) | irbpnr
    # 'codigo_porcentaje': Porcentaje de IVA únicamente (0, 12, 14...) ** la tarifa ICE tiene sus propios códigos (VER TABLA 19 SRI) *** la tarifa IRBPNR tiene sus propios códigos

    imp1 = Impuesto()
    imp1.codigo = 'ice'
    imp1.codigo_porcentaje = 3011 #Puede ser int o str
    imp1.tarifa = 0
    imp1.base_imponible = 2
    imp1.valor = 2

    imp2 = Impuesto()
    imp2.codigo = 'iva'
    imp2.codigo_porcentaje = 'excento' #Puede ser int o str
    imp2.tarifa = 0
    imp2.base_imponible = 4
    imp2.valor = 0

    imp3 = Impuesto()
    imp3.codigo = 'irbpnr'
    imp3.codigo_porcentaje = 5001 #Puede ser int o str
    imp3.tarifa = 0
    imp3.base_imponible = 0
    imp3.valor = 1

    impuestos.append(imp1)
    impuestos.append(imp2)
    impuestos.append(imp3)

    return impuestos

# Retorna una lista de entidades del tipo Impuesto
def Impuestos_Prod2():
    # ETIQUETA XML: <impuestos>
    # Apartado impuestos (Por cada producto en el detalle de la factura)

    # Simulación de los impuestos en el detalle
    impuestos = []

    # 'codigo': Nombre del impuesto: iva (IVA 0% e IVA 12%) | ice (ICE %) | irbpnr
    # 'codigo_porcentaje': Porcentaje de IVA únicamente (0, 12, 14...) ** la tarifa ICE tiene sus propios códigos (VER TABLA 19 SRI) *** la tarifa IRBPNR tiene sus propios códigos

    imp1 = Impuesto()
    imp1.codigo = 'iva'
    imp1.codigo_porcentaje = 'noiva' #Puede ser int o str
    imp1.tarifa = 0
    imp1.base_imponible = 15
    imp1.valor = 0

    imp2 = Impuesto()
    imp2.codigo = 'ice'
    imp2.codigo_porcentaje = 3011 #Puede ser int o str
    imp2.tarifa = 0
    imp2.base_imponible = 12
    imp2.valor = 3

    imp3 = Impuesto()
    imp3.codigo = 'irbpnr'
    imp3.codigo_porcentaje = 5001 #Puede ser int o str
    imp3.tarifa = 0
    imp3.base_imponible = 0
    imp3.valor = 3

    impuestos.append(imp1)
    impuestos.append(imp2)
    impuestos.append(imp3)

    return impuestos

# Retorna una lista de entidades del tipo Detalle_Factura
def Formato_Detalle_Factura():
    # ETIQUETA XML: <detalles>
    # Apartado detalle de cada producto

    productos = []

    # Simulacion de productos en el detalle
    # ------------ Producto 1 -------------
    prod1 = Detalle_Factura()
    prod1.codigo_principal = 'AUX1'
    prod1.codigo_auxiliar = 'UAX2'  # Opcional
    prod1.descripcion = 'PRUEBA'
    prod1.cantidad =  1
    prod1.precio_unitario = 2
    prod1.descuento = 0
    prod1.precio_total_sin_impuesto = 2
    #prod1.detalles_adicionales = Detalle_Adicional_Prod1() # Opcional
    prod1.impuestos = Impuestos_Prod1()

    # ------------ Producto 2 -------------
    prod2 = Detalle_Factura()
    prod2.codigo_principal = '2'
    prod2.codigo_auxiliar = '23'  # Opcional
    prod2.descripcion = 'PRUEBA 2'
    prod2.cantidad = 1
    prod2.precio_unitario = 12
    prod2.descuento = 0
    prod2.precio_total_sin_impuesto = 12
    prod2.impuestos = Impuestos_Prod2()

    productos.append(prod1)
    productos.append(prod2)

    return productos

# Retorna una lista de entidades del tipo Pago
def Formato_Pagos():
    # ETIQUETA XML: <pagos>
    # Apartado forma de pago de la factura

    pagos = []

    # Simulacion de formas de pago

    # ------ FORMAS DE PAGO VALIDAS ------
    # 'efectivo': SIN UTILIZACION DEL SISTEMA FINANCIERO
    # 'deudas': COMPENSACIÓN DE DEUDAS
    # 'debito': TARJETA DE DÉBITO
    # 'electronico': DINERO ELECTRÓNICO
    # 'prepago': TARJETA PREPAGO
    # 'credito': TARJETA DE CRÉDITO
    # 'otros': OTROS CON UTILIZACION DEL SISTEMA FINANCIERO
    # 'endoso': ENDOSO DE TÍTULOS

    pag1 = Pago()
    pag1.forma_pago = 'efectivo' # FORMAS DE PAGO VALIDAS
    pag1.total = 23
    pag1.plazo = -1
    pag1.unidad_tiempo = None

    pagos.append(pag1)

    return pagos

# ------------------------------------------ Crear entidades -------------------------------------------

# ******************************** Empresa ********************************
emp = Empresa()
emp.razon_social = 'NOBLECILLA CASTRO RAUL NICOLAS'
emp.ruc = '0701010498001'
emp.dir_matriz = 'BOLIVAR Y MACHALA'
emp.nombre_comercial = 'FINCA PIEDAD' # Opcional
emp.dir_establecimiento = None # Opcional
emp.contribuyente_especial = None # Opcional
emp.obligado_contabilidad = 'SI' # Opcional

# ******************************** Cliente ********************************
cli = Cliente()
cli.tipo_identificacion_comprador = 'cedula' # ruc | cedula | pasaporte | consumidor_final | identificacion_exterior | placa
cli.razon_social_comprador = 'JENNIFER'
cli.identificacion_comprador = '0706418514'
cli.direccion_comprador = 'NADA' # Opcional

# ******************************** Factura ********************************

# Recibe los parametros:
# El ambiente (por defecto 'pruebas')
# El tipo de documento (por defecto 'factura')
# Un codigo numérico de 8 dígitos (por defecto '12345678') <- Servirá para crear la clave de acceso

fac = Factura('produccion', 'factura', '12345678')  # [pruebas | produccion] , [factura | credito | debito  | guia | retencion], [(cualquier valor numérico de 8 dígitos)]
fac.tipo_emision = 'normal' # normal | indisp (Indisponibilidad del sistema)
fac.estab = '001'
fac.pto_emi = '001'
fac.secuencial = '000000002'
fac.fecha_emision = '22/02/2018' #Puede ser str o datetime
fac.guia_remision = None # Opcional
fac.total_sin_impuestos = 14
fac.total_descuento = 0
fac.total_con_impuestos = Formato_Total_Con_Impuestos()
fac.propina = 0
fac.importe_total = 23
fac.pagos = Formato_Pagos()
fac.valor_ret_iva = -1 # Opcional
fac.valor_ret_renta = -1 # Opcional
fac.info_adicional = Formato_Info_Adicional() # Opcional

# ******************************* Detalle Factura ******************************
detalle =  Formato_Detalle_Factura()

# Construir archivo XML a partir de los datos de las entidades
try:
    # Enviar las entidades 'Empresa', 'Cliente', 'Factura' y la lista de Entidades 'Detalle_Factura'
    estado = Crear_XML(emp, cli, fac, detalle)

    if estado[0]:
        rootWrite = estado[1]
        rootWrite.write(os.path.join(ruta_archivos, fac.clave_acceso + '.xml'), encoding='utf8', xml_declaration=True)

        # import requests
        #
        # root = rootWrite.getroot()
        # xml_str = ETXML.tostring(root, encoding="utf8", method='xml')
        # unic = unicode(xml_str, "utf8")
        # print type(unic)
        # print unic
        #
        # r = requests.post('http://192.168.1.6:8000/firmar/', data={'credential': '65546ee3595560ba047b67307e0a87',
        #                                                          'file': xml_str,
        #                                                          'key': 'E:/PROYECTOS/API/apps/firmado/firma/certificado.p12',
        #                                                          'password': '1234'})
        # xml_firmado =  r.json()
        # result = xml_firmado['result']
        # message = xml_firmado['message']
        # file = xml_firmado['file']
        #
        # print result, message
        # print file
        # link para convertir str a element https://kite.com/docs/python;xml.etree.ElementTree.fromstring
        # Convertir string en XML
        # load_str = '<factura id="comprobante" version="1.0.0"><infoTributaria><ambiente>1</ambiente><tipoEmision>1</tipoEmision><razonSocial>á</razonSocial><nombreComercial>ee</nombreComercial><ruc>0701010498001</ruc><claveAcceso>2302201801070101049800110010010000000011234567816</claveAcceso><codDoc>01</codDoc><estab>001</estab><ptoEmi>001</ptoEmi><secuencial>000000001</secuencial><dirMatriz>Pasaje</dirMatriz></infoTributaria><infoFactura><fechaEmision>23/02/2018</fechaEmision><dirEstablecimiento>Pasaje</dirEstablecimiento><contribuyenteEspecial>SI</contribuyenteEspecial><obligadoContabilidad>NO</obligadoContabilidad><tipoIdentificacionComprador>04</tipoIdentificacionComprador><razonSocialComprador>CCCCC</razonSocialComprador><identificacionComprador>0701786360001</identificacionComprador><direccionComprador>Pasaje</direccionComprador><totalSinImpuestos>1</totalSinImpuestos><totalDescuento>1</totalDescuento><totalConImpuestos><totalImpuesto><codigo>2</codigo><codigoPorcentaje>0</codigoPorcentaje><descuentoAdicional>12</descuentoAdicional><baseImponible>1</baseImponible><valor>10</valor></totalImpuesto><totalImpuesto><codigo>2</codigo><codigoPorcentaje>2</codigoPorcentaje><descuentoAdicional>12</descuentoAdicional><baseImponible>1</baseImponible><valor>10</valor></totalImpuesto><totalImpuesto><codigo>3</codigo><codigoPorcentaje>3072</codigoPorcentaje><baseImponible>1</baseImponible><valor>10</valor></totalImpuesto></totalConImpuestos><propina>1</propina><importeTotal>2</importeTotal><moneda>DOLAR</moneda></infoFactura><detalles><detalle><codigoPrincipal>cod 0</codigoPrincipal><codigoAuxiliar>codigo0</codigoAuxiliar><descripcion>producto0</descripcion><cantidad>1</cantidad><precioUnitario>2</precioUnitario><descuento>0</descuento><precioTotalSinImpuesto>2</precioTotalSinImpuesto><detallesAdicionales><detAdicional nombre="Marca Chevrolet" valor="Chevrolet" /><detAdicional nombre="Modelo" valor="2012" /></detallesAdicionales><impuestos><impuesto><codigo>2</codigo><codigoPorcentaje>0</codigoPorcentaje><tarifa>1</tarifa><baseImponible>2</baseImponible><valor>2</valor></impuesto><impuesto><codigo>2</codigo><codigoPorcentaje>2</codigoPorcentaje><tarifa>1</tarifa><baseImponible>2</baseImponible><valor>2</valor></impuesto><impuesto><codigo>3</codigo><codigoPorcentaje>3072</codigoPorcentaje><tarifa>1</tarifa><baseImponible>2</baseImponible><valor>2</valor></impuesto></impuestos></detalle><detalle><codigoPrincipal>cod 1</codigoPrincipal><codigoAuxiliar>codigo1</codigoAuxiliar><descripcion>producto1</descripcion><cantidad>1</cantidad><precioUnitario>2</precioUnitario><descuento>0</descuento><precioTotalSinImpuesto>2</precioTotalSinImpuesto><detallesAdicionales><detAdicional nombre="Marca Chevrolet" valor="Chevrolet" /><detAdicional nombre="Modelo" valor="2012" /></detallesAdicionales><impuestos><impuesto><codigo>2</codigo><codigoPorcentaje>0</codigoPorcentaje><tarifa>1</tarifa><baseImponible>2</baseImponible><valor>2</valor></impuesto><impuesto><codigo>2</codigo><codigoPorcentaje>2</codigoPorcentaje><tarifa>1</tarifa><baseImponible>2</baseImponible><valor>2</valor></impuesto><impuesto><codigo>3</codigo><codigoPorcentaje>3072</codigoPorcentaje><tarifa>1</tarifa><baseImponible>2</baseImponible><valor>2</valor></impuesto></impuestos></detalle></detalles><infoAdicional><campoAdicional nombre="Direccion Secundaria">Bolivar y Machala</campoAdicional><campoAdicional nombre="Telefono">0999548253</campoAdicional></infoAdicional></factura>'
        #
        # root_str = ETXML.fromstring(load_str)
        # root_str_Write = ETXML.ElementTree(root_str)
        # root_str_Write.write(os.path.join(ruta_archivos, 'from_string.xml'), encoding='utf8', xml_declaration=True)
    else:
        print estado[1]
except Exception as exc:
    print 'Ha ocurrido un error'
    print exc
