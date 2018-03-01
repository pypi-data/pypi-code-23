"""DustCli bootstrapping."""

from DustCli.cli.controllers.base import BaseController
from DustCli.cli.controllers.project import ProjectController 
from pathlib import Path

def load(app):
    app.handler.register(BaseController)
    app.handler.register(ProjectController)
