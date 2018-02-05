from __future__ import print_function
import logging
import click
import requests
import json
import sys

from cluspro_api import CONFIG, make_sig

logger = logging.getLogger(__name__)

URL_SCHEME = "https"
API_ENDPOINT = "/api_download.php"
CP_CONFIG = CONFIG['cluspro']
FORM_KEYS = [
    'username', 'secret', 'jobid'
]


@click.command('download', short_help="Download jobs from ClusPro.")
@click.option("--username", default=CP_CONFIG['username'])
@click.option("--secret", default=CP_CONFIG['api_secret'])
@click.argument("jobids", nargs=-1, required=True)
def cli(username, secret, jobids):
    if username is None or username == "None" or secret is None or secret == "None":
        if username is None or username == "None":
            username = click.prompt("Please enter your cluspro username")
            CP_CONFIG['username'] = username
        if secret is None or secret == "None":
            secret = click.prompt("Please enter your cluspro api secret")
            CP_CONFIG['api_secret'] = secret
        CONFIG.write()

    api_address = "{0}://{1}{2}".format(URL_SCHEME, CP_CONFIG['server'], API_ENDPOINT)
    for jobid in jobids:
        form = {
            k: v for k, v in locals().items() if k in FORM_KEYS and v is not None
        }

        form['sig'] = make_sig(form, secret)
        print(form)

        try:
            print("Downloading {}...".format(jobid), end="", file=sys.stderr)
            r = requests.post(api_address, data=form)

            if r.status_code != requests.codes.ok:
                print("ERROR", file=sys.stderr)
                for e in json.loads(r.text)['errors']:
                    print(e, file=sys.stderr)
                continue
            else:
                with open("cluspro.{}.tar.bz2".format(jobid), "wb") as out:
                    out.write(r.content)
            print("OK", file=sys.stderr)
        except:
            logger.error("Error downloading job {}".format(jobid))
