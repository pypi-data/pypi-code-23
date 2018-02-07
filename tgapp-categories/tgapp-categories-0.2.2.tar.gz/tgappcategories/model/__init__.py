# -*- coding: utf-8 -*-
import logging
import tg
from tgext.pluggable import PluggableSession

log = logging.getLogger('tgappcategories')

DBSession = PluggableSession()
provider = None

Category = None
CategoryImage = None


def init_model(app_session):
    DBSession.configure(app_session)


def configure_models():
    global provider, Category, CategoryImage

    if tg.config.get('use_sqlalchemy', False):
        log.info('Configuring TgappCategories for SQLAlchemy')
        from tgappcategories.model.sqla.models import Category, CategoryImage
        from sprox.sa.provider import SAORMProvider
        provider = SAORMProvider(session=DBSession, engine=False)
    elif tg.config.get('use_ming', False):
        log.info('Configuring TgappCategories for Ming')
        from tgappcategories.model.ming.models import Category, CategoryImage
        from sprox.mg.provider import MingProvider
        provider = MingProvider(DBSession)
    else:
        raise ValueError('TgappCategories should be used with sqlalchemy or ming')
