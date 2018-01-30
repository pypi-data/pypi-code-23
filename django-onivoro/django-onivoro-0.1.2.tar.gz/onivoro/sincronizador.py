# coding: utf-8
import tarfile
import shutil
import os
import urllib2
import logging
from zipfile import ZipFile
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.gis.utils.layermapping import LayerMapping
from django.db.models.query_utils import Q
from django.contrib.gis.gdal import DataSource
from .signals import (
    pre_sync,
    post_sync
)
from .exceptions import SincronizadorException
from .ogr_utils import OGRField, ErroMapeamento, ConversorTipoCampo


log = logging.getLogger("django-onivoro")


def notificar(sucesso, fonte_externa, count_anterior=None, count_atual=None, mensagem=None):
    if not settings.ONIVORO_MAIL_NOTIFY:
        return

    if not settings.ONIVORO_MAIL_RECIPIENTS:
        return

    if not settings.ONIVORO_MAIL_SENDER:
        return

    if sucesso:
        assunto = _(u"[Django-Onivoro] Sucesso")
        template = get_template("onivoro/email_sucesso.txt")
    else:
        assunto = _(u"[Django-Onivoro] Falha")
        template = get_template("onivoro/email_falha.txt")

    context = Context({"fonte_externa": fonte_externa,
                       "registros_atual": count_atual,
                       "registros_anterior": count_anterior,
                       "mensagem": mensagem,
                       "data": now()})

    email = template.render(context)

    send_mail(assunto, email, settings.ONIVORO_MAIL_SENDER, settings.ONIVORO_MAIL_RECIPIENTS, fail_silently=True)


class Sincronizador(object):
    """
    Classe que sincroniza entre uma fonte externa e um modelo geo.
    Em tese esta classe suporta todo um range de formatos, listados em:
    http://www.gdal.org/ogr/ogr_formats.html
    """

    # fonte externa a ser sincronizada
    fonte_externa = None

    # arquivo mais antigo importado
    arquivo_v2 = None

    # ultimo arquivo importado
    arquivo_v1 = None

    # arquivo sendo importado agora
    arquivo_v0 = None

    # caminho para o arquivo de fonte que será lido e importado (.json, .shp, etc)
    arquivo_alvo = None

    def __init__(self, fonte_externa):

        if not os.path.exists(settings.ONIVORO_DATA_ROOT):
            os.makedirs(settings.ONIVORO_DATA_ROOT)

        self.fonte_externa = fonte_externa

    def sincronizar(self):
        """
        Principal método do sincronizador.
        """
        pre_sync.send_robust(sender=self, fonte_externa=self.fonte_externa)
        sucesso = False
        numero_registros_anterior = None
        try:

            numero_registros_anterior = self.fonte_externa.ref_modelo.objects.all().count()

            if (self.fonte_externa.deve_limpar_registros_antigos and
               self.fonte_externa.ref_modelo.objects.all().count() > 0):

                max_id = self.fonte_externa.ref_modelo.objects.order_by("-id")[0].id
            else:
                max_id = -1

            self._download()

            self._carrega()

            sucesso = True

            # se existiam registros e o número de registros novos for > 0, remova os antigos
            if max_id > 0 and self.fonte_externa.ref_modelo.objects.order_by("-id")[0].id - max_id != 0:
                self.fonte_externa.ref_modelo.objects.filter(id__lte=max_id).delete()

            numero_registros_atual = self.fonte_externa.ref_modelo.objects.all().count()

            notificar(sucesso,
                      self.fonte_externa,
                      numero_registros_anterior,
                      numero_registros_atual,
                      "Sucesso!")
            post_sync.send_robust(sender=self, fonte_externa=self.fonte_externa, sucesso=True)

        except Exception as exc:
            notificar(sucesso,
                      self.fonte_externa,
                      None,
                      numero_registros_anterior,
                      exc.message)
            post_sync.send_robust(sender=self, fonte_externa=self.fonte_externa, sucesso=False)
            log.error(exc.message)

    def _download(self, url=""):

        if url:
            self.fonte_externa.url_sincronia = url

        try:

            request = urllib2.Request(self.fonte_externa.url_sincronia)
            remoto = urllib2.urlopen(request)
            nome = os.path.split(self.fonte_externa.url_sincronia)[-1]

            # remove o arquivo mais antigo
            self.arquivo_v2 = os.path.join(settings.ONIVORO_DATA_ROOT, nome + ".old")
            if os.path.exists(self.arquivo_v2):
                os.remove(os.path.join(settings.ONIVORO_DATA_ROOT, nome + ".old"))

            # renomeia o antigo para .old
            self.arquivo_v1 = os.path.join(settings.ONIVORO_DATA_ROOT, nome)
            if os.path.exists(self.arquivo_v1):
                os.rename(os.path.join(settings.ONIVORO_DATA_ROOT, nome),os.path.join(settings.ONIVORO_DATA_ROOT, nome + ".old"))

            if self.fonte_externa.formato in ("TAR.GZ","ZIP","SHP","SHX","DBF"):
                formato = "wb"
            elif self.fonte_externa.formato == "REQUEST":
                formato = "w"
            else:
                raise SincronizadorException(u"Não foi possível determinar o formato dos dados para sincronização.")

            self.arquivo_v0 = os.path.join(settings.ONIVORO_DATA_ROOT, nome)
            local = open(self.arquivo_v0, formato)
            local.write(remoto.read())
            local.close()

            if self.fonte_externa.tipo == "SHAPEFILE" and nome[-3:].upper() == "SHP":
                # caso esta fonte externa seja um shapefile puro, ele também é o arquivo alvo!
                self.arquivo_alvo = self.arquivo_v0

                # caso esta fonte externa seja um shapefile puro, devemos baixar também seus complementos, dbf, shx e prj (opcional)
                dbf = self.fonte_externa.url_sincronia.replace("shp", "dbf")
                shx = self.fonte_externa.url_sincronia.replace("shp", "shx")

                self._download(url=dbf)
                self._download(url=shx)

            if nome[-3:].upper() in ("ZIP", "RAR") or nome[-6:].upper == "TAR.GZ":
                self._descompactar()

        except urllib2.HTTPError as httpEx:

            mensagem = u"Ocorreu um problema HTTP.\n%s" % httpEx.message
            log.error(mensagem)
            raise

        except urllib2.URLError as urlEx:

            mensagem = u"Ocorreu um problema de URL.\n %s" % urlEx.message
            log.error(mensagem)
            raise

    def _descompactar_zip(self):
        """
        Descompacta um arquivo zip e retorna o arquivo
        principal de fonte de dados.
        """
        nome_arquivo = os.path.split(self.arquivo_v0)[-1]
        zip = ZipFile(self.arquivo_v0)

        badzips = zip.testzip()

        if badzips:
            raise SincronizadorException("Não é possível sincronizar a fonte externa %s pois o arquivo zip %s está corrompido ou danificado. Arquivo %s com problemas." % (self.fonte_externa,self.arquivo_v0,badzips))

        unzip_dir = os.path.join(os.path.dirname(self.arquivo_v0), nome_arquivo[:-4])
        if not os.path.exists(unzip_dir):
            os.mkdir(unzip_dir)

        nomes = self._extrair_nomes(self.fonte_externa.tipo, [fileinfo.filename for fileinfo in zip.infolist()])

        if not nomes:
            raise SincronizadorException(_(u"O arquivo compactado %s não é válido. Confira se os arquivos estão dentro do arquivo compactado.") % self.arquivo_v0)

        try:
            for nome in nomes:

                with zip.open(nome) as src:
                    with open(os.path.join(unzip_dir, os.path.basename(nome)), "wb") as dest:
                        shutil.copyfileobj(src, dest)

        except Exception as e:
            log.error(e.message)

        self.arquivo_alvo = os.path.join(unzip_dir, self._determina_fonte_local(nomes))

    def _descompactar_tar(self):
        """
        Descompacta um arquivo tar e retorna o arquivo
        principal de fonte de dados.
        """

        nome_arquivo = os.path.split(self.arquivo_v0)[-1]
        tar = tarfile.open(self.arquivo_v0,"r:gz")

        if not tarfile.is_tarfile(self.arquivo_v0):
            raise SincronizadorException(u"Não é possível sincronizar a fonte externa %s pois o arquivo tar %s está corrompido ou danificado." % (self.fonte_externa,self.arquivo_v0))

        unzip_dir = os.path.join(os.path.dirname(self.arquivo_v0), nome_arquivo[:-7])
        if not os.path.exists(unzip_dir):
            os.mkdir(unzip_dir)

        members = tar.getmembers()

        nomes = self._extrair_nomes(self.fonte_externa.tipo, [n.name for n in members])

        if not nomes:
            raise SincronizadorException(_(u"FALHA! Não foi possível determinar os arquivos necessários para importação. Arquivos contidos no container: %s") % [n.name for n in members])

        for nome in nomes:
            tar.extract(nome, path=unzip_dir)

        self.arquivo_alvo = os.path.join(unzip_dir, self._determina_fonte_local(nomes))

    def _descompactar_rar(self):
        """
        Descompacta um arquivo rar e determina o arquivo
        da fonte de dados.
        todo: implementar descompatação rar.
        perguntas: é viável? necessário?
        """
        pass

    def _descompactar(self):
        """
        Descompacta um arquivo compactado e retorna o arquivo principal
        de fonte de dados
        """

        # self.processo.log(u"Descompactando arquivo %s." % self.arquivo_v0)

        if self.arquivo_v0[-3:].upper() == "ZIP":
            return self._descompactar_zip()

        elif self.arquivo_v0.upper()[-6:] == "TAR.GZ":
            return self._descompactar_tar()

        elif self.arquivo_v0.upper()[-3:] == "RAR":
            return self._descompactar_rar()

        else:
            log.error(_(u"FALHA! Não foi possível determinar o formato do descompactador a ser utilizado para o arquivo %s.") % self.arquivo_v0)
            raise SincronizadorException(_(u"FALHA! Não foi possível determinar o formato do descompactador a ser utilizado."))

    def _determina_fonte_local(self, nomes):
        """
        Determina, após a extração, qual é nosso arquivo alvo.
        """

        if self.fonte_externa.tipo == "SHAPEFILE":

            if self.fonte_externa.nome_alvo:

                basenames = [os.path.basename(n) for n in nomes]

                fontes_locais = [n for n in basenames if unicode(n).upper() == self.fonte_externa.nome_alvo.upper()]

                fonte_local = fontes_locais[0]

                return fonte_local

            return [os.path.basename(n) for n in nomes if n.upper().endswith("SHP")][0]

        elif self.fonte_externa.tipo == "GEOJSON":
            return nomes[0]
        else:
            raise SincronizadorException(_(u"Não é possível determinar a fonte local deste arquivo."))

    def _extrair_nomes(self, tipo, arquivos):
        """
        Busca os arquivos que devem ser extraídos do arquivo compactado.
        Este método existe pois buscamos um nome arbitário dentro do shapefile e ao longo do caminho,
        aproveitamos para verificar se os auxiliares realmente estão lá.
        """

        log.info(_(u"Validando shapefile compactado"))

        if tipo == "SHAPEFILE":

            shps = [shp for shp in arquivos if os.path.basename(shp).upper().endswith("SHP")]
            dbfs = [dbf for dbf in arquivos if os.path.basename(dbf).upper().endswith("DBF")]
            shxs = [shx for shx in arquivos if os.path.basename(shx).upper().endswith("SHX")]

            # mapeando o tipo prj também, para obtenção de informaçoes de projecao!
            prjs = [prj for prj in arquivos if os.path.basename(prj).upper().endswith("PRJ")]

            if len(shps) < 0:
                log.error(_(u"FALHA! Não existe nenhum shapefile disponível no arquivo compactado."))
                return False

            if len(shps) > 1 and self.fonte_externa.nome_alvo is None:
                log.error(_(u"FALHA! Existe mais de um shapefile disponível no arquivo compactado."))
                return False

            log.info(_(u"Arquivo SHP presente!"))

            try:

                if self.fonte_externa.nome_alvo is not None:

                    shp = [shp for shp in shps if unicode(os.path.basename(shp).upper()) == self.fonte_externa.nome_alvo.upper()][0]

                else:
                    shp = shps[0]

            except IndexError:
                log.error(_(u"FALHA! O arquivo .shp não está disponível no arquivo."))
                return None

            if shp.replace("shp", "shx") not in shxs:
                log.error(_(u"FALHA! O arquivo .shx do shapefile %s não está disponível no arquivo.") % shp)
                return None

            if shp.replace("shp", "dbf") not in dbfs:
                log.error(_(u"FALHA! O arquivo .shx do shapefile %s não está disponível no arquivo.") % shp)
                return None

            log.info(_(u"Arquivos adicionais .dbf e .shx presentes"))
            log.info(_(u"SUCESSO! Arquivo %s contém todas os componentes.") % self.arquivo_v0)

            nomes = []

            if len(prjs) > 0:
                nomes.append(prjs[0])
            return nomes + [shp,
                            shp.replace("shp", "shx"),
                            shp.replace("shp", "dbf")]

        elif tipo == "GEOJSON":

            jsons = [json for json in arquivos if json.upper().endswith("JSON")]

            if len(jsons) <= 0:
                log.error(_(u"FALHA! Não existe nenhum arquivo json disponível no arquivo compactado."))
                return None

            if len(jsons) > 1:
                log.error(_(u"FALHA! Existe mais de um JSON disponível no arquivo compactado."))
                return None

            return jsons[0]

        else:
            msg = _(u"FALHA! Não foi possível extrair os nomes deste arquivo pois este tipo (%s) de fonte externa não é suportado.") % self.fonte_externa.tipo
            log.error(msg)
            return None

    def _validar_campos(self):
        """
        Este método valida se os mapeamentos de campos externos/internos está ok.
        """

        erros = []

        datasource = DataSource(self.arquivo_alvo)

        camada_interna = self.fonte_externa.ref_modelo
        campos_internos = {}
        for ci in camada_interna._meta.fields:
            campos_internos[ci.name] = ci

        camada_externa = datasource[0]
        campos_externos = {}
        for i,ce in enumerate(camada_externa.fields):
            name = ce
            type = camada_externa.field_types[i]
            width = camada_externa.field_widths[i]
            precision = camada_externa.field_precisions[i]
            campos_externos[ce] = OGRField(name,type,width,precision)

        for fm in self.fonte_externa.mapeamentos.filter(~Q(tipo_origem="GEO")):

            interno_existe = campos_internos.has_key(fm.campo_destino)
            externo_existe = campos_externos.has_key(fm.campo_origem)

            if not interno_existe:
                erros.append(ErroMapeamento(fm,"NAO_EXISTE",u"O modelo %s não possui o campo %s." % (fm.camada_interna.name,fm.campo_destino)))

            if not externo_existe:
                erros.append(ErroMapeamento(fm,"NAO_EXISTE",u"A fonte externa %s não possui o campo %s." % (camada_externa.name,fm.campo_origem)))

            if interno_existe and externo_existe:
                campo_interno = campos_internos[fm.campo_destino]
                campo_externo = campos_externos[fm.campo_origem]

                if not ConversorTipoCampo.tipo_coincide(campo_externo.type, fm.tipo_origem):
                    msg = _(u"O campo de origem %(campo_origem)s foi mapeado como %(tipo_mapeado)s, mas %(fonte_externa)s ele tem o tipo %(tipo_externo)s.") % {"campo_origem"  : campo_externo.name,
                                                                                                                                                            "tipo_mapeado"  : fm.tipo_origem,
                                                                                                                                                            "fonte_externa" : camada_externa,
                                                                                                                                                            "tipo_externo"  : campo_externo.type.__name__ }

                    erros.append(ErroMapeamento(fm,"TIPO_INCOMPATIVEL",msg))

        return erros

    def _carrega(self):
        try:

            if not self.arquivo_alvo:
                raise SincronizadorException(_(u"Não foi possível determinar quem é o arquivo alvo para sincronização."))

            temp_datasource = DataSource(self.arquivo_alvo)
            temp_layer = temp_datasource[0]
            temp_srs = temp_layer.srs

            erros_validacao = self._validar_campos()

            if len(erros_validacao) > 0:
                errs = [e.mensagem for e in erros_validacao]
                raise SincronizadorException(_(u"Não é possível sincronizar com a fonte externa pois existem erros de campos e mapeamentos. Possivelmente a fonte externa mudou.\nErros:\n %s") % errs)

            if not temp_srs:

                temp_srs = self.fonte_externa.srid

                lm = LayerMapping(self.fonte_externa.ref_modelo,
                                  self.arquivo_alvo,
                                  self.fonte_externa.mapa_campos,
                                  transform=True,
                                  encoding=self.fonte_externa.encoding,
                                  source_srs=temp_srs)
            else:
                lm = LayerMapping(self.fonte_externa.ref_modelo,
                                  self.arquivo_alvo,
                                  self.fonte_externa.mapa_campos,
                                  encoding=self.fonte_externa.encoding,
                                  source_srs=temp_srs)

            lm.save(verbose=True)

        except Exception as ex:
            log.error(_(u"Ocorreu um erro ao tentar importar os dados da fonte externa.\n %s") % ex.message)
            raise SincronizadorException(_(u"Ocorreu um erro ao tentar importar os dados da fonte externa.\n %s") % ex.message)
