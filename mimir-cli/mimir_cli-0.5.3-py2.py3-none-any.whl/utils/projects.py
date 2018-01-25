"""
project related utility functions
"""
import click
import json
import requests
from mimir_cli.strings import (
    API_URL,
    PROJECT_PROMPT
)
from mimir_cli.utils.io import (
    js_ts_to_str
)


NAME_JUSTIFY = 40


def print_projects(projects):
    """print a list of projects in a nice way"""
    project_strings = [
        '[{num}]\t{name}\t{remaining}\t{due}'.format(
            num=x,
            name=p['name'][:NAME_JUSTIFY].ljust(NAME_JUSTIFY),
            remaining=(
                '∞' if p['unlimitedSubmissions']
                else '{} left'.format(p['submissionsLeft'])
            ).ljust(10),
            due=js_ts_to_str(p['dueDate'])
        )
        for x, p in enumerate(projects)
    ]
    click.echo('num\t{}\tsubmissions\tdue date'.format(
        'project'.ljust(NAME_JUSTIFY),
    ))
    click.echo('-' * 91)
    click.echo('\n'.join(project_strings))


def get_projects_list(credentials):
    """gets the projects list for a user, sorted by due date"""
    url = '{base_url}/lms/projects'.format(base_url=API_URL)
    headers = {'Authorization': credentials['authToken']}
    projects_request = requests.get(url, headers=headers)
    result = json.loads(projects_request.text)
    sorted_projects = sorted(result['projects'], key=lambda x: x['dueDate'])
    return sorted_projects


def prompt_for_project(projects):
    """prompts for which project"""
    print_projects(projects)
    choice = click.prompt(PROJECT_PROMPT, type=int, default=0)
    return projects[choice]
