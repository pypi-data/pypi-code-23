#    Copyright 2018 Ultronix
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import requests
import sys
import click


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('prbit v.0.1.5')
    ctx.exit()


@click.group()
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def cli():
    pass


@click.command()
@click.option('--username', '-u', prompt='Username',  help='Username of Bitbucket Account')
@click.option('--password', '-p', prompt='Password', hide_input=True,
              confirmation_prompt=True,  help='Password of Bitbucket Account')
def config(username, password):
    data = {}
    data['username'] = username
    data['password'] = password
    with open('config.json', 'w') as f:
        json.dump(data, f)
    click.echo('.:Config Complete:.')


@click.command()
@click.option('--topic', '-t', prompt='Pull Request\nTopic', help='Topic of Pull-Request')
@click.option('--description', '-d', prompt='Description', help='Description of Pull-Request')
@click.option('--repo', '-r', prompt='Repository', help='Repository of Pull-Request')
@click.option('--source', '-s', prompt='From Branch', help='Source Branch')
@click.option('--target', '-t', prompt='To Branch', help='Target Branch')
@click.option('--reviewer', '-u', prompt='Reviewer', help='Assign some user to review')
def create(topic, description, source, repo, target, reviewer):
    config = {}
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        click.echo('!! Please Create Config file with: prbit create')
        sys.exit()

    try:
        url = "https://bitbucket.org/api/2.0/repositories/"+repo+"/pullrequests"
        headers = {'Content-Type': 'application/json'}

        data = '''{ "title": "%s", "description": "%s"
            , "source": { "branch": { "name": "%s" }
            , "repository": { "full_name": "%s" } }
            , "destination": { "branch": { "name": "%s" } }
            , "reviewers": [ { "username": "%s" } ]
            , "close_source_branch": false }''' % (topic, description, source, repo, target, reviewer)

        response = requests.post(url, auth=(
            config['username'], config['password']), headers=headers, data=data)
        click.echo('.:Create Pull Request Complete:.')
    except:
        click.echo('!! Something went wrong, Please try again')


cli.add_command(config)
cli.add_command(create)
