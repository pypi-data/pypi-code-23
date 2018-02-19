# -*- coding:utf-8 -*-
from interlegis.portalmodelo.policy.config import PROJECTNAME
from plone.app.upgrade.utils import loadMigrationProfile
from plone import api

import logging

PROFILE_ID = 'interlegis.portalmodelo.policy:default'
DEFAULT_FUNCTIONALITIES = ('foruns', 'blog', 'intranet')
INSTALL_PRODUCTS = ('plone.formwidget.recaptcha', 'collective.plonetruegallery')
UNINSTALL_PRODUCTS = ('Ploneboard', 'sc.blog', 'sc.galleria.support', 'plone.formwidget.captcha')

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


