# -*- coding: utf-8 -*-
from tgext.pluggable import PluggableSession
import logging
import tg


log = logging.getLogger(__name__)

DBSession = PluggableSession()
provider = None

ProfileActivation = None


def init_model(app_session):
    DBSession.configure(app_session)


def configure_models():
    global provider, ProfileActivation

    if tg.config.get('use_sqlalchemy', False):
        log.info('Configuring tgapp-userprofile for SQLAlchemy')
        from userprofile.model.sqla.models import ProfileActivation
        from sprox.sa.provider import SAORMProvider
        provider = SAORMProvider(session=DBSession, engine=False)
    elif tg.config.get('use_ming', False):
        log.info('Configuring tgapp-userprofile for Ming')
        from userprofile.model.ming.models import ProfileActivation
        from sprox.mg.provider import MingProvider
        provider = MingProvider(DBSession)
    else:
        raise ValueError('tgapp-userprofile should be used with sqlalchemy or ming')
