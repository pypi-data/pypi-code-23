"""
hrjota ecs service roller
"""
import boto3
import click
import time
from hrjota.globals import (
    BAD_FIELDS,
    DEFAULT_INTERVAL,
    DEFAULT_WAIT_TIME
)
from hrjota.utils.text import (
    jsond
)

ECS = boto3.client('ecs')


def is_rolling(cluster='', service=''):
    """determines if the service is still rolling"""
    state = ECS.describe_services(cluster=cluster, services=[service])
    deployments = state['services'][0]['deployments']
    if len(deployments) == 1:
        return False
    return True


def get_definition(task):
    """given a task name, return the definition"""
    task_def = ECS.describe_task_definition(taskDefinition=task)
    return task_def['taskDefinition']


@click.group()
def cli():
    """create a cli interface super group"""
    pass


@cli.group()
def tasks():
    """tasks subgroup"""
    pass


@tasks.command(name='ls')
@click.option('--cluster', '-c', required=True, help='cluster name')
def ls_tasks(cluster):
    """list tasks"""
    data = ECS.list_tasks(cluster=cluster)
    click.echo(data['taskArns'])


@tasks.command(name='def')
@click.option('--task', '-t', required=True, help='task name')
def def_task(task):
    """list tasks"""
    click.echo(jsond(get_definition(task)))


@cli.group()
def services():
    """services sub group"""
    pass


@services.command(name='ls')
@click.option('--cluster', '-c', required=True, help='cluster name')
def ls_services(cluster):
    """list services"""
    data = ECS.list_services(cluster=cluster)
    click.echo(data['serviceArns'])


@cli.command()
@click.option('--cluster', '-c', required=True, help='cluster name')
@click.option('--service', '-s', required=True, help='service name')
@click.option('--image', '-i', required=True, help='image name')
@click.option('--dry', is_flag=True, default=False)
@click.option('--timeout', '-t', default=DEFAULT_WAIT_TIME, help='max time to wait')
@click.option('--interval', '-i', default=DEFAULT_INTERVAL, help='interval to poll at')
@click.option('--rollback', '-r', is_flag=True, default=True, help='enable rollback')
@click.option('--nowait', is_flag=True, default=False, help='enable nowait for the service to roll')
def roll(cluster, service, image, dry, timeout, interval, rollback, nowait):
    """roll the ecs service to the new image"""
    def update(task_definition, force=True):
        """given a task definition, update the service"""
        return ECS.update_service(
            cluster=cluster,
            service=service,
            taskDefinition=task_definition,
            forceNewDeployment=force
        )

    # grab the old definition
    old_task_definition = get_definition(service)
    old_arn = old_task_definition['taskDefinitionArn']
    new_task_definition = get_definition(service)

    # update the new image
    new_task_definition['containerDefinitions'][0]['image'] = image

    # remove fields we don't need
    for field in BAD_FIELDS:
        del new_task_definition[field]

    # print if dry run, else, register new
    if dry:
        click.echo(jsond(new_task_definition))
        return False
    else:
        # create a new task based on the old one
        new_task = ECS.register_task_definition(**new_task_definition)
        if not new_task['taskDefinition']['taskDefinitionArn']:
            click.echo('[-] failed to create new task')
            return False

        # try to roll the task
        click.echo('rolling {service}'.format(service=service))
        updated = update(new_task['taskDefinition']['taskDefinitionArn'])

        if not nowait:
            # lets wait for the update
            time_waited = 0
            while is_rolling(cluster=cluster, service=service):
                if time_waited >= timeout:
                    # if we've waited too long, attempt a rollback
                    click.echo('[-] failed to roll before the timeout!')
                    click.echo('[-] rolling back {service}'.format(service=service))
                    updated = update(old_arn, force=False)
                    return False
                click.echo('[+] waiting for roll to complete - pending')
                time_waited += interval
                time.sleep(interval)
        click.echo(
            '[+] rolled {service}:\n{response}'.format(
                service=service,
                response=updated
            )
        )
    return True


if __name__ == '__main__':
    cli()
