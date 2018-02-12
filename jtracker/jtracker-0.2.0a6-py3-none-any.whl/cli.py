import datetime
import json
import click
from click import echo
from . import __version__ as ver
from jtracker.cli import UserClient
from .client import OrgClient
from .client import WorkflowClient
from .client import JobClient
from .client import QueueClient
from .client import Config
from jtracker.execution import Executor


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('jtracker %s' % ver)
    ctx.exit()


@click.group()
@click.option('--config-file', '-c', envvar='JT_CONFIG_FILE', default='.jt/config', required=False)
@click.option('--version', '-v', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.pass_context
def main(ctx, config_file):
    # initialize configuration from config_file
    jt_config = Config(config_file).dict

    # initializing ctx.obj
    ctx.obj = {
        'JT_CONFIG_FILE': config_file,
        'JT_CONFIG': jt_config
    }


@main.command()
@click.pass_context
def config(ctx):
    """
    View or update JT cli configuration
    """
    echo(json.dumps(ctx.obj.get('JT_CONFIG')))
    echo('*** other features to be implemented ***')


@main.command()
@click.option('-w', '--workflow-name', help='Workflow full name, eg, [{owner}/]{workflow}:{ver}')
@click.option('-f', '--workflow-file', type=click.Path(exists=True), help='Local workflow file')
@click.option('-j', '--job-file', type=click.Path(exists=True), help='Job file')
@click.option('-q', '--queue', type=str, help='Job queue ID')
@click.option('-n', '--n-workers', type=int, default=2, help='Max number of parallel workers')
@click.option('-m', '--n-jobs', type=int, default=1, help='Max number of parallel running jobs')
@click.pass_context
def executor(ctx, job_file, queue, workflow_name, workflow_file, n_jobs, n_workers):
    """
    Launch JT executor
    """
    jt_executor = Executor(jt_home=ctx.obj['JT_CONFIG'].get('jt_home'),
                           ams_server=ctx.obj['JT_CONFIG'].get('ams_server'),
                           wrs_server=ctx.obj['JT_CONFIG'].get('wrs_server'),
                           jess_server=ctx.obj['JT_CONFIG'].get('jess_server'),
                           job_file=job_file,
                           queue=queue,
                           workflow_name=workflow_name,
                           workflow_file=workflow_file,
                           parallel_jobs=n_jobs,
                           parallel_workers=n_workers,
                           )

    jt_executor.run()


@main.command()
@click.pass_context
def workflow(ctx):
    """
    Operations related to workflow
    """
    pass


@main.command()
@click.pass_context
def job(ctx):
    """
    Operations related to job
    """
    pass


@main.command()
@click.pass_context
def queue(ctx):
    """
    Operations related to job queue
    """
    pass


@main.command()
@click.pass_context
def user(ctx):
    """
    Operations related to user
    """
    pass


@main.command()
@click.pass_context
def org(ctx):
    """
    Operations related to organization
    """
    pass


if __name__ == '__main__':
    main()

