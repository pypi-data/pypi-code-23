"""

authenticate.py
~~~~~~~~

authenticates your quoteBot with twitter

Authenticates your quoteBot app using the quotebot "app" via twitter if an
auth.py file is not present for use. Note: This "app" does nothing but create
the necessary credentials for your bot to tweet from the commandline.

If you do not trust the app, please read the docs for how to acquire the
credentials necessary for your bot :).

TODO: oauth dance for those who did not make an auth.py file

:copyright: @ 2018
:author: elias julian marko garcia
:license: MIT, see LICENSE

"""

import click
import webbrowser

from time import sleep
from tweepy import OAuthHandler, TweepError, API
from quoteBot.commands.secrets import CONSUMER_KEY, CONSUMER_SECRET


@click.command()
def authenticate():
    """Authenticate your quoteBot with twitter."""

    click.echo("Lets get your quoteBot ready to tweet!")
    # TODO check for auth.py
    user_auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    try:
        app_url = user_auth.get_authorization_url()
    except TweepError:
        click.echo('Error! Failed to get authentification url. Retry again.')

    click.echo("""
twitter will now ask for app permission for Quotebot. After giving permission,
twitter will give you a PIN number. Copy and paste it back here.
    """)

    # opening browser puts error output to terminal that can hide instructions
    sleep(5)

    webbrowser.open(app_url)

    # opening browser is also a lagged command and can also hide input prompt
    sleep(2)

    click.echo("Enter your PIN: ")

    try:
        verifier = input()
    except RuntimeError:
        click.echo(
            "Something went wrong with that input. Try authenticating again")
    click.echo(verifier)

    user_auth.get_access_token(verifier)
    click.echo(user_auth.access_token)
    click.echo(user_auth.access_token_secret)

    user_auth.set_access_token(user_auth.access_token,
                               user_auth.access_token_secret)
    user_api = API(user_auth)
    click.echo("Success! Nice to meet you, {}".format(user_api.me().name))
