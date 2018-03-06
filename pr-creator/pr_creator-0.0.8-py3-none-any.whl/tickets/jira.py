from os import getenv
import requests
from requests.auth import HTTPBasicAuth
from .password import Password

JIRA_BASE_URL = 'https://workflow.advisory.com'
JIRA_PASSWD = getenv('JIRA_PASSWD', Password())
JIRA_USER = getenv('JIRA_USER', getenv('USER'))


def make_ticket(args):
    payload = {
        "fields": {
            "project": {
                "key": "NAV"
            },
            "summary": args.ticket_id,
            "customfield_10327": "{0} needs to write an acceptance.".format(args.user),
            "customfield_13600": "{0} needs to write a story.".format(args.user),
            "issuetype": {
                "name": "Story"
            }
        }
    }
    resp = requests.post(
        "{0}/rest/api/2/issue/".format(JIRA_BASE_URL),
        auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWD),
        json=payload
    )
    # returns {"id":"315527","key":"NAV-5467","self":"https://workflow.advisory.com/rest/api/2/issue/315527"}
    if resp.status_code in (200, 201):
        resp_data = resp.json()
        resp_data['access_url'] = ticket_url(args.ticket_id)
        return resp_data
    else:
        raise RuntimeError("Something went wrong talking to jira. {0}".format(dir(resp)))


def ticket_url(key):
    return "https://workflow.advisory.com/browse/{0}".format(key)
