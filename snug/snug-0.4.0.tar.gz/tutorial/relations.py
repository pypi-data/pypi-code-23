import json
import snug
from collections import namedtuple
from gentools import reusable, map_send, map_yield, map_return

add_prefix = snug.prefix_adder('https://api.github.com')
add_headers = snug.header_adder({
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'my awesome app',
})

Repository = namedtuple(...)
Issue = namedtuple(...)
User = namedtuple(...)

class ApiException(Exception):
    """an error from the github API"""

def handle_errors(resp):
    """raise a descriptive exception on a "bad request" response"""
    if resp.status_code == 400:
        raise ApiException(json.loads(resp.data).get('message'))
    return resp

def load_json_content(resp):
    """get the response body as JSON"""
    return json.loads(resp.data)

def follow_redirects(req):
    resp = yield req
    while resp.status_code in (301, 302, 307):
        resp = yield req.replace(url=resp.headers['Location'])
    return resp

class repo(snug.Query[Repository]):
    """a repository lookup by owner and name"""
    def __init__(self, name, owner):
        self.name, self.owner = name, owner

    @map_send(load_json_content, handle_errors)
    @map_yield(add_headers, add_prefix, snug.GET)
    def __iter__(self):
        return Repository(**(yield f'/repos/{self.owner}/{self.name}'))

    @reusable
    @map_send(load_json_content, handle_errors)
    @map_yield(add_headers, add_prefix)
    def new_issue(self, title: str, body: str='') -> snug.Query[Issue]:
        """create a new issue in this repo"""
        request = snug.POST(
            f'/repos/{self.owner}/{self.name}/issues',
            data=json.dumps({'title': title, 'body': body}))
        return Issue(**(yield request))

    @reusable
    @map_send(handle_errors)
    @map_yield(add_headers, add_prefix, snug.PUT)
    def star(self) -> snug.Query[bool]:
        """star this repo"""
        response = yield f'/user/starred/{self.owner}/{self.name}'
        return response.status_code == 204


class user(snug.Query[User]):
    """a user lookup by name"""
    def __init__(self, username):
        self.username = username

    @map_send(load_json_content, handle_errors)
    @map_yield(add_headers, add_prefix, snug.GET)
    def __iter__(self):
        return User(**(yield f'/users/{self.username}'))

    @snug.query(related=True)
    @map_send(handle_errors)
    @map_yield(add_headers, add_prefix, snug.PUT)
    def follow(self) -> snug.Query[bool]:
        """follow this user"""
        return (yield f'/user/following/{self.username}').status_code == 204
