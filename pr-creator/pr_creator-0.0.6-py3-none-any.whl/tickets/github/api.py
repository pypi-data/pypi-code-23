import re
import subprocess
import requests
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
from ..settings import GITHUB_TOKEN

pr_urls = OrderedDict()
pr_urls['eab_base'] = "https://api.github.com/repos/advisory/eab_base/pulls"
pr_urls['student-path'] = "https://api.github.com/repos/advisory/student-path/pulls"
pr_urls['greendale'] = "https://api.github.com/repos/advisory/greendale/pulls"
pr_urls['notification-service'] = "https://api.github.com/repos/advisory/notification-service/pulls"


def get_user():
    regex = re.compile("(?<=Hi )(.*)(?=! You've)")

    try:
        subprocess.check_output("ssh -T git@github.com 2>&1", shell=True)
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode('utf-8')
        if "You've successfully authenticated, but GitHub does not provide shell access." in output:
            # We were actually successful
            return regex.search(output).group(1)
        else:
            raise


def get_or_create_pull_request(url, params, args):

    payload = {
        "title": args.branch_name,
        "body": "Placeholder",
    }
    payload.update(params)

    payload['head'] = "advisory:{0}".format(payload['head'])

    # Check for existence
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(args.user, GITHUB_TOKEN),
        params=payload
    )

    if resp.status_code in (200, 201):
        # PR already exists
        if len(resp.json()) == 1:
            return resp.json()[0]
        elif len(resp.json()) > 1:
            raise RuntimeError("Too many PRs exist for url: {0}, user: {1}, params: {2}".format(
                url, args.user, params))

    # We need to create
    resp = requests.post(
        url,
        auth=HTTPBasicAuth(args.user, GITHUB_TOKEN),
        json=payload
    )

    if resp.status_code in (200, 201):
        return resp.json()
    else:
        raise RuntimeError("We couldn't get or create the PR for url: {0}, user: {1}, params: {2}".format(
            url, args.user, params))


def update_pr(url, body, args):

    payload = {
        "body": body,
    }

    # Check for existence
    resp = requests.patch(
        url,
        auth=HTTPBasicAuth(args.user, GITHUB_TOKEN),
        json=payload
    )

    if resp.status_code not in (200, 201):
        # PR already exists
        raise RuntimeError("Couldn't update PR {0}".format(url))
