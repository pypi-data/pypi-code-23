"""
hrjota ecs service roller
"""
import boto3
import click
import json


ECS = boto3.client('ecs')


def jsond(data, sort=True, indent=2):
    """dumps a pretty looking json of the data"""
    return json.dumps(data, sort_keys=sort, indent=indent)


def get_definition(task):
    """given a task name, return the definition"""
    try:
        task_def = ECS.describe_task_definition(taskDefinition=task)
        return task_def['taskDefinition']
    except Exception:
        return False


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
def roll(cluster, service, image, dry):
    """roll the ecs service to the new image"""
    # grab the old definition
    new_task_definition = get_definition(service)

    # update the new image
    new_task_definition['containerDefinitions'][0]['image'] = image

    # remove fields we don't need
    del new_task_definition['compatibilities']
    del new_task_definition['revision']
    del new_task_definition['status']
    del new_task_definition['taskDefinitionArn']
    del new_task_definition['requiresAttributes']

    # print if dry run, else, register new
    if dry:
        click.echo(jsond(new_task_definition))
        return
    else:
        new_task = ECS.register_task_definition(**new_task_definition)
        if not new_task['taskDefinition']['taskDefinitionArn']:
            click.echo('failed to create new task')
            return
        click.echo('rolling {service}'.format(service=service))
        updated = ECS.update_service(
            cluster=cluster,
            service=service,
            taskDefinition=new_task['taskDefinition']['taskDefinitionArn'],
            forceNewDeployment=True
        )
        click.echo(
            'rolled {service}:\n{response}'.format(
                service=service,
                response=updated
            )
        )


if __name__ == '__main__':
    cli()
