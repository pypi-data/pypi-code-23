"""
submission related util functions
"""
import click
import json
import os
import requests
import shutil
from mimir_cli.strings import (
    API_SUBMIT_URL,
    ERR_INVALID_FILE,
    SUB_CONFIRM_FORCE,
    SUB_SUCCESS_URL,
    SUB_WARNING,
    ZIP_LOC
)


def collect_submission_file(filename):
    """tries to collect the submission file and zip if need be"""
    submission_file = False
    if filename.lower().endswith('.zip'):
        submission_file = open(filename, 'rb')
    else:
        if os.path.isdir(filename):
            try:
                os.remove(ZIP_LOC)
            except OSError:
                pass
            shutil.make_archive(os.path.splitext(ZIP_LOC)[0], 'zip', filename)
            submission_file = open(ZIP_LOC, 'rb')
        else:
            submission_file = open(filename, 'rb')
    if not submission_file:
        click.echo(ERR_INVALID_FILE.format(filename))
    return submission_file


def _submit_post(url, filename, project_id, credentials):
    """actually perform the submit"""
    data = {'projectSubmission[projectId]': project_id}
    headers = {'Authorization': credentials['authToken']}
    submission_file = collect_submission_file(filename)
    files = {'zip_file[]': submission_file}
    click.echo('Submitting...')
    submission_request = requests.post(url, files=files, data=data, headers=headers)
    submission_file.close()
    result = json.loads(submission_request.text)
    if 'projectSubmission' in result:
        click.echo(SUB_SUCCESS_URL.format(result['projectSubmission']['id']))
    return result


def submit_to_mimir(filename, project_id, credentials):
    """submits file(s) to the mimir platform"""
    url = API_SUBMIT_URL.format(project_id)
    force_url = '{url}?ignore_filenames=true'.format(url=url)
    result = _submit_post(url, filename, project_id, credentials)
    if 'submitErrorMessage' in result:
        click.echo(SUB_WARNING)
        click.echo(result['submitErrorMessage'])
        if click.confirm(SUB_CONFIRM_FORCE):
            result = _submit_post(force_url, filename, project_id, credentials)
