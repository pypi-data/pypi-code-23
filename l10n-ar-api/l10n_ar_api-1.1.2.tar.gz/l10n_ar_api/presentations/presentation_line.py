# -*- coding: utf-8 -*-

class PresentationLine(object):

    __slots__ = []

    @staticmethod
    def factory(presentation, line_name):
        '''
        :param presentation: Tipo de presentacion
        :param line_name: Nombre de la linea a completar para la presentacion
        '''
        
        if presentation == "ventasCompras":
                
            if line_name == "cabecera": return PurchaseSalesPresentationCabeceraLine()
            if line_name == "ventasCbte": return PurchaseSalesPresentationVentasCbteLine()
            if line_name == "ventasAlicuotas": return PurchaseSalesPresentationVentasAlicuotasLine()
            if line_name == "comprasCbte": return PurchaseSalesPresentationComprasCbteLine()
            if line_name == "comprasAlicuotas": return PurchaseSalesPresentationComprasAlicuotasLine()
            if line_name == "comprasImportaciones": return PurchaseSalesPresentationComprasImportacionesLine()
            if line_name == "creditoFiscalImportacionServ": return PurchaseSalesPresentationCreditoFiscalImportacionServLine()

        if presentation == "sifere":

            if line_name == "retenciones": return SifereRetentionLine()
            if line_name == "percepciones": return SiferePerceptionLine()

        assert 0, "No existe la presentacion: "+presentation+", o el tipo: "+line_name
        
    def _fill_and_validate_len(self, attribute, variable, length, numeric=True):
        '''
        :param attribute: Atributo a validar la longitud
        :param length: Longitud que deberia tener
        '''
          
        attribute = self._convert_to_string(attribute, variable)
        attribute = attribute.zfill(length) if numeric else attribute.ljust(length)[:length]
            
        if len(attribute) > length and len(attribute.decode('utf-8')) > length:
            
            raise ValueError(('El valor {variable} contiene mas digitos de '
                'los pre-establecidos').format(variable=variable))
        
        return attribute

    def _convert_to_string(self, attribute, variable):
        '''
        :param attribute: Atributo para pasar a str
        '''

        try:
            attribute = str(attribute)
        except ValueError:
            raise ValueError('Valor {variable} erroneo o incompleto'.format(variable=variable))
             
        return attribute
    
    def get_line_string(self):
        
        try:
            line_string = ''.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")
        
        return line_string
    
    def get_values(self):
        raise NotImplementedError("Funcion get_values no implementada para esta clase")
    
class PurchaseSalesPresentationCabeceraLine(PresentationLine):
    
    __slots__ = ['_cuit', '_periodo', '_secuencia', '_sinMovimiento',
                 '_prorratearCFC', '_cFCGlobal', '_importeCFCG', '_importeCFCAD',
                 '_importeCFCP', '_importeCFnCG', '_cFCSSyOC', '_cFCCSSyOC']
    
    def __init__(self):
        
        self._cuit = None 
        self._periodo = None
        self._secuencia = None
        self._sinMovimiento = None
        self._prorratearCFC = None
        self._cFCGlobal = None
        self._importeCFCG = None
        self._importeCFCAD = None
        self._importeCFCP = None
        self._importeCFnCG = None
        self._cFCSSyOC = None
        self._cFCCSSyOC = None
        
    @property
    def cuit(self):
        return self._cuit
    
    @cuit.setter
    def cuit(self, cuit):
        
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 11)    
        
    @property
    def periodo(self):
        return self._periodo

    @periodo.setter
    def periodo(self, periodo):
        
        self._periodo = self._fill_and_validate_len(periodo, 'periodo', 6)
            
    @property
    def secuencia(self):
        return self._secuencia

    @secuencia.setter
    def secuencia(self, secuencia):
        
        self._secuencia = self._fill_and_validate_len(secuencia, 'secuencia', 2)
  
    @property
    def sinMovimiento(self):
        return self._sinMovimiento

    @sinMovimiento.setter
    def sinMovimiento(self, sinMovimiento):
        
        self._sinMovimiento = self._fill_and_validate_len(sinMovimiento, 'sinMovimiento', 1, numeric=False)  
            
    @property
    def prorratearCFC(self):
        return self._prorratearCFC
    
    @prorratearCFC.setter
    def prorratearCFC(self, prorratearCFC):
        
        self._prorratearCFC = self._fill_and_validate_len(prorratearCFC, 'prorratearCFC', 1, numeric=False)  
            
    @property
    def cFCGlobal(self):
        return self._cFCGlobal

    @cFCGlobal.setter
    def cFCGlobal(self, cFCGlobal):
        
        self._cFCGlobal = self._fill_and_validate_len(cFCGlobal, 'cFCGlobal', 1, numeric=False) 
            
    @property
    def importeCFCG(self):
        return self._importeCFCG
    
    @importeCFCG.setter
    def importeCFCG(self, importeCFCG):
        
        self._importeCFCG = self._fill_and_validate_len(importeCFCG, 'importeCFCG', 15) 

    @property
    def importeCFCAD(self):
        return self._importeCFCAD

    @importeCFCAD.setter
    def importeCFCAD(self, importeCFCAD):
        
        self._importeCFCAD = self._fill_and_validate_len(importeCFCAD, 'importeCFCAD', 15) 
            
    @property
    def importeCFCP(self):
        return self._importeCFCP

    @importeCFCP.setter
    def importeCFCP(self, importeCFCP):
        
        self._importeCFCP = self._fill_and_validate_len(importeCFCP, 'importeCFCP', 15) 
                
    @property
    def importeCFnCG(self):
        return self._importeCFnCG

    @importeCFnCG.setter
    def importeCFnCG(self, importeCFnCG):
        
        self._importeCFnCG = self._fill_and_validate_len(importeCFnCG, 'importeCFnCG', 15) 
            
    @property
    def cFCSSyOC(self):
        return self._cFCSSyOC

    @cFCSSyOC.setter
    def cFCSSyOC(self, cFCSSyOC):
        
        self._cFCSSyOC = self._fill_and_validate_len(cFCSSyOC, 'cFCSSyOC', 15) 
            
    @property
    def cFCCSSyOC(self):
        return self._cFCCSSyOC

    @cFCCSSyOC.setter
    def cFCCSSyOC(self, cFCCSSyOC):
        
        self._cFCCSSyOC = self._fill_and_validate_len(cFCCSSyOC, 'cFCCSSyOC', 15) 
        
    def get_values(self):
        
        values = [self.cuit, self.periodo, self.secuencia, self.sinMovimiento,
                  self.prorratearCFC, self.cFCGlobal, self.importeCFCG, 
                  self.importeCFCAD, self.importeCFCP, self.importeCFnCG,
                  self.cFCSSyOC, self.cFCCSSyOC]
       
        return values

class PurchaseSalesPresentationVentasCbteLine(PresentationLine):
    
    __slots__ = ['_fecha', '_tipo', '_puntoDeVenta', '_numeroComprobante', '_numeroHasta',
                 '_codigoDocumento', '_numeroComprador', '_denominacionComprador',
                 '_importeTotal', '_importeTotalNG', '_percepcionNC', '_importeExentos',
                 '_importePercepciones', '_importePerIIBB', '_importePerIM', 
                 '_importeImpInt', '_codigoMoneda', '_tipoCambio', '_cantidadAlicIva', 
                 '_codigoOperacion', '_otrosTributos', '_fechaVtoPago']
    
    def __init__(self):
        self._fecha = None
        self._tipo = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._numeroHasta = None
        self._codigoDocumento = None
        self._numeroComprador = None
        self._denominacionComprador = None
        self._importeTotal = None
        self._importeTotalNG = None
        self._percepcionNC = None
        self._importeExentos = None
        self._importePercepciones = None
        self._importePerIIBB = None
        self._importePerIM = None
        self._importeImpInt = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cantidadAlicIva = None
        self._codigoOperacion = None
        self._otrosTributos = None
        self._fechaVtoPago = None

    def get_values(self):
        
        values = [self.fecha, self.tipo, self.puntoDeVenta, self.numeroComprobante,
                  self.numeroHasta, self.codigoDocumento, self.numeroComprador, 
                  self.denominacionComprador, self.importeTotal, self.importeTotalNG,
                  self.percepcionNC, self.importeExentos, self.importePercepciones,
                  self.importePerIIBB, self.importePerIM, self.importeImpInt,
                  self.codigoMoneda, self.tipoCambio, self.cantidadAlicIva,
                  self.codigoOperacion, self.otrosTributos, self.fechaVtoPago]
       
        return values
        
    @property
    def fecha(self):
        return self._fecha
    
    @fecha.setter
    def fecha(self, fecha):
        
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 8)
  
    @property
    def tipo(self):
        return self._tipo
    
    @tipo.setter
    def tipo(self, tipo):
        
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 3)  
        
    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta
    
    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)  
        
    @property
    def numeroComprobante(self):
        return self._numeroComprobante
    
    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    
    @property
    def numeroHasta(self):
        return self._numeroHasta
    
    @numeroHasta.setter
    def numeroHasta(self, numeroHasta):
        
        self._numeroHasta = self._fill_and_validate_len(numeroHasta, 'numeroHasta', 20)      
     
    @property
    def codigoDocumento(self):
        return self._codigoDocumento
    
    @codigoDocumento.setter
    def codigoDocumento(self, codigoDocumento):
        
        self._codigoDocumento = self._fill_and_validate_len(codigoDocumento, 'codigoDocumento', 2)  
        
    @property
    def numeroComprador(self):
        return self._numeroComprador
    
    @numeroComprador.setter
    def numeroComprador(self, numeroComprador):
        
        self._numeroComprador = self._fill_and_validate_len(numeroComprador, 'numeroComprador', 20)  
        
    @property
    def denominacionComprador(self):
        return self._denominacionComprador
    
    @denominacionComprador.setter
    def denominacionComprador(self, denominacionComprador):
        
        self._denominacionComprador = self._fill_and_validate_len(denominacionComprador, 'denominacionComprador', 30, numeric=False)  
        
    @property
    def importeTotal(self):
        return self._importeTotal
    
    @importeTotal.setter
    def importeTotal(self, importeTotal):
        
        self._importeTotal = self._fill_and_validate_len(importeTotal, 'importeTotal', 15)  
    
    @property
    def importeTotalNG(self):
        return self._importeTotalNG
    
    @importeTotalNG.setter
    def importeTotalNG(self, importeTotalNG):
        
        self._importeTotalNG = self._fill_and_validate_len(importeTotalNG, 'importeTotalNG', 15)    
                                   
    @property
    def percepcionNC(self):
        return self._percepcionNC
    
    @percepcionNC.setter
    def percepcionNC(self, percepcionNC):
        
        self._percepcionNC = self._fill_and_validate_len(percepcionNC, 'percepcionNC', 15)  
        
    @property
    def importeExentos(self):
        return self._importeExentos
    
    @importeExentos.setter
    def importeExentos(self, importeExentos):
        
        self._importeExentos = self._fill_and_validate_len(importeExentos, 'importeExentos', 15)  
        
    @property
    def importePercepciones(self):
        return self._importePercepciones
    
    @importePercepciones.setter
    def importePercepciones(self, importePercepciones):
        
        self._importePercepciones = self._fill_and_validate_len(importePercepciones, 'importePercepciones', 15)  
        
    @property
    def importePerIIBB(self):
        return self._importePerIIBB
    
    @importePerIIBB.setter
    def importePerIIBB(self, importePerIIBB):
        
        self._importePerIIBB = self._fill_and_validate_len(importePerIIBB, 'importePerIIBB', 15)
  
    @property
    def importePerIM(self):
        return self._importePerIM
    
    @importePerIM.setter
    def importePerIM(self, importePerIM):
        
        self._importePerIM = self._fill_and_validate_len(importePerIM, 'importePerIM', 15)      
     
    @property
    def importeImpInt(self):
        return self._importeImpInt
    
    @importeImpInt.setter
    def importeImpInt(self, importeImpInt):
        
        self._importeImpInt = self._fill_and_validate_len(importeImpInt, 'importeImpInt', 15)  
        
    @property
    def codigoMoneda(self):
        return self._codigoMoneda
    
    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):
        
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3)  
        
    @property
    def tipoCambio(self):
        return self._tipoCambio
    
    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):
        
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)  
        
    @property
    def cantidadAlicIva(self):
        return self._cantidadAlicIva
    
    @cantidadAlicIva.setter
    def cantidadAlicIva(self, cantidadAlicIva):
        
        self._cantidadAlicIva = self._fill_and_validate_len(cantidadAlicIva, 'cantidadAlicIva', 1)  
    
    @property
    def codigoOperacion(self):
        return self._codigoOperacion
    
    @codigoOperacion.setter
    def codigoOperacion(self, codigoOperacion):
        
        self._codigoOperacion = self._fill_and_validate_len(codigoOperacion, 'codigoOperacion', 1, numeric=False)
        
    @property
    def otrosTributos(self):
        return self._otrosTributos
    
    @otrosTributos.setter
    def otrosTributos(self, otrosTributos):
        
        self._otrosTributos = self._fill_and_validate_len(otrosTributos, 'otrosTributos', 15)
    
    @property
    def fechaVtoPago(self):
        return self._fechaVtoPago
    
    @fechaVtoPago.setter
    def fechaVtoPago(self, fechaVtoPago):
        
        self._fechaVtoPago = self._fill_and_validate_len(fechaVtoPago, 'fechaVtoPago', 8)
                
class PurchaseSalesPresentationVentasAlicuotasLine(PresentationLine):
    
    __slots__ = ['_tipoComprobante', '_puntoDeVenta', '_numeroComprobante',
                 '_importeNetoGravado', '_alicuotaIva', '_impuestoLiquidado']
    
    def __init__(self):
        self._tipoComprobante = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        
        values = [self.tipoComprobante, self.puntoDeVenta, self.numeroComprobante,
                  self.importeNetoGravado, self.alicuotaIva, self.impuestoLiquidado]
       
        return values
    
    @property
    def tipoComprobante(self):
        return self._tipoComprobante
    
    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 3)
      
    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta
    
    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)      

    @property
    def numeroComprobante(self):
        return self._numeroComprobante
    
    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado
    
    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):
        
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)      

    @property
    def alicuotaIva(self):
        return self._alicuotaIva
    
    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):
        
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)      
                                    
    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado
    
    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):
        
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)      

class PurchaseSalesPresentationComprasCbteLine(PresentationLine):
    
    __slots__ = [ '_fecha', '_tipo', '_puntoDeVenta', '_numeroComprobante',
                 '_despachoImportacion', '_codigoDocumento', '_numeroVendedor',
                 '_denominacionVendedor', '_importeTotal', '_importeTotalNG',
                 '_importeOpExentas', '_importePerOIva', '_importePerOtrosImp',
                 '_importePerIIBB', '_importePerIM', '_importeImpInt',
                 '_codigoMoneda', '_tipoCambio', '_cantidadAlicIva',
                 '_codigoOperacion', '_credFiscComp', '_otrosTrib',
                 '_cuitEmisor', '_denominacionEmisor', '_ivaComision']
    
    def __init__(self):
        self._fecha = None
        self._tipo = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._despachoImportacion = None
        self._codigoDocumento = None
        self._numeroVendedor = None
        self._denominacionVendedor = None
        self._importeTotal = None
        self._importeTotalNG = None
        self._importeOpExentas = None
        self._importePerOIva = None
        self._importePerOtrosImp = None
        self._importePerIIBB = None
        self._importePerIM = None
        self._importeImpInt = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cantidadAlicIva = None
        self._codigoOperacion = None
        self._credFiscComp = None
        self._otrosTrib = None
        self._cuitEmisor = None
        self._denominacionEmisor = None
        self._ivaComision = None
        

    def get_values(self):
        
        values = [self.fecha, self.tipo, self.puntoDeVenta, self.numeroComprobante,
                  self.despachoImportacion, self.codigoDocumento, self.numeroVendedor, 
                  self.denominacionVendedor, self.importeTotal, self.importeTotalNG,
                  self.importeOpExentas, self.importePerOIva, self.importePerOtrosImp,
                  self.importePerIIBB, self.importePerIM, self.importeImpInt,
                  self.codigoMoneda, self.tipoCambio, self.cantidadAlicIva,
                  self.codigoOperacion, self.credFiscComp, self.otrosTrib,
                  self.cuitEmisor, self.denominacionEmisor, self.ivaComision]
       
        return values
            
    @property
    def fecha(self):
        return self._fecha
        
    @fecha.setter
    def fecha(self, fecha):        
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 8)
  
    @property
    def tipo(self):
        return self._tipo
        
    @tipo.setter
    def tipo(self, tipo):        
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 3)  

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta
        
    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):        
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)
        
    @property
    def numeroComprobante(self):
        return self._numeroComprobante
        
    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):        
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)
        
    @property
    def despachoImportacion(self):
        return self._despachoImportacion
        
    @despachoImportacion.setter
    def despachoImportacion(self, despachoImportacion):               
        self._despachoImportacion = self._fill_and_validate_len(despachoImportacion, 'despachoImportacion', 16, numeric=False)
        
    @property
    def codigoDocumento(self):
        return self._codigoDocumento
        
    @codigoDocumento.setter
    def codigoDocumento(self, codigoDocumento):             
        self._codigoDocumento = self._fill_and_validate_len(codigoDocumento, 'codigoDocumento', 2)  
        
    @property
    def numeroVendedor(self):
        return self._numeroVendedor
        
    @numeroVendedor.setter
    def numeroVendedor(self, numeroVendedor):             
        self._numeroVendedor = self._fill_and_validate_len(numeroVendedor, 'numeroVendedor', 20)     
        
    @property
    def denominacionVendedor(self):
        return self._denominacionVendedor
        
    @denominacionVendedor.setter
    def denominacionVendedor(self, denominacionVendedor):        
        self._denominacionVendedor = self._fill_and_validate_len(denominacionVendedor, 'denominacionVendedor', 30, numeric=False)  
        
    @property
    def importeTotal(self):
        return self._importeTotal
        
    @importeTotal.setter
    def importeTotal(self, importeTotal):        
        self._importeTotal = self._fill_and_validate_len(importeTotal, 'importeTotal', 15)  
        
    @property
    def importeTotalNG(self):
        return self._importeTotalNG
        
    @importeTotalNG.setter
    def importeTotalNG(self, importeTotalNG):        
        self._importeTotalNG = self._fill_and_validate_len(importeTotalNG, 'importeTotalNG', 15)      
        
    @property
    def importeOpExentas(self):
        return self._importeOpExentas
        
    @importeOpExentas.setter
    def importeOpExentas(self, importeOpExentas):        
        self._importeOpExentas = self._fill_and_validate_len(importeOpExentas, 'importeOpExentas', 15)      
        
    @property
    def importePerOIva(self):
        return self._importePerOIva
        
    @importePerOIva.setter
    def importePerOIva(self, importePerOIva):        
        self._importePerOIva = self._fill_and_validate_len(importePerOIva, 'importePerOIva', 15)      
        
    @property
    def importePerOtrosImp(self):
        return self._importePerOtrosImp
        
    @importePerOtrosImp.setter
    def importePerOtrosImp(self, importePerOtrosImp):        
        self._importePerOtrosImp = self._fill_and_validate_len(importePerOtrosImp, 'importePerOtrosImp', 15)    
        
    @property
    def importePerIIBB(self):
        return self._importePerIIBB
        
    @importePerIIBB.setter
    def importePerIIBB(self, importePerIIBB):        
        self._importePerIIBB = self._fill_and_validate_len(importePerIIBB, 'importePerIIBB', 15)  
    
    @property
    def importePerIM(self):
        return self._importePerIM
        
    @importePerIM.setter
    def importePerIM(self, importePerIM):        
        self._importePerIM = self._fill_and_validate_len(importePerIM, 'importePerIM', 15)  
    
    @property
    def importeImpInt(self):
        return self._importeImpInt
        
    @importeImpInt.setter
    def importeImpInt(self, importeImpInt):        
        self._importeImpInt = self._fill_and_validate_len(importeImpInt, 'importeImpInt', 15)  
    
    @property
    def codigoMoneda(self):
        return self._codigoMoneda
        
    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):        
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3, numeric=False)  
    
    @property
    def tipoCambio(self):
        return self._tipoCambio
        
    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):        
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)      
    
    @property
    def cantidadAlicIva(self):
        return self._cantidadAlicIva
        
    @cantidadAlicIva.setter
    def cantidadAlicIva(self, cantidadAlicIva):        
        self._cantidadAlicIva = self._fill_and_validate_len(cantidadAlicIva, 'cantidadAlicIva', 1)  
        
    @property
    def codigoOperacion(self):
        return self._codigoOperacion
        
    @codigoOperacion.setter
    def codigoOperacion(self, codigoOperacion):        
        self._codigoOperacion = self._fill_and_validate_len(codigoOperacion, 'codigoOperacion', 1, numeric=False)      
        
    @property
    def credFiscComp(self):
        return self._credFiscComp
        
    @credFiscComp.setter
    def credFiscComp(self, credFiscComp):        
        self._credFiscComp = self._fill_and_validate_len(credFiscComp, 'credFiscComp', 15)  
    
    @property
    def otrosTrib(self):
        return self._otrosTrib
        
    @otrosTrib.setter
    def otrosTrib(self, otrosTrib):        
        self._otrosTrib = self._fill_and_validate_len(otrosTrib, 'otrosTrib', 15)  
        
    @property
    def cuitEmisor(self):
        return self._cuitEmisor
        
    @cuitEmisor.setter
    def cuitEmisor(self, cuitEmisor):        
        self._cuitEmisor = self._fill_and_validate_len(cuitEmisor, 'cuitEmisor', 11)      
        
    @property
    def denominacionEmisor(self):
        return self._denominacionEmisor
        
    @denominacionEmisor.setter
    def denominacionEmisor(self, denominacionEmisor):        
        self._denominacionEmisor = self._fill_and_validate_len(denominacionEmisor, 'denominacionEmisor', 30, numeric=False)      
    
    @property
    def ivaComision(self):
        return self._ivaComision
        
    @ivaComision.setter
    def ivaComision(self, ivaComision):        
        self._ivaComision = self._fill_and_validate_len(ivaComision, 'ivaComision', 15)    

class PurchaseSalesPresentationComprasAlicuotasLine(PresentationLine):
  
    __slots__ = [ '_tipoComprobante', '_puntoDeVenta', '_numeroComprobante',
                 '_codigoDocVend', '_numeroIdVend', '_importeNetoGravado',
                 '_alicuotaIva', '_impuestoLiquidado']
    
    def __init__(self):
        self._tipoComprobante = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._codigoDocVend = None
        self._numeroIdVend = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        
        values = [self.tipoComprobante, self.puntoDeVenta, self.numeroComprobante,
                  self.codigoDocVend, self.numeroIdVend, self.importeNetoGravado,
                  self.alicuotaIva, self.impuestoLiquidado]
       
        return values
            
    @property
    def tipoComprobante(self):
        return self._tipoComprobante
        
    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):        
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 3)     
        
    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta
        
    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):        
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)  
    
    @property
    def numeroComprobante(self):
        return self._numeroComprobante
        
    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):        
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)  
        
    @property
    def codigoDocVend(self):
        return self._codigoDocVend
        
    @codigoDocVend.setter
    def codigoDocVend(self, codigoDocVend):        
        self._codigoDocVend = self._fill_and_validate_len(codigoDocVend, 'codigoDocVend', 2)
        
    @property
    def numeroIdVend(self):
        return self._numeroIdVend
        
    @numeroIdVend.setter
    def numeroIdVend(self, numeroIdVend):        
        self._numeroIdVend = self._fill_and_validate_len(numeroIdVend, 'numeroIdVend', 20)  
        
    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado
        
    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):        
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)  
                 
    @property
    def alicuotaIva(self):
        return self._alicuotaIva
        
    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):        
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)  
    
    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado
        
    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):        
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)  
        
class PurchaseSalesPresentationComprasImportacionesLine(PresentationLine):
          
    __slots__ = [ '_despachoImportacion', '_importeNetoGravado', 
                  '_alicuotaIva', '_impuestoLiquidado']
        
    def __init__(self):
        self._despachoImportacion = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None
    
    def get_values(self):
        
        values = [self.despachoImportacion, self.importeNetoGravado,
                  self.alicuotaIva, self.impuestoLiquidado]
       
        return values
        
    @property
    def despachoImportacion(self):
        return self._despachoImportacion
        
    @despachoImportacion.setter
    def despachoImportacion(self, despachoImportacion):        
        self._despachoImportacion = self._fill_and_validate_len(despachoImportacion, 'despachoImportacion', 16, numeric=False)
        
    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado
        
    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):        
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)
  
    @property
    def alicuotaIva(self):
        return self._alicuotaIva
        
    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):        
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)  
    
    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado
        
    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):        
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)  
        
class PurchaseSalesPresentationCreditoFiscalImportacionServLine(PresentationLine):

    __slots__ = ['_tipoComprobante', '_descripcion', '_identificacionComprobante',
                 '_fechaOperacion', '_montoMonedaOriginal', '_codigoMoneda',
                 '_tipoCambio', '_cuitPrestador', '_nifPrestador', '_nombrePrestador',
                 '_alicuotaAplicable', '_fechaIngresoImpuesto', '_montoImpuesto',
                 '_impuestoComputable', '_idPago', '_cuitEntidadPago']
    
    def __init__(self):
        self._tipoComprobante = None
        self._descripcion = None
        self._identificacionComprobante = None
        self._fechaOperacion = None
        self._montoMonedaOriginal = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cuitPrestador = None
        self._nifPrestador = None
        self._nombrePrestador = None
        self._alicuotaAplicable = None
        self._fechaIngresoImpuesto = None
        self._montoImpuesto = None
        self._impuestoComputable = None
        self._idPago = None
        self._cuitEntidadPago = None

    def get_values(self):
        
        values = [self.tipoComprobante, self.descripcion, self.identificacionComprobante,
                  self.fechaOperacion, self.montoMonedaOriginal, self.codigoMoneda,
                  self.tipoCambio, self.cuitPrestador, self.nifPrestador, self.nombrePrestador,
                  self.alicuotaAplicable, self.fechaIngresoImpuesto, self.montoImpuesto,
                  self.impuestoComputable, self.idPago, self.cuitEntidadPago]
       
        return values
            
    @property
    def tipoComprobante(self):
        return self._tipoComprobante
        
    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):        
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 1)  
    
    @property
    def descripcion(self):
        return self._descripcion
        
    @descripcion.setter
    def descripcion(self, descripcion):        
        self._descripcion = self._fill_and_validate_len(descripcion, 'descripcion', 20, numeric=False)
      
    @property
    def identificacionComprobante(self):
        return self._identificacionComprobante
        
    @identificacionComprobante.setter
    def identificacionComprobante(self, identificacionComprobante):        
        self._identificacionComprobante = self._fill_and_validate_len(identificacionComprobante, 'identificacionComprobante', 20, numeric=False)
   
    @property
    def fechaOperacion(self):
        return self._fechaOperacion
        
    @fechaOperacion.setter
    def fechaOperacion(self, fechaOperacion):        
        self._fechaOperacion = self._fill_and_validate_len(fechaOperacion, 'fechaOperacion', 8)
        
    @property
    def montoMonedaOriginal(self):
        return self._montoMonedaOriginal
        
    @montoMonedaOriginal.setter
    def montoMonedaOriginal(self, montoMonedaOriginal):        
        self._montoMonedaOriginal = self._fill_and_validate_len(montoMonedaOriginal, 'montoMonedaOriginal', 15)  
   
    @property
    def codigoMoneda(self):
        return self._codigoMoneda
        
    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):        
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3)  
   
    @property
    def tipoCambio(self):
        return self._tipoCambio
        
    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):        
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)  
   
    @property
    def cuitPrestador(self):
        return self._cuitPrestador
        
    @cuitPrestador.setter
    def cuitPrestador(self, cuitPrestador):        
        self._cuitPrestador = self._fill_and_validate_len(cuitPrestador, 'cuitPrestador', 11)  

    @property
    def nifPrestador(self):
        return self._nifPrestador
        
    @nifPrestador.setter
    def nifPrestador(self, nifPrestador):        
        self._nifPrestador = self._fill_and_validate_len(nifPrestador, 'nifPrestador', 20, numeric=False)  
   
    @property
    def nombrePrestador(self):
        return self._nombrePrestador
        
    @nombrePrestador.setter
    def nombrePrestador(self, nombrePrestador):        
        self._nombrePrestador = self._fill_and_validate_len(nombrePrestador, 'nombrePrestador', 30, numeric=False)  
   
    @property
    def alicuotaAplicable(self):
        return self._alicuotaAplicable
        
    @alicuotaAplicable.setter
    def alicuotaAplicable(self, alicuotaAplicable):        
        self._alicuotaAplicable = self._fill_and_validate_len(alicuotaAplicable, 'alicuotaAplicable', 4)  

    @property
    def fechaIngresoImpuesto(self):
        return self._fechaIngresoImpuesto
        
    @fechaIngresoImpuesto.setter
    def fechaIngresoImpuesto(self, fechaIngresoImpuesto):        
        self._fechaIngresoImpuesto = self._fill_and_validate_len(fechaIngresoImpuesto, 'fechaIngresoImpuesto', 8)  
   
    @property
    def montoImpuesto(self):
        return self._montoImpuesto
        
    @montoImpuesto.setter
    def montoImpuesto(self, montoImpuesto):        
        self._montoImpuesto = self._fill_and_validate_len(montoImpuesto, 'montoImpuesto', 15)  
   
    @property
    def impuestoComputable(self):
        return self._impuestoComputable
        
    @impuestoComputable.setter
    def impuestoComputable(self, impuestoComputable):        
        self._impuestoComputable = self._fill_and_validate_len(impuestoComputable, 'impuestoComputable', 15)  
   
    @property
    def idPago(self):
        return self._idPago
        
    @idPago.setter
    def idPago(self, idPago):        
        self._idPago = self._fill_and_validate_len(idPago, 'idPago', 20, numeric=False)  
   
    @property
    def cuitEntidadPago(self):
        return self._cuitEntidadPago
        
    @cuitEntidadPago.setter
    def cuitEntidadPago(self, cuitEntidadPago):        
        self._cuitEntidadPago = self._fill_and_validate_len(cuitEntidadPago, 'cuitEntidadPago', 11)


class SifereLine(PresentationLine):
    __slots__ = ['_jurisdiccion', '_cuit', '_fecha',
                 '_puntoDeVenta', '_tipo', '_letra',
                 '_importe']

    def __init__(self):
        self._jurisdiccion = None
        self._cuit = None
        self._fecha = None
        self._puntoDeVenta = None
        self._tipo = None
        self._letra = None
        self._importe = None

    @property
    def jurisdiccion(self):
        return self._jurisdiccion

    @jurisdiccion.setter
    def jurisdiccion(self, jurisdiccion):
        self._jurisdiccion = self._fill_and_validate_len(jurisdiccion, 'jurisdiccion', 3)

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 13)
        
    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 4)

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 1)
    
    @property
    def letra(self):
        return self._letra

    @letra.setter
    def letra(self, letra):
        self._letra = self._fill_and_validate_len(letra, 'letra', 1)
    
    @property
    def importe(self):
        return self._importe

    @importe.setter
    def importe(self, importe):
        self._importe = self._fill_and_validate_len(importe, 'importe', 11)


class SifereRetentionLine(SifereLine):
    __slots__ = ['_numeroBase', '_numeroComprobante']

    def __init__(self):
        super(SifereRetentionLine, self).__init__()
        self._numeroBase = None
        self._numeroComprobante = None
        
    @property
    def numeroBase(self):
        return self._numeroBase

    @numeroBase.setter
    def numeroBase(self, numeroBase):
        self._numeroBase = self._fill_and_validate_len(numeroBase, 'numeroBase', 20)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 16)

    def get_values(self):
        values = [self._jurisdiccion, self._cuit, self._fecha, self._puntoDeVenta,
                  self._numeroComprobante, self._tipo, self._letra, self._numeroBase,
                  self._importe]

        return values
        

class SiferePerceptionLine(SifereLine):
    __slots__ = ['_numeroComprobante']
    
    def __init__(self):
        super(SiferePerceptionLine, self).__init__()
        self._numeroComprobante = None

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 8)

    def get_values(self):
        values = [self._jurisdiccion, self._cuit, self._fecha, self._puntoDeVenta,
        self._numeroComprobante, self._tipo, self._letra, self._importe]

        return values
