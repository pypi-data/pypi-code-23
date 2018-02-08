# -*- coding: utf-8 -*-
import json
import os
import os.path
from typing import List

from chaoslib.discovery import discover as disco
from chaoslib.exceptions import DiscoveryFailed
from chaoslib.types import Experiment
from chaostoolkit.cli import discover as chtk_discover
from chaostoolkit.cli import init as chtk_init
from chaostoolkit.cli import run as chtk_run
import click
from logzero import logger
import requests

from chaosiq.api import call_chaosiq_api
from chaosiq.config import load_config, CHAOISQ_CONFIG_PATH
from chaosiq.exceptions import ConfigurationMissingError

__all__ = ["discover", "init"]


###############################################################################
# chaostoolkit CLI overloading
###############################################################################
@click.command(help=chtk_discover.__doc__)
@click.option('--no-system-info', is_flag=True,
              help='Do not discover system information.')
@click.option('--no-install', is_flag=True,
              help='Assume package already in PYTHONPATH.')
@click.option('--discovery-report-path', default="./discovery.json",
              help='Path where to save the report from the discovery.',
              show_default=True)
@click.argument('package')
@click.pass_context
def discover(ctx: click.Context, package: str,
             discovery_report_path: str = "./discovery.json",
             no_system_info: bool = False, no_install: bool = False):
    # invoking actual chaostoolkit parent discovery function
    try:
        discovery = disco(
            package_name=package, discover_system=not no_system_info,
            download_and_install=not no_install)
    except DiscoveryFailed as err:
        logger.debug("Failed to discover {}".format(package), exc_info=err)
        click.echo(str(err), err=True, nl=True)
        return

    try:
        config_file = os.environ.get(
            "CHAOISQ_CONFIG_PATH", CHAOISQ_CONFIG_PATH)
        config = load_config(click.format_filename(config_file))
    except ConfigurationMissingError as err:
        display_missing_config_message(config_file)
    else:
        logger.info("Calling chaosiq to fetch potential experiments")

        r = call_chaosiq_api(
            "/v1/flow/discovery/", payload=discovery, config=config,
            expected_status=201)

        if r:
            discovery = r.json()
            count = len(discovery.get("experiments", []))
            m = "{d} experiment suggestions were found"
            if count == 1:
                m = "{d} experiment suggestion was found"
            logger.info(m.format(d=count))

    with open(discovery_report_path, "w") as d:
        d.write(json.dumps(discovery, indent=2))

    logger.info("Discovery report saved in {p}".format(
        p=discovery_report_path))

    return discovery


@click.command(help=chtk_init.__doc__)
@click.option('--discovery-path', default="./discovery.json",
              help='Path to the discovery outcome.',
              show_default=True, type=click.Path(exists=False))
@click.option('--experiment-path', default="./experiment.json",
              help='Path where to save the experiment.',
              show_default=True)
@click.pass_context
def init(ctx: click.Context, discovery_path: str = "./discovery.json",
         experiment_path: str = "./experiment.json"):
    config = None
    choice = "default"
    try:
        config_file = os.environ.get(
            "CHAOISQ_CONFIG_PATH", CHAOISQ_CONFIG_PATH)
        config = load_config(click.format_filename(config_file))
    except ConfigurationMissingError as err:
        display_missing_config_message(config_file)
    else:
        choice = click.prompt(
            click.style(
                "Use 'chaosiq' init feature or the chaostoolkit 'default'",
                dim=True),
            default="default", show_default=True,
            type=click.Choice(['default', 'chaosiq']))

    if choice == "default":
        experiment = ctx.forward(chtk_init)

        if config:
            call_chaosiq_api(
                "/v1/flow/init/", payload=experiment, config=config,
                expected_status=201)
        return

    if not os.path.exists(discovery_path):
        click.secho(
            "No discovery output found.\n\n"
            "Are you running from a directory where the discovery\n"
            "output, usually `discovery.json`, is located? You can\n"
            "specify the path to that file with `--discovery-path`.\n"
            "Alternatively, have you run `chaos discover` already?\n",
            err=True)
        return

    discovery = None
    with open(discovery_path) as d:
        discovery = json.loads(d.read())

    suggested_experiments = discovery.get("experiments", [])
    if not suggested_experiments:
        click.secho(
            "No experiments found in the discovery output.\n\n"
            "Have you run the `chaos discover command yet?\n", err=True)
        return

    experiments = []
    for experiment in suggested_experiments:
        experiments.append((
            experiment["title"],
            experiment
        ))

    experiment = select_experiment(experiments)
    m = "You have selected experiment: '{t}'".format(t=experiment["title"])
    logger.debug(m)
    click.echo(m)

    r = call_chaosiq_api(
        "/v1/flow/init/", payload=experiment, config=config,
        expected_status=201)
    if r:
        experiment = r.json()

    m = "Saving to '{e}'".format(e=experiment_path)
    logger.debug(m)
    click.echo(m)
    with open(experiment_path, "w") as e:
        e.write(json.dumps(experiment, indent=4))

    m = "You may now run this experiment with `chaos run {e}`".format(
        e=experiment_path)
    logger.debug(m)
    click.echo(m)

    return experiment


@click.command(help=chtk_run.__doc__)
@click.option('--journal-path', default="./journal.json",
              help='Path where to save the journal from the execution.')
@click.option('--dry', is_flag=True,
              help='Run the experiment without executing activities.')
@click.option('--no-validation', is_flag=True,
              help='Do not validate the experiment before running.')
@click.argument('path', type=click.Path(exists=True))
@click.pass_context
def run(ctx: click.Context, path: str, journal_path: str="./journal.json",
        dry: bool=False, no_validation: bool=False):
    journal = ctx.forward(chtk_run)

    try:
        config_file = os.environ.get(
            "CHAOISQ_CONFIG_PATH", CHAOISQ_CONFIG_PATH)
        config = load_config(click.format_filename(config_file))
    except ConfigurationMissingError as err:
        display_missing_config_message(config_file)
    else:
        r = call_chaosiq_api(
            "/v1/flow/run/", payload=journal, config=config,
            expected_status=201)
        if r:
            journal = r.json()

    return journal


###############################################################################
# Private functions
###############################################################################
def select_experiment(experiments: List[Experiment]) -> Experiment:
    """
    Prompt the user to select an experiment from the list of experiments
    found in the discovery.
    """
    echo = click.echo
    if len(experiments) > 10:
        echo = click.echo_via_pager

    echo("\n".join([
        "{i}) {t}".format(
            i=idx+1, t=title) for (idx, (title, exp)) in enumerate(
                experiments)]))
    index = click.prompt(
        click.style('Please select an experiment', fg='green'), type=int)

    index = index - 1
    if index > len(experiments):
        click.secho("This is not a valid experiment", fg="yellow")
        return select_experiment(experiments)

    experiment = experiments[index]
    return experiment[1]


def display_missing_config_message(config_file: str):
    """
    Log a user-friendly and actionable message when chaosiq was not configured.
    """
    logger.debug("chaosiq not configured")
    click.secho("\nYou have installed the `chaosiq` package but you\n"
                "don't seem to have configured it.\n\n"
                "To benefit from ChaosIQ, you must have registered\n"
                "with http://chaosiq.io and used the `chaosiq login`\n"
                "command to store your token in '{}'.\n\n"
                "If you do not intend on using the ChaosIQ services,\n"
                "you should uninstall the package with\n"
                "`pip uninstall chaosiq` and run this command again.\n\n"
                "We will continue with the default chaostoolkit behavior.\n"
                .format(config_file), dim=True, err=True)
