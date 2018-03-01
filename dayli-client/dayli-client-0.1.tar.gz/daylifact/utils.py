# -*- coding: utf-8 -*-
import datetime

TIPO_AMBIENTE = {
    'pruebas': '1',
    'produccion': '2',
}

TIPO_EMISION = {
    'normal': '1',
    'indisp': '2',
}

TIPO_COMPROBANTE = {
    'factura': '01',
    'credito': '04',
    'debito': '05',
    'guia': '06',
    'retencion': '07'
}

TIPO_IDENTIFICACION = {
    'ruc': '04',
    'cedula': '05',
    'pasaporte': '06',
    'consumidor_final': '07',
    'identificacion_exterior': '08',
    'placa': '09',
}

FORMAS_PAGO = {
    'efectivo': '01',
    'deudas': '15',
    'debito': '16',
    'electronico': '17',
    'prepago': '18',
    'credito': '19',
    'otros': '20',
    'endoso': '21'
}

# Tabla 17
CODIGOS_IMPUESTO = {
    'iva': '2',
    'ice': '3',
    'irbpnr': '5'
}

# Tabla 18
TARIFA_IMPUESTOS = {
    '0': '0',
    '12': '2',
    '14': '3',
    'noiva': '6',
    'excento': '7'
}

""""
GENERACIÓN DE CLAVE DE ACCESO
- Retorna un String de[49] caracteres
"""""
# Recibe la entidad factura, el ruc de la empresa y el código numérico elegido
def Generar_Clave_Acceso(fac, ruc):
    # Necesita de 9 campos:
    # 1. Fecha de emision (fac.fecha_emision)   2. Codigo de documento (fac.cod_doc)  3. Ruc de la empresa (ruc)
    # 4. Tipo de ambiente (fac.ambiente)    5. Número de establecimiento (fac.estab)    6. Número punto de emisión (fac.pto_emi)
    # 7. Número secuencial (fac.secuencial)   8. Un código de 8 dígitos numérico (codigo_numerico)   9. Tipo de emisión (fac.tipo_emision)

    if type(fac.fecha_emision) is str:
        vector = fac.fecha_emision.split("/")
        fecha_parseada = vector[0] + vector[1] + vector[2]
    else:
        fecha_parseada = fac.fecha_emision.strftime('%d') + fac.fecha_emision.strftime('%m') + fac.fecha_emision.strftime('%Y')

    codigo_tipo_comprobante = TIPO_COMPROBANTE[fac.cod_doc]
    codigo_ambiente = TIPO_AMBIENTE[fac.ambiente]
    codigo_tipo_emision = TIPO_EMISION[fac.tipo_emision]

    cadena = fecha_parseada + codigo_tipo_comprobante + ruc + codigo_ambiente + fac.estab + fac.pto_emi + fac.secuencial + fac.codigo_numerico + codigo_tipo_emision

    coeficientes = (7, 6, 5, 4, 3, 2)
    indice = 0
    resultado = 0

    for i in cadena:
        if indice == 6:
            indice = 0

        posicion = int(i)
        posicion *= coeficientes[indice]
        resultado += posicion
        indice += 1

    digito_verificador = 11 - (resultado % 11)

    if digito_verificador >= 10:
        digito_verificador = 11 - digito_verificador

    return cadena + str(digito_verificador)

""""
VALIDACIONES ANTES DE CREAR EL XML
"""""

# Puede retornar el campo corregido (ajustar al tamaño maximo)
def Longitud(campo_nombre, campo_valor, maximo, minimo=1, obligatorio=True, cortar=False):
    estado = True
    resultado = campo_valor
    l = len(campo_valor) if campo_valor else 0

    if l > 0:
        if l < minimo:
            estado = False
            resultado = "Ingrese mínimo " + str(minimo) + " caracteres en el campo " + campo_nombre +", usted ingresó: " + str(l)

            return estado, resultado
        if l > maximo:
            if cortar:
                resultado = campo_valor[0:maximo]
                return True, resultado

            estado = False
            resultado = "Debe ingresar hasta " + str(maximo) + " caracteres en el campo " + campo_nombre +", usted ingresó: " + str(l)
    else:
        if obligatorio:
            estado = False
            resultado = "El campo " + campo_nombre + " es obligatorio, debe ingresar un valor"

    return estado, resultado

# El formato de la fecha puede ser datetime o str y retorna un str con formato dd/mm/AAAA o dd/mm/AAAA HH:MM
def Formato_Fecha(fecha, hh_mm=False):
    estado = True

    try:
        if type(fecha) is str:
            if hh_mm:
                datetime.datetime.strptime(str(fecha), '%d/%m/%Y %H:%M')
                result = fecha
            else:
                datetime.datetime.strptime(str(fecha), "%d/%m/%Y").date()
                result = fecha
        else:
            if hh_mm:
                result = fecha.strftime('%d') + "/" + fecha.strftime('%m') + "/" + fecha.strftime('%Y') + " " + fecha.strftime('%H') + ":" + fecha.strftime('%M')
                #result = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
            else:
                result = fecha.strftime('%d') + "/" + fecha.strftime('%m') + "/" + fecha.strftime('%Y')
                #result = datetime.datetime.strftime(fecha, '%d/%m/%Y')
    except:
        if hh_mm:
            result = "Ingrese una fecha válida (formato dd/mm/AAAA HH:MM)"
        else:
            result = "Ingrese una fecha válida (formato dd/mm/AAAA)"
        estado = False

    return estado, result

def Longitud_Identificacion(identificacion, tipo):
    if tipo in TIPO_IDENTIFICACION:
        if tipo == 'ruc':
            if identificacion.isdigit():
                result = Longitud(tipo, identificacion, 13, 13, True)
            else:
                result = False, "El número de identificación (" + identificacion + ") no es correcto"
        elif tipo == 'cedula':
            if identificacion.isdigit():
                result = Longitud(tipo, identificacion, 10, 10, True)
            else:
                result = False, "El número de identificación (" + identificacion + ") no es correcto"
        elif tipo == 'pasaporte':
            result = Longitud(tipo, identificacion, 13, 3, True)
        elif tipo == 'consumidor_final':
            result = Longitud(tipo, identificacion, 13, 13, True)
        elif tipo == 'identificacion_exterior':
            result = Longitud(tipo, identificacion, 13, 3, True)
        else:
            result = Longitud(tipo, identificacion, 20, 3, True)
    else:
        result = False, "El código del tipo de identificación (" + tipo + ") no es correcto"

    return result[0], result[1]

# Ajustar al formato x.xx (dos decimales)
def Numerico(entidad):
    try:
        s = "%.2f"

        for a, valor in entidad.__dict__.iteritems():
            if type(valor) is int or type(valor) is float:
                if valor < 0:
                    valor = None
                else:
                    valor = s % valor

                setattr(entidad, a, valor)
    except Exception as exc:
        return False, "Ha ocurrido un error: " + exc.message

    return True, entidad