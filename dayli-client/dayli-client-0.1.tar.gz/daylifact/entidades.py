# -*- coding: utf-8 -*-

class Empresa(object):
    def __init__(self, razon_social = None, ruc = None, dir_matriz = None):
        self.razon_social = razon_social
        self.ruc = ruc
        self.dir_matriz = dir_matriz
        self.nombre_comercial = None
        self.dir_establecimiento = None
        self.contribuyente_especial = None
        self.obligado_contabilidad = None
        self.credencial = None #Para firmar archivo xml
        self.password = None #Para firmar archivo xml

class Cliente(object):
    def __init__(self, tipo_identificacion_comprador = None, razon_social_comprador = None, identificacion_comprador = None):
        self.tipo_identificacion_comprador = tipo_identificacion_comprador
        self.razon_social_comprador = razon_social_comprador
        self.identificacion_comprador = identificacion_comprador
        self.direccion_comprador = None

#Datos numéricos opcionales (ponerlos en -1)
class Factura(object):
    id = "comprobante"
    version = "1.0.0"
    moneda = "DOLAR"

    def __init__(self, ambiente = 'pruebas', cod_doc = 'factura', codigo_numerico = '12345678'):
        self.ambiente = ambiente
        self.cod_doc = cod_doc
        self.tipo_emision = None
        self.clave_acceso = None
        self.estab = None
        self.pto_emi = None
        self.secuencial = None
        self.fecha_emision = None
        self.guia_remision = None
        self.total_sin_impuestos = 0 #Subtotal neto
        self.total_descuento = 0
        self.total_con_impuestos = []
        self.propina = 0
        self.importe_total = 0
        self.pagos = []
        self.valor_ret_iva = -1
        self.valor_ret_renta = -1
        self.info_adicional = []

        # Sirve para construir la clave de acceso una vez validados todos los datos de la factura
        self.codigo_numerico = codigo_numerico # Un código de 8 números cualquiera

#Datos numéricos opcionales (ponerlos en -1)
class Detalle_Factura(object):
    def __init__(self):
        self.codigo_principal = None
        self.codigo_auxiliar = None
        self.descripcion = None
        self.cantidad = 0
        self.precio_unitario = 0
        self.descuento = 0
        self.precio_total_sin_impuesto = 0
        self.detalles_adicionales = []
        self.impuestos = []

#Datos numéricos opcionales (ponerlos en -1)
class Impuesto(object):
    def __init__(self):
        self.codigo = None
        self.codigo_porcentaje = None
        self.tarifa = 0
        self.base_imponible = 0
        self.descuento_adicional = -1
        self.valor = 0

class Pago(object):
    def __init__(self):
        self.forma_pago = None
        self.total = 0
        self.plazo = -1
        self.unidad_tiempo = None

class Detalle_Adicional(object):
    def __init__(self, nombre = None, valor = None):
        self.nombre = nombre
        self.valor = valor