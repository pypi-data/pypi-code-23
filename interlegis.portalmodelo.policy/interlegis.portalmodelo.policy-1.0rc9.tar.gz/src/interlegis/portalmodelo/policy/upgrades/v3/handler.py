# -*- coding:utf-8 -*-
from interlegis.portalmodelo.policy.config import CREATORS
from interlegis.portalmodelo.policy.config import PROJECTNAME
from interlegis.portalmodelo.policy.utils import _add_id
from plone.app.upgrade.utils import loadMigrationProfile
from plone import api

import logging

PROFILE_ID = 'interlegis.portalmodelo.policy:default'
DEFAULT_FUNCTIONALITIES = ('foruns', 'blog', 'intranet')
INSTALL_PRODUCTS = ('plone.formwidget.recaptcha', 'collective.plonetruegallery')
UNINSTALL_PRODUCTS = ('Ploneboard', 'sc.blog', 'plone.formwidget.captcha')

def apply_configurations(context):
    """Atualiza perfil para versao 3."""
    logger = logging.getLogger(PROJECTNAME)
    profile = 'profile-interlegis.portalmodelo.policy.upgrades.v3:default'
    loadMigrationProfile(context, profile)
    logger.info('Atualizado para versao 3')

    site = api.portal.getSite()
    for item in DEFAULT_FUNCTIONALITIES:
        if hasattr(site, item):
            api.content.delete(site[item])
            logger.debug(u'    {0} apagado'.format(item))
    logger.info('Apagando pasta de fórum e blog')

    q_i = api.portal.get_tool(name='portal_quickinstaller')
    for ip in INSTALL_PRODUCTS:
        if not q_i.isProductInstalled(ip):
            q_i.installProduct(ip)
    logger.info('Instalando produtos para recaptcha e galeria')

    site.institucional.fotos.setLayout('galleryview')
    logger.info('Configurando a visão da pasta galeria de fotos')

    for up in UNINSTALL_PRODUCTS:
        if q_i.isProductInstalled(up):
            q_i.uninstallProducts([up])
    logger.info('Desinstalando produtos que não serão mais usados')

    SITE_STRUCTURE = [
        dict(
            type='Link',
            title=u'Cartilha TCE/RS',
            description=u'Link para cartilha de acesso à informação na pática - O que publicar no Portal? Orientações para Prefeituras e Câmaras. (este link é apenas uma referência, está privado e pode ser removido)',
            remoteUrl='https://portal.tce.rs.gov.br/portal/page/portal/tcers/publicacoes/orientacoes_gestores/acesso_informacao_pratica.pdf',
            _transition=None,
        ),
    ]
    SITE_STRUCTURE = _add_id(SITE_STRUCTURE)
    for item in SITE_STRUCTURE:
        id = item['id']
        title = item['title']
        description = item.get('description', u'')
        if id not in site:
            if 'creators' not in item:
                item['creators'] = CREATORS
            obj = api.content.create(site, **item)
            obj.setTitle(title)
            obj.setDescription(description)
            obj.reindexObject()
            logger.debug(u'    {0} criado e publicado'.format(title))
        else:
            logger.debug(u'    pulando {0}; conteúdo existente'.format(title))


