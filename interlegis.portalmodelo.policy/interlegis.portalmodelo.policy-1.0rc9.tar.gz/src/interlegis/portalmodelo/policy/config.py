# -*- coding:utf-8 -*-
from interlegis.portalmodelo.policy.utils import _add_id
from StringIO import StringIO

import os

PROJECTNAME = 'interlegis.portalmodelo.policy'
PROFILE_ID = '{0}:default'.format(PROJECTNAME)

# content created at Plone's installation
DEFAULT_CONTENT = ('front-page', 'news', 'events', 'Members')

NEWS_DESCRIPTION = u'Este é um exemplo de notícia que pode ser criado e publicado no Portal Modelo. Você pode excluí-la e criar suas próprias notícias. Divirta-se! ;-)'
NEWS_TEXT = u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no site, e clicar na aba <em><a href="edit">Edição</a></em>, que fica logo acima do título da notícia, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta notícia está dentro da pasta <em>notícias</em> e foi criada como exemplo, logo, pode ser excluída. Dentro desta pasta você pode criar outras notícias através do menu <em>Adicionar item...</em>, e então publicá-as através do menu <em>Estado</em>. Elas irão aparecer automaticamente na página inicial do site e você poderá selecionar as notícias de destaque no carrossel da página inicial, clicando a aba <em>Compor</em> e arrastando-as para o carrossel.</p>'
VIDEO_TEXT = u'<p>O programa mensal mostra a repercussão de assuntos locais no Congresso Nacional e como as decisões do Legislativo impactam o dia a dia dos cidadãos. Com linguagem informal, o programa apresenta notícias, projetos, debates, serviços e um pouco de história dos 5.570 municípios brasileiros.</p>'
HOME_TILE_TEXT = u'<h2>Nossos Parlamentares</h2><div class="tile-parlamentares"><ul><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Carlos Drummond de Andrade" class="image-inline" src="imagens/carlos-drummond-de-andrade.jpg/image_tile" /><br />Carlos Drummond</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto da Clarice Lispector" class="image-inline" src="imagens/clarice-lispector.jpg/image_tile" /><br />Clarice Lispector</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Érico Veríssimo" class="image-inline" src="imagens/erico-verissimo.jpg/image_tile" /><br />Érico Veríssimo</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Euclides da Cunha" class="image-inline" src="imagens/euclides-da-cunha.jpg/image_tile" /><br />Euclides da Cunha</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Gilberto Freyre" class="image-inline" src="imagens/gilberto-freyre.jpg/image_tile" /><br />Gilberto Freyre</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Guimarães Rosa" class="image-inline" src="imagens/guimaraes-rosa.jpg/image_tile" /><br />Guimarães Rosa</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Jorge Amado" class="image-inline" src="imagens/jorge-amado.jpg/image_tile" /><br />Jorge Amado</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Machado de Assis" class="image-inline" src="imagens/machado-de-assis.jpg/image_tile" /><br />Machado de Assis</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Monteiro Lobato" class="image-inline" src="imagens/monteiro-lobato.jpg/image_tile" /><br />Monteiro Lobato</a></li><li><a href="processo-legislativo/parlamentares"><img alt="Foto do Parlamentar" class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" /><br />Rui Barbosa</a></li></ul></div>'
HOME_TILE_TEXT_NOTICE = u'<h2>Notas Importantes</h2><h3>Transparência no Portal</h3><p>Informações sobre transparência são constantemente auditadas pelos TCEs dos estados. Para estar conforme a <a href="http://www.acessoainformacao.gov.br/assuntos/conheca-seu-direito/a-lei-de-acesso-a-informacao">Lei de Acesso à Informação</a>, deve-se levar em consideração alguns requisitos:</p><ul><li><strong><a href="ouvidoria">Ouvidoria</a></strong>: canal de participação popular que não deve ser excluído ou o seu estado colocado como "privado".</li><li><strong>Ouvidoria X E-SIC</strong>: a Ouvidoria do portal possui opção de "<strong>Pedido de Acesso à Informação</strong>" no formulário de solicitação, sendo assim, não necessita de uma ferramenta específica de E-SIC.</li><li><strong><a href="faq"> Perguntas Frequentes (FAQ)</a></strong>: a página não deve ser excluída ou o seu estado colocado como "privado", nem estar vazia. Deve conter perguntas e repostas relevantes para a população, como, por exemplo, horário de funcionamento, telefones úteis, como funcionam comissões, votações, etc.</li><li><a class="internal-link" href="resolveuid/89bbc364371b493e8d818a88f76aba84" target="_self" title=""><strong>Transparência</strong></a>: não deve ser excluída ou seu estado colocado como "privado".</li><ul><li><strong>Orçamentos e Finanças</strong>: deve conter um histórico com tabelas anteriores para comparação.</li><li><strong>Licitações e Contratos</strong>: deve conter arquivos e caso não tenha havido licitações e contratos recentemente, colocar mensagem informando que naquele mês/ano não foram realizadas licitações/contratos, não deixando a área vazia.</li><li><strong>Recursos Humanos</strong>: deve conter planilha com informações funcionais.</li><li><strong>Parlamentares e Gabinetes</strong>: deve conter informações sobre diárias, passagens e caso não tenha havido nenhuma despesa parlamentar recentemente, colocar mensagem informando que naquele mês/ano não foram realizadas despesas, não deixando a área vazia.</li><li><strong>Atos Administrativos</strong>: documentos referentes à atividade administrativa.</li><li><strong>Dados Abertos</strong>: dados do portal disponibilizados para análise.</li></ul></ul><h3>Ajuda</h3><p>No portal há um link para a <a class="external-link" href="http:// https//portal.tce.rs.gov.br/portal/page/portal/tcers/publicacoes/orientacoes_gestores/acesso_informacao_pratica.pdf" target="_self" title="Cartilha de boas práticas">cartilha de boas práticas do TCE/RS</a>, com dicas do que publicar no portal.</p><p>Também é disponibilizado um <a class="external-link" href="http://colab.interlegis.leg.br/raw-attachment/wiki/ProjetoPortalModelo/ManualPortalModelo3.pdf" target="_self" title="Manual de uso do Portal">manual de gerenciamento</a> do portal.</p><p><strong>ESTE ITEM DEVE SER REMOVIDO DA CAPA ANTES DO PORTAL SER PUBLICADO.</strong></p>'
HOME_TILE_EMBED1 = u'<iframe width="320" height="180" src="https://www.youtube.com/embed/yjPwZ5rQ4RU?rel=0&amp;controls=0&amp;showinfo=0" frameborder="0" allowfullscreen></iframe>'
HOME_TILE_EMBED2 = u'<iframe width="320" height="180" src="https://www.youtube.com/embed/IgswW4Z4WLg?rel=0&amp;controls=0&amp;showinfo=0" frameborder="0" allowfullscreen></iframe>'
HOME_TILE_BANNER_URL = u'http://www.interlegis.leg.br/solucaoweb'
CREATORS = (u'Interlegis', )

IMAGE1 = open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'congresso-nacional.jpg')).read()
IMAGE2 = open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'plenario-senado.jpg')).read()
IMAGE3 = open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'bandeira-brasil.jpg')).read()
IMAGE4 = open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'plenario-camara.jpg')).read()
VIDEO1 = StringIO(open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'campanha-legbr.mp4')).read())
VIDEO2 = StringIO(open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'solucao-web-interlegis.mp4')).read())
AUDIO1 = StringIO(open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'campanha-legbr.mp3')).read())
AUDIO2 = StringIO(open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'solucao-web-interlegis.mp3')).read())

# new site structure; this dictionary defines the objects that are going to be
# created on the root of the site; it also includes information about folder
# constraints and objects to be created inside them
SITE_STRUCTURE = [
    dict(
        type='collective.cover.content',
        id='front-page',
        title=u'Página Inicial',
        description=u'Objeto que compõem a página inicial do site. (atenção: este objeto não deve ser excluído)',
        template_layout='Portal Modelo',
        excludeFromNav=True,
    ),
    dict(
        type='Document',
        id='footer-page',
        title=u'Rodapé do Portal',
        description=u'Conteúdo editável do rodapé do site. (atenção: este objeto não deve ser excluído e nem tornado privado)',
        text=u'<table class="invisible"><tbody><tr><th style="text-align:left">Institucional</th><th style="text-align:left">Atividade Legislativa</th><th style="text-align:left">Serviços</th><th style="text-align:left">Atendimento</th></tr><tr><td><ul><li><a href="institucional/acesso">Acesso</a></li><li><a href="institucional/historia">História</a></li><li><a href="institucional/funcao-e-definicao">Função e Definição</a></li><li><a href="institucional/estrutura">Estrutura</a></li><li><a href="institucional/noticias">Notícias</a></li><li><a href="institucional/eventos/event_listing">Eventos</a></li></ul></td><td><ul><li><a href="processo-legislativo/parlamentares">Parlamentares</a></li><li><a href="processo-legislativo/legislaturas">Legislaturas</a></li><li><a href="processo-legislativo/@@mesa-diretora">Mesa Diretora</a></li><li><a href="processo-legislativo/comissoes">Comissões</a></li><li><a href="institucional/regimento-interno">Regimento Interno</a></li><li><a href="leis/lei-organica-municipal">Lei Orgância Municipal</a></li><li><a href="leis/legislacao-municipal">Legislação Municipal</a></li></ul></td><td><ul><li><a href="transparencia">Transparência</a></li><li><a href="ouvidoria">e-SIC</a></li><li><a href="transparencia/dados-abertos">Dados Abertos</a></li><li><a href="boletins">Boletim Informativo</a></li><li><a href="faq">FAQ</a></li><li><a href="rss-info">RSS</a></li></ul></td><td><address>Endereço da Casa Legislativa, nº do prédio<br />Município, UF &#8212; CEP: 12345-678<br />CNPJ: 00.000.000/0001-00<br />Fone: +55 12 3456-7890 &#8212; Fax: +55 09 8765-4321<br />E-mail: <a href="mailto:atendimento@dominio.leg.br">atendimento@dominio.leg.br</a></address><br /><br /><strong>Expediente</strong><br /><br />De segunda-feira a sexta-feira:<br />&#8226; manhã das 8hs às 12hs<br />&#8226; tarde das 14hs às 18hs</td></tr></tbody></table>',
        excludeFromNav=True,
    ),
    dict(
        type='Folder',
        id='institucional',
        title=u'Sobre a Câmara',
        description=u'Seção que contém as informações básicas relacionadas à Casa Legislativa, como sua história, estrutura, eventos e notícias.',
        excludeFromNav=True,
        _addable_types=['Folder', 'FormFolder', 'File', 'Link', 'Document', 'Window'],
        _children=[
            dict(
                type='Folder',
                title=u'Acesso',
                description=u'Informações gerais de como interagir com a Casa Legislativa, presencialmente ou por qualquer meio de comunicação, tais como, fotos da sede, mapa de como chegar, endereço completo, horários de atendimento, telefones de contato, endereços de e-mail relevantes, links para serviços e o que mais for importante.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'Acesso',
                        description=u'Informações gerais de como interagir com a Casa Legislativa, presencialmente ou por qualquer meio de comunicação, tais como, fotos da sede, mapa de como chegar, endereço completo, horários de atendimento, telefones de contato, endereços de e-mail relevantes, links para serviços e o que mais for importante.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no site, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar informações gerais de como interagir com a Casa Legislativa, presencialmente ou por qualquer meio de comunicação, tais como, fotos da sede, mapa de como chegar, endereço completo, horários de atendimento, telefones de contato, endereços de e-mail relevantes, links para serviços e o que mais for importante.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'História',
                description=u'Textos sobre a história da Casa Legislativa, desde sua criação, bem como, fotos, vídeos, áudios, entre outros.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'História',
                        description=u'Textos sobre a história da Casa Legislativa, desde sua criação, bem como, fotos, vídeos, áudios, entre outras.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no site, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar textos sobre a história da Casa Legislativa, desde sua criação, bem como, fotos, vídeos, áudios, etc, que permitam às pessoas conhecer o seu legislativo.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Função e Definição',
                description=u'Informações sobre as funções da Casa Legislativa e definições sobre como ela funciona, bem como, sobre o Processo Legislativo, plenário, número de parlamentares, entre outras.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'Função e Definição',
                        description=u'Informações sobre as funções da Casa Legislativa e definições sobre como ela funciona, bem como, sobre o Processo Legislativo, plenário, número de parlamentares, entre outras.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no site, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar informações sobre as funções da Casa Legislativa e definições sobre como ela funciona, bem como, sobre o Processo Legislativo, plenário, número de parlamentares, etc.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Estrutura',
                description=u'Informações sobre a estrutura organizacional da Casa Legislativa, tais como, organograma, setores, chefias e responsáveis com fotos e seus respectivos contatos.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'Estrutura',
                        description=u'Informações sobre a estrutura organizacional da Casa Legislativa, tais como, organograma, setores, chefias e responsáveis com fotos e seus respectivos contatos.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no site, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar informações sobre a estrutura organizacional da Casa Legislativa, tais como, organograma, setores, chefias e responsáveis com fotos e seus contatos, para que os cidadãos os conheçam e possam contactá-los.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Regimento Interno',
                description=u'Regimento Interno atualizado, que rege o seu funcionamento da Casa Legislativa e do Processo Legislativo.',
            ),
            dict(
                type='Folder',
                title=u'Notícias',
                description=u'Banco de notícias desta Casa Legislativa.',
                _addable_types=['Collection', 'Folder', 'News Item'],
                _children=[
                    dict(
                        type='Collection',
                        id='agregador',
                        title=u'Notícias',
                        description=u'Banco de notícias desta Casa Legislativa.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v='News Item',
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                    dict(
                        type='News Item',
                        title=u'Primeira Notícia',
                        description=NEWS_DESCRIPTION,
                        text=NEWS_TEXT,
                        image=IMAGE1,
                    ),
                    dict(
                        type='News Item',
                        title=u'Segunda Notícia',
                        description=NEWS_DESCRIPTION,
                        text=NEWS_TEXT,
                        image=IMAGE2,
                    ),
                    dict(
                        type='News Item',
                        title=u'Terceira Notícia',
                        description=NEWS_DESCRIPTION,
                        text=NEWS_TEXT,
                        image=IMAGE3,
                    ),
                    dict(
                        type='News Item',
                        title=u'Quarta Notícia',
                        description=NEWS_DESCRIPTION,
                        text=NEWS_TEXT,
                        image=IMAGE4,
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Clipping',
                description=u'Coleção de notícias publicadas por terceiros, relacionadas a esta Casa Legislativa.',
                _addable_types=['Collection', 'Folder', 'Link', 'News Item'],
                _children=[
                    dict(
                        type='Collection',
                        id='agregador',
                        title=u'Clipping',
                        description=u'Coleção de notícias publicadas por terceiros, relacionadas a esta Casa Legislativa.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v='News Item',
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                ],
            ),
            dict(
                type='Folder',
                id='eventos',
                title=u'Agenda de Eventos',
                description=u'Calendário de eventos ocorridos nesta Casa Legislativa ou acontecimentos relevantes que tenham participação de parlamentares, funcionários, cidadãos em destaque, entre outros.',
                _addable_types=['Collection', 'Event', 'Folder'],
                _layout='solgemafullcalendar_view',
                _children=[
                    dict(
                        type='Event',
                        title=u'1º Ano do Site',
                        description=u'Aniversário de primeiro ano do site desta Casa Legislativa. (este evento é um conteúdo de exemplo e pode ser removido)',
                        text=u'<strong>Parabéns para esta Casa Legislativa!</strong><p>Já passou um ano desde a disponibilização do seu <a href="http://www.interlegis.leg.br/solucaoweb">Portal Modelo</a> na web. Isso significa mais transparência, diálogo com os cidadãos, aderência às leis nacionais e padrões internacionais. Veja por que é importante utilizar o portal:</p><iframe src="http://www.youtube.com/embed/D_Sm7R1yY8g?feature=oembed" width="400" height="300" allowfullscreen="" frameborder="0"></iframe>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                id='fotos',
                title=u'Galeria de Fotos',
                description=u'Galeria de fotos da Casa Legislativa, sessões, parlamentares, funcionários, eventos ocorridos, cidadãos colaboradores, entre outros.',
                _addable_types=['Image', 'Folder'],
                _layout='galleryview',
                #_children=[
                #    dict(
                #        type='Collection',
                #        title=u'Todas as Fotos',
                #        description=u'Lista de todas as fotos armazenadas dentro desta pasta.',
                #        sort_reversed=True,
                #        sort_on=u'effective',
                #        limit=1000,
                #        query=[
                #            dict(
                #                i='portal_type',
                #                o='plone.app.querystring.operation.selection.is',
                #                v=['Image', 'Link', 'sc.embedder'],
                #            ),
                #            dict(
                #                i='path',
                #                o='plone.app.querystring.operation.string.relativePath',
                #                v='../',
                #            ),
                #        ],
                #    ),
                #],
            ),
            dict(
                type='Folder',
                id='videos',
                title=u'Galeria de Vídeos',
                description=u'Acervo de vídeos da Casa Legislativa sobre eventos ocorridos, sessões legislativas, promocionais, informativos, entre outros, em formato MP4 e/ou streaming de serviços multimídia pela Internet.',
                _addable_types=['Collection', 'Folder', 'File', 'Link', 'sc.embedder'],
                _children=[
                    dict(
                        type='Collection',
                        id='agregador',
                        title=u'Galeria de Vídeos',
                        description=u'Acervo de vídeos da Casa Legislativa sobre eventos ocorridos, sessões legislativas, promocionais, informativos, entre outros, em formato MP4 e/ou serviços de streaming de multimídia pela Internet.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v=['File', 'Link', 'sc.embedder'],
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                    dict(
                        type='Folder',
                        id='videoaulas',
                        title=u'Videoaulas de Portal Modelo',
                        description=u'Curso de Portal Modelo em formato de videoaulas que explicam como usar os principais recursos dessa ferramenta. (esta pasta é apenas uma referência, está privada e pode ser removida)',
                        _addable_types=['Link'],
                        _transition=None,
                        _layout='folder_tabular_view',
                        _children=[
                            dict(
                                type='Link',
                                title=u'Apresentação do portal',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=lxOxJoPR4iI',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Funções da barra de gestão de conteúdo',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=M9x1P2Oo9MI',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Tipos de conteúdo',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=Xy_fm9FEGio',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Edição e inserção de conteúdo',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=M3Yn1EXa6k4',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como criar pastas',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=7hk6G8H0TM4',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Adicionando uma subpasta',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=vniM-_wDsV0',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Adicionando uma página de conteúdo',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=qX2ZXnwZyWQ',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Inserindo uma tabela no texto',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=1HXhfXRPGRw',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como criar um link externo em uma palavra no conteúdo',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=Y70k2KwVRuM',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Inserindo notícias',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=fcSN3n0-qqA',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Apresentação das notícias',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=hHYgs0BfrCE',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Inserindo imagens',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=h8p-d8MEl2g',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Inserindo arquivos',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=oJ0V7sKluRs',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como adicionar um arquivo em formato PDF',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=z1sysHEld6w',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Inserindo múltiplos arquivos em lote',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=V_orVJDFUzY',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Inserindo eventos na agenda',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=Wpul5HvW32s',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Inserindo um conteúdo link',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=P3Gh2neJ7kI',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Adicionando uma enquete',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=ihcVlF05M-A',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Embutindo multimídia',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=bW2wuxJGpGc',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Gerenciando coleções',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=ss2vYlI8LqE',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Alterando o nome curto (ID) de um conteúdo',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=Dj-M6VRBUmA',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como alterar a ordem dos itens da pasta',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=ALiH-P2JkZE',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Alterando a visão de uma pasta',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=GpnjV5B-SR0',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Configurações do cabeçalho',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=xf1SbM6jc0o',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como editar o cabeçalho do site',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=6yJqVee53m8',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como editar o rodapé do site',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=7XCgu4bmhzA',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Layout da página inicial',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=lAXwLxhC5t8',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como gerenciar os portlets',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=9eNdvfhCs5E',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                            dict(
                                type='Link',
                                title=u'Como alterar o tema (layout) do site',
                                description=u'Vídeoaula sobre o Portal Modelo feita pelo Instituto Legislativo Brasileiro e hospedada no YouTube. (este link é um conteúdo de exemplo e pode ser removido)',
                                excludeFromNav=True,
                                remoteUrl='https://www.youtube.com/watch?v=R9SA7Rh6HB4',
                                _transition=None,
                                _layout='link_oembed_view',
                            ),
                        ],
                    ),
                    dict(
                        type='Link',
                        title=u'Adesão à Rede Legislativa de TV e Rádio',
                        description=u'Link para a página do projeto da Câmara dos Deputados que informa como as Casas Legislativas podem aderir à Rede Legislativa de TV Digital. (este link é apenas informativo, está privado e deve ser removido)',
                        remoteUrl='http://www2.camara.leg.br/comunicacao/rede-legislativa-radio-tv',
                        _transition=None,
                    ),
                    dict(
                        type='Link',
                        title=u'Rede Legislativa de TV Digital',
                        description=u'Vídeo em formato MP4 e hospedado pelo Interlegis, feito pela Câmara Municipal de São Paulo, que informa sobre o projeto da Câmara dos Deputados para disponibilizar canais de TV digital para as Casas Legislativas Brasileiras. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='http://arquivos.interlegis.leg.br/interlegis/video/rede-legislativa-de-tv-digital.mp4',
                    ),
                    dict(
                        type='Link',
                        title=u'Domínio .leg.br',
                        description=u'Vídeo em formato MP4 e hospedado pelo Interlegis, que informa sobre o domínio do legislativo brasileiro .leg.br. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='http://ftp.interlegis.gov.br/interlegis/video/dominio-legbr.mp4',
                    ),
                    dict(
                        type='Link',
                        title=u'O Portal para o Legislativo Brasileiro',
                        description=u'Vídeo hospedado no YouTube, feito pelo programa Município Brasil da TV Senado, falando sobre a ferramenta feita pelo Interlegis que oferece sites com tecnologias abertas e sem custos para as Casas Legislativas Brasileiras. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='https://www.youtube.com/watch?v=f1vAZ5cp-sc',
                        _layout='folder_summary_view',
                    ),
                    dict(
                        type='Link',
                        id='portal-modelo-proporciona-transparencia',
                        title=u'Portal Modelo Proporciona Transparência para o Legislativo',
                        description=u'Vídeo hospedado no YouTube, feito pelo Instituto Legislativo Brasileiro, explicando as possibilidades de uso do Portal Modelo em relação à Lei de Acesso à Informação e Lei de Responsabilidade Fiscal. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='https://www.youtube.com/watch?v=E6tSSVRMejA',
                        _layout='link_oembed_view',
                    ),
                    dict(
                        type='sc.embedder',
                        title=u'Por que utilizar o Portal Modelo?',
                        description=u'Vídeo hospedado no Vimeo sobre as exigências da Lei da Transparência e os benefícios no uso gratuito do Portal Modelo pelas Casas Legislativas Brasileiras para cumprir a legislação. (este embedder é um conteúdo de exemplo e pode ser removido)',
                        url=u'https://vimeo.com/123851431',
                        embed_html=u'<iframe src="https://player.vimeo.com/video/123851431?title=0&byline=0" width="500" height="375" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
                        width=500,
                        height=375,
                    ),
                    dict(
                        type='sc.embedder',
                        title=u'Município Brasil',
                        description=u'O programa Município Brasil é desenvolvido pela TV Senado e conta com a participação das Casas Legislativas Brasileiras. (este embedder é um conteúdo de exemplo e pode ser removido)',
                        url=u'https://www.youtube.com/watch?v=Sll8S1_ksfU',
                        embed_html=u'<iframe width="459" height="344" src="http://www.youtube.com/embed/Sll8S1_ksfU?feature=oembed" frameborder="0" allowfullscreen></iframe>',
                        width=459,
                        height=344,
                    ),
                    dict(
                        type='File',
                        id='solucao-web-interlegis.mp4',
                        title=u'Todas as Casas Legislativas podem ter um site na Internet',
                        description=u'Arquivo em formato MP4 hospedado localmente neste site sobre a campanha da Solução Web Interlegis que visa disponibilizar gratuitamente um site para cada Câmara Municipal que ainda não possui. (este arquivo é um conteúdo de exemplo e pode ser removido)',
                        file=VIDEO2,
                        _layout='flowplayer',
                    ),
                    dict(
                        type='File',
                        id='campanha-legbr.mp4',
                        title=u'Como acessar os sites do Legislativo',
                        description=u'Arquivo em formato MP4 hospedado localmente neste site com a campanha para informar os cidadãos sobre como usar o domínio do legislativo brasileiro .leg.br para acessar os sites do poder legislativo. (este arquivo é um conteúdo de exemplo e pode ser removido)',
                        file=VIDEO1,
                        _layout='flowplayer',
                    ),
                ],
            ),
            dict(
                type='Folder',
                id='audios',
                title=u'Galeria de Áudios',
                description=u'Acervo de áudios e podcasts da Casa Legislativa sobre eventos ocorridos, sessões legislativas, promocionais, informativos, entre outros, em formato MP3 e/ou algum serviço de streaming de som pela Internet.',
                _addable_types=['Collection', 'Folder', 'File', 'Link', 'sc.embedder'],
                _layout='flowplayer',
                _children=[
                    dict(
                        type='Collection',
                        title=u'Todos os Áudios',
                        description=u'Lista de todos os áudios armazenados dentro desta pasta.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v=['File', 'Link', 'sc.embedder'],
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                    dict(
                        type='File',
                        id='campanha-legbr.mp3',
                        title=u'Campanha para o cidadão usar o domínio leg.br',
                        description=u'Arquivo em formato MP3 hospedado localmente neste site sobre a campanha para orientar os cidadãos a usar o domínio do legislativo brasileiro na internet. (este arquivo é um conteúdo de exemplo e pode ser removido)',
                        file=AUDIO1,
                        _layout='flowplayer',
                    ),
                    dict(
                        type='File',
                        id='solucao-web-interlegis.mp3',
                        title=u'Solução Web Interlegis',
                        description=u'Arquivo em formato MP3 hospedado localmente neste site sobre a campanha da Solução Web Interlegis que visa disponibilizar gratuitamente um site para cada Câmara Municipal que ainda não possui. (este arquivo é um conteúdo de exemplo e pode ser removido)',
                        file=AUDIO2,
                        _layout='flowplayer',
                    ),
                    dict(
                        type='Link',
                        title=u'Sobre o domínio .leg.br',
                        description=u'Link para o áudio em formato MP3 sobre o domínio do legislativo brasileiro. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='http://arquivos.interlegis.leg.br/interlegis/audio/dominio-legbr.mp3',
                    ),
                    dict(
                        type='Link',
                        title=u'Hino Nacional Brasileiro',
                        description=u'Link para o áudio em formato MP3 do Hino Nacional Brasileiro. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='http://arquivos.interlegis.leg.br/interlegis/audio/hino-nacional-brasileiro.mp3',
                    ),
                ],
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Processo Legislativo',
        description=u'Seção que contém as informações relacionadas à atividade legislativa, parlamentares, legislatura atual e anteriores.',
        excludeFromNav=True,
        _addable_types=['Folder', 'File', 'Link', 'Document', 'Window'],
    ),
    dict(
        type='Folder',
        title=u'Leis',
        description=u'Seção que contém as leis válidas para o município, que poderão ser buscadas e acessadas pelos visitantes.',
        excludeFromNav=True,
        _addable_types=['Folder', 'File', 'Link', 'Document', 'Window'],
        _children=[
            dict(
                type='Folder',
                title=u'Lei Orgânica Municipal',
                description=u'Conteúdo atualizado da Lei Orgânica do Município.',
            ),
            dict(
                type='Folder',
                title=u'Legislação Municipal',
                description=u'Acervo com os textos integrais das normas jurídicas do município. (se a Casa Legislativa tiver um sistema de processo legislativo esta pasta pode ser substituída por um link)',
            ),
            dict(
                type='Link',
                title=u'Legislação Estadual',
                description=u'Link para o acervo de normas jurídicas do Estado.',
                remoteUrl='http://leis.al.uf.leg.br',
            ),
            dict(
                type='Link',
                title=u'Legislação Federal',
                description=u'Link para o acervo de normas jurídicas da República.',
                remoteUrl='http://www.planalto.gov.br/legislacao',
            ),
            dict(
                type='Link',
                title=u'Pesquisar no LexML',
                description=u'Link para a pesquisa LexML na legislação das três esferas (Municipal, Estadual e Federal) dos três poderes (Legislativo, Executivo e Judiciário).',
                remoteUrl='../lexml',
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Transparência',
        description=u'Seção que contém os dados relacionados a transparência da Casa Legislativa, como as prestações de contas, publicação de editais e licitações, formulários e links para o acesso à informação e atendimento ao cidadão.',
        excludeFromNav=True,
        _addable_types=['CSVData', 'Folder', 'File', 'Link', 'Document', 'Window'],
        _children=[
            dict(
                type='Document',
                id='pagina-padrao',
                title=u'Transparência',
                description=u'Seção que contém os dados relacionados a transparência da Casa Legislativa, como as prestações de contas, publicação de editais e licitações, formulários e links para o acesso à informação e atendimento ao cidadão.',
                text=u'<table class="invisible"><tbody><tr><td><p><a href="orcamento-e-financas"><img class="image-inline" src="../imagens/transparencia-orcamento.png" alt="Orçamento e Finanças" /></a></p><h3><a href="orcamento-e-financas">Orçamento e Finanças</a></h3><p>Receitas e despesas da Casa Legislativa, suprimento de fundos, relatórios de gestão fiscal e outros demonstrativos.</p></td><td><p><a href="licitacoes-e-contratos"><img class="image-inline" src="../imagens/transparencia-contratos.png" alt="Licitações e Contratos" /></a></p><h3><a href="licitacoes-e-contratos">Licitações e Contratos</a></h3><p>Informações relativas a todas as modalidades de licitação e contratos firmados pela Casa Legislativa.</p></td></tr><tr><td><p><a href="recursos-humanos"><img class="image-inline" src="../imagens/transparencia-pessoas.png" alt="Gestão de Pessoas" /></a></p><h3><a href="recursos-humanos">Gestão de Pessoas</a></h3><p>Informações sobre servidores ativos, aposentados, concursos, terceirizados, estagiários, pensionistas e colaboradores eventuais.</p></td><td><p><a href="parlamentares-e-gabinetes"><img class="image-inline" src="../imagens/transparencia-parlamentares.png" alt="Parlamentares e Gabinetes" /></a></p><h3><a href="parlamentares-e-gabinetes">Parlamentares e Gabinetes</a></h3><p>Informações sobre os recursos utilizados pelos parlamentares no exercício do mandato parlamentar.</p></td></tr><tr><td><p><a href="atos-administrativos"><img class="image-inline" src="../imagens/transparencia-administrativa.png" alt="Atos Administrativos" /></a></p><h3><a href="atos-administrativos">Atos Administrativos</a></h3><p>Dados sobre planejamento e gestão da Casa Legislativa, estrutura administrativa, boletim administrativo e demais atos administrativos.</p></td><td><p><a href="dados-abertos"><img class="image-inline" src="../imagens/transparencia-dados.png" alt="Dados Abertos" /></a></p><h3><a href="dados-abertos">Dados Abertos</a></h3><p>Informações em formato de dados abertos disponíveis neste site, utilizáveis por qualquer pessoa e processáveis por máquinas.</p></td></tr><tr><td><p><a href="acesso-a-informacao"><img class="image-inline" src="../imagens/transparencia-informacao.png" alt="Acesso à Informação / Ouvidoria / e-SIC" /></a></p><h3><a href="acesso-a-informacao">Acesso à Informação / e-SIC / Ouvidoria</a></h3><p>Se você deseja alguma informação que ainda não está publicada neste site, faça um <a href="../ouvidoria/++add++Claim?form.widgets.kind=pedido-de-acesso-a-informaassapso&amp;form.widgets.area=ouvidoria">pedido de acesso à informação</a>! Você também pode enviar outras <a href="../ouvidoria/++add++Claim?form.widgets.kind=solicitaassapso&amp;form.widgets.area=ouvidoria">solicitações</a>, <a href="../ouvidoria/++add++Claim?form.widgets.kind=reclamaassapso&amp;form.widgets.area=ouvidoria">reclamações</a>, <a href="../ouvidoria/++add++Claim?form.widgets.kind=elogio&amp;form.widgets.area=ouvidoria">elogios</a>, <a href="../ouvidoria/++add++Claim?form.widgets.kind=denaoncia&amp;form.widgets.area=ouvidoria">denúncias</a>, <a href="../ouvidoria/++add++Claim?form.widgets.kind=daovida&amp;form.widgets.area=ouvidoria">dúvidas</a> e <a href="../ouvidoria/++add++Claim?form.widgets.kind=sugestapso&amp;form.widgets.area=ouvidoria">sugestões</a> sobre as atividades administrativas e legislativas desta Casa.</p></td><td><p><a href="indice-de-transparencia"><img class="image-inline" src="../imagens/transparencia-indice.png" alt="Índice de Transparência" /></a></p><h3><a href="indice-de-transparencia">Índice de Transparência</a></h3><p>Como cidadão consciente e participativo, você pode avaliar este site e os demais sites do Poder Legislativo com base na Lei de Responsabilidade Fiscal (LRF) e na Lei de Acesso à Informação (LAI), basta baixar o manual e a planilha de avaliação. Participe!</p></td></tr></tbody></table>',
            ),
            dict(
                type='Folder',
                title=u'Orçamento e Finanças',
                description=u'Prestação de contas das receitas, despesas, repasses e transferências da Casa Legislativa e relatórios do controle interno.',
                _layout='folder_tabular_view',
            ),
            dict(
                type='Folder',
                title=u'Licitações e Contratos',
                description=u'Publicação de editais e informações sobre os processos de licitação e contratos da Casa Legislativa.',
                _layout='folder_tabular_view',
            ),
            dict(
                type='Folder',
                title=u'Recursos Humanos',
                description=u'Folha de pagamento, viagens, horas extras e outras informações sobre servidores, contratados, aposentados e pensionistas da Casa Legislativa.',
                _layout='folder_tabular_view',
            ),
            dict(
                type='Folder',
                title=u'Parlamentares e Gabinetes',
                description=u'Repasses, verbas indenizatórias, cotas, subsídios, viagens e demais despesas dos parlamentares e seus gabinetes.',
                _layout='folder_tabular_view',
            ),
            dict(
                type='Folder',
                title=u'Atos Administrativos',
                description=u'Publicação dos atos administrativos e outros documentos referentes à atividade administrativa da Casa Legislativa.',
                _layout='folder_tabular_view',
            ),
            dict(
                type='Document',
                title=u'Acesso à Informação',
                description=u'Instruções sobre como fazer solicitações com base na Lei de Acesso à Informação a esta Casa Legislativa.',
                text=u'<p><a href="http://www.acessoainformacao.gov.br"><img class="image-right" src="../imagens/acesso-a-informacao.png/image_mini" alt="Acesso à Informação" /></a>A Lei de Acesso à Informação (LAI) - <a href="http://www.lexml.gov.br/urn/urn:lex:br:federal:lei:2011-11-18;12527">lei nº 12.527/2011</a> - regulamenta o direito constitucional de obter informações públicas. Essa norma entrou em vigor em 16 de maio de 2012 e criou mecanismos que possibilitam a qualquer pessoa, física ou jurídica, sem necessidade de apresentar motivo, o recebimento de informações públicas dos órgãos e entidades.</p><p>Os pedidos de informações devem ser realizados nas <a href="../institucional/acesso">instalações físicas</a> desta Casa Legislativa ou através do <a href="../ouvidoria/++add++Claim?form.widgets.kind=pedido-de-acesso-a-informaassapso&form.widgets.area=ouvidoria">formulário de solicitação de informações</a> no site. Preenchendo este formulário o cidadão receberá um número de protocolo e poderá acompanhar a tramitação do seu pedido de informação.</p><p>A LAI estabelece também um conjunto mínimo de informações que devem ser publicadas nas seções de acesso à informação dos sites dos órgãos e entidades públicas. Além da publicação das informações exigidas, os órgãos podem divulgar outros dados de interesse público por iniciativa própria, ou seja, de forma proativa.</p><p>Portanto, antes de apresentar um pedido de acesso à informação, é importante que você verifique se a informação desejada já está disponível na seção de <a href="./">Transparência</a> deste site ou se ela já foi publicada como resposta a uma outra solicitação de informações realizada anteriormente através da <a href="../ouvidoria">Ouvidoria</a> deste site, que é caracterizada também como o e-SIC (Sistema Eletrônico de Informações ao Cidadão) desta Casa Legislativa.</p><h3>e-SIC — Sistema Eletrônico de Informações ao Cidadão</h3><p>Este site está equipado com um <a href="../ouvidoria">Sistema de Ouvidoria</a> que atende ao e-SIC. Se você deseja alguma informação que ainda não está publicada, faça um <a href="../ouvidoria/++add++Claim?form.widgets.kind=pedido-de-acesso-a-informaassapso&amp;form.widgets.area=ouvidoria">pedido de acesso à informação</a>. Os tipos de demandas que você pode enviar para a Ouvidoria são:</p><ul><li><a href="../ouvidoria/++add++Claim?form.widgets.kind=solicitaassapso&amp;form.widgets.area=ouvidoria">Denúncias</a></li><li><a href="../ouvidoria/++add++Claim?form.widgets.kind=daovida&amp;form.widgets.area=ouvidoria">Dúvidas</a></li><li><a href="../ouvidoria/++add++Claim?form.widgets.kind=solicitaassapso&amp;form.widgets.area=ouvidoria">Elogios</a></li><li><a href="../ouvidoria/++add++Claim?form.widgets.kind=pedido-de-acesso-a-informaassapso&amp;form.widgets.area=ouvidoria">Pedidos de Acesso à Informação</a></li><li><a href="../ouvidoria/++add++Claim?form.widgets.kind=solicitaassapso&amp;form.widgets.area=ouvidoria">Reclamações</a></li><li><a href="../ouvidoria/++add++Claim?form.widgets.kind=solicitaassapso&amp;form.widgets.area=ouvidoria">Solicitações</a></li><li><a href="../ouvidoria/++add++Claim?form.widgets.kind=sugestapso&amp;form.widgets.area=ouvidoria">Sugestões</a></li></ul><h3>Saiba mais sobre a LAI</h3><iframe width="560" height="315" src="https://www.youtube.com/embed/HiVKTKkI3nE?list=PLfcgNxuoKmUFWcqVOu--1aZJGfU97m0tG" frameborder="0" allowfullscreen></iframe><h3>Veja o Infográfico</h3><a href="../imagens/entenda-a-lai.jpg/image_view_fullscreen" title="Entenda a LAI"><img src="../imagens/entenda-a-lai.jpg/@@images/image/large" alt="Infográfico sobre a LAI" /></a>',
            ),
            dict(
                type='Document',
                title=u'Dados Abertos',
                description=u'Informações sobre os dados disponíveis neste site em formato aberto e legível por máquinas.',
                text=u'<p><a href="http://commons.wikimedia.org/wiki/File:Open_Data_stickers.jpg#mediaviewer/File:Open_Data_stickers.jpg"><img class="image-right" alt="Selos de Dados Abertos" width="193" height="145" src="http://upload.wikimedia.org/wikipedia/commons/c/cc/Open_Data_stickers.jpg" /></a></p><p>De acordo com o portal de <a href="http://dados.gov.br">Dados Abertos</a> do Governo Federal e segundo a <a href="http://opendefinition.org/">definição</a> da <a href="http://okfn.org">Open Knowledge Foundation</a>, dados ou conteúdos são abertos quando qualquer pessoa pode livremente usá-los, reutilizá-los e redistribuí-los, estando sujeito a, no máximo, a exigência de creditar a sua autoria e compartilhar pela mesma licença. Isso geralmente é satisfeito pela publicação dos dados em formato aberto e sob uma <a href="http://opendefinition.org/licenses/">licença aberta</a>, como a que está declarada no rodapé deste site.</p><p>Publicamos 4 conjuntos de dados abertos em formato <a href="http://json.org/json-pt.html">JSON</a>, que podem ser acessados a partir das seguintes APIs:</p><ul><li><a href="../@@portalmodelo-json">Dados da Instituição</a></li><li><a href="../@@ombudsman-json">Dados da Ouvidoria (e-SIC)</a></li><li><a href="../@@pl-json">Dados do Processo Legislativo</a></li><li><a href="../@@transparency-json">Dados de Transparência</a></li></ul><p>Disponibilizamos ainda uma API em <a href="../apidata">/apidata</a> que fornece no mesmo formato, além dos dados já citados, todos os conteúdos padrão publicados no site. Veja a documentação dessa API em <a href="../open-data">/open-data</a>.</p><p>Além disso, cada seção do site têm um link <a href="../rss-info">RSS</a> que publica seus conteúdos disponíveis em formato RSS (RDF Site Summary 1.0).</p>',
            ),
            dict(
                type='Document',
                title=u'Índice de Transparência',
                description=u'Índice de transparência do poder legislativo, criado para classificar e avaliar as Casas Legislativas por sua adesão à Lei da Transparência e à Lei de Acesso à Informação.',
                text=u'<p><a href="https://colab.interlegis.leg.br/wiki/IndiceTransparencia"><img class="image-right" src="../imagens/indice-de-transparencia.jpg" /></a>É um projeto elaborado pela <a href="http://www.senado.leg.br/transparencia">Secretaria da Transparência</a> do Senado Federal, que incentiva a cultura de transparência no Brasil e permite à sociedade avaliar a evolução dos Legislativos Brasileiros no cumprimento da <a href="http://www.lexml.gov.br/urn/urn:lex:br:federal:lei:2011-11-18;12527">Lei de Acesso à Informação</a> (LAI) e da <a href="http://www.lexml.gov.br/urn/urn:lex:br:federal:lei.complementar:2000-05-04;101">Lei de Responsabilidade Fiscal</a> (LRF). Ele segue padrões internacionais, com a construção de um ranking nacional de transparência legislativa.</p><p>O processo de avaliação deve ser feito em duas fases:</p><ol><li>Análise preliminar;</li><li>Reavaliação para consolidação dos dados.</li></ol><p>Serão analisadas quatro vertentes básicas da abertura de dados expostos por meio eletrônico:</p><ul><li>Informações sobre atividades legislativas;</li><li>Informações administrativas;</li><li>Controle social - atividades pró-interação e participação social;</li><li>Adequação aos parâmetros da LAI.</li></ul><p><a href="https://colab.interlegis.leg.br/wiki/IndiceTransparencia">Acesse a página do Índice de Transparência</a> e faça download da planilha de avaliação e do manual.</p><h3>Veja o Infográfico</h3><a href="../imagens/entenda-o-indice-de-transparencia.jpg/image_view_fullscreen"><img class="image-inline" src="../imagens/entenda-o-indice-de-transparencia.jpg/@@images/image/large" alt="Infográfico sobre o Índice de Transparência" /></a>',
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Links Úteis',
        description=u'Seção que contém os links para sites externos.',
        excludeFromNav=True,
        _addable_types=['Folder', 'Link'],
        _children=[
            dict(
                type='Link',
                title=u'Prefeitura Municipal',
                description=u'Site da Prefeitura Municipal. (este link deve ser editado)',
                remoteUrl='http://www.municipio.uf.gov.br',
            ),
            dict(
                type='Link',
                title=u'Diario Oficial do Município',
                description=u'Site do diário oficial do município. (este link deve ser editado ou removido se não existir)',
                remoteUrl='http://diario.municipio.uf.gov.br',
            ),
            dict(
                type='Link',
                title=u'Assembleia Legislativa',
                description=u'Site da Assembleia Legislativa do Estado. (este link deve ser editado)',
                remoteUrl='http://www.al.uf.leg.br',
            ),
            dict(
                type='Link',
                title=u'Câmara dos Deputados',
                description=u'Site da Câmara dos Deputados Federal.',
                remoteUrl='http://www.camara.leg.br',
            ),
            dict(
                type='Link',
                title=u'Senado Federal',
                description=u'Site do Senado Federal do Brasil.',
                remoteUrl='http://www.senado.leg.br',
            ),
            dict(
                type='Link',
                title=u'Programa Interlegis',
                description=u'Site do Programa de Integração e Modernização do Legislativo Brasileiro.',
                remoteUrl='http://www.interlegis.leg.br',
            ),
        ],
    ),
    dict(
        type='Folder',
        id='imagens',
        title=u'Banco de Imagens',
        description=u'Banco de imagens usadas e referenciadas nos conteúdos do site.',
        excludeFromNav=True,
        _addable_types=['Folder', 'Image', 'Link'],
        _layout='atct_album_view',
    ),
    dict(
        type='Folder',
        title=u'Boletins',
        description=u'Boletins informativos da Casa Legislativa. Cadastre seu e-mail para ficar sabendo das nossas novidades.',
        excludeFromNav=True,
        _addable_types=['EasyNewsletter'],
        _children=[
            dict(
                type='EasyNewsletter',
                id='acompanhe',
                title=u'Acompanhe a Câmara',
                description=u'Receba por e-mail periodicamente o que acontece de novo na nossa Casa Legislativa.',
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Enquetes',
        description=u'Pesquisas de opinião feitas pela Casa Legislativa.',
        excludeFromNav=True,
        _addable_types=['collective.polls.poll'],
        _children=[
            dict(
                type='collective.polls.poll',
                title=u'Gostou do novo site?',
                description=u'O que você achou do novo site desta Casa Legislativa?',
                options=[
                    dict(option_id=0, description=u'Sim, gostei'),
                    dict(option_id=1, description=u'Não gostei'),
                    dict(option_id=2, description=u'Pode melhorar'),
                ],
                _transition='open',
            ),
        ],
    ),
    dict(
        type='OmbudsOffice',
        title=u'Ouvidoria',
        description=u'Sistema Eletrônico de Informações ao Cidadão (e-SIC), que controla as demandas dos cidadãos à Casa Legislativa, permitindo seu acompanhamento e pesquisas.',
        claim_types=[
            dict(claim_type='Denúncia'),
            dict(claim_type='Dúvida'),
            dict(claim_type='Elogio'),
            dict(claim_type='Pedido de Acesso à Informação'),
            dict(claim_type='Solicitação'),
            dict(claim_type='Sugestão'),
            dict(claim_type='Reclamação'),
        ],
        areas=[
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Administração'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Assessoria Legislativa e Jurídica'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Comissões'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Ouvidoria'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Secretaria Legislativa'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Plenário'),
        ],
    ),
    dict(
        type='Document',
        id='faq',
        title=u'Perguntas Frequentes',
        description=u'Esta é a FAQ do site, uma relação de perguntas que são feitas com frequência para a Casa Legislativa e suas respectivas respostas.',
        text=u'<img class="image-right" src="imagens/faq-logo.png/image_thumb" alt="FAQ" /><h2>Perguntas</h2><ol><li><a href="#p1">O conteúdo desta FAQ deve ser modificado?</a></li><li><a href="#p2">Como posso modificar este conteúdo e compor a FAQ real deste site?</a></li></ol><br/><h2>Respostas</h2><h3>O conteúdo desta FAQ deve ser modificado?<a name="p1"></a></h3><p>Sim, este é um conteúdo padrão que foi criado automaticamente junto com o Portal Modelo. O objetivo dele é lhe orientar a formatar a seção de perguntas e respostas do seu site. <a href="edit">Edite-o</a> e crie sua FAQ real!</p><h3>Como posso modificar este conteúdo e compor a FAQ real deste site?<a name="p2"></a></h3><p>Para alterá-lo basta <a href="login">se autenticar</a> no site, e clicar na aba <em><a href="edit">Edição</a></em>, que fica logo acima do título desta página. Então inserir o conteúdo real e clicar no botão <em>Salvar</em>. Preste atenção na formatação, cada pergunta acima tem um link para a sua respectiva âncora aqui embaixo na resposta.</p>',
    ),
    dict(
        type='Document',
        id='rss-info',
        title=u'RSS',
        description=u'Assine os canais RSS disponíveis em cada seção do site e receba automaticamente todas as suas atualizações.',
        text=u'<p><img class="image-right" src="imagens/rss-logo.png" alt="RSS" />RSS é um recurso que serve para agregar conteúdos da web, podendo ser acessados por programas ou sites agregadores, facilitando o intercâmbio de informação e sua atualização. Uma descrição mais abrangente sobre essa tecnologia está disponível na <a href="http://pt.wikipedia.org/wiki/RSS">Wikipédia</a>.</p><p>Este site possui vários canais RSS (RDF Site Summary 1.0) habilitados. Basicamente, cada seção do site tem seu canal RSS que você pode assinar para receber automaticamente suas atualizações. Quando um novo conteúdo é publicado em um desses canais, ele é automaticamente transferido para os dispositivos que estiverem usando-o. Os principais canais são:</p><ul><li><a href="RSS">Geral (todos os conteúdos do site)</a></li><li><a href="institucional/noticias/RSS">Notícias</a></li><li><a href="institucional/eventos/RSS">Agenda</a></li><li><a href="ouvidoria/RSS">Ouvidoria (e-SIC)</a></li><li><a href="enquetes/RSS">Enquetes</a></li></ul><p>Além disso, a busca do site também pode ser retornada como um canal RSS. Por exemplo, se você fizer uma busca pela palavra <em>lei</em>, mesmo após usar os filtros para melhorar o resultado, é possível usar sua URL como resposta em formato RSS, apenas trocando sua base de <a href="@@search?SearchableText=lei">@@search</a> para <a href="@@search_rss?SearchableText=lei">@@search_rss</a>.</p>',
    ),
    dict(
        type='Link',
        title=u'Manual de Uso',
        description=u'Link para o arquivo PDF do Manual do Portal Modelo 3 para Gestores de Conteúdo. (este link é apenas uma referência, está privado e pode ser removido)',
        remoteUrl='http://colab.interlegis.leg.br/raw-attachment/wiki/ProjetoPortalModelo/ManualPortalModelo3.pdf',
        _transition=None,
    ),
    dict(
        type='Link',
        title=u'Cartilha TCE/RS',
        description=u'Link para cartilha de acesso à informação na pática - O que publicar no Portal? Orientações para Prefeituras e Câmaras. (este link é apenas uma referência, está privado e pode ser removido)',
        remoteUrl='https://portal.tce.rs.gov.br/portal/page/portal/tcers/publicacoes/orientacoes_gestores/acesso_informacao_pratica.pdf',
        _transition=None,
    ),
]

SITE_STRUCTURE = _add_id(SITE_STRUCTURE)

