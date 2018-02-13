# -*- coding: utf-8 -*-
import io
import json
import os
import os.path
import re
import textwrap
from typing import Dict, List

from chaoslib.discovery import discover as disco
from chaoslib.exceptions import DiscoveryFailed
from chaoslib.types import Activity, Discovery, Experiment
from chaostoolkit.cli import discover as chtk_discover
from chaostoolkit.cli import init as chtk_init
from chaostoolkit.cli import run as chtk_run
import click
from logzero import logger
import requests

from chaosiq.api import call_chaosiq_api
from chaosiq.config import load_config, CHAOISQ_CONFIG_PATH
from chaosiq.discovery import discover_system_info
from chaosiq.exceptions import ConfigurationMissingError

__all__ = ["discover", "init", "run"]
CandidateHashRe = re.compile(r"\{\{([a-z0-9]{56,56})\}\}")


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
        info = discover_system_info(discovery.get("target"))
        if info:
            discovery["system"] = info

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
        click.secho(
            "\nYou have installed `chaosiq` and can take the opportunity to\n"
            "let ChaosIQ guide you through creating rich chaos experiments\n"
            "tailored to your system.", fg="blue")

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
    m = "\nYou have selected the experiment: '{t}'".format(
        t=experiment["title"])
    logger.debug(m)
    click.secho(m, fg="magenta")

    desc = experiment.get("description")
    if desc:
        click.secho("\n".join(textwrap.wrap(desc, width=70)), dim=True)

    set_experiment_arguments(discovery, experiment)

    r = call_chaosiq_api(
        "/v1/flow/init/", payload=experiment, config=config,
        expected_status=201)
    if r:
        experiment = r.json()

    m = "\nSaving your experiment in '{e}'".format(e=experiment_path)
    logger.debug(m)
    click.secho(m)
    with open(experiment_path, "w") as e:
        experiment = sort_experiment_keys(experiment)
        e.write(json.dumps(experiment, indent=4, sort_keys=False))

    m = "\nYour experiment is now completed and saved. In some cases, this\n"\
        "is enough to go and run via `chaos run {}`. However,\n"\
        "we suggest you open the experiment and review it before executing\n"\
        "it.".format(experiment_path)
    logger.debug(m)
    click.secho(m, fg="blue")

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
            with io.open(journal_path, "w") as r:
                json.dump(journal, r, indent=2, ensure_ascii=False)

    return journal


###############################################################################
# Private functions
###############################################################################
def select_experiment(experiments: List[Experiment]) -> Experiment:
    """
    Prompt the user to select an experiment from the list of experiments
    found in the discovery.
    """
    click.secho(
        "\nWith the discovery of your system capabilities, ChaosIQ\n"
        "correlated relevant experiments with your system. You may now\n"
        "select one of those returned experiments to learn from your system\n"
        "under stress.\n"
        "Select now one of the experiments suggested by ChaosIQ:\n",
        fg="blue")

    echo = click.echo
    if len(experiments) > 10:
        echo = click.echo_via_pager

    echo("\n".join([
        "{i}) {t}".format(
            i=idx+1, t=title) for (idx, (title, exp)) in enumerate(
                experiments)]))
    index = click.prompt(
        click.style('\nPlease select an experiment', dim=True), type=int)

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


def set_experiment_arguments(discovery: Discovery, experiment: Experiment):
    """
    Iterate through all activities arguments and prompt the user for a choice
    whenever we gathered a candidate during discovery.
    """
    candidates = discovery.get("candidates")
    if not candidates:
        click.secho(
            "This experiment could not be matched against your system's\n"
            "state. This either means that none of the activities of this\n"
            "experiment expect your input. Or none could be set against any\n"
            "the discovered aspects of your system. Please, open the\n"
            "experiment file once this command finishes.\n", fg="blue")
        return

    exp_ref = experiment["chaosiq"]["suggested_experiment_ref"]
    if exp_ref in candidates:
        candidates = candidates[exp_ref]
        click.secho(
            "\nThis experiment contains activities which arguments were\n"
            "matched with candidates from your system by ChaosIQ. You can\n"
            "now pick the appropriate value for each argument now.",
            fg="blue")
        q = "Do you wish to set arguments from your discovered system?"

        if click.confirm(click.style(q, dim=True)):
            click.echo("")
            hypo = experiment.get("steady-state-hypothesis", {})
            probes = hypo.get("probes", [])
            if requires_filling(probes):
                click.secho(
                    "Fill the steady-state hypothesis probe arguments:")
                set_activity_arguments(probes, candidates)

            method = experiment.get("method", [])
            if requires_filling(method):
                click.secho("Fill the method activities arguments:")
                set_activity_arguments(method, candidates)

            rollbacks = experiment.get("rollbacks", [])
            if requires_filling(rollbacks):
                click.secho("Fill the rollbacks arguments:")
                set_activity_arguments(rollbacks, candidates)

            click.secho(
                "\nYou have now set all activities arguments!", fg="blue")

        replace_not_matched_arguments(experiment, candidates)


def replace_not_matched_arguments(experiment: Experiment,
                                  candidates: Dict[str, str]):
    """
    In case the experiment has remaining hashes that were not matched with a
    candidate, we replace those tokens with empty striings as friendlier to
    the user.
    """
    hypo = experiment.get("steady-state-hypothesis", {})
    activities = []
    activities.extend(hypo.get("probes", []))
    activities.extend(experiment.get("method", []))
    activities.extend(experiment.get("rollbacks", []))

    for activity in activities:
        arguments = activity.get("provider", {}).get("arguments", {})
        if arguments:
            for k, v in arguments.items():
                for m in CandidateHashRe.finditer(v):
                    hsh = m.group(1)
                    if hsh not in candidates:
                        v = v.replace(m.group(0), "")
                arguments[k] = v


def requires_filling(activities: List[Activity]):
    """
    Go through all activities and return `True` as soon as one of them
    requires the user to select a value from the candidates we discovered.
    """
    for activity in activities:
        arguments = activity.get("provider", {}).get("arguments", {})
        if arguments:
            for k, v in arguments.items():
                if CandidateHashRe.match(v):
                    return True
    return False


def set_activity_arguments(activities: List[Activity],
                           candidates: Dict[str, str]):
    """
    Prompt the user for argument values from the discovered candidates.
    """
    for activity in activities:
        arguments = activity.get("provider", {}).get("arguments", {})
        if not arguments:
            continue
        click.secho("\nActivity: {}".format(activity["name"]), fg="green")
        for (arg_key, arg_value) in arguments.items():
            click.secho(" Argument: {}".format(arg_key), fg="yellow")
            for m in CandidateHashRe.finditer(arg_value):
                hsh = m.group(1)
                if hsh in candidates:
                    values = candidates[hsh]
                    q = "Please, pick one of the following value "\
                        "for this argument"

                    click.secho("\n".join([
                        " {i}) {t}".format(
                            i=i+1,
                            t=v) for (i, v) in enumerate(values)]))
                    index = click.prompt(click.style(
                            'Select a value (0 to leave empty)',
                            dim=True), type=int)

                    index = index - 1
                    if index > len(values):
                        click.secho("Invalid choice", fg="red")
                        continue
                    elif index == -1:
                        arg_value = arg_value.replace(m.group(0), "")
                    else:
                        arg_value = arg_value.replace(
                            m.group(0), values[index])

            arguments[arg_key] = arg_value
            click.echo("")


def sort_experiment_keys(experiment: Experiment) -> Experiment:
    """
    Ensure the experiment keys are in the right order for use-friendlyness.
    The toolkit doesn't care either way but it makes the experiment much more
    readable and comprehensible.

    This works because in recent Python versions, insertion ordering is kept in
    a dictionary.
    """
    exp = {}
    if "version" in experiment:
        exp["version"] = experiment["version"]

    if "title" in experiment:
        exp["title"] = experiment["title"]

    if "description" in experiment:
        exp["description"] = experiment["description"]

    if "tags" in experiment:
        exp["tags"] = experiment["tags"]

    if "chaosiq" in experiment:
        exp["chaosiq"] = experiment["chaosiq"]

    if "configuration" in experiment:
        exp["configuration"] = experiment["configuration"]

    if "secrets" in experiment:
        exp["secrets"] = experiment["secrets"]

    if "steady-state-hypothesis" in experiment:
        exp["steady-state-hypothesis"] = experiment["steady-state-hypothesis"]

    if "method" in experiment:
        exp["method"] = experiment["method"]

    if "rollbacks" in experiment:
        exp["rollbacks"] = experiment["rollbacks"]

    return exp
