from puer.module import AbstractModule
from aiohttp_swagger import setup_swagger

class Swagger(AbstractModule):
    name = None

    def __init__(self, manager, app):
        settings = manager.settings.swagger
        setup_swagger(app,
                      swagger_url=settings.url,
                      swagger_from_file=settings.yaml)
