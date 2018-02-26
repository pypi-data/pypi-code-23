# -*- coding: utf-8 -*-
from collective.flowplayer.interfaces import IAudio
from collective.flowplayer.interfaces import IVideo
from dateutil.relativedelta import relativedelta
from five import grok
from interlegis.portalmodelo.policy.config import CREATORS
from interlegis.portalmodelo.policy.config import DEFAULT_CONTENT
from interlegis.portalmodelo.policy.config import HOME_TILE_EMBED1
from interlegis.portalmodelo.policy.config import HOME_TILE_EMBED2
from interlegis.portalmodelo.policy.config import HOME_TILE_TEXT
from interlegis.portalmodelo.policy.config import HOME_TILE_TEXT_NOTICE
from interlegis.portalmodelo.policy.config import HOME_TILE_BANNER_URL
from interlegis.portalmodelo.policy.config import PROJECTNAME
from interlegis.portalmodelo.policy.config import SITE_STRUCTURE
from interlegis.portalmodelo.policy.config import VIDEO_TEXT
from plone import api
from plone.event.interfaces import IEventAccessor
from plone.namedfile.file import NamedBlobImage
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFQuickInstallerTool import interfaces as qi
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
from datetime import datetime
from StringIO import StringIO

import logging
import os

logger = logging.getLogger(PROJECTNAME)


class HiddenProducts(grok.GlobalUtility):

    grok.implements(qi.INonInstallable)
    grok.provides(qi.INonInstallable)
    grok.name(PROJECTNAME)

    def getNonInstallableProducts(self):
        return [
            u'Products.windowZ'
        ]


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [
            u'interlegis.portalmodelo.policy.upgrades.v2:default'
            u'Products.windowZ:default'
        ]


# XXX: we should found a way to avoid creating default content on first place
def delete_default_content(site):
    """Delete content created at Plone's installation.
    """
    logger.info(u'Apagando conteúdo padrão do Plone')
    for item in DEFAULT_CONTENT:
        if hasattr(site, item):
            api.content.delete(site[item])
            logger.debug(u'    {0} apagado'.format(item))


# XXX: we should found a way to avoid creating default portlets on first place
def delete_default_portlets(site):
    """Delete default portlets created at Plone's installation.
    """
    def get_assignment(column):
        assert column in [u'left', u'right']
        name = u'plone.{0}column'.format(column)
        manager = getUtility(IPortletManager, name=name, context=site)
        return getMultiAdapter((site, manager), IPortletAssignmentMapping)

    logger.info(u'Apagando portlets padrão do Plone')
    for column in [u'left', u'right']:
        assignment = get_assignment(column)
        for portlet in assignment.keys():
            del assignment[portlet]
            logger.debug(u'    {0} apagado'.format(portlet))


def constrain_types(folder, addable_types):
    """Constrain addable types in folder.
    """
    folder.setConstrainTypesMode(True)
    folder.setImmediatelyAddableTypes(addable_types)
    folder.setLocallyAllowedTypes(addable_types)


def create_site_structure(root, structure):
    """Create and publish new site structure as defined in config.py."""
    for item in structure:
        id = item['id']
        title = item['title']
        description = item.get('description', u'')
        if id not in root:
            if 'creators' not in item:
                item['creators'] = CREATORS
            obj = api.content.create(root, **item)
            # publish private content or make a workflow transition
            if item['type'] not in ['Image', 'File']:
                if '_transition' not in item and api.content.get_state(obj) == 'private':
                    api.content.transition(obj, 'publish')
                elif item.get('_transition', None):
                    api.content.transition(obj, item['_transition'])
            # constrain types in folder?
            if '_addable_types' in item:
                constrain_types(obj, item['_addable_types'])
            # the content has more content inside? create it
            if '_children' in item:
                create_site_structure(obj, item['_children'])
            # add an image to all news items
            if obj.portal_type == 'News Item':
                if 'image' in item:
                    obj.setImage(item['image'])
            # set the default view to object
            if '_layout' in item:
                obj.setLayout(item['_layout'])
            # XXX: workaround for https://github.com/plone/plone.api/issues/99
            obj.setTitle(title)
            obj.setDescription(description)
            obj.reindexObject()
            logger.debug(u'    {0} criado e publicado'.format(title))
        else:
            logger.debug(u'    pulando {0}; conteúdo existente'.format(title))
            


def setup_csvdata_permissions(portal):
    """CSVData content type is allowed **only** within its own folder
    """
    permission = 'interlegis.portalmodelo.transparency: Add CSVData'
    roles = ('Manager', 'Site Administrator', 'Owner', 'Contributor')
    folder = portal['transparencia']
    folder.manage_permission(
        permission,
        roles=roles
    )
    logger.debug(u'Permissoes ajustadas em Transparencia')

    # Remove permission on the root of the site
    portal.manage_permission(
        permission,
        roles=(),
    )


def setup_transparency_permissions(portal):
    """Transparency section and FAQ can't be deleted.
    """
    permission = 'Delete objects'
    roles = ('Manager', 'Owner')
    folder = portal['transparencia']
    folder.manage_permission(
        permission,
        roles=roles
    )

    permission = 'Delete objects'
    roles = ('Manager', 'Owner')
    folder = portal['faq']
    folder.manage_permission(
        permission,
        roles=roles
    )


def install_legislative_process_integration(self):
    """Install interlegis.portalmodelo.pl package.

    We need to deffer the installation of this package until the structure is
    created to avoid having to move the folder to the right position.
    """
    profile = 'profile-interlegis.portalmodelo.pl:default'
    setup_tool = api.portal.get_tool('portal_setup')
    setup_tool.runAllImportStepsFromProfile(profile)


def populate_cover(site):
    """Populate site front page. The layout is composed by 4 rows:

    1. 1 carousel tile
    2. 1 banner tile
    3. 1 collection tile
    4. 1 parlamientarians tile
    5. 2 embed tiles

    Populate and configure those tiles.
    """
    from cover import set_tile_configuration
    from plone.uuid.interfaces import IUUID

    frontpage = site['front-page']
    # first row
    tiles = frontpage.list_tiles('collective.cover.carousel')
    obj1 = site['institucional']['noticias']['terceira-noticia']
    obj2 = site['institucional']['noticias']['primeira-noticia']
    uuid1 = IUUID(obj1)
    uuid2 = IUUID(obj2)
    data = dict(uuids=[uuid1, uuid2])
    frontpage.set_tile_data(tiles[0], **data)
    set_tile_configuration(frontpage, tiles[0], image={'scale': 'large'})
    # second row
    tiles = frontpage.list_tiles('collective.cover.banner')
    path = os.path.dirname(__file__)
    banner_name = u'banner.jpg'
    banner_file = open(os.path.join(path, 'browser/static', banner_name)).read()
    banner_image = NamedBlobImage(banner_file, 'image/jpeg', banner_name)
    data = dict(
        title=u'Banner de Exemplo',
        image=banner_image,
        remote_url=HOME_TILE_BANNER_URL
    )
    frontpage.set_tile_data(tiles[0], **data)
    set_tile_configuration(frontpage, tiles[0], image={'scale': 'large'})
    # third row
    tiles = frontpage.list_tiles('collective.cover.collection')
    obj = site['institucional']['noticias']['agregador']
    assert obj.portal_type == 'Collection'
    uuid = IUUID(obj)
    data = dict(header=u'Últimas Notícias', footer=u'Mais notícias…', uuid=uuid)
    frontpage.set_tile_data(tiles[0], **data)
    set_tile_configuration(
        frontpage,
        tiles[0],
        image=dict(order=0, scale='thumb'),
        date=dict(order=1),
        title=dict(htmltag='h3')
    )
    # fourth row
    tiles = frontpage.list_tiles('collective.cover.richtext')
    data = dict(text=HOME_TILE_TEXT)
    frontpage.set_tile_data(tiles[0], **data)
    # fifth row
    tiles = frontpage.list_tiles('collective.cover.embed')
    data = dict(embed=HOME_TILE_EMBED1)
    frontpage.set_tile_data(tiles[0], **data)
    data = dict(embed=HOME_TILE_EMBED2)
    frontpage.set_tile_data(tiles[1], **data)
    # notice rows
    tiles = frontpage.list_tiles('collective.cover.richtext')
    data = dict(text=HOME_TILE_TEXT_NOTICE)
    frontpage.set_tile_data(tiles[1], **data)



def set_site_default_page(site):
    """Set front page as site default page."""
    site.setDefaultPage('front-page')
    logger.info(u'Visão padrão do site estabelecida')


def set_default_view_on_folder(folder, object_id=''):
    """Create and publish a Document (or other content type) inside a folder
    and set it as the default view of that folder.
    """
    assert folder.portal_type == 'Folder'
    id = folder.id
    title = folder.title
    object_id = object_id or id
    folder.setDefaultPage(object_id)
    logger.info(u'Visão padrão criada e estabelecida para {0}'.format(title))


def set_flowplayer_file_type(obj):
    """Set flowplayer as default view on object or folder."""
    if obj.id.endswith('mp3'):
        alsoProvides(obj, IAudio)
        obj.reindexObject(idxs=['object_provides'])
    elif obj.id.endswith('mp4'):
        alsoProvides(obj, IVideo)
        obj.reindexObject(idxs=['object_provides'])
    logger.info(u'Tipo de arquivo estabelecido')


def import_images(site):
    """Import all images inside the "import" folder of the package and import
    them inside the "Banco de Imagens" folder. We are assuming the folder
    contains only valid image files so no validation is done.
    """
    image_bank = site['imagens']
    # look inside "images" folder and import all files
    path = os.path.dirname(os.path.abspath(__file__)) + '/browser/images/'
    logger.info(u'Importando imagens')
    for name in os.listdir(path):
        with open(path + name) as f:
            image = StringIO(f.read())
        img_name = name.split('.')[0]
        title = img_name.replace('-', ' ').title()
        api.content.create(
            image_bank,
            type = 'Image',
            id = name,
            title = title,
            description = u'Esta imagem é referenciada nos conteúdos do portal.',
            image = image,
            creators = CREATORS,
        )
        logger.debug(u'    {0} importada'.format(name))


def import_photos(site):
    """Import some photos inside the "static" folder of the package and import
    them inside the "Galeria de Fotos" folder.
    """
    image_bank = site['institucional']['fotos']
    image_names = ['plenario-camara.jpg', 'plenario-senado.jpg', 'congresso-nacional.jpg']
    # look inside "static" folder and import some files
    path = os.path.dirname(os.path.abspath(__file__)) + '/browser/static/'
    logger.info(u'Importando imagens')
    for name in image_names:
        with open(path + name) as f:
            image = StringIO(f.read())
        img_name = name.split('.')[0]
        title = img_name.replace('-', ' ').title()
        api.content.create(
            image_bank,
            type = 'Image',
            id = name,
            title = title,
            description = u'Foto de demonstração no tamanho 3x2. (esta imagem é um conteúdo de exemplo e pode ser removida)',
            image = image,
            creators = CREATORS,
        )
        logger.debug(u'    {0} importada'.format(name))


def miscelaneous_house_folder(site):
    """Set various adjustments on site content on "Sobre a Câmara" folder:

    - Set default views on subfolders
    - Set flowplayer file types on "Áudios" and "Vídeos"
    """
    folder = site['institucional']
    set_default_view_on_folder(folder['acesso'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['historia'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['funcao-e-definicao'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['estrutura'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['noticias'], object_id='agregador')
    set_default_view_on_folder(folder['clipping'], object_id='agregador')
    set_default_view_on_folder(folder['videos'], object_id='agregador')
    set_default_view_on_folder(site['transparencia'], object_id='pagina-padrao')

    videos = folder['videos']
    set_flowplayer_file_type(videos['campanha-legbr.mp4'])
    set_flowplayer_file_type(videos['solucao-web-interlegis.mp4'])

    audios = folder['audios']
    set_flowplayer_file_type(audios['campanha-legbr.mp3'])
    set_flowplayer_file_type(audios['solucao-web-interlegis.mp3'])


def import_registry_settings(site):
    """Import registry settings; we need to do this before other stuff here,
    like using a cover layout defined there.

    XXX: I don't know if there is other way to do this on ZCML or XML.
    """
    PROFILE_ID = 'profile-interlegis.portalmodelo.policy:default'
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')


def setup_event(site):
    """Set the default start and end event properties."""
    folder = site['institucional']['eventos']
    event = folder['1o-ano-do-site']
    acc = IEventAccessor(event)
    future = datetime.now() + relativedelta(years=1)
    year = future.year
    month = future.month
    day = future.day
    acc.start = datetime(year, month, day, 0, 0, 0)
    acc.end = datetime(year, month, day, 23, 59, 59)
    notify(ObjectModifiedEvent(event))
    event.reindexObject()
    logger.debug(u'Evento padrao configurado')


def setup_embedder_video(site):
    """Set a few properties on Youtube video embedders."""
    folder = site['institucional']['videos']
    videos = [
        {'id': 'municipio-brasil', 'img': 'capa-video1.jpg', 'text': VIDEO_TEXT},
        {'id': 'por-que-utilizar-o-portal-modelo', 'img': 'capa-video2.jpg'}
    ]

    for v in videos:
        embedder = folder[v['id']]
        if v.get('text'):
            embedder.text = v['text']
        path = os.path.dirname(__file__)
        data = open(os.path.join(path, 'browser/static', v['img'])).read()
        image = NamedBlobImage(data, 'image/jpeg', u'hqdefault.jpg')
        embedder.image = image
        embedder.reindexObject()
        logger.debug(u'Video embedder {0} configurado'.format(v['id']))



def setup_various(context):
    marker_file = '{0}.txt'.format(PROJECTNAME)
    if context.readDataFile(marker_file) is None:
        return

    portal = api.portal.get()
    import_registry_settings(portal)
    delete_default_content(portal)
    delete_default_portlets(portal)
    create_site_structure(portal, SITE_STRUCTURE)
    setup_csvdata_permissions(portal)
    setup_transparency_permissions(portal)
    install_legislative_process_integration(portal)
    set_site_default_page(portal)
    miscelaneous_house_folder(portal)
    import_images(portal)
    import_photos(portal)
    populate_cover(portal)
    setup_event(portal)
    setup_embedder_video(portal)


def fix_image_links_in_static_portlet(portal):
    """Fix image links in "midias-sociais" and "acesso-informacao" portlets. To
    make this independent portal site name we need to use `resolveuid/UID` as
    source of images instead of using a fixed URL.
    """

    def get_image_uid(image):
        """Return image UID."""
        folder = portal['imagens']
        if image in folder:
            return folder[image].UID()

    manager = getUtility(IPortletManager, name='plone.rightcolumn', context=portal)
    mapping = getMultiAdapter((portal, manager), IPortletAssignmentMapping)

    assert 'midias-sociais' in mapping
    portlet = mapping['midias-sociais']
    images = [
        'ico-facebook.png', 'ico-twitter.png', 'ico-linkedin.png',
        'ico-youtube.png', 'ico-flickr.png'
    ]
    for i in images:
        uid = 'resolveuid/' + get_image_uid(i)
        portlet.text = portlet.text.replace(i, uid)
    logger.debug(u'Links substituidos no portlet de midias sociais')

    assert 'banners' in mapping
    portlet = mapping['banners']
    image = 'acesso-a-informacao.png'
    uid = 'resolveuid/' + get_image_uid(image) + '/image_mini'
    portlet.text = portlet.text.replace(image, uid)
    logger.debug(u'Link substituido no portlet de acesso a informacao')


def set_flowplayer_portlet(portal):
    """Set target and splash objects in flowplayer radio-legislativa portlet."""
    manager = getUtility(IPortletManager, name='plone.rightcolumn', context=portal)
    mapping = getMultiAdapter((portal, manager), IPortletAssignmentMapping)

    assert 'radio-legislativa' in mapping
    portlet = mapping['radio-legislativa']
    portlet.data.splash = '/imagens/audio-player.png'
    portlet.data.target = '/institucional/audios'
    logger.debug(u'Definidos os objetos em vez dos paths no portlet da radio')


def setup_portlets(context):
    """This is called after import of portlets.xml.
    """
    marker_file = '{0}.txt'.format(PROJECTNAME)
    if context.readDataFile(marker_file) is None:
        return

    portal = api.portal.get()
    fix_image_links_in_static_portlet(portal)
    set_flowplayer_portlet(portal)


