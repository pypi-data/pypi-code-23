import click

from seed_services_client.control_interface import ControlInterfaceApiClient


def get_api_client(url, token):
    return ControlInterfaceApiClient(
        api_url=url,
        auth_token=token
    )


@click.pass_context
def status(ctx):
    """ Get service status
    """
    api = get_api_client(ctx.obj.ci.api_url, ctx.obj.ci.token)
    click.echo("Getting all service status")
    for service in api.get_services()['results']:
        if service["up"]:
            status = "up"
        else:
            status = "down"
        click.echo("Service %s is %s. Last check: %s" % (service["name"],
                   status, service["updated_at"]))


@click.option(
    '--email', '-e',
    help='Email address')
@click.option(
    '--user', '-u',
    help='User ID')
@click.pass_context
def user_tokens_generate(ctx, email, user):
    """ Trigger generation of a users service tokens
    """
    api = get_api_client(ctx.obj.ci.api_url, ctx.obj.ci.token)
    if not all((email, user)):
        raise click.UsageError(
            "Please specify all user information. See --help.")
    click.echo("Triggering token creation for %s" % (email,))
    user = {
        "email": email,
        "user_id": user
    }
    result = api.generate_user_service_tokens(user)
    if result["user_service_token_initiated"]:
        click.echo("Triggered generation of %s tokens" % result["count"])
    else:
        click.echo("Triggering generation of tokens failed")
