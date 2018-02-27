# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from ..connector import connector as conn
import req_body, ucfe_requirement
import math
from datetime import datetime
from random import choice
from xml.etree.ElementTree import Element, SubElement, tostring

# Cuidado de respetar el orden !!!!!!!!!
# En caso de cambiar el orden podria generar
# problemas al validar comprobantes en Uruware
# Ejemplo: Si previo a informar detalles enviamos
# las referencias no da un error diciendo que
# no se encuentra el elemento detalles.

TAXES = {
    'basic': '22',
    'minimum': '10'
}

INVOICE_INDICATOR = {
    'exempt': 1,
    'taxable_minimum': 2,
    'taxable_basic': 3,
    'taxable': 4,
    'free_delivery': 5,
    'no_invoiceable': 6,
    'negative_no_invoiceable': 7,
    'refund': 9,
    'exportation': 10,
    'tax': 11,
    'suspend': 12,
    'no_taxable': 15,
}

MESSAGES_TYPES = {
    'request': '310',
    'lot_request': '340',
    'response': '311',
    'lot_response': '341',
    'state_request': '360',
    'state_response': '361',
}

LOCAL_COUNTRY_CODE = 'UY'


class Manager(object):
    __slots__ = ['emisor', 'comprobante', 'connection_data']

    def __init__(self, emisor, comprobante, connection_data):
        self.emisor = emisor
        self.comprobante = comprobante
        self.connection_data = connection_data

    def create_req_body(self):
        ReqBody = req_body.ReqBody()
        ReqBody.commerce_code = self.connection_data.commerce_code
        ReqBody.terminal_code = self.connection_data.terminal_code
        ReqBody.timeout = self.connection_data.timeout
        ReqBody.request_date = datetime.now().isoformat('T')
        return ReqBody

    def create_ucfe_req(self, message_type, xml=None):
        UcfeReq = ucfe_requirement.UcfeRequirement()
        UcfeReq.message_type = message_type
        UcfeReq.commerce_code = self.connection_data.commerce_code
        UcfeReq.serial = self.comprobante.cfe_serial
        UcfeReq.cfe_number = self.comprobante.cfe_number
        UcfeReq.cfe_type = self.comprobante.cfe_code
        UcfeReq.terminal_code = self.connection_data.terminal_code
        UcfeReq.adenda = self.comprobante.description
        UcfeReq.email_envio_pdf_receptor = self.comprobante.partner.email
        UcfeReq.request_date = datetime.now().strftime('%Y%m%d')
        UcfeReq.request_time = datetime.now().strftime('%H%M%S')
        UcfeReq.id_req = 1
        UcfeReq.uuid = self._get_uuid_cfe()
        UcfeReq.cfe_xml_or_text = xml
        return UcfeReq

    def __send(self, ReqBody, UcfeReq):
        """
        Envia a webservice los datos que se encuentren en reqBody y ucfeReq,
        utilizando un conector.
        :return: dict. con mensaje de respuesta,  cuerpo de respuesta y request
        """
        conn_obj = conn.Connector()
        conn_obj.send(ReqBody, UcfeReq, self.connection_data)
        return {
            'responseMsg': conn_obj.response_msg,
            'responseBody': conn_obj.response_body,
            'request': conn_obj.request
        }

    def get_cfe_state(self):
        """
        Obtiene el estado del comprobante a partir del codigo de consulta del UcfeReq y un comprobante
        :return: dict. con mensaje de respuesta,  cuerpo de respuesta y request
        """

        ReqBody = self.create_req_body()
        UcfeReq = self.create_ucfe_req(message_type=MESSAGES_TYPES.get('state_request'))

        return self.__send(ReqBody, UcfeReq)

    def get_document_report(self):

        conn_obj = conn.Connector()

        return conn_obj.get_document_report(
            self.connection_data,
            self.emisor.vat.number,
            self.comprobante.cfe_code,
            self.comprobante.cfe_serial,
            self.comprobante.cfe_number
        )

    def send_document(self):
        """
        Envia los datos del comprobante a webservice para su validacion
        :return: dict. con mensaje de respuesta, cuerpo de respuesta y request
        """

        # Creamos ReqBody
        ReqBody = self.create_req_body()

        # Creamos xml con datos de comprobante y lo asignamos al ucfeReq
        xml = self.fill_xml()
        UcfeReq = self.create_ucfe_req(message_type=MESSAGES_TYPES.get('request'), xml=xml)

        # Enviar
        return self.__send(ReqBody, UcfeReq)

    def fill_xml(self):
        """
        Completa un elemento xml plano con los datos del comprobante.
        :return: objeto xml
        """
        type = self.comprobante.cfe_type
        root = Element(type)
        Encabezado = SubElement(root, "Encabezado")
        self.build_IdDoc(Encabezado)
        self.build_Emisor(Encabezado)
        self.build_Receptor(Encabezado, type)
        self.build_Totales(Encabezado, type)
        self.build_Detalles(root, type)
        self.build_Referencias(root)
        self.build_Compl_Fiscal_Data(root)
        xml_msg = '<CFE version="1.0" xmlns="http://cfe.dgi.gub.uy">' + tostring(root) + '</CFE>'
        return xml_msg

    def build_IdDoc(self, Encabezado):

        IdDoc = SubElement(Encabezado, "IdDoc")
        SubElement(IdDoc, "TipoCFE").text = str(self.comprobante.cfe_code)

        if self.comprobante.document_type == 'cfc':
            SubElement(IdDoc, "Serie").text = str(self.comprobante.cfe_serial)
            SubElement(IdDoc, "Nro").text = str(self.comprobante.cfe_number)

        SubElement(IdDoc, "FchEmis").text = str(self.comprobante.date)
        if self.comprobante.include_tax: SubElement(IdDoc, "MntBruto").text = '1'
        if self.comprobante.payment_method: SubElement(IdDoc, "FmaPago").text = str(self.comprobante.payment_method)
        if self.comprobante.date_due: SubElement(IdDoc, "FchVenc").text = str(self.comprobante.date_due)

        if self.comprobante.incoterm_code: SubElement(IdDoc, "ClauVenta").text = str(self.comprobante.incoterm_code)
        if self.comprobante.transport_type: SubElement(IdDoc, "TipoTraslado").text = str(self.comprobante.transport_type)
        if self.comprobante.sale_mode_code: SubElement(IdDoc, "ModVenta").text = str(self.comprobante.sale_mode_code if self.comprobante.sale_mode_code else 'N/A')
        if self.comprobante.transport_route_code: SubElement(IdDoc, "ViaTransp").text = str(self.comprobante.transport_route_code)

        return IdDoc

    def build_Emisor(self, Encabezado):
        """
        Construye el elemento emisor del objeto xml, que contiene datos del emisor del comprobante.
        :param Encabezado: elemento encabezado xml
        :param emisor: objeto emisor
        """
        # ELEMENTOS DEL EMISOR (COMPANIA)
        Emisor = SubElement(Encabezado, "Emisor")
        SubElement(Emisor, "RUCEmisor").text = str(self.emisor.vat.number or '')
        SubElement(Emisor, "RznSoc").text = str(self.emisor.name)
        SubElement(Emisor, "CdgDGISucur").text = str(self.connection_data.sucursal_code or '')
        SubElement(Emisor, "DomFiscal").text = str(self.emisor.street or '').encode('ascii')
        SubElement(Emisor, "Ciudad").text = str(self.emisor.city or '')
        SubElement(Emisor, "Departamento").text = str(self.emisor.state or '')

    def build_Receptor(self, Encabezado, type):

        Receptor = SubElement(Encabezado, "Receptor")

        RECEPTOR_BUILDER = {
            'eFact_Exp': self.build_exportation_receptor,
            'eFact': self.build_local_receptor,
            'eTck': self.build_local_receptor,
            'eBoleta': self.build_local_receptor,
            'eResg': self.build_local_receptor,
            'eRem': self.build_local_receptor,
            'eRem_Exp': self.build_exportation_receptor,
        }

        RECEPTOR_BUILDER.get(type)(Receptor)

    def get_doc_recep_type(self, country_code):
        return "DocRecep" if country_code == LOCAL_COUNTRY_CODE else "DocRecepExt"

    def build_exportation_receptor(self, Receptor):

        SubElement(Receptor, "TipoDocRecep").text = str(self.comprobante.partner.vat.code or '')
        SubElement(Receptor, "CodPaisRecep").text = str(self.comprobante.partner.country_code or '')
        SubElement(Receptor, self.get_doc_recep_type(self.comprobante.partner.country_code)).text = str(self.comprobante.partner.vat.number or '')
        SubElement(Receptor, "RznSocRecep").text = str(self.comprobante.partner.name)
        SubElement(Receptor, "DirRecep").text = str(self.comprobante.partner.street or '')
        SubElement(Receptor, "CiudadRecep").text = str(self.comprobante.partner.city or '')
        SubElement(Receptor, "DeptoRecep").text = str(self.comprobante.partner.state or '')
        SubElement(Receptor, "PaisRecep").text = str(self.comprobante.partner.country or '')
        if self.comprobante.partner.zip: SubElement(Receptor, "CP").text = str(self.comprobante.partner.zip or '')

    def build_local_receptor(self, Receptor):

        SubElement(Receptor, "TipoDocRecep").text = str(self.comprobante.partner.vat.code or '')
        SubElement(Receptor, "CodPaisRecep").text = str(self.comprobante.partner.country_code or '')
        SubElement(Receptor, self.get_doc_recep_type(self.comprobante.partner.country_code)).text = str(self.comprobante.partner.vat.number or '')
        SubElement(Receptor, "RznSocRecep").text = str(self.comprobante.partner.name)
        SubElement(Receptor, "DirRecep").text = str(self.comprobante.partner.street or '')
        SubElement(Receptor, "CiudadRecep").text = str(self.comprobante.partner.city or '')
        SubElement(Receptor, "DeptoRecep").text = str(self.comprobante.partner.state or '')

    def build_Totales(self, Encabezado, type):
        """
        Completa los totales para el comprobante, segun el tipo
        :param Encabezado: elemento Encabezado del xml
        :param type: string tipo
        """
        Totales = SubElement(Encabezado, "Totales")

        TOTALES_BUILDER = {
            'eFact_Exp': self.totales_eFact_Exp,
            'eFact': self.totales_eFact,
            'eTck': self.totales_eFact,
            'eBoleta': self.totales_eFact,
            'eResg': self.totales_eResg,
            'eRem': self.totales_eRem,
            'eRem_Exp': self.totales_eFact_Exp,
        }

        TOTALES_BUILDER.get(type)(Totales)

    def totales_eFact_Exp(self, Totales):
        SubElement(Totales, "TpoMoneda").text = str(self.comprobante.currency) or ''
        if self.comprobante.currency_rate:  SubElement(Totales, "TpoCambio").text = self._format_tipo_cambio(self.comprobante.currency_rate)
        SubElement(Totales, "MntExpoyAsim").text = self._format_amount(self.get_mnt_exportation())
        SubElement(Totales, "MntTotal").text = self._format_amount(self.get_total_amount())
        SubElement(Totales, "CantLinDet").text = str(len(self.comprobante.invoice_lines))
        SubElement(Totales, "MntPagar").text = self._format_amount(self.get_total_to_pay())

    def totales_eFact(self, Totales):
        SubElement(Totales, "TpoMoneda").text = str(self.comprobante.currency) or ''
        if self.comprobante.currency_rate: SubElement(Totales, "TpoCambio").text = self._format_tipo_cambio(self.comprobante.currency_rate)
        if self.get_mnt_non_taxable() or self.get_mnt_exempt(): SubElement(Totales, "MntNoGrv").text = self._format_amount(self.get_mnt_non_taxable() + self.get_mnt_exempt())
        if self.get_mnt_base_iva_tasa_min(): SubElement(Totales, "MntNetoIvaTasaMin").text = self._format_amount(self.get_mnt_base_iva_tasa_min())
        if self.get_mnt_base_iva_tasa_basic(): SubElement(Totales, "MntNetoIVATasaBasica").text = self._format_amount(self.get_mnt_base_iva_tasa_basic())
        if self.get_mnt_base_iva_tasa_min(): SubElement(Totales, "IVATasaMin").text = TAXES.get('minimum')
        if self.get_mnt_base_iva_tasa_basic(): SubElement(Totales, "IVATasaBasica").text = TAXES.get('basic')
        if self.get_mnt_iva_tasa_min(): SubElement(Totales, "MntIVATasaMin").text = self._format_amount(self.get_mnt_iva_tasa_min())
        if self.get_mnt_iva_tasa_basic(): SubElement(Totales, "MntIVATasaBasica").text = self._format_amount(self.get_mnt_iva_tasa_basic())
        SubElement(Totales, "MntTotal").text = self._format_amount(self.get_total_amount())
        SubElement(Totales, "CantLinDet").text = str(len(self.comprobante.invoice_lines))
        if self.get_mnt_non_invoiceable(): SubElement(Totales, "MontoNF").text = self._format_amount(self.get_mnt_non_invoiceable())
        SubElement(Totales, "MntPagar").text = self._format_amount(self.get_total_to_pay())

    def totales_eResg(self, Totales):

        factor = -1 if hasattr(self.comprobante, 'refund_info') else 1

        SubElement(Totales, "TpoMoneda").text = self.comprobante.currency or ''
        if self.comprobante.currency_rate: SubElement(Totales, "TpoCambio").text = self._format_tipo_cambio(self.comprobante.currency_rate)
        SubElement(Totales, "MntTotRetenido").text = self._format_amount(self.get_total_retention() * factor)
        SubElement(Totales, "CantLinDet").text = '1'
        retentions = {}
        ret_nro = 0
        for ret in self.comprobante.retentions:
            ret_nro += 1
            retentions[ret_nro] = SubElement(Totales, "RetencPercep")
            SubElement(retentions[ret_nro], "CodRet").text = str(ret.retention_code)
            SubElement(retentions[ret_nro], "ValRetPerc").text = self._format_amount(ret.get_amount() * factor)

    def totales_eRem(self, Totales):
        SubElement(Totales, "CantLinDet").text = str(len(self.comprobante.invoice_lines))

    def build_Compl_Fiscal_Data(self, root):
        if hasattr(self.comprobante, 'fiscal_data'):
            Compl_Fiscal = SubElement(root, "Compl_Fiscal")
            Compl_Fiscal_Data = SubElement(Compl_Fiscal, "Compl_Fiscal_Data")
            SubElement(Compl_Fiscal_Data, "RUCEmisor").text = str(self.emisor.vat.number or '')
            SubElement(Compl_Fiscal_Data, "TipoDocMdte").text = str(self.comprobante.fiscal_data.vat.code or '')
            SubElement(Compl_Fiscal_Data, "Pais").text = str(self.comprobante.fiscal_data.country_code or '')
            SubElement(Compl_Fiscal_Data, "DocMdte").text = str(self.comprobante.fiscal_data.vat.number or '')
            SubElement(Compl_Fiscal_Data, "NombreMdte").text = str(self.comprobante.fiscal_data.name or '')

    def build_Referencias(self, root):

        refund_info = self.comprobante.refund_info if hasattr(self.comprobante, 'refund_info') else None
        references = self.comprobante.references if hasattr(self.comprobante, 'references') else None
        reference_details = refund_info or references

        if reference_details:

            if reference_details.refund_invoices:

                # ELEMENTOS DE REFERENCIA NOTA DE CREDITO / DEBITO
                Referencia = SubElement(root, "Referencia")
                NroLinRef = 0

                for refund in reference_details.refund_invoices:
                    ReferenciaChild = SubElement(Referencia, "Referencia")

                    NroLinRef += 1

                    SubElement(ReferenciaChild, "NroLinRef").text = str(NroLinRef)
                    SubElement(ReferenciaChild, "IndGlobal").text = '1'
                    SubElement(ReferenciaChild, "TpoDocRef").text = refund.cfe_code
                    SubElement(ReferenciaChild, "Serie").text = refund.cfe_serial
                    SubElement(ReferenciaChild, "NroCFERef").text = refund.cfe_number
                    SubElement(ReferenciaChild, "RazonRef").text = reference_details.refund_reason or 'N/A'
                    SubElement(ReferenciaChild, "FechaCFEref").text = refund.date

            else:

                Referencia = SubElement(root, "Referencia")
                ReferenciaChild = SubElement(Referencia, "Referencia")

                SubElement(ReferenciaChild, "NroLinRef").text = '1'
                SubElement(ReferenciaChild, "IndGlobal").text = '1'
                SubElement(ReferenciaChild, "RazonRef").text = reference_details.refund_reason or 'N/A'

    def build_Detalles(self, root, type):

        Detalle = SubElement(root, "Detalle")

        DETALLES_BUILDER = {
            'eFact_Exp': self.detalle_eFact,
            'eFact': self.detalle_eFact,
            'eTck': self.detalle_eFact,
            'eBoleta': self.detalle_eFact,
            'eResg': self.detalle_eResg,
            'eRem': self.detalle_eRem,
            'eRem_Exp': self.detalle_eFact,
        }

        DETALLES_BUILDER.get(type)(Detalle)

    def detalle_eRem(self, Detalle):
        item_nro = 0
        Item = {}
        for line in self.comprobante.invoice_lines:
            item_nro += 1
            Item[item_nro] = SubElement(Detalle, "Item")
            SubElement(Item[item_nro], "NroLinDet").text = str(item_nro)
            if line.invoice_indicator: SubElement(Item[item_nro], "IndFact").text = str(line.invoice_indicator)
            SubElement(Item[item_nro], "NomItem").text = str(line.description)
            SubElement(Item[item_nro], "Cantidad").text = str(line.quantity)
            SubElement(Item[item_nro], "UniMed").text = str(line.uom_code) if line.uom_code else 'N/A'

    def detalle_eFact(self, Detalle):
        item_nro = 0
        Item = {}
        for line in self.comprobante.invoice_lines:
            item_nro += 1
            Item[item_nro] = SubElement(Detalle, "Item")
            SubElement(Item[item_nro], "NroLinDet").text = str(item_nro)
            if line.invoice_indicator: SubElement(Item[item_nro], "IndFact").text = str(line.invoice_indicator)
            SubElement(Item[item_nro], "NomItem").text = str(line.description)
            SubElement(Item[item_nro], "Cantidad").text = str(line.quantity)
            SubElement(Item[item_nro], "UniMed").text = str(line.uom_code) if line.uom_code else 'N/A'
            SubElement(Item[item_nro], "PrecioUnitario").text = self._format_amount(line.unit_price)
            if hasattr(line, 'discount') and hasattr(line, 'discount_amount'):
                SubElement(Item[item_nro], "DescuentoPct").text = self._format_amount(line.discount)
                SubElement(Item[item_nro], "DescuentoMonto").text = self._format_amount(line.discount_amount)
            SubElement(Item[item_nro], "MontoItem").text = self._format_amount(line.amount)

    def detalle_eResg(self, Detalle):

        Item = {0: SubElement(Detalle, "Item")}

        if self.comprobante.retentions:
            SubElement(Item[0], "NroLinDet").text = '1'

        if hasattr(self.comprobante, 'refund_info'):
            SubElement(Item[0], "IndFact").text = str(INVOICE_INDICATOR.get('refund'))

        for retention in self.comprobante.retentions:
            for detail in retention.retention_detail:
                RetencPercep = SubElement(Item[0], "RetencPercep")
                SubElement(RetencPercep, "CodRet").text = str(retention.retention_code)
                
                # Se decidio no enviar la tasa dado que puede haber diferencias y el % es legal
                # en el caso de identificar que comience a ser necesario simplemente se debera
                # descomentar la siguiente linea.
                # SubElement(RetencPercep, "Tasa").text = str(detail.get_tax())

                SubElement(RetencPercep, "MntSujetoaRet").text = self._format_amount(detail.taxable_base)
                SubElement(RetencPercep, "ValRetPerc").text =self._format_amount(math.fabs(detail.amount))

    @staticmethod
    def _format_tipo_cambio(rate):
        return '{:.3f}'.format(rate)

    @staticmethod
    def _format_amount(rate):
        return '{:.2f}'.format(rate)

    def _get_uuid_cfe(self):
        longitud = 12
        valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
        p = ""
        p = p.join([choice(valores) for i in range(longitud)])
        return p

    def get_mnt(self, indicator):
        total = sum([line.amount for line in self.comprobante.invoice_lines if
                     str(line.invoice_indicator) == str(indicator)])
        return total

    def get_tax(self, indicator):
        total = sum([line.tax for line in self.comprobante.invoice_lines if
                     str(line.invoice_indicator) == str(indicator)])
        return total

    def get_mnt_base(self, indicator):
        if self.comprobante.include_tax:
            total = sum([line.amount - line.tax for line in self.comprobante.invoice_lines if str(line.invoice_indicator) == str(indicator)])
        else:
            total = sum([line.amount for line in self.comprobante.invoice_lines if str(line.invoice_indicator) == str(indicator)])
        return total

    def get_mnt_non_invoiceable(self):
        return self.get_mnt(INVOICE_INDICATOR.get('no_invoiceable'))

    def get_mnt_non_taxable(self):
        return self.get_mnt(INVOICE_INDICATOR.get('no_taxable'))

    def get_mnt_exempt(self):
        return self.get_mnt(INVOICE_INDICATOR.get('exempt'))

    def get_mnt_exportation(self):
        return self.get_mnt(INVOICE_INDICATOR.get('exportation'))

    def get_mnt_base_iva_tasa_min(self):
        return self.get_mnt_base(INVOICE_INDICATOR.get('taxable_minimum'))

    def get_mnt_iva_tasa_min(self):
        return self.get_tax(INVOICE_INDICATOR.get('taxable_minimum'))

    def get_mnt_base_iva_tasa_basic(self):
        return self.get_mnt_base(INVOICE_INDICATOR.get('taxable_basic'))

    def get_mnt_iva_tasa_basic(self):
        return self.get_tax(INVOICE_INDICATOR.get('taxable_basic'))

    def get_total_amount(self):
        total_basic = self.get_mnt_iva_tasa_basic() + self.get_mnt_base_iva_tasa_basic()
        total_min = self.get_mnt_iva_tasa_min() + self.get_mnt_base_iva_tasa_min()
        total_no_taxable = self.get_mnt_non_taxable()
        total_exempt = self.get_mnt_exempt()
        total_exportation = self.get_mnt_exportation()
        return total_basic + total_min + total_no_taxable + total_exempt + total_exportation

    def get_total_to_pay(self):
        return self.get_total_amount() + self.get_mnt_non_invoiceable()

    def get_total_retention(self):

        return sum([ret.get_amount() for ret in self.comprobante.retentions])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
