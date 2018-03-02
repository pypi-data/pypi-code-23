import click
import webbrowser

import russell
from russell.client.auth import AuthClient
from russell.manager.auth_config import AuthConfigManager
from russell.model.access_token import AccessToken
from russell.log import logger as russell_logger
from russell.client.common import get_basic_token


def login_with_token(token):
    access_code = get_basic_token(token)

    user = AuthClient().get_user(access_code)
    access_token = AccessToken(username=user.username,
                               token=access_code)
    AuthConfigManager.set_access_token(access_token)
    russell_logger.info("Login Successful as " + user.username)


def login_with_username_and_password(username, password):
    token_dict = AuthClient().get_token(username, password)
    login_with_token(token_dict['token'])


@click.command()
@click.option('-t', '--token', is_flag=True, default=False, help='Just enter token')
@click.option('-u', '--username',
              help='Input username/email to login. If --token if provided, this option will be ignored')
@click.option('-p', '--password',
              help="Input password to login. If password is not given it's asked from the tty."
                   "If --token if provided, this option will be ignored")
def login(token, username, password):
    """
    Log into Russell via Auth0.
    """
    if token:
        token = str(click.prompt('Please copy and paste the token here', type=str, hide_input=True))
        login_with_token(token)
    elif username:
        if not password:
            password = str(click.prompt("Password", type=str, hide_input=True))
        login_with_username_and_password(username, password)
    elif click.confirm('Authentication token page will now open in your browser. Continue?', default=True):
        webbrowser.open(russell.russell_web_host + "/welcome")
        token = str(click.prompt('Please copy and paste the token here', type=str, hide_input=True))
        if not token:
            russell_logger.info("Empty token received. Make sure your shell is handling the token appropriately.")
            russell_logger.info("See FAQ for help: http://docs.russellcloud.cn/")
        else:
            login_with_token(token)
    else:
        russell_logger.info("Login with your russell username/email and password. "
                            "If you don't have a Russell account, "
                            "head over to http://russellcloud.com to create one.")
        username = str(click.prompt("Username/Email", type=str))
        password = str(click.prompt("Password", type=str, hide_input=True))
        if not username or not password:
            russell_logger.info("Please make sure username and password are both provided.")
        else:
            login_with_username_and_password(username, password)


@click.command()
def logout():
    """
    Logout of Russell.
    """
    AuthConfigManager.purge_access_token()
