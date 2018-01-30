# coding: utf-8
from django.contrib.gis.gdal.field import *

__author__ = 'George'

class OGRField(object):
    """
    Classe para representar um campo OGR (que vem de um Layer do DataSource)
    """

    name = None
    type = None
    width = None
    precision = None

    def __init__(self,name,type,width,precision):
        self.name = name
        self.type = type
        self.width = width
        self.precision = precision

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class ErroMapeamento(object):
    """
    Classe simples para segurar um erro de mapeamento.
    """

    mapeamento = None
    mensagem = None
    tipo_erro = None

    def __init__(self,mapeamento,tipo_erro,mensagem):
        self.mapeamento = mapeamento
        self.tipo_erro = tipo_erro
        self.mensagem = mensagem

    def __unicode__(self):
        return "%s - %s" % (self.tipo_erro,self.mensagem)

class ConversorTipoCampo(object):
    """
    Esta classe compatibiliza os tipos de campos
    encontrados no OGR com o nosso mapeamento.
    """

    def __init__(self):
        pass

    @staticmethod
    def tipo_coincide(campo_ogr,campo_mapeamento,lado="DESTINO"):
        """
        Compara os tipos de dois campos ogr e mapeados
        e veem se sao compativeis.
        Caso lado seja diferente de "DESTINO", ele irá retornar o campo da origem.
        Como esta verificação é mais para os campos externos que podem mudar mais,
        faz mais sentido deixar este o default.
        """

        if lado == "DESTINO":
            return ConversorTipoCampo._tipo_coincide_impl(campo_ogr.type,campo_mapeamento.tipo_destino)
        else:
            return ConversorTipoCampo._tipo_coincide_impl(campo_ogr.type,campo_mapeamento.tipo_origem)

    @staticmethod
    def tipo_coincide(tipo_ogr,tipo_mapeamento):
        """
        Compara dois tipos de campos e veem se sao compativeis
        """
        return ConversorTipoCampo._tipo_coincide_impl(tipo_ogr,tipo_mapeamento)

    @staticmethod
    def _tipo_coincide_impl(ogr_code,campo_mapeamento):
        """
        Implementação para comparacao de tipos
        """

        if ogr_code in (OFTIntegerList,OFTRealList,OFTStringList,OFTWideStringList,OFTTime,OFTBinary):
            # não temos equivalentes aos campos lista.
            return False

        if ogr_code == OFTInteger and campo_mapeamento == "INT":
            return True

        if ogr_code == OFTReal and campo_mapeamento == "FLOAT":
            return True

        if ogr_code == OFTString and campo_mapeamento == "STRING":
            return True

        if ogr_code == OFTWideString and campo_mapeamento == "STRING":
            return True

        if ogr_code == OFTDate and campo_mapeamento == "DATA":
            return True

        if ogr_code == OFTDateTime and campo_mapeamento == "DATA-HORA":
            return True

        if campo_mapeamento == "FK":
            # não temos como verificar se esta FK coincide com o que precisamos.
            return True

        return False

    @staticmethod
    def mapeamento_para_ogr(campo_mapeamento):
        pass

    @staticmethod
    def ogr_para_mapeamento(campo_ogr):
        pass