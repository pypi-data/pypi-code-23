import sys

import pandas as pd
import psycopg2

from .config import oltp_login

lista_uf = {'0110': 'Distrito Federal',
            '0111': 'Spu - Distrito Federal',
            '0120': 'Goiás',
            '0130': 'Mato Grosso',
            '0140': 'Mato Grosso Do Sul',
            '0150': 'Tocantins',
            '0190': 'Exterior',
            '0210': 'Pará',
            '0220': 'Amazonas',
            '0230': 'Acre',
            '0240': 'Amapá',
            '0250': 'Rondônia',
            '0260': 'Roraima',
            '0310': 'Ceará',
            '0320': 'Maranhão',
            '0330': 'Piauí',
            '0410': 'Pernambuco',
            '0420': 'Rio Grande Do Norte',
            '0430': 'Paraíba',
            '0440': 'Alagoas',
            '0510': 'Bahia',
            '0520': 'Sergipe',
            '0610': 'Minas Gerais',
            '0710': 'Rio De Janeiro',
            '0720': 'Espírito Santo',
            '0810': 'São Paulo',
            '0910': 'Paraná',
            '0920': 'Santa Catarina',
            '1010': 'Rio Grande Do Sul'}


def conecta_oltp():
    ''' Conecta ao OLTP(Produção)'''
    host = '10.209.9.227'
    port = 5432
    dbname = 'oltp'
    user = oltp_login['user']
    password = oltp_login['password']

    try:
        conn = psycopg2.connect(host=host, port=port,
                                dbname=dbname, user=user,
                                password=password)

        assert conn.closed == 0
        return conn
    except:
        e = sys.exc_info()
        print(e)
        print('Não foi possível conectar ao Banco de Dados.')
        return None


def carrega_tabela(nomeTabela, con, colunas=('*'), chunkSize=None,
                   parse_dates=None, index=None, filtro=None):
    ''' Carrega a tabela do banco de dados e retorna DataFrame ou
    generator caso seja passado o parametro chunksize'''
    con = conecta_oltp()
    colunas = ','.join(colunas)

    if filtro is not None:
        sql = 'SELECT {} FROM siapa.{} WHERE {}; '''.format(colunas, nomeTabela,
                                                            filtro)
    else:
        sql = 'SELECT {} FROM siapa.{}; '''.format(colunas, nomeTabela)
    dataFrame = pd.read_sql_query(sql, con=con, index_col=index,
                                  chunksize=chunkSize, parse_dates=None)
    return dataFrame


def calc_dv_rip(valor):
    '''
    Calcula o digito verificador do RIP
    RETORNA: RIP com dígito (13 dígitos)
    '''
    if len(valor) < 13:
        if len(valor) == 11:
            prog = [4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        else:
            prog = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        dv = 0
        for i in range(0, len(valor)):
            dv += int(valor[i]) * prog[i]
        dv = dv % 11

        if any([dv == 0, dv == 1]):
            dv = 0
        else:
            dv = 11 - dv
        return calc_dv_rip(valor + str(dv))
    else:
        return valor


def traduz_nomes_colunas(dataFrame):
    VOCABULARIO = {'nu_rip': 'RIP', 'nu_resp': 'Número do Responsável',
                   'no_resp': 'Nome do Responsável', 'sg_uf': 'UF',
                   'no_mun': 'Município', 'ed_tipo_logr': 'Tipo de Logradouro',
                   'ed_numero': 'Número', 'ed_complemento': 'Complemento',
                   'ed_bairro_distrito': 'Bairro', 'ed_cep': 'CEP',
                   'no_classe_imov': 'Classe do Imóvel',
                   'co_classe_imov': 'Classe do Imóvel', 'ed_logr': 'Endereço'}

    def pega_nomes_colunas(dataFrame):
        nome_colunas = dataFrame.columns
        return nome_colunas

    def traduz_nomes_colunas(nomes_colunas):
        traducao = None
        colunas_no_vocabulario = ([col for col in nomes_colunas if col
                                   in VOCABULARIO])
        if len(colunas_no_vocabulario) > 0:
            traducao = {}
            for coluna in colunas_no_vocabulario:
                traducao[coluna] = VOCABULARIO.pop(coluna)
        return traducao

    colunas_originais = pega_nomes_colunas(dataFrame)
    traducao = traduz_nomes_colunas(colunas_originais)

    dataFrameTraduzido = dataFrame.rename(columns=traducao)

    return dataFrameTraduzido


class SIAPA():
    def __init__(self):
        self.con = conecta_oltp()
        self.minAnoDtBase = 2007
        self.chunkSize = 50000
        self.gera_tabelas_dominio()

    @property
    def imoveis(self):
        colunas = ('nu_rip', 'nu_dpu', 'nu_resp',
                   'no_resp', 'co_classe_imov', 'co_situacao_imov',
                   'co_tipo_ocupacao', 'co_tipo_terreno', 'ed_tipo_logr',
                   'ed_logr', 'ed_numero', 'ed_complemento',
                   'ed_bairro_distrito', 'ed_cep', 'ed_mun', 'ed_numero_uf',
                   'nu_processo_adm_inclusao', 'op_fator_corretivo_total')

        dataFrame = carrega_tabela('siapa_a_imovel', self.con, colunas=colunas)
        return dataFrame

    @property
    def utilizacoes(self):
        colunas = ['nu_utiliz', 'nu_rip', 'da_inicio_utiliz',
                   'da_encerr_utiliz', 'co_estado_utiliz', 'co_regime_utiliz',
                   'mq_area_primitiva_utilizada', 'mq_area_uniao_utilizada']
        dataFrame = carrega_tabela('siapa_a_utilizacao', self.con,
                                   colunas=colunas)
        return dataFrame

    @property
    def responsaveis(self, calc_dv=False):
        ''' Calcula o dígito verificador utilizando a função do banco de dados
          se o paramêtro for verdadeiro '''
        if calc_dv is True:
            calc_dv_cpf = 'siapa.fn_calcula_dv_cpf(nu_basico_cpf_cgc)'
            calc_dv_cnpj = '''siapa.fn_calcula_dv_cnpj(RIGHT(nu_basico_cpf_cgc, 8)
                           || nu_ordem_cgc)'''
        else:
            calc_dv_cpf = 'nu_basico_cpf_cgc'
            calc_dv_cnpj = 'RIGHT(nu_basico_cpf_cgc, 8) || nu_ordem_cgc'

        colunas = ('nu_resp', 'no_resp', 'in_cpf_cgc',
                   '''CASE
                          WHEN in_cpf_cgc = '1' THEN {}
                          WHEN in_cpf_cgc = '2' THEN {}
                          ELSE NULL
                      END as nu_cpf_cgc'''.format(calc_dv_cpf,
                                                  calc_dv_cnpj),
                   'in_espolio_massa_falida')
        dataFrame = carrega_tabela('siapa_a_responsavel', self.con,
                                   colunas=colunas)
        return dataFrame

    @property
    def debitos(self):
        ''' Retorna generator da tabela de débitos dividido em self.chunSize
        partes '''

        # print('Relacionando débitos cujo ano da data base de cálculo é maior'
        #      ' ou igual a {}. Para alterar o ano a insira novo valor na'
        #      ' propriedade SIAPA.minAnoDtBase'.format(self.minAnoDtBase))
        assert self.chunkSize is not None
        chunkSize = self.chunkSize

        filtro = ("DATE_PART('YEAR', da_base_calculo) >= {}"
                  .format(self.minAnoDtBase))
        colunas = ('nu_debito', 'nu_rip', 'nu_utiliz',
                   'nu_resp_contraiu_debito', 'da_base_calculo',
                   'qt_cota_concedida', 'co_receita', 'co_situacao_debito',
                   'va_debito_total')

        dataFrame = carrega_tabela('siapa_a_debito', self.con,
                                   colunas=colunas, filtro=filtro,
                                   chunkSize=chunkSize)
        return dataFrame

    def pega_debitos(self, filtro_situacao=None, colunas=None):
        '''
        Retorna a tabela de débitos conforme o filtro de situação
        utilizado. Se o filtro não for fornecido gera erro evitando o
        travamento da máquina devido ao carregamento da tabela completa.

        :param filtro_situacao - Lista de códigos de situação do débito.
                                 Ex: ['01', '02']

        :param colunas - Lista contendo nomes das colunas para seleção
                         na query. Ex: ['nu_debito', 'va_debito_total']

        '''
        if filtro_situacao is None or filtro_situacao == []:
            raise ValueError('Parametro filtro_situacao não pode ser None '
                             'ou vazio.')

        assert self.chunkSize is not None
        chunkSize = self.chunkSize

        filtro = ("DATE_PART('YEAR', da_base_calculo) >= {}"
                  .format(self.minAnoDtBase))
        if filtro_situacao is not None:
            cod_situacao = ','.join("'" + situacao + "'" for situacao in filtro_situacao)
            filtro = filtro + (" AND co_situacao_debito IN (" + cod_situacao + ")")
            # não retorna chunks uma vez que o usuário realizou filtros
            chunkSize = None

        if colunas is None:
            colunas = ('nu_debito', 'nu_rip', 'nu_utiliz',
                       'nu_resp_contraiu_debito', 'da_base_calculo',
                       'qt_cota_concedida', 'co_receita',
                       'co_situacao_debito',
                       'va_debito_total')

        dataFrame = carrega_tabela('siapa_a_debito', self.con,
                                   colunas=colunas, filtro=filtro,
                                   chunkSize=chunkSize)
        return dataFrame

    @property
    def UF(self):
        UF = self.nu_uf
        UF['nu_dpu'] = UF['nu_uf'].map(lambda x: x + '0')
        UF['no_dpu'] = UF["nu_dpu"].map(lambda x: lista_uf[x])
        return UF

    def gera_tabelas_dominio(self):
        ''' Cria atributos de classe que retornam um DataFrame contento valores
        das tabelas de domínio do SIAPA. É gerado um atributo para cada item
        da lista tabelasDominio'''

        tabelasDominio = {'siapa_t_classe_imovel': 'co_classe_imov',
                          'siapa_t_dpu': 'nu_dpu',
                          'siapa_t_municipio': 'nu_mun',
                          'siapa_t_receita': 'co_receita',
                          'siapa_t_regime_utilizacao': 'co_regime_utiliz',
                          'siapa_t_situacao_debito': 'co_situacao_debito',
                          'siapa_t_situacaocred': 'co_situacao_cred',
                          'siapa_t_uf': 'nu_uf',
                          'siapa_t_unidadevalor': 'co_unid_valor'}

        # Cria o atributo utilizando o valor referente a tabela no dicionario
        for tab in tabelasDominio:
            nomeAtributo = tabelasDominio[tab]
            setattr(self, nomeAtributo, carrega_tabela(tab, self.con))
