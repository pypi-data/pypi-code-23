# -*- coding: utf-8 -*-
import compiler
import logging
try:
    from django.db.models import get_model
except:
    from django.apps import apps
    get_model = apps.get_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models
from .choices import (
    EXTERNAL_SOURCE_TYPE,
    EXTERNAL_SOURCE_FORMAT,
    FIELD_TYPE,
    FIELD_MAPPING_ERROR_TYPE,
)
from .exceptions import (
    TransformacaoException,
    CodigoPerigosoException,
)
log = logging.getLogger("django-onivoro")


class AppModelMixin(models.Model):

    """
    Este modelo tem em seus atributos dados para referenciar uma
    aplicação e um modelo django.
    """

    app = models.CharField(max_length=128,
                           verbose_name=_(u"Aplicação Django"),
                           help_text=_(u"Aplicação Django que contém o modelo em questão"))

    modelo = models.CharField(max_length=128,
                              verbose_name=_(u"Modelo Django"),
                              help_text=_(u"Modelo Django que será utilizado."))

    @property
    def validar_modelo(self):
        """
        Valida se o modelo é válido ou não.
        """
        try:
            modelo = get_model(self.app, self.modelo)
            if modelo is None:
                return False
            else:
                return True
        except Exception:
            # todo: qualificar a exceção que é lançada quando não achamos um modelo.
            return False

    @property
    def ref_modelo(self):
        """
        Retorna uma referência ao modelo Django.
        Caso o modelo não exista ou seja inválido, retorna None.
        todo: este método duplica uma chamada a get_model. Reduzir esta duplicação.
        """
        if self.validar_modelo:
            return get_model(self.app, self.modelo)
        else:
            return None

    class Meta:
        abstract = True


class FonteExterna(AppModelMixin):
    """
    Classe utilizada para representar uma fonte externa, capaz de ser atualizada
    através de comandos de gerenciamento.
    """

    criado_em = models.DateTimeField(auto_now_add=True,
                                     editable=False,
                                     verbose_name=_(u"Criado em"),
                                     help_text=_(u"Data de criação da fonte externa."))

    atualizado_em = models.DateTimeField(auto_now=True,
                                         editable=False,
                                         verbose_name=_(u"Atualizado em"),
                                         help_text=_(u"Data da última atualização desta fonte externa."))

    nome = models.CharField(max_length=128,
                            unique=True,
                            verbose_name=_(u"Nome"),
                            help_text=_(u"Texto identificador da fonte externa."))

    descricao = models.CharField(max_length=512,
                                 verbose_name=_(u"Descrição da Fonte Externa"),
                                 help_text=_(u"Texto descritivo da fonte externa"))

    srid = models.IntegerField(verbose_name=_(u"SRID (nativo)"), 
                               help_text=_(u"SRID do sistema de referência de entrada."),
                               default=4326)

    encoding = models.CharField(max_length=16,
                                verbose_name=_(u"Codificação"),
                                help_text=_(u"Codificação em que o dado original se encontra. Ex: utf-8, latin-1, etc. Padrão é latin-1."),
                                default="latin-1")

    tipo = models.CharField(max_length=32,
                            verbose_name=_(u"Tipo da Fonte Externa"),
                            choices=EXTERNAL_SOURCE_TYPE)

    url_sincronia = models.URLField(verbose_name=_(u"Endereço Sincronia"),
                                    help_text=_(u"URL do recurso a ser sincronizado"))

    formato = models.CharField(max_length=6,
                               choices=EXTERNAL_SOURCE_FORMAT,
                               verbose_name=_(u"Formato Arquivo"),
                               help_text=_(u"Formato do arquivo utilizado para sincronziação."))

    ultima_sincronizacao = models.DateTimeField(auto_now=False,
                                                verbose_name=_(u"Última sincronização"),
                                                help_text=_(u"Data em que o modelo foi sincronizado pela última vez."))

    nome_alvo = models.CharField(max_length=128,
                                 verbose_name=_(u"Nome do Arquivo Alvo"),
                                 help_text=_(u"Nome do arquivo alvo. Só é necessário se um zip contém mais de um arquivo do mesmo tipo."),
                                 null=True,
                                 blank=True)

    @property
    def mapa_campos(self):
        """
        Retorna um dicionário com o mapa de campos
        """
        mapa = {}

        for fm in self.mapeamentos.all():
            if mapa.has_key(fm.campo_destino):
                raise MapeamentoException(
                    _(u"Não é possível ter duas chaves com o mesmo valor. Não é possível criar este mapeamento de campos."))

            if fm.tipo_destino == "FK":
                mapa[fm.campo_destino] = {fm.campo_destino_estrangeira: fm.campo_origem}
            else:
                mapa[fm.campo_destino] = fm.campo_origem

        return mapa

    @property
    def deve_limpar_registros_antigos(self):
        """
        Esta propriedade diz se devemos limpar os
        dados antigos apos a importaçao dos
        novos dados.

        Basicamente verificamos se a PK possui
        nome id. Se verdadeiro, devemos executar
        a limpeza, pois não podemos confiar no
        comportamento de LayerMapping (onde existe PK
        confiável, ele atualiza os dados e faz inserts
        onde necessário).
        """
        if self.ref_modelo._meta.pk.name == "id":
            return True

        return False

    def url_valida(self):
        """
        Valida a URL com o tipo.
        """

        extensao = self.url_sincronia[-3:].upper()

        if self.tipo == "SHAPEFILE":
            if extensao not in ("ZIP", "SHP") and self.url_sincronia[-6:].upper() != "TAR.GZ":
                return False

            return True
        elif self.tipo == "GEOJSON":
            if extensao not in ("", "ZIP", "TAR.GZ", "JSON") and not extensao.endswith("/"):
                return False

            return True

        elif self.tipo == "WFS":
            if extensao != "":
                return False

            return True
        else:
            raise Exception(_("Tipo de fonte externa não suportado."))

    def __unicode__(self):
        """
        Representação unicode do modelo FonteExterna
        """
        return unicode(self.nome)

    def get_absolute_url(self):
        """
        Stub de permalink para FonteExterna
        todo: implementar permalink para fonte externa
        """
        return ("detalhe_fonte_externa", [str(self.id)])

    def save(self, *args, **kwargs):
        """
        Método customizado de salvar o objeto.
        """
        if not self.validar_modelo:
            raise ValueError(_(u"Não foi possível carregar o modelo especificado."))

        super(FonteExterna, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _(u"Fonte Externa")
        verbose_name_plural = _(u"Fontes Externas")
        ordering = ("-atualizado_em",)


class Transformacao(models.Model):
    """
    Modelo que transforma valores de um lado para outro no ETL.
    Transformações possíveis são arredondamentos, encurtamentos de string,
    tranformações de SRID, etc.
    Este modelo é extremamente sensível, portanto somente pessoas de extrema
    confiança devem atualizá-lo.
    """

    nome = models.CharField(max_length=256,
                            verbose_name=_(u"Nome"),
                            help_text=_(u"Nome da Transformação"),
                            unique=True)

    # este campo é obrigatório para facilitar a identificação das transformações.
    descricao = models.CharField(max_length=256,
                                 verbose_name=_(u"Descrição"),
                                 help_text=_(u"Descrição da Transformação."))

    tipo_campo = models.CharField(max_length=32,
                                  choices=FIELD_TYPE,
                                  verbose_name=_(u"Tipo de Campo Aplicável"),
                                  help_text=_(u"Tipo de Campo a qual esta transformação se aplica."))

    metodo_conversao = models.TextField(verbose_name=_(u"Código utilizado na transformação"),
                                        help_text=_(u"Código que será utilizado para transformar os valores. A entrada deverá ser obrigatóriamente uma função com um argumento e exatamente um retorno."))

    _metodo_conversao = None

    def __unicode__(self):
        return self.nome

    def get_absolute_url(self):
        """
        Stub de permalink para Transformação
        todo: implementar get_absolute_url em Transformacao
        """
        pass

    def codigo_perigoso(self):
        """
        Método que tenta identificar se um código é perigoso
        ou não.
        Sei que esta tentativa é bem simples, mas a idéia é que poucos usuários
        tenham acesso a este modelo.
        """
        # exec
        if self.metodo_conversao.find("exec") != -1:
            log.info(_("Contém um statement exec. Código potencialmente perigoso."))
            return True

        # eval
        if self.metodo_conversao.find("eval") != -1:
            log.info(_("Contém um statement eval. Código potencialmente perigoso."))
            return True

        # import
        if self.metodo_conversao.find("import") != -1:
            log.info(_("Contém um statement import. Código potencialmente perigoso."))
            return True

        # import
        if self.metodo_conversao.find("from") != -1:
            log.info(_("Contém um statement from. Código potencialmente perigoso."))
            return True

        # wild import
        if self.metodo_conversao.find("*") != -1:
            log.info(_("Contém um statement * 'all'. Código potencialmente perigoso."))
            return True

        # whiles não são permitidos
        if self.metodo_conversao.find("while") != -1:
            log.info(_("Contém um statement while. Código potencialmente perigoso."))
            return True

        return False

    def sintaxe_valida(self):
        """
        Testa se a sintaxe do código é válida e se
        o código contém, por obrigatoriedade uma função
        chamada converter, com dois parametros (entrada e campo_novo),
        retornando um valor especifico.
        Exemplo:

        def converter(entrada,campo_novo):
            return "a"
        """

        try:
            mod = compiler.parse(self.metodo_conversao)

            # em um mundo ideal, sem imports, sem outras funcoes, etc

            #            funcao_converte = mod.getChildren()[1].getChildren()[0]
            #
            #            if funcao_converte.name != "converte":
            #                log.info(u"O código não atende as especificações (primeira função do módulo deve se chamar 'converte').")
            #                return False
            #
            #            if len(funcao_converte.argnames) != 2:
            #                log.info(u"O código não atende as especificações (a função converte deve ter somente dois argumentos).")
            #                return False
            #
            #            if funcao_converte.argnames[0] != "entrada":
            #                log.info(u"O código não atende as especificações (primeiro parametro da função converte deve se chamar entrada).")
            #                return False
            #
            #            if funcao_converte.argnames[0] != "campo_novo":
            #                log.info(u"O código não atende as especificações (segundo parametro da função converte deve se chamar campo_novo).")
            #                return False

            return True
        except SyntaxError as synEx:
            return False

    def transforma(self, entrada, campo_novo):
        """
        Método para transformação de valores
        """

        log.info(_("Transformando valor via %s" % self.nome))

        if not self.sintaxe_valida():
            raise TransformacaoException(_(u"A sintaxe do código não é válida."))

        if self.codigo_perigoso():
            log.info(_("Código considerado perigoso. Não será executado."))
            raise ValueError(
                _(u"O código da transformação foi considerado potencialmente perigoso e não poderá ser salvo/executado no sistema."))

        valor_novo = None

        try:
            if not self._metodo_conversao:
                self._metodo_conversao = compile(self.metodo_conversao, "<string>", "exec")

            ns = {"__builtins__": __builtins__, "entrada": entrada, "campo_novo": campo_novo}
            exec self._metodo_conversao in ns

            return ns["valor_novo"]

        except Exception as ex:
            return None

    def save(self, *args, **kwargs):
        """
        Método customizado de save. Impede que código potencialmente perigoso seja
        armazenado e ou executado pelo servidor.
        """

        if not self.sintaxe_valida():
            raise TransformacaoException(_(u"A sintaxe do código não é válida."))

        if self.codigo_perigoso():
            raise CodigoPerigosoException(
                _(u"O código da transformação foi considerado potencialmente perigoso e não poderá ser salvo/executado no sistema."))

        super(Transformacao, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _(u"Transformação")
        verbose_name_plural = _(u"Transformações")


class Mapeamento(models.Model):
    """
    Mapeamento entre dois campos, um externo e um interno.
    """

    fonte_externa = models.ForeignKey(FonteExterna,
                                      verbose_name=_(u"Fonte Externa"),
                                      help_text=_(u"Fonte externa em que este mapeamento de campos está associado."),
                                      related_name="mapeamentos")

    campo_origem = models.CharField(max_length=64,
                                    verbose_name=_(u"Nome do Campo (fonte externa)"),
                                    help_text=_(u"Nome do campo, na origem (fonte externa)."))

    campo_destino = models.CharField(max_length=64,
                                     verbose_name=_(u"Nome do Campo (modelo GeoDjango)"),
                                     help_text=_(u"Nome do campo, no destino (modelo GeoDjango)."))

    campo_destino_estrangeira = models.CharField(max_length=64,
                                                 null=True,
                                                 blank=True,
                                                 verbose_name=_(u"Nome do Campo Chave Estrangeira (modelo GeoDjango)"),
                                                 help_text=_(u"Chave estrangeira do modelo."))

    tipo_origem = models.CharField(max_length=32,
                                   choices=FIELD_TYPE,
                                   editable=False,
                                   verbose_name=_(u"Tipo do Campo (fonte externa)"),
                                   help_text=_(u"Tipo do campo, na origem (fonte externa)."))

    tipo_destino = models.CharField(max_length=32,
                                    choices=FIELD_TYPE,
                                    editable=False,
                                    verbose_name=_(u"Tipo do Campo (modelo GeoDjango)"),
                                    help_text=_(u"Tipo do Campo, no destino (modelo GeoDjango)."))

    transformacoes = models.ManyToManyField(Transformacao,
                                            verbose_name=_(u"Transformações"),
                                            help_text=_(u"Transformações serão executadas para cada campo, de forma a adequar o mesmo ao modelo interno."))

    def transforma(self, registro_origem, registro_destino):
        pass

    def conversao_valida(self):
        """
        Valida se o mapeamento de campos é coerente e está tudo no lugar.
        """

        if self.tipo_origem == self.tipo_destino:
            # ok, o tipo é o mesmo.
            return True

        if self.tipo_origem == "STRING" and self.tipo_destino != "STRING" and self.tipo_destino != "FK":
            # o tipo de string é complicado de mapear para outros tipos, portanto vamos desabilitar
            return False

        if self.tipo_origem == "GEO" and self.tipo_destino != "GEO":
            # por enquanto só vamos converter geom para geom
            return False

        if self.tipo_origem in ("INT", "FLOAT", "DATA", "DATA-HORA") and self.tipo_destino == "STRING":
            # ok, podemos fazer uma conversão coxa
            return True

        if self.tipo_origem in ("INT", "FLOAT") and self.tipo_destino in ("INT", "FLOAT"):
            # ok, podemos truncar o valor ou subir a conversão
            return True

        if self.tipo_origem in ("DATA", "DATA-HORA") and self.tipo_destino == ("DATA", "DATA-HORA"):
            # ok, podemos passar data sem horas ou truncar a hora
            return True

        if self.tipo_destino == "FK" and self.campo_destino_estrangeira:
            # se o tipo for FK, é necessário especificar quem é destino final da bagaça!
            return True

        return False

    def __unicode__(self):
        """
        Representação de um mapeamento.
        Exemplo:
        [Unidades de Conservação] nome_uc -> nome_oficial_uc
        """
        modelo = get_model(self.fonte_externa.app, self.fonte_externa.modelo)

        return "[%s] - %s -> %s" % (modelo._meta.verbose_name, self.campo_origem, self.campo_destino)

    class Meta:
        # não é possível ter dois campos apontando para somente um ou um apontando para dois.
        unique_together = (("fonte_externa", "campo_destino"),)

        verbose_name = _(u"Mapeamento de Campo")
        verbose_name_plural = _(u"Mapeamento de Campos")
