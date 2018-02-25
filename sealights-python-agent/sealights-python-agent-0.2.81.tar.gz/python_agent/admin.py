import logging
import sys
from distutils.util import strtobool

from coverage.cmdline import Opts, unshell_list

from python_agent.build_scanner.executors.build import Build
from python_agent.build_scanner.executors.config import Config
from python_agent.common import constants
from python_agent.common.config_data import ConfigData
from python_agent.common.configuration_manager import ConfigurationManager
from python_agent.common.constants import DEFAULT_WORKSPACEPATH
from python_agent.packages import click
from python_agent.test_listener.executors.end_execution import EndAnonymousExecution
from python_agent.test_listener.executors.run import Run
from python_agent.test_listener.executors.send_footprints import SendFootprintsAnonymousExecution
from python_agent.test_listener.executors.start_execution import StartAnonymousExecution
from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution
from python_agent.test_listener.executors.test_frameworks.pytest_execution import PytestAgentExecution
from python_agent.test_listener.executors.test_frameworks.unittest2_execution import Unittest2AgentExecution
from python_agent.test_listener.executors.test_frameworks.unittest_execution import UnittestAgentExecution
from python_agent.test_listener.executors.upload_reports import UploadReports
from python_agent.test_listener.managers.agent_manager import AgentManager

log = logging.getLogger(__name__)


CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower(), ignore_unknown_options=True, allow_extra_args=True)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--token", help="Token (mandatory. Can also be provided by 'tokenfile' argument). Case-sensitive.")
@click.option("--tokenfile", help="A path to a file where the program can find the token. Case-sensitive.")
@click.option("--buildsessionid", help="Provide build session id manually, case-sensitive.")
@click.option("--buildsessionidfile", help="Path to a file to save the build session id in (default: <user.dir>/buildSessionId.txt).")
@click.option("--proxy", help="Proxy. Must be of the form: http[s]://<server>")
@click.pass_context
def cli(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy):
    configuration_manager = ConfigurationManager()
    token_data, token = configuration_manager.resolve_token_data(token, tokenfile)
    if not token:
        sys.exit(1)

    configuration_manager.config_data = ConfigData(token, token_data.customerId, token_data.server, proxy, None)
    if ctx.invoked_subcommand != "config":
        build_session_id = configuration_manager.resolve_build_session_id(buildsessionid, buildsessionidfile)
        configuration_manager.config_data.buildSessionId = build_session_id
        configuration_manager.update_build_session_data()
        configuration_manager.try_load_configuration()
        if not build_session_id:
            log.error("--buildsessionid or --buildsessionidfile must be provided")
            sys.exit(1)

    configuration_manager.init()

    ctx.obj = {
        "config_data": configuration_manager.config_data
    }


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--appname", required=True, help="Application name, case-sensitive.")
@click.option("--branchname", required=True, help="Branch name, case-sensitive.")
@click.option("--buildname", required=True, help="Build id, case-sensitive. Should be unique between builds.")
@click.option("--buildsessionid", required=False, help="Provide build session id manually, case-sensitive.")
@click.option("--workspacepath", help="Path to the workspace where the source code exists", default=DEFAULT_WORKSPACEPATH, type=unshell_list)
@click.option("--include", help=Opts.include.help, default=None, type=unshell_list)
@click.option("--exclude", help=Opts.omit.help, default=None, type=unshell_list)
@click.pass_context
def config(ctx, appname, branchname, buildname, buildsessionid, workspacepath, include, exclude):
    Config(ctx.obj["config_data"], appname, branchname, buildname, buildsessionid, workspacepath, include, exclude).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def build(ctx):
    Build(ctx.obj["config_data"]).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV, help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def pytest(ctx, labid, teststage, args):
    PytestAgentExecution(ctx.obj["config_data"], labid, teststage, args).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV, help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.option("--junit", default="false", type=strtobool, help="Output results in the a junit xml format")
@click.option("--output", default=".", help="Output location of the junit xml report")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def unittest(ctx, labid, teststage, junit, output, args):
    UnittestAgentExecution(ctx.obj["config_data"], labid, teststage, junit, output, args).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV, help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def unit2(ctx, labid, teststage,  args):
    Unittest2AgentExecution(ctx.obj["config_data"], labid, teststage, args).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV,
              help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.pass_context
def start(ctx, teststage, labid):
    StartAnonymousExecution(ctx.obj["config_data"], teststage, labid).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.pass_context
def end(ctx, labid):
    EndAnonymousExecution(ctx.obj["config_data"], labid).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--reportfile", type=unshell_list,
              help="Report files. This argument can be declared multiple times in order to upload multiple files.")
@click.option("--reportfilesfolder", type=unshell_list,
              help="Folders that contains nothing but report files. All files in folder will be uploaded. This argument can be declared multiple times in order to upload multiple files from multiple folders.")
@click.option("--source", default="Junit xml report", help="The reports provider. If not set, the default will be 'Junit xml report'")
@click.option("--type", default="JunitReport", help="The report type. If not set, the default will be 'JunitReport'")
@click.option("--hasmorerequests", default="true", type=strtobool,
              help="flag indicating if test results contains multiple reports. True for multiple reports. False otherwise")
@click.pass_context
def uploadreports(ctx, labid, reportfile, reportfilesfolder, source, type, hasmorerequests):
    UploadReports(ctx.obj["config_data"], labid, reportfile, reportfilesfolder, source, type, hasmorerequests).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.argument('args', required=True, nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, labid, args):
    ctx.obj["config_data"].args = sys.argv
    Run(ctx.obj["config_data"], labid).execute(args)


@cli.command(hidden=True, context_settings=CONTEXT_SETTINGS)
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.pass_context
def sendfootprints(ctx, labid):
    ctx.obj["config_data"].isOfflineMode = True
    SendFootprintsAnonymousExecution(ctx.obj["config_data"], labid).execute()


@cli.command(hidden=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def bootstrap(ctx):
    AgentManager(config_data=ctx.obj["config_data"])


@cli.command(hidden=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def init(ctx):
    AgentExecution(ctx.obj["config_data"], None)


if __name__ == '__main__':
    cli()
