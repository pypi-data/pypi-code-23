import click
from lantern_cli import settings
from cookiecutter.main import cookiecutter


def startapp():
    """
		Will create a new Lantern Engine Microservice app based on the cookiecutter template
    """
    cookiecutter(settings.MICROSERVICE_TEMPLATE_repo)
