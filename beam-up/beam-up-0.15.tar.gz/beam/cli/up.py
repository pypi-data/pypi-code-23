from beam import Site
from beam.config import load_config

import logging
import click
import os

logger = logging.getLogger(__name__)

@click.command("up")
@click.option("--site", default="site.yml")
def up(site):
    if not os.path.exists(site):
        logger.error("Site {} not found!".format(site))
        return -1
    config = load_config(site)
    site = Site(config)
    site.build()

