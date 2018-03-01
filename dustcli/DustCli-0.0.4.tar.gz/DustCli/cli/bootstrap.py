"""DustCli bootstrapping."""

from DustCli.cli.controllers.base import BaseController
from DustCli.cli.controllers.project import ProjectController 
from DustCli.cli.controllers.package import PackageController
from pathlib import Path

def load(app):
    app.handler.register(BaseController)
    app.handler.register(ProjectController)
    app.handler.register(PackageController)
