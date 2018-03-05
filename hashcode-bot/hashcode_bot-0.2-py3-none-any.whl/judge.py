import json
import re
import base64
import functools

import attr
import pendulum
import requests

from googleapiclient import discovery
from google.oauth2.credentials import Credentials

DISCOVERY_URL = (
    'https://hashcode-judge.appspot.com/api/discovery/v1'
    '/apis/{api}/{apiVersion}/rest'
)

BLOBS_BASE_URL = 'https://hashcodejudge.withgoogle.com/download/'


def get_client_config(client_id, client_secret):
    return {
        'installed': {
            'client_id': client_id,
            'client_secret': client_secret,
            'project_id': '',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',  # NOQA
            'redirect_uris': [],
        },
    }


def build_hashcode_resource(credentials):
    return discovery.build(
        serviceName='judge',
        version='v1',
        discoveryServiceUrl=DISCOVERY_URL,
        credentials=credentials,
    )


def serialize_credentials(credentials):
    to_serialize = {
        'token': credentials.token,
        'id_token': credentials.id_token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
    }
    return base64.b64encode(
        json.dumps(to_serialize).encode('utf-8'),
    ).decode('ascii')


def unserialize_credentials(data):
    data = json.loads(base64.b64decode(data).decode('utf-8'))
    return Credentials(**data)


@attr.s
class Account:
    _client = attr.ib(repr=False)
    id = attr.ib(repr=False)
    email = attr.ib()
    first_name = attr.ib()
    last_name = attr.ib()
    country = attr.ib()
    _active_contestant = attr.ib()
    _active_hub_manager = attr.ib()
    _admin = attr.ib()
    _admin_ui_access = attr.ib()
    team = attr.ib()
    disabled = attr.ib()
    _can_be_admin = attr.ib()
    _team_id = attr.ib()
    _managed_hub_id = attr.ib()
    display_name = attr.ib()

    def __attrs_post_init__(self):
        if self.team:
            self.team = Team(
                client=self._client,
                **camelcase_to_snake_case(self.team),
            )


@attr.s
class Team:
    _client = attr.ib(repr=False)
    id = attr.ib(repr=False)
    name = attr.ib()
    finalist = attr.ib()
    _creation_time = attr.ib(convert=pendulum.parse, repr=False)
    countries = attr.ib()
    _hub_id = attr.ib(repr=False)
    team_size = attr.ib()


@attr.s
class DataSet:
    _client = attr.ib(repr=False)
    id = attr.ib(repr=False)
    name = attr.ib()
    _input_blob_key = attr.ib(repr=False)

    def request_input(self):
        return requests.get(
            BLOBS_BASE_URL + self._input_blob_key,
            stream=True,
        )

    @property
    def slug(self):
        return re.sub('[^a-z0-9]+', '_', self.name.lower())

    def submit(self, sources_blob, solution_path):
        return self._client.submit(
            self.id,
            sources_blob,
            self._client.upload(solution_path),
        )


@attr.s
class Round:
    _client = attr.ib(repr=False)
    id = attr.ib(repr=False)
    _problem_blob_key = attr.ib(repr=False)
    _scorer_label = attr.ib(repr=False)
    _visualization = attr.ib(repr=False)
    _hide_scoreboard = attr.ib(repr=False)
    _finalist_only = attr.ib(repr=False)
    _admin_only = attr.ib(repr=False)
    name = attr.ib()
    active = attr.ib()
    start = attr.ib(convert=pendulum.parse)
    end = attr.ib(convert=pendulum.parse)
    data_sets = attr.ib(
        repr=False,
    )
    freeze_start = attr.ib(
        default=None,
        converter=attr.converters.optional(pendulum.parse),
    )
    freeze_end = attr.ib(
        default=None,
        converter=attr.converters.optional(pendulum.parse),
    )

    def __attrs_post_init__(self):
        if self.data_sets:
            self.data_sets = [
                DataSet(client=self._client, **camelcase_to_snake_case(ds))
                for ds in self.data_sets
            ]

    def is_open(self, now=None):
        if now is None:
            now = pendulum.now()
        return self.active and self.start <= now < self.end

    def request_statement(self):
        return requests.get(
            BLOBS_BASE_URL + self._problem_blob_key,
            stream=True,
        )

    def submissions(self):
        return self._client.submissions(self.id)


@attr.s
class Submission:
    _client = attr.ib(repr=False)
    id = attr.ib(repr=False)
    _data_set = attr.ib(repr=False)
    _submission_blob_key = attr.ib(repr=False)
    _sources_blob_key = attr.ib(repr=False)
    creation_time = attr.ib(convert=pendulum.parse)
    scored = attr.ib()
    valid = attr.ib()
    best = attr.ib()
    score = attr.ib(convert=int)
    _team_id = attr.ib(repr=False)
    _extra_json_blob_key = attr.ib(default=None, repr=False)
    data_set = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.data_set = DataSet(
            client=self._client,
            **camelcase_to_snake_case(self._data_set),
        )


def camelcase_to_snake_case(kwargs):
    def conv(key):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return {conv(k): v for k, v in kwargs.items()}


def wrap(resource_class, args_converter=camelcase_to_snake_case):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            resource = func(self, *args, **kwargs)
            return resource_class(client=self, **args_converter(resource))
        return wrapper
    return decorator


@attr.s
class ListOf:
    wrapper = attr.ib()
    args_converter = attr.ib(default=camelcase_to_snake_case)

    def __call__(self, client, items):
        return [
            self.wrapper(client=client, **self.args_converter(r))
            for r in items
        ]


@attr.s
class JudgeClient:
    _resource = attr.ib()

    @wrap(Account)
    def whoami(self):
        return self._resource.accounts().current().execute()

    @wrap(ListOf(Round))
    def rounds(self):
        return self._resource.rounds().list().execute()

    @wrap(Round)
    def round(self, id):
        return self._resource.rounds().get(id=id).execute()

    def upload(self, path):
        upload_url = self._resource.upload().createUrl().execute()['value']
        with path.open('rb') as fh:
            r = requests.post(upload_url, files={
                'file': (
                    path.name,
                    fh,
                ),
            })
        return r.json()['file'][0]

    @wrap(ListOf(Submission))
    def submissions(self, round_id):
        return self._resource.submissions().list(roundId=round_id).execute()

    @wrap(Submission)
    def submit(self, dataset_id, code_blob, solution_blob):
        return self._resource.submissions().insert(
            dataSet=dataset_id,
            sourcesBlobKey=code_blob,
            submissionBlobKey=solution_blob,
        ).execute()
