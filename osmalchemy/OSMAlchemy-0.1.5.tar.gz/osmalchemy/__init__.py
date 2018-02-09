# ~*~~ coding: utf-8 ~*~

# Define the version of OSMAlchemy
__version__ = "0.1.5"

# Monkey patch SQLAlchemy to support some query constructs
from .util.patch import monkey_patch_sqlalchemy, monkey_patch_flask_restless
monkey_patch_sqlalchemy()
monkey_patch_flask_restless()

from .osmalchemy import OSMAlchemy
