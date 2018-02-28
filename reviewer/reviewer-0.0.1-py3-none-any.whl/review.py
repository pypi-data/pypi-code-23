#!/usr/bin/env python
import logging
import os
import re
import subprocess

import fire
import requests


def cmr(name=None, assignee=None, ds=False, help=False):
    """Create a gitlab merge request.

    :param name(String): the name of your branch and merge request that will be created
    :param assignee(String): the gitlab name to who you want to assign the MR
    :param ds(Boolean): flag to mark if the source branch will be deleted after merging
    :param help(Boolean): get usage info
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    logger.addHandler(ch)
    
    if help:
        subprocess.run(['review.py', '--', '--help'])
        return
    gitlab_token = os.getenv('GITLAB_TOKEN')
    if gitlab_token is None:
        print("No Gitlab private token found in environment variables, please set one and try again")
        return
    subprocess.run(['git', 'branch', name])
    subprocess.run(['git', 'push', 'origin', name])
    headers = {'PRIVATE-TOKEN': gitlab_token}

    # remote_url = subprocess.check_output(['git', 'remote', '-v'])

    output = subprocess.check_output(['git', 'ls-remote', '--get-url', 'origin']).decode("utf-8")
    project_name = re.sub(r'^.+\:(.+)\.git', r'\1', output).strip()
    project_id_url = re.sub(r'/', r'%2F', project_name)
    
    hostname = re.sub(r'^.*[@:](.+\..+)[\:].+', r'\1', output).strip()
    
    logger.info('URL safe project name: ' + project_id_url)
    logger.info('Remote hostname: ' + hostname)
    project_id_int = int(requests.get("http://" + hostname + "/api/v4/projects/" + project_id_url, headers=headers).json()['id'])

    payload = {
            'id': project_id_int,
            'source_branch': name,
            'target_branch': 'master',
            'title': name
            }
    if assignee:
        assignee_id = _get_user_id(assignee, hostname)
        if assignee_id:
            assignee_id_int = int(assignee_id)
        else:
            print("Assignee not found")
            return

        payload['assignee_id'] = assignee_id_int

    if ds:
        payload['remove_source_branch'] = 'true'

    req = requests.post('http://' + hostname + '/api/v4/projects/' + project_id_url + '/merge_requests', headers=headers, data=payload)
    logger.info('Response Status: %d' % (req.status_code))
    response_json = req.json()
    print("Merge request successfully created with name {name}.\n Click here {url}".format(name=response_json['title'], url=response_json['web_url']))


def _get_user_id(assignee, hostname):
    users = _get_users(hostname)
    for user in users:
        if user['name'] == assignee:
            return user['id']
    return None

def _get_users(hostname, url=None):
    gitlab_token = os.getenv('GITLAB_TOKEN')
    headers = {'PRIVATE-TOKEN': gitlab_token}
    if url:
        response = requests.get(url, headers=headers)
    else:
        response = requests.get("http://" + hostname + "/api/v4/users?per_page=80", headers=headers)
    users = response.json()
    if 'next' in response.links:
        return users + _get_users(hostname, response.links['next']['url'])
    else:
        return users

if __name__ == "__main__":
    fire.Fire(cmr)
