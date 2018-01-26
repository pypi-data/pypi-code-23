import click

from seed_services_client.auth import AuthApiClient


def get_api_client(email, password, url):
    return AuthApiClient(
        email=email,
        password=password,
        api_url=url
    )


@click.option(
    '--email', '-e',
    help='Email address')
@click.option(
    '--password', '-p',
    help='Password')
@click.option(
    '--first_name', '-f',
    help='Email address')
@click.option(
    '--last_name', '-l',
    help='Email address')
@click.option(
    '--admin', '-a',
    help='Admin', is_flag=True)
@click.pass_context
def user_add(ctx, email, password, first_name, last_name, admin):
    """ Create a user
    """
    api = get_api_client(ctx.obj.auth.email,
                         ctx.obj.auth.password,
                         ctx.obj.auth.api_url
                         )
    if not all((email, password, first_name, last_name)):
        raise click.UsageError(
            "Please specify all new user information. See --help.")
    click.echo("Creating account for %s" % (email,))
    user = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "admin": admin
    }
    result = api.create_user(user)
    click.echo("Created user. ID is %s." % result["id"])


@click.option(
    '--email', '-e',
    help='Email address')
@click.option(
    '--password', '-p',
    help='Password')
@click.pass_context
def user_change_password(ctx, email, password):
    """Change a user's password
    """
    api = get_api_client(ctx.obj.auth.email,
                         ctx.obj.auth.password,
                         ctx.obj.auth.api_url
                         )
    click.echo('{}'.format(api))
    if not all((email, password)):
        raise click.UsageError(
            "Please specify both the email and new password. See --help.")
    click.echo("Changing password for %s" % (email,))

    users = api.get_users()
    user = None
    for u in users:
        if u.get('email') == email:
            user = u
            break
    if user is None:
        raise click.UsageError(
            "No user found for email {}".format(email))

    user['password'] = password
    result = api.update_user(user['id'], user)
    click.echo("Updated user. {}".format(result))


@click.option(
    '--user', '-u',
    help='User ID')
@click.option(
    '--team', '-t',
    help='Team ID')
@click.pass_context
def user_add_team(ctx, user, team):
    """ Add a user to a team
    """
    api = get_api_client(ctx.obj.auth.email,
                         ctx.obj.auth.password,
                         ctx.obj.auth.api_url
                         )
    if not all((user, team)):
        raise click.UsageError(
            "Please specify user and team. See --help.")
    click.echo("Adding user %s to team %s" % (user, team,))
    result = api.add_user_to_team(user, team)
    if result:
        click.echo("Added user %s to team %s" % (user, team,))
    else:
        click.echo("Failed to add %s to %s" % (user, team,))
