__version__ = '0.0.8'
__year__ = 2018

def main(global_config, **settings):

    from pyramid.config import Configurator
    from pyramid.session import SignedCookieSessionFactory

    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    from .security import groupfinder

    from sqlalchemy import engine_from_config
    from .models import DBSession, Base, Root

    #engine = engine_from_config(settings, 'sqlalchemy.', pool_recycle=3600)
    engine = engine_from_config(settings, 'sqlalchemy.', pool_pre_ping=True) # From V 1.2
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    my_session_factory = SignedCookieSessionFactory(
        settings['session.secret'])

    config = Configurator(settings=settings,
                    session_factory=my_session_factory,
                    root_factory='wdwapp.models.Root')

    config.include('pyramid_chameleon')

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'], callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    
    # Routes for web site
    config.add_route('overview', '/')
    config.add_route('detail', '/detail/{lid}')
    config.add_route('wikipage_add', '/add')
    config.add_route('wikipage_edit', '/{uid}/edit')
    config.add_route('home', '/howdy/{first}/{last}')

    # Static things
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static/')

    # Let's go
    config.scan('.views')
    return config.make_wsgi_app()
