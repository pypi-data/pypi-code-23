# -*- coding: utf-8 -*- #
"""
autor                   :   Marcos Felipe da Silva
versão atual            :   1.0
data da versão atual    :   20-02-2017
-----------------------------------------------------------------------
Notas de versão:

versão 1.0  :   20-02-2017 Classe pagina para retornar uma pagina html

------------------------------------------------------------------------

"""

## Classse Pagina usada para instanciar objetos pagina

class Pagina:
    __cabecalho = ''
    __rodape = ''
    __corpo = ''
    __pagina = 'Content-type: text/html;charset=utf-8;\n\n'
    __menu = ''
    def __init__(self, cabecalho, rodape, corpo = ''):
        self.__cabecalho += cabecalho
        self.__rodape = rodape
        self.__corpo = corpo
       
    def setMenuAdm(self, dicionario, usuario = ''):
        """ Recebe um dicionario e itera sobre as chaves para realizar a criação do menu dinâmico. O segundo parametro define o nome do usuario. """
        if not isinstance(dicionario, dict):
            return 'Erro, não é um dicionario'
        menu = "<nav class='navbar navbar-inverse'> \
        <div class='container-fluid'><div class='navbar-header'> \
        <button type='button' class='navbar-toggle' data-toggle='collapse' data-target='#myNavbar'> \
        <span class='icon-bar'></span><span class='icon-bar'></span><span class='icon-bar'></span> \
        </button></div><div  class='collapse navbar-collapse' id='myNavbar'><ul class='nav navbar-nav'> "
        ## Fazer a inclusao do menu dinamico que o usuario tem acesso
        for chave in sorted(dicionario.keys()):
            ## Verificando se o indice do dicionario tem 2 ou mais
            if len(dicionario[chave]) >= 2:
                menu += "<li class='dropdown'><a class='dropdown-toggle' data-toggle='dropdown' href='#'>%s<span class='caret'></span> \
                </a><ul class='dropdown-menu'>" % chave
            else:
                menu += dicionario[chave].pop()
                continue
            for link in dicionario[chave]:
                menu += str(link)
            menu += "</ul></li>"
    
        menu += "</ul><ul class='nav navbar-nav navbar-right'><li style='display: none'class='%s' id='baixar'><a href='#'><span class='text-danger glyphicon glyphicon-download-alt'></span> </a></li><li><a href='#'><span class='text-danger glyphicon glyphicon-user'> \
        </span> Olá %s </a></li><li><a href='altera_senha.html'> Alterar senha</a></li><li class='text-success'><a href='index.html' onclick='obterCookies();'> \
        <span class='text-danger glyphicon glyphicon-log-out'></span> Logout</a></li></ul></div></div></nav></div>" % (usuario, usuario)
        
        self.__menu = menu
    
    def setCorpo(self, corpo):
        self.__corpo = corpo

    def getPagina(self):
        '''Retorna a pagina do objeto Pagina. Com cabecalho, rodape e corpo '''
        if self.__cabecalho != '' and self.__rodape != '':
            try:
                cabe = open(self.__cabecalho, 'r', encoding = 'utf-8')
                for linha in cabe.readlines():
                    self.__pagina += linha
                cabe.close()
                #Gerando o menu em substituicao uma palavra chave
                self.__pagina = self.__pagina.replace('menu_lateral_13', self.__menu)
                # Gerando corpo
                self.__pagina += self.__corpo
                # Gerando o rodape
                roda = open(self.__rodape, encoding = 'utf-8')
                for linha in roda.readlines():
                    self.__pagina += linha
                    
                roda.close()
            except IOError as err:
                print('Erro de arquivo: %s' % str(err))
            
            return (self.__pagina)
        else:
            return None

## Classe utilizada para criar divs no sistema de grid utilizado Pelo Bootstrap.
## Limite maximo de grids é igual á 12
class DivRow():
    __conteudo = ''
    __livre = 0

    def __init__(self, livre = 12):
        '''Inicia um objeto div '''
        self.__livre = livre
    def addDiv(self, conteudo, tamanho, classe='', Identificador = ''):
        ''' Adiciona no container row outra div de tamanho informado. Tamanho nao pode ultrapassar o tamanho maximo'''
        # Verificacao do tamanho da div, se exceder o disponivel a div nao sera criada
        if self.__livre >= tamanho:
            ## Utilizando o tamanho para criar uma div com o conteudo informado e apendar em conteudo
            self.__conteudo += "<div class='col-sm-%d %s' id='%s'>%s</div>" % (int(tamanho), str(classe), str(Identificador), str(conteudo))
            self.__livre -= tamanho
        else:
            print('A div não pode ser inserida, seu tamanho excede os limites disponiveis')
        
    def getDivRow(self):
        '''Retorna a div formatada e completa'''
        compo = "<div class='row'>" + self.__conteudo + "</div>"
        return compo


## Retorna paragrafos
def para(conteudo = '', classe = '', Identificador = ''):
    '''Retorna um paragrafo para o codigo que o chamou'''
    return "<p class='%s' id='%s'>%s</p>" % (str(classe),
                                             str(Identificador), str(conteudo))
## Retorna titulos
def titulo(conteudo = '', tam = 1 ,classe = '', iDentificador = ''):
    '''Retorna um titulo para o codigo que o chamou'''
    return "<h%d class='%s' id='%s'>%s</h%d>" % (tam, str(classe),
                                                 str(iDentificador), str(conteudo), tam)
## Retorna divs
def div(conteudo = '', classe = '', Identificador = ''):
    '''Retorna uma div utilizando as classes e ids informados pelo usuario '''
    return "<div class='%s' id='%s'>%s</div>" % (str(classe),
                                                 str(Identificador), str(conteudo))
## Retorna tags img para imagens
def img(local, alt = '', classe= '', Identificador = ''):
    ''' Retorna uma tag img. Obrigatorio enviar o caminho da imagem'''
    return "<img src='%s' alt='%s' class='%s' id='%s' />" % (str(local),
                                                             str(alt), str(classe), str(Identificador))
## Retorna botoes
def button(conteudo, classe = '', Identificador = '', atrPersonalizado = ''):
    '''Retorna uma tag button o ultimo parametro disponibiliza a possibilidade de criar atributos personalizados'''
    return "<button class='btn %s' id='%s' %s >%s</button>" % (str(classe),
                                                               str(Identificador), str(atrPersonalizado) ,str(conteudo))
## Retorna um link
def link(link, nome,  classe = '', Identificador = '', atrPersonalizado = ''):
    '''Retorna uma tag link (tag a) para o sistema '''
    return "<a href='%s' class='%s' id='%s' %s>%s</a>" % (str(link), str(classe),
                                                          str(Identificador), str(atrPersonalizado), str(nome))
## Retorna uma tag script
def script(link):
    '''Retorna uma tag script com o caminho de um arquivo js externo'''
    return "<script type=text/javascript src='%s'></script>" % link

## Retorna um campo de entrada para ser inserido dados para o usuario
def entrada(tipo, variavel, valor = '', classe = '', Identificador = '', nome = '', atrPersonalizado = ''):
    ''' Cria um campo de entrada personalizado para ser usado nos formularios '''
    return "<div class='form-group'>%s<input type='%s' name='%s' value='%s' class='form-control %s' id='%s' %s /></div>" % (str(nome), str(tipo), str(variavel), str(valor), str(classe),
                                                                             str(Identificador), str(atrPersonalizado))
## Retorna um checkbox para o usuario
def checkBox(nome, variavel, valor='', classe = '', Identificador = ''):
    '''Retorna um checkbox '''
    return "%s <input type='checkbox' name='%s' value='%s' class='%s', id='%s' /><br/>" % (str(nome), str(variavel), str(valor), str(classe),
                                                                             str(Identificador))
## Retorna um campo select normal
def selecao(nome, variavel, dicionario, classe = '', Identificador = ''):
    ''' Retorna um select usando o dicionario. O campo value é preenchido com o valor e prefixado pela chave'''
    sele = "<div>%s<select name='%s' class='form-control %s' id='%s'>" % (nome, variavel, classe, Identificador)
    opt = "<option value='%s'>%s</option>"
    for key in sorted(dicionario.keys()):
        sele += opt % (str(dicionario[key]), str(key))
    sele += "</select></div>"
    return sele

## Retorna um campo com select com selecionaveis personalizados
def selecaoPer(nome, variavel, lista, listaSelecionados = [], classe = '', Identificador = 'lojas', uni = False):
    '''
    Recebe Um nome Para o campo, o nome da variavel e uma lista com numeros das filiais. Esta lista é selecionavel
    e as filiais selecionadas no formulario antigo são marcadas de uma vez neste.
    
    Retorna um campo de seleção com os selecionaveis disponiveis todas as vezes que o selecionador for escolhido
    '''
    sele = "%s<select name='grupos' multiple class='form-control %s' id='%s'>" % (str(nome), str(classe), str(Identificador))
    filiais = ''
    selecionados = 'selected'
    if not isinstance(lista, list):
        return 'Não é uma lista'
    opt = "<option %s value='%s'>%s</option>"
    for item in lista:
        if item in listaSelecionados:
            sele += opt % (selecionados, str(item), str(item[0:17]))
        else:
            sele += opt % ('', str(item), str(item[0:17]))
        filiais += str(item)+","
    # Se nao quiser que os acessos sejam individuais uni deve ser False
    if not uni:
        optTodas = "<option %s value=\"%s\">%s</option>"
        if 'Todas' in listaSelecionados:
            sele += optTodas % (selecionados, filiais[:-1], 'Todas')
        else:
            sele += optTodas % ('', filiais[:-1], 'Todas')
    else:
        sele = sele.replace('multiple', '')

    sele += "</select>"
    return sele



### Define uma classe chamada Tabela. Esta classe lida com a formatacao de uma tabela completa em html.
class Tabela:
    __cabecalho = ''
    __corpo = ''
    __rodape = ''

    def __init__(self, cabecalho, corpo = [()], rodape = ''):
        """Define uma classe que cria tabelas de dados. O unico parametro solicitado é o cabecalho que deve ser uma lista simples. """
        self.setCabecalho(cabecalho)
        self.setRodape(rodape)
        self.setCorpo(corpo)

    def getCabecalho(self):
        '''Retorna os dados do cabecalho '''
        return self.__cabecalho

    def getRodape(self):
        '''Retorna todos os dados do rodape '''
        return self.__rodape

    def getCorpo(self):
        '''Retorna todos os dados do corpo '''
        return self.__corpo

    def setCorpo(self, corpo):
        '''Recebe uma lista com tuplas aninhadas para armazenar o corpo das tabelas
        Formato do que o corpo deve receber : [('item','item'),('item2','item2')]
        self.setCorpo([('item','item'),('item2','item2')])
        '''
        if isinstance(corpo, list):
            for item in corpo:
                if isinstance(item, tuple):
                    if len(item) == len(self.__cabecalho):
                        continue
                    else:
                        return 'Existem mais itens por linha no corpo do que no cabecalho'
                else:
                    return 'Os dados nao estao dentro de uma tupla'
        else:
            return 'O que você quer definir como corpo nem mesmo é uma lista'

        self.__corpo = corpo

    def setCabecalho(self, cabecalho):
        ''' Define um cabecalho para a tabela.'''
        if isinstance(cabecalho, list):
            self.__cabecalho = cabecalho
        else:
            return 'O cabecalho da tabela nao e uma lista'

    def setRodape(self, rodape):
        ''' Define um rodape para a tabela.'''
        if isinstance(rodape, list):
            self.__rodape = rodape
        else:
            return 'O rodape nao foi enviado como uma lista'

    def getTabela(self):
        '''Retorna uma tabela HTML se todos os dados estiverem nos conformes '''
        if isinstance(self.__corpo, list) and isinstance(self.__cabecalho, list) and isinstance(self.__rodape, list):
            ##Criando uma string com composicao de 3 itens, cabecalho, corpo e rodape
            tab = "<div class='table table-responsive small'><table class='minhaTabela table text-center table-bordered table-responsive small' id='minhaTabela'><thead><tr class='info'>%s</tr></thead><tbody>%s</tbody><tfoot><tr class='info'>%s</tr></tfoot></table></div>"
            # Gerando cabecalho
            tcabe = "<th>%s</th>"
            cabe = ''
            for item in self.getCabecalho():
                cabe +=  tcabe % item
            ## Gerando o corpo da tabela
            tcorpo = "<td>%s</td>"
            corpo = ''
            for reg in self.getCorpo():
                corpo += "<tr>"
                for item in reg:
                    corpo += tcorpo % item
                corpo += "</tr>"
            ## Finalmente, gerando o rodape
            trodape = "<td>%s</td>"
            roda = ''
            for item in self.getRodape():
                roda += trodape % item

            tab = tab % (cabe, corpo, roda)
            return tab
        else:
            return 'Um dos itens não esta em conformidade com itens das tabelas'
        

## Retorna uma tag script com dados dentro da tag, ao inves de gerir um arquivo cria uma tag com valores a serem inseridos dentro
def tagScript(conteudo = ''):
    ''' Retorna uma tag script com o conteudo desejado dentro dela'''
    tag = "<script type=text/javascript>%s</script>" % conteudo
    return tag

## Classe para criar graficos
class Grafico:
    __opcoes = {}
    __dados = []
    __tipo = {'pizza':'PieChart', 'barra':'BarChart', 'coluna':'ColumnChart', 'linha':'LineChart'}

    def __init__(self, dados, opcoes = {}):
        '''Cria uma tag script para o grafico de pizza e retorna esta tag totalmente formatada para uso no javascript '''
        self.__setDados(dados)
        self.__setOpcoes(opcoes)

    def __setDados(self, dados):
        ''' Recebe os dados como uma lista bidimensional para criacao do grafico de pizza '''
        if isinstance(dados, list):
            for item in dados:
                if isinstance(item, list) and len(item) >= 2:
                    continue
                else:
                    return 'Não é uma lista bidimensional ou a quantidade da lista interna não é igual maior á 2'
        else:
            return 'Isto não é nem mesmo uma lista'

        self.__dados = dados

    def __setOpcoes(self, opcoes):
        ''' Verifica se os dados lancados sao como um dicionario e entao os atribui em opcoes'''
        if isinstance(opcoes, dict):
            self.__opcoes = opcoes
        else:
            return 'Os dados enviados nao sao um dicionario'

    def getGrafico(self, div, tipo = 'pizza', funcao = 'drawChart'):
        ''' Retorna uma funcao para ser usada na geracao de graficos.
        O tipo do grafico deve ser enviado assim como o id da div e o nome da funcao que se deseja retornar.
        Tipos de dados conhecidos:
        pizza, barra. O padrao é enviar um grafico de pizza
        O id da div deve ser informado corretamente senão o grafico nao sera criado.
        O nome da funcao tambem deve ser passado, caso nenhum seja passado a funcao se chamara drawChart

        '''
        dados = " google.charts.setOnLoadCallback(%s); \
        function %s() { var data = new google.visualization.arrayToDataTable(" % (funcao, funcao)
          
        dados += str(self.__dados)
        dados += """);
        // Set chart options
        var options = """ 
        dados += str(self.__opcoes) +";"

        dados += """
        // Inicializando um objeto pizza na funcao. Funcao esta para ser usada na criacao do grafico em uma div pizza
        var chart = new google.visualization.%s(document.getElementById('%s'));
        chart.draw(data, options);
        } """ % (self.__tipo[tipo], div)

        return dados
