# -*- coding: utf-8 -*-

import utils
import xml.etree.cElementTree as ETXML
import sys

def Validar_Numeros_Impuesto(lista, validar_codigos=False):
    nuevo_detalle = []
    for d in lista:
        if validar_codigos:
            if (d.codigo in utils.CODIGOS_IMPUESTO) == False:
                return {'result': "El campo código en impuestos debe tener los valores: 'iva', 'ice' o 'irbpnr'. Se ha encontrado '" + str(d.codigo) + "'"}

            if d.codigo == 'iva' and (str(d.codigo_porcentaje) in utils.TARIFA_IMPUESTOS) == False:
                return {'result': "El campo código porcentaje en impuestos debe tener los valores: '0', '12', '14', 'noiva' o 'excento'. Se ha encontrado '" + str(d.codigo_porcentaje) + "'"}

            d.codigo_porcentaje = str(d.codigo_porcentaje)

        det = utils.Numerico(d)

        if det[0]:
            nuevo_detalle.append(det[1])
        else:
            return {'result': det[1]}

    return {'valores': nuevo_detalle, 'result': "OK"}

def Validar_Empresa(empresa):
    razon_social = utils.Longitud("razón social", empresa.razon_social, 300)
    if not razon_social[0]:
        return {'result': razon_social[1]}

    nombre_comercial = utils.Longitud("nombre comercial", empresa.nombre_comercial, 300, obligatorio=False, cortar=True)
    if nombre_comercial[0]:
        empresa.nombre_comercial = nombre_comercial[1]
    else:
        return {'result': nombre_comercial[1]}

    ruc = utils.Longitud_Identificacion(empresa.ruc, "ruc")
    if not ruc[0]:
        return {'result': ruc[1]}

    dir_matriz = utils.Longitud("dirección de matriz", empresa.dir_matriz, 300)
    if not dir_matriz[0]:
        return {'result': dir_matriz[1]}

    dir_establec = utils.Longitud("dirección de establecimiento", empresa.dir_establecimiento, 300, obligatorio=False,
                                  cortar=True)
    if dir_establec[0]:
        empresa.dir_establecimiento = dir_establec[1]
    else:
        return {'result': dir_establec[1]}

    contribuyente = utils.Longitud("contribuyente especial", empresa.contribuyente_especial, 13, obligatorio=False)
    if not contribuyente[0]:
        return {'result': contribuyente[1]}

    if empresa.obligado_contabilidad:
        if empresa.obligado_contabilidad.upper() in ("SI", "NO"):
            empresa.obligado_contabilidad = empresa.obligado_contabilidad.upper()
        else:
            return {'result': "El campo obligado a llevar contabilidad, debe tener los valores SI o NO"}

    return {'empresa': empresa, 'result': "OK"}

def Validar_Cliente(cliente):
    tipo = utils.Longitud_Identificacion(cliente.identificacion_comprador, cliente.tipo_identificacion_comprador)
    if not tipo[0]:
        return {'result': tipo[1]}

    razon = utils.Longitud("razón social", cliente.razon_social_comprador, maximo=300)
    if not razon[0]:
        return {'result': razon[1]}

    direccion = utils.Longitud("dirección", cliente.direccion_comprador, maximo=300, obligatorio=False, cortar=True)
    if not direccion[0]:
        return {'result': direccion[1]}
    else:
        cliente.direccion_comprador = direccion[1]

    return {'cliente': cliente, 'result': "OK"}

def Validar_Factura(factura):
    if (factura.ambiente in utils.TIPO_AMBIENTE) == False:
        return {'result': "El campo ambiente debe tener los valores: 'pruebas' o 'produccion'. Se ha encontrado '" + str(factura.ambiente) + "'"}

    if (factura.cod_doc in utils.TIPO_COMPROBANTE) == False:
        return {'result': "El campo tipo de comprobante debe tener los valores: 'factura', 'credito', 'debito', 'guia' o 'retencion'. Se ha encontrado '" + str(factura.cod_doc) + "'"}

    if (factura.tipo_emision in utils.TIPO_EMISION) == False:
        return {'result': "El campo tipo de emisión debe tener los valores: 'normal' o 'indisp'. Se ha encontrado '" + str(factura.tipo_emision) + "'"}

    if factura.estab.isdigit():
        estab = utils.Longitud("establecimiento", factura.estab, maximo=3, minimo=3)
        if not estab[0]:
            return {'result': estab[1]}
    else:
        return {'result': "El campo establecimiento debe tener valores numéricos. Se ha encontrado " + str(factura.estab)}

    if factura.pto_emi.isdigit():
        pto = utils.Longitud("punto de emisión", factura.pto_emi, maximo=3, minimo=3)
        if not pto[0]:
            return {'result': pto[1]}
    else:
        return {'result': "El campo punto de emisión debe tener valores numéricos. Se ha encontrado " + str(factura.pto_emi)}

    if factura.secuencial.isdigit():
        sec = utils.Longitud("secuencial", factura.secuencial, maximo=9, minimo=9)
        if not sec[0]:
            return {'result': sec[1]}
    else:
        return {'result': "El campo secuencial debe tener valores numéricos. Se ha encontrado " + str(factura.secuencial)}

    fecha = utils.Formato_Fecha(factura.fecha_emision)
    if fecha[0]:
        factura.fecha_emision = fecha[1]
    else:
        return {'result': fecha[1]}

    guia = utils.Longitud("guía de remisión", factura.guia_remision, maximo=15, minimo=15, obligatorio=False)
    if not guia[0]:
        return {'result': guia[1]}

    #Formato x.xx en valores numéricos de la factura
    val_factura = utils.Numerico(factura)
    if val_factura[0]:
        factura = val_factura[1]
    else:
        return {'result': val_factura[1]}

    #Formas de pago
    if not factura.pagos:
        return {'result': "La lista de pagos de la factura no debe estar vacía"}
    else:
        for pag in factura.pagos:
            if (pag.forma_pago in utils.FORMAS_PAGO) == False:
                return {'result': "El campo forma de pago debe tener los valores: 'efectivo', 'deudas', 'debito', 'electronico', 'prepago', 'credito', 'otros' o 'endoso'. Se ha encontrado '" + str(pag.forma_pago) + "'"}

            if type(pag.total) is not int and type(pag.total) is not float:
                return {'result': "El campo total de forma de pago debe ser un valor numérico. " + str(pag.total) + " es de tipo " + str(type(pag.total).__name__)}

            if pag.plazo != -1:
                if type(pag.plazo) is not int and type(pag.plazo) is not float:
                    return {'result': "El campo plazo en forma de pago debe ser un valor numérico. " + str(pag.plazo) + " es de tipo " + str(type(pag.plazo).__name__)}

            unidad_tiempo = utils.Longitud("unidad de tiempo", pag.unidad_tiempo, maximo=10, obligatorio=False)
            if not unidad_tiempo[0]:
                return {'result': unidad_tiempo[1]}

    # Formato x.xx en totalImpuesto
    if not factura.total_con_impuestos:
        return {'result': "La lista de impuestos de la factura no debe estar vacía"}
    else:
        val_impuesto = Validar_Numeros_Impuesto(factura.total_con_impuestos, True)
        if val_impuesto['result'] != "OK":
            return {'result': val_impuesto['result']}
        else:
            factura.total_con_impuestos = val_impuesto['valores']

    return {'factura': factura, 'result': "OK"}

def Validar_Detalle(detalle_factura):
    val_detalle = Validar_Numeros_Impuesto(detalle_factura)
    if val_detalle['result'] != "OK":
        return {'result': val_detalle['result']}
    else:
        detalle_factura = val_detalle['valores']

    # Formato x.xx en impuestos
    for i in detalle_factura:
        val_impuesto = Validar_Numeros_Impuesto(i.impuestos, True)
        if val_impuesto['result'] != "OK":
            return {'result': val_impuesto['result']}
        else:
            i.impuestos = val_impuesto['valores']


    return {'detalle_factura': detalle_factura, 'result': "OK"}

def Validar_Datos(empresa, cliente, factura, detalle_factura):
    # Empresa
    val_empresa = Validar_Empresa(empresa)
    if val_empresa['result'] != "OK":
        return {'result': val_empresa['result']}
    else:
        empresa = val_empresa['empresa']

    # Cliente
    val_cliente = Validar_Cliente(cliente)
    if val_cliente['result'] != "OK":
        return {'result':val_cliente['result']}
    else:
        cliente = val_cliente['cliente']

    # Factura
    val_factura = Validar_Factura(factura)
    if val_factura['result'] != "OK":
        return {'result': val_factura['result']}
    else:
        factura = val_factura['factura']

        # Generar clave de acceso. Enviar la entidad factura y el ruc de la empresa
        factura.clave_acceso = utils.Generar_Clave_Acceso(factura, empresa.ruc)

        clave = utils.Longitud("clave de accesso", factura.clave_acceso, maximo=49, minimo=49)
        if not clave[0]:
            return {'result': clave[1]}

    # Detalle factura
    val_detalle = Validar_Detalle(detalle_factura)
    if val_detalle['result'] != "OK":
        return {'result': val_detalle['result']}
    else:
        detalle_factura = val_detalle['detalle_factura']

    dic = {
        'empresa': empresa,
        'cliente': cliente,
        'factura': factura,
        'detalle_factura': detalle_factura,
        'result': "OK"
    }
    return dic

def Crear_XML(empresa, cliente, factura, detalle_factura):
    try:
        validaciones = Validar_Datos(empresa, cliente, factura, detalle_factura)

        if(validaciones['result'] == "OK"):
            empresa = validaciones['empresa']

            # <factura id="comprobante" version="1.0.0">
            head = ETXML.Element("factura", id=factura.id, version=factura.version)

            # <infoTributaria>
            infoTributaria = ETXML.SubElement(head, "infoTributaria")
            ETXML.SubElement(infoTributaria, "ambiente").text = utils.TIPO_AMBIENTE[factura.ambiente]
            ETXML.SubElement(infoTributaria, "tipoEmision").text = utils.TIPO_EMISION[factura.tipo_emision]
            ETXML.SubElement(infoTributaria, "razonSocial").text = empresa.razon_social.decode("utf8")

            if empresa.nombre_comercial:
                ETXML.SubElement(infoTributaria, "nombreComercial").text = empresa.nombre_comercial.decode("utf8")

            ETXML.SubElement(infoTributaria, "ruc").text = empresa.ruc
            ETXML.SubElement(infoTributaria, "claveAcceso").text = factura.clave_acceso
            ETXML.SubElement(infoTributaria, "codDoc").text = utils.TIPO_COMPROBANTE[factura.cod_doc]
            ETXML.SubElement(infoTributaria, "estab").text = factura.estab
            ETXML.SubElement(infoTributaria, "ptoEmi").text = factura.pto_emi
            ETXML.SubElement(infoTributaria, "secuencial").text = factura.secuencial
            ETXML.SubElement(infoTributaria, "dirMatriz").text = empresa.dir_matriz.decode("utf8")
            # </infoTributaria>

            # <infoFactura>
            infoFactura = ETXML.SubElement(head, "infoFactura")
            ETXML.SubElement(infoFactura, "fechaEmision").text = factura.fecha_emision

            if empresa.dir_establecimiento:
                ETXML.SubElement(infoFactura, "dirEstablecimiento").text = empresa.dir_establecimiento.decode("utf8")
            if empresa.contribuyente_especial:
                ETXML.SubElement(infoFactura, "contribuyenteEspecial").text = empresa.contribuyente_especial
            if empresa.obligado_contabilidad:
                ETXML.SubElement(infoFactura, "obligadoContabilidad").text = empresa.obligado_contabilidad

            ETXML.SubElement(infoFactura, "tipoIdentificacionComprador").text = utils.TIPO_IDENTIFICACION[cliente.tipo_identificacion_comprador]

            if factura.guia_remision:
                ETXML.SubElement(infoFactura, "guiaRemision").text = factura.guia_remision

            ETXML.SubElement(infoFactura, "razonSocialComprador").text = cliente.razon_social_comprador.decode("utf8")
            ETXML.SubElement(infoFactura, "identificacionComprador").text = cliente.identificacion_comprador.replace("-", "")

            if cliente.direccion_comprador:
                ETXML.SubElement(infoFactura, "direccionComprador").text = cliente.direccion_comprador.decode("utf8")

            ETXML.SubElement(infoFactura, "totalSinImpuestos").text = factura.total_sin_impuestos
            ETXML.SubElement(infoFactura, "totalDescuento").text = factura.total_descuento

            # <totalConImpuestos>
            totalConImpuestos = ETXML.SubElement(infoFactura, "totalConImpuestos")

            # <totalImpuesto>
            for i in factura.total_con_impuestos:
                totalImpuesto = ETXML.SubElement(totalConImpuestos, "totalImpuesto")
                ETXML.SubElement(totalImpuesto, "codigo").text = utils.CODIGOS_IMPUESTO[i.codigo]

                if utils.CODIGOS_IMPUESTO[i.codigo] == '2':
                    ETXML.SubElement(totalImpuesto, "codigoPorcentaje").text = utils.TARIFA_IMPUESTOS[str(i.codigo_porcentaje)]
                else:
                    ETXML.SubElement(totalImpuesto, "codigoPorcentaje").text = i.codigo_porcentaje

                if i.descuento_adicional:
                    ETXML.SubElement(totalImpuesto, "descuentoAdicional").text = i.descuento_adicional

                ETXML.SubElement(totalImpuesto, "baseImponible").text = i.base_imponible
                ETXML.SubElement(totalImpuesto, "valor").text = i.valor
            # </totalImpuesto>
            # </totalConImpuestos>

            ETXML.SubElement(infoFactura, "propina").text = factura.propina
            ETXML.SubElement(infoFactura, "importeTotal").text = factura.importe_total
            ETXML.SubElement(infoFactura, "moneda").text = factura.moneda

            # <pagos>
            pagos = ETXML.SubElement(infoFactura, "pagos")

            # <pago>
            for p in factura.pagos:
                pago = ETXML.SubElement(pagos, "pago")

                ETXML.SubElement(pago, "formaPago").text = utils.FORMAS_PAGO[p.forma_pago]
                ETXML.SubElement(pago, "total").text = "%.2f" % p.total

                if p.plazo != -1:
                    ETXML.SubElement(pago, "plazo").text = str(p.plazo)

                if p.unidad_tiempo:
                    ETXML.SubElement(pago, "unidadTiempo").text = p.unidad_tiempo
            # </pago>
            # </pagos>

            if factura.valor_ret_iva:
                ETXML.SubElement(infoFactura, "valorRetIva").text = factura.valor_ret_iva

            if factura.valor_ret_renta:
                ETXML.SubElement(infoFactura, "valorRetRenta").text = factura.valor_ret_renta
            # </infoFactura>

            # <detalles>
            detalles = ETXML.SubElement(head, "detalles")

            # <detalle>
            for d in detalle_factura:
                detalle = ETXML.SubElement(detalles, "detalle")
                ETXML.SubElement(detalle, "codigoPrincipal").text = str(d.codigo_principal)

                if d.codigo_auxiliar:
                    ETXML.SubElement(detalle, "codigoAuxiliar").text = str(d.codigo_auxiliar)

                ETXML.SubElement(detalle, "descripcion").text = d.descripcion.decode("utf8")
                ETXML.SubElement(detalle, "cantidad").text = d.cantidad
                ETXML.SubElement(detalle, "precioUnitario").text = d.precio_unitario
                ETXML.SubElement(detalle, "descuento").text = d.descuento
                ETXML.SubElement(detalle, "precioTotalSinImpuesto").text = d.precio_total_sin_impuesto

                # <detallesAdicionales>
                if d.detalles_adicionales:
                    detallesAdicionales = ETXML.SubElement(detalle, "detallesAdicionales")
                    for da in d.detalles_adicionales:
                        ETXML.SubElement(detallesAdicionales, "detAdicional", nombre=da.nombre.decode("utf8"), valor=da.valor.decode("utf8"))
                # </detallesAdicionales>

                # <impuestos>
                impuestos = ETXML.SubElement(detalle, "impuestos")

                # <impuesto>
                for im in d.impuestos:
                    impuesto = ETXML.SubElement(impuestos, "impuesto")
                    ETXML.SubElement(impuesto, "codigo").text = utils.CODIGOS_IMPUESTO[im.codigo]

                    if utils.CODIGOS_IMPUESTO[im.codigo] == '2':
                        ETXML.SubElement(impuesto, "codigoPorcentaje").text = utils.TARIFA_IMPUESTOS[str(im.codigo_porcentaje)]
                    else:
                        ETXML.SubElement(impuesto, "codigoPorcentaje").text = im.codigo_porcentaje

                    ETXML.SubElement(impuesto, "tarifa").text = str(im.tarifa)
                    ETXML.SubElement(impuesto, "baseImponible").text = str(im.base_imponible)
                    ETXML.SubElement(impuesto, "valor").text = str(im.valor)
                # </impuesto>
                # </impuestos>
            # </detalle>
            # </detalles>

            # <infoAdicional>
            if factura.info_adicional:
                infoAdicional = ETXML.SubElement(head, "infoAdicional")
                for ia in factura.info_adicional:
                    ETXML.SubElement(infoAdicional, "campoAdicional", nombre=ia.nombre.decode("utf8")).text = ia.valor.decode("utf8")
            # </infoAdicional>
            # </factura>

            estructura = ETXML.ElementTree(head)
            return True, estructura
        else:
            return False, validaciones
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            'line': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': exc_value.message,  # or see traceback._some_str()
        }

        print (traceback_details)
        return False, 'No se ha podido crear el archivo XML. Error: ' + ex.message