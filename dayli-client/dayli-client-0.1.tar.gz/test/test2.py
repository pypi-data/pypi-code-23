# -*- coding: utf-8 -*-
from daylifact.entidades import *
from daylifact.logica import Crear_XML
import datetime
import os

# Ruta en donde se van a guardar los archivos generados
ruta_archivos = os.path.abspath("E:/test")

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
    imp1.codigo_porcentaje = 0 #Puede ser int o str
    imp1.base_imponible = 7
    imp1.valor = 0

    total_con_impuestos.append(imp1)

    return total_con_impuestos

def Formato_Info_Adicional():
    # ETIQUETA XML: <infoAdicional>
    # Apartado info adicional (OPCIONAL)

    # Simulación de la info adicional
    info_adicional = []

    inf1 = Detalle_Adicional('Direccion', 'Pasaje')
    inf2 = Detalle_Adicional('Email', 'danilo_das16@hotmail.com')

    info_adicional.append(inf1)
    info_adicional.append(inf2)

    return info_adicional

def Detalle_Adicional_Prod1():
    # Apartado detalles adicionales (OPCIONAL)
    # Simulación de los detalles adicionales (En caso de tenerlos)
    detalles_adicionales_prod1 = []

    det_prod1_1 = Detalle_Adicional('Marca Chevrolet', 'Chevrolet')
    det_prod1_2 = Detalle_Adicional('Modelo', '2012')

    detalles_adicionales_prod1.append(det_prod1_1)
    detalles_adicionales_prod1.append(det_prod1_2)

    return  detalles_adicionales_prod1

def Impuestos_Prod1():
    # ETIQUETA XML: <impuestos>
    # Apartado impuestos (Por cada detalle la factura)

    # Simulación de los impuestos en el detalle
    impuestos = []

    # 'codigo': Nombre del impuesto: iva (IVA 0% e IVA 12%) | ice (ICE %) | irbpnr
    # 'codigo_porcentaje': Porcentaje de IVA únicamente (0, 12, 14...) ** la tarifa ICE tiene sus propios códigos (VER TABLA 19 SRI) *** la tarifa IRBPNR tiene sus propios códigos

    imp1 = Impuesto()
    imp1.codigo = 'iva'
    imp1.codigo_porcentaje = 0 #Puede ser int o str
    imp1.tarifa = 0
    imp1.base_imponible = 7
    imp1.valor = 0

    impuestos.append(imp1)

    return impuestos

def Impuestos_Prod2():
    # ETIQUETA XML: <impuestos>
    # Apartado impuestos (Por cada detalle la factura)

    # Simulación de los impuestos en el detalle
    impuestos = []

    # 'codigo': Nombre del impuesto: iva (IVA 0% e IVA 12%) | ice (ICE %) | irbpnr
    # 'codigo_porcentaje': Porcentaje de IVA únicamente (0, 12, 14...) ** la tarifa ICE tiene sus propios códigos (VER TABLA 19 SRI) *** la tarifa IRBPNR tiene sus propios códigos

    imp1 = Impuesto()
    imp1.codigo = 'iva'
    imp1.codigo_porcentaje = 'noiva'
    imp1.tarifa = 0
    imp1.base_imponible = 15
    imp1.valor = 0

    imp2 = Impuesto()
    imp2.codigo = 'ice'
    imp2.codigo_porcentaje = '3011'
    imp2.tarifa = 0
    imp2.base_imponible = 12
    imp2.valor = 3

    imp3 = Impuesto()
    imp3.codigo = 'irbpnr'
    imp3.codigo_porcentaje = '5001'
    imp3.tarifa = 0
    imp3.base_imponible = 0
    imp3.valor = 3

    impuestos.append(imp1)
    impuestos.append(imp2)
    impuestos.append(imp3)

    return impuestos

def Formato_Detalle_Factura():
    productos = []

    # Simulacion de productos en el detalle
    # ------------ Producto 1 -------------
    prod1 = Detalle_Factura()
    prod1.codigo_principal = '0'
    prod1.descripcion = 'ACTH'
    prod1.cantidad =  1
    prod1.precio_unitario = 7
    prod1.descuento = 0
    prod1.precio_total_sin_impuesto = 7
    prod1.impuestos = Impuestos_Prod1()


    productos.append(prod1)

    return productos

def Formato_Pagos():
    pagos = []

    # Simulacion de formas de pago

    # ------ forma_pago ------
    # 'efectivo': SIN UTILIZACION DEL SISTEMA FINANCIERO
    # 'deudas': COMPENSACIÓN DE DEUDAS
    # 'debito': TARJETA DE DÉBITO
    # 'electronico': DINERO ELECTRÓNICO
    # 'prepago': TARJETA PREPAGO
    # 'credito': TARJETA DE CRÉDITO
    # 'otros': OTROS CON UTILIZACION DEL SISTEMA FINANCIERO
    # 'endoso': ENDOSO DE TÍTULOS

    pag1 = Pago()
    pag1.forma_pago = 'efectivo'
    pag1.total = 7

    pagos.append(pag1)

    return pagos

# ------------------------------------------ Crear entidades -------------------------------------------

# ******************************** Empresa ********************************
emp = Empresa()
emp.razon_social = 'Daylisoft Cia Ltda'
emp.ruc = '0791786371001'
emp.dir_matriz = 'Machala'

# ******************************** Cliente ********************************
cli = Cliente()
cli.tipo_identificacion_comprador = 'ruc' # ruc | cedula | pasaporte | consumidor_final | identificacion_exterior | placa
cli.razon_social_comprador = 'El Papu'
cli.identificacion_comprador = '0705325678001'
cli.direccion_comprador = 'Pasaje' # Opcional

# ******************************** Factura ********************************

# Recibe los parametros:
# El ambiente (por defecto 'pruebas')
# El tipo de documento (por defecto 'factura')
# Un codigo numérico de 8 dígitos (por defecto '12345678') <- Servirá para crear la clave de acceso

fac = Factura('pruebas', 'factura', '66140806')  # pruebas | produccion , factura | credito | debito  | guia | retencion, (cualquier valor numérico de 8 dígitos)
fac.tipo_emision = 'normal' # normal | indisp (Indisponibilidad del sistema)
fac.estab = '001'
fac.pto_emi = '001'
fac.secuencial = '000000090'
fac.fecha_emision = '12/01/2018' #Puede ser str o datetime
fac.total_sin_impuestos = 7
fac.total_descuento = 0
fac.total_con_impuestos = Formato_Total_Con_Impuestos()
fac.propina = 0
fac.importe_total = 7
fac.pagos = Formato_Pagos()
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
    else:
        print estado[1]
except Exception as exc:
    print 'Ha ocurrido un error'
    print exc
