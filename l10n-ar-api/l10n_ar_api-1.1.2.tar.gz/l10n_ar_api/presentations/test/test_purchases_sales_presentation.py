# -*- coding: utf-8 -*-
import unittest
import sys
sys.path.append("../")
import presentation

class TestPurchaseSalesPresentationLine(unittest.TestCase):

    def _set_cabecera_line(self, cabecera):
        
        cabecera.cuit = 30709653543
        cabecera.periodo = 201611
        cabecera.secuencia = 00
        cabecera.sinMovimiento = 'S'
        cabecera.prorratearCFC = 'Ñ'
        cabecera.cFCGlobal = 'Ó'
        cabecera.importeCFCG = 100000001251200
        cabecera.importeCFCAD = 100000001251200
        cabecera.importeCFCP = 100000001251200
        cabecera.importeCFnCG = 100000001251200
        cabecera.cFCSSyOC = 100000001251200
        cabecera.cFCCSSyOC = 100000001251200

    def _set_ventas_cbte_line(self, ventasCbte):
        
        ventasCbte.fecha = 20151030
        ventasCbte.tipo = '091'
        ventasCbte.puntoDeVenta = 00001
        ventasCbte.numeroComprobante = 4590
        ventasCbte.numeroHasta = 4600
        ventasCbte.codigoDocumento = 20
        ventasCbte.numeroComprador = 51231
        ventasCbte.denominacionComprador = 'Test Test'
        ventasCbte.importeTotal = 5800
        ventasCbte.importeTotalNG = 5000
        ventasCbte.percepcionNC = 300
        ventasCbte.importeExentos = 123   
        ventasCbte.importePercepciones = 5123
        ventasCbte.importePerIIBB = 3331
        ventasCbte.importePerIM = 4234
        ventasCbte.importeImpInt = '12312'
        ventasCbte.codigoMoneda = '321'
        ventasCbte.tipoCambio = '4444000000'
        ventasCbte.cantidadAlicIva = 1
        ventasCbte.codigoOperacion = 1
        ventasCbte.otrosTributos = 0
        ventasCbte.fechaVtoPago = 20151130
    
    def _set_ventas_alicuotas_line(self, ventasAlicuotas):
        
        ventasAlicuotas.tipoComprobante = 91
        ventasAlicuotas.puntoDeVenta = 00001
        ventasAlicuotas.numeroComprobante = 9898989898
        ventasAlicuotas.importeNetoGravado = 10000
        ventasAlicuotas.alicuotaIva = 21
        ventasAlicuotas.impuestoLiquidado = 2100
 
    def _set_compras_cbte_line(self, comprasCbte):
        
        comprasCbte.fecha = 20161212
        comprasCbte.tipo = 98
        comprasCbte.puntoDeVenta = 0001
        comprasCbte.numeroComprobante = '12345678'
        comprasCbte.despachoImportacion = 'despaimportacion'
        comprasCbte.codigoDocumento = 'CD'
        comprasCbte.numeroVendedor = '30709653543'
        comprasCbte.denominacionVendedor = 'Test test'
        comprasCbte.importeTotal = 100000
        comprasCbte.importeTotalNG = 0
        comprasCbte.importeOpExentas = 0
        comprasCbte.importePerOIva = 0
        comprasCbte.importePerOtrosImp = 0
        comprasCbte.importePerIIBB = 0
        comprasCbte.importePerIM = 0
        comprasCbte.importeImpInt = 1000
        comprasCbte.codigoMoneda = 'ARS'
        comprasCbte.tipoCambio = '1'
        comprasCbte.cantidadAlicIva = '5'
        comprasCbte.codigoOperacion = 'A'
        comprasCbte.credFiscComp = '0'
        comprasCbte.otrosTrib = '0'
        comprasCbte.cuitEmisor = '11022598'
        comprasCbte.denominacionEmisor = 'Responsable Inscripto'
        comprasCbte.ivaComision = '100' 
    
    def _set_compras_alicuotas_line(self, comprasAlicuotas):
        
        comprasAlicuotas.tipoComprobante = '093'
        comprasAlicuotas.puntoDeVenta = '00005'
        comprasAlicuotas.numeroComprobante = 123516129872
        comprasAlicuotas.codigoDocVend = 13
        comprasAlicuotas.numeroIdVend = 26288940
        comprasAlicuotas.importeNetoGravado = 50000
        comprasAlicuotas.alicuotaIva = 3
        comprasAlicuotas.impuestoLiquidado = 10000
     
    def _set_compras_importaciones_line(self, comprasImportaciones):
        
        comprasImportaciones.despachoImportacion = '18273918273JKL'
        comprasImportaciones.importeNetoGravado = '100000'
        comprasImportaciones.alicuotaIva = '912'
        comprasImportaciones.impuestoLiquidado = '1000'
        
    def _set_credito_fiscal_importacion_serv_line(self, creditoFiscalImportacionServ):
        
        creditoFiscalImportacionServ.tipoComprobante = '3'
        creditoFiscalImportacionServ.descripcion = 'Descripcion'
        creditoFiscalImportacionServ.identificacionComprobante = '981273918CCLL'
        creditoFiscalImportacionServ.fechaOperacion = '20161212'
        creditoFiscalImportacionServ.montoMonedaOriginal = '10000'
        creditoFiscalImportacionServ.codigoMoneda = 'USD'
        creditoFiscalImportacionServ.tipoCambio = '15'
        creditoFiscalImportacionServ.cuitPrestador = '262841231'
        creditoFiscalImportacionServ.nifPrestador = '123123123245927'
        creditoFiscalImportacionServ.nombrePrestador = 'Nombre Apellido Prestador'
        creditoFiscalImportacionServ.alicuotaAplicable = '2100'
        creditoFiscalImportacionServ.fechaIngresoImpuesto = '20141213'
        creditoFiscalImportacionServ.montoImpuesto = '1300'
        creditoFiscalImportacionServ.impuestoComputable = '1000'
        creditoFiscalImportacionServ.idPago = '0001-8192839192'
        creditoFiscalImportacionServ.cuitEntidadPago = '30709612352'

    purchaseSalesCabecera = presentation.Presentation("ventasCompras", "cabecera")
    purchaseSalesVentasCbte = presentation.Presentation("ventasCompras", "ventasCbte")
    purchaseSalesVentasAlicuotas = presentation.Presentation("ventasCompras", "ventasAlicuotas")
    purchaseSalesComprasCbte = presentation.Presentation("ventasCompras", "comprasCbte")
    purchaseSalesComprasAlicuotas = presentation.Presentation("ventasCompras", "comprasAlicuotas")
    purchaseSalesComprasImportaciones = presentation.Presentation("ventasCompras", "comprasImportaciones")
    purchaseSalesCreditoFiscalImportacionServ = presentation.Presentation("ventasCompras", "creditoFiscalImportacionServ")
         
    def _create_cabecera_lines(self):
        for i in xrange(3):
            self._set_cabecera_line(self.purchaseSalesCabecera.create_line())
            
    def _create_ventas_cbte_lines(self):
        for i in xrange(3):
            self._set_ventas_cbte_line(self.purchaseSalesVentasCbte.create_line())
    
    def _create_ventas_alicuotas_lines(self):
        for i in xrange(5):
            self._set_ventas_alicuotas_line(self.purchaseSalesVentasAlicuotas.create_line())
       
    def _create_compras_cbte_lines(self):
        for i in xrange(1): 
            self._set_compras_cbte_line(self.purchaseSalesComprasCbte.create_line())
  
    def _create_compras_alicuotas_lines(self):
        for i in xrange(2): 
            self._set_compras_alicuotas_line(self.purchaseSalesComprasAlicuotas.create_line())
    
    def _create_compras_importaciones_lines(self):
        for i in xrange(7): 
            self._set_compras_importaciones_line(self.purchaseSalesComprasImportaciones.create_line())
       
    def _create_credito_fiscal_importacion_serv_lines(self):
        for i in xrange(1):
            self._set_credito_fiscal_importacion_serv_line(self.purchaseSalesCreditoFiscalImportacionServ.create_line())
          
    def _create_lines(self):
        self._create_cabecera_lines()
        self._create_ventas_cbte_lines()
        self._create_ventas_alicuotas_lines()
        self._create_compras_cbte_lines()
        self._create_compras_alicuotas_lines()
        self._create_compras_importaciones_lines()
        self._create_credito_fiscal_importacion_serv_lines()        
  
    def test_create_presentation_string(self):
        self._create_lines()

        #3 de 112 y 2 de los \n
        self.assertEqual(len(self.purchaseSalesCabecera.get_string()), 338)
        
        #3 de 266 y 2 de los \n
        self.assertEqual(len(self.purchaseSalesVentasCbte.get_string()), 800)
        
        #5 de 62 y 4 de los \n
        self.assertEqual(len(self.purchaseSalesVentasAlicuotas.get_string()), 314)
        
        #1 de 325
        self.assertEqual(len(self.purchaseSalesComprasCbte.get_string()), 325)
        
        #2 de 168 y 1 \n
        self.assertEqual(len(self.purchaseSalesComprasAlicuotas.get_string()), 169)
        
        #7 de 50 y 6 \n
        self.assertEqual(len(self.purchaseSalesComprasImportaciones.get_string()), 356)
        
        #1 de 211
        self.assertEqual(len(self.purchaseSalesCreditoFiscalImportacionServ.get_string()), 211)

if __name__ == '__main__':
    unittest.main()