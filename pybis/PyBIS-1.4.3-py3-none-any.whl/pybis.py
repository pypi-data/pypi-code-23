#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pybis.py

Work with openBIS from Python.

"""

from __future__ import print_function
import os
import random

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import copy
import time
import json
import re
from urllib.parse import urlparse, urljoin, quote
import zlib
import base64
from collections import namedtuple
from texttable import Texttable
from tabulate import tabulate

from pybis.utils import parse_jackson, check_datatype, split_identifier, format_timestamp, is_identifier, is_permid, nvl
from pybis.property import PropertyHolder, PropertyAssignments
from pybis.masterdata import Vocabulary
from . import data_set as pbds

import pandas as pd
from pandas import DataFrame, Series

import threading
from threading import Thread
from queue import Queue

from datetime import datetime

PYBIS_PLUGIN = "dataset-uploader-api"


def _definitions(entity):
    entities = {
        "Space": {
            "attrs_new": "code description".split(),
            "attrs_up": "description".split(),
            "attrs": "code permId description registrator registrationDate modificationDate".split(),
            "multi": "".split(),
            "identifier": "spaceId",
        },
        "Project": {
            "attrs_new": "code description space attachments".split(),
            "attrs_up": "description space attachments".split(),
            "attrs": "code description permId identifier space leader registrator registrationDate modifier modificationDate attachments".split(),
            "multi": "".split(),
            "identifier": "projectId",
        },
        "Experiment": {
            "attrs_new": "code type project tags attachments".split(),
            "attrs_up": "project tags attachments".split(),
            "attrs": "code permId identifier type project tags attachments".split(),
            "multi": "tags attachments".split(),
            "identifier": "experimentId",
        },
        "Sample": {
            "attrs_new": "code type parents children space experiment tags attachments".split(),
            "attrs_up": "parents children space experiment tags attachments".split(),
            "attrs": "code permId identifier type parents children components space experiment tags attachments".split(),
            "ids2type": {
                'parentIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
                'childIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
                'componentIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
            },
            "identifier": "sampleId",
            "cre_type": "as.dto.sample.create.SampleCreation",
            "multi": "parents children components tags attachments".split(),
        },
        "DataSet": {
            "attrs_new": "type experiment sample parents children components tags".split(),
            "attrs_up": "parents children experiment sample components tags".split(),
            "attrs": "code permId type experiment sample parents children components tags accessDate dataProducer dataProductionDate registrator registrationDate modifier modificationDate dataStore measured".split(),

            "ids2type": {
                'parentIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'childIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'componentIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'containerIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
            },
            "multi": "parents children container".split(),
            "identifier": "dataSetId",
        },
        "Material": {
            "attrs_new": "code description type creation tags".split(),
            "attrs": "code description type creation registrator tags".split()
        },
        "Tag": {
            "attrs_new": "code description experiments samples dataSets materials".split(),
            "attrs": "code description experiments samples dataSets materials registrationDate".split(),
        },
        "attr2ids": {
            "space": "spaceId",
            "project": "projectId",
            "sample": "sampleId",
            "samples": "sampleIds",
            "dataSet": "dataSetId",
            "dataSets": "dataSetIds",
            "experiment": "experimentId",
            "experiments": "experimentIds",
            "material": "materialId",
            "materials": "materialIds",
            "container": "containerId",
            "component": "componentId",
            "components": "componentIds",
            "parents": "parentIds",
            "children": "childIds",
            "tags": "tagIds",
        },
        "ids2type": {
            'spaceId': {'permId': {'@type': 'as.dto.space.id.SpacePermId'}},
            'projectId': {'permId': {'@type': 'as.dto.project.id.ProjectPermId'}},
            'experimentId': {'permId': {'@type': 'as.dto.experiment.id.ExperimentPermId'}},
            'tagIds': {'code': {'@type': 'as.dto.tag.id.TagCode'}},
        },
    }
    return entities[entity]


search_criteria = {
    "space": "as.dto.space.search.SpaceSearchCriteria",
    "project": "as.dto.project.search.ProjectSearchCriteria",
    "experiment": "as.dto.experiment.search.ExperimentSearchCriteria",
    "sample": "as.dto.sample.search.SampleSearchCriteria",
    "dataset": "as.dto.dataset.search.DataSetSearchCriteria",
    "code": "as.dto.common.search.CodeSearchCriteria",
    "sample_type": "as.dto.sample.search.SampleTypeSearchCriteria",
}

fetch_option = {
    "space": {"@type": "as.dto.space.fetchoptions.SpaceFetchOptions"},
    "project": {"@type": "as.dto.project.fetchoptions.ProjectFetchOptions"},
    "experiment": {
        "@type": "as.dto.experiment.fetchoptions.ExperimentFetchOptions",
        "type": {"@type": "as.dto.experiment.fetchoptions.ExperimentTypeFetchOptions"}
    },
    "sample": {
        "@type": "as.dto.sample.fetchoptions.SampleFetchOptions",
        "type": {"@type": "as.dto.sample.fetchoptions.SampleTypeFetchOptions"}
    },
    "samples": {"@type": "as.dto.sample.fetchoptions.SampleFetchOptions"},
    "dataSets": {
        "@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions",
        "properties": {"@type": "as.dto.property.fetchoptions.PropertyFetchOptions"},
        "type": {"@type": "as.dto.dataset.fetchoptions.DataSetTypeFetchOptions"},
    },
    "physicalData": {"@type": "as.dto.dataset.fetchoptions.PhysicalDataFetchOptions"},
    "linkedData": {
        "externalDms": {"@type": "as.dto.externaldms.fetchoptions.ExternalDmsFetchOptions"},
        "@type": "as.dto.dataset.fetchoptions.LinkedDataFetchOptions"
    },

    "properties": {"@type": "as.dto.property.fetchoptions.PropertyFetchOptions"},
    "propertyAssignments": {
        "@type": "as.dto.property.fetchoptions.PropertyAssignmentFetchOptions",
        "propertyType": {
            "@type": "as.dto.property.fetchoptions.PropertyTypeFetchOptions",
            "vocabulary": {
                "@type": "as.dto.vocabulary.fetchoptions.VocabularyFetchOptions",
            }
        }
    },
    "tags": {"@type": "as.dto.tag.fetchoptions.TagFetchOptions"},

    "registrator": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "modifier": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "leader": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},

    "attachments": {"@type": "as.dto.attachment.fetchoptions.AttachmentFetchOptions"},
    "attachmentsWithContent": {
        "@type": "as.dto.attachment.fetchoptions.AttachmentFetchOptions",
        "content": {
            "@type": "as.dto.common.fetchoptions.EmptyFetchOptions"
        },
    },
    "history": {"@type": "as.dto.history.fetchoptions.HistoryEntryFetchOptions"},
    "dataStore": {"@type": "as.dto.datastore.fetchoptions.DataStoreFetchOptions"},
}


def search_request_for_identifier(ident, entity):
    search_request = {}

    if is_identifier(ident):
        search_request = {
            "identifier": ident.upper(),
            "@type": "as.dto.{}.id.{}Identifier".format(entity.lower(), entity.capitalize())
        }
    else:
        search_request = {
            "permId": ident,
            "@type": "as.dto.{}.id.{}PermId".format(entity.lower(), entity.capitalize())
        }
    return search_request


def extract_code(obj):
    if not isinstance(obj, dict):
        return str(obj)
    return obj['code']


def extract_deletion(obj):
    del_objs = []
    for deleted_object in obj['deletedObjects']:
        del_objs.append({
            "reason": obj['reason'],
            "permId": deleted_object["id"]["permId"],
            "type": deleted_object["id"]["@type"]
        })
    return del_objs


def extract_identifier(ident):
    if not isinstance(ident, dict):
        return str(ident)
    return ident['identifier']


def extract_nested_identifier(ident):
    if not isinstance(ident, dict):
        return str(ident)
    return ident['identifier']['identifier']


def extract_permid(permid):
    if not isinstance(permid, dict):
        return str(permid)
    return permid['permId']


def extract_nested_permid(permid):
    if not isinstance(permid, dict):
        return str(permid)
    return permid['permId']['permId']


def extract_property_assignments(pas):
    pa_strings = []
    for pa in pas:
        if not isinstance(pa['propertyType'], dict):
            pa_strings.append(pa['propertyType'])
        else:
            pa_strings.append(pa['propertyType']['label'])
    return pa_strings


def extract_person(person):
    if not isinstance(person, dict):
        return str(person)
    return person['userId']


def crc32(fileName):
    """since Python3 the zlib module returns unsigned integers (2.7: signed int)
    """
    prev = 0
    for eachLine in open(fileName, "rb"):
        prev = zlib.crc32(eachLine, prev)
    # return as hex
    return "%x" % (prev & 0xFFFFFFFF)


def _create_tagIds(tags=None):
    if tags is None:
        return None
    if not isinstance(tags, list):
        tags = [tags]
    tagIds = []
    for tag in tags:
        tagIds.append({"code": tag, "@type": "as.dto.tag.id.TagCode"})
    return tagIds


def _tagIds_for_tags(tags=None, action='Add'):
    """creates an action item to add or remove tags. Action is either 'Add', 'Remove' or 'Set'
    """
    if tags is None:
        return
    if not isinstance(tags, list):
        tags = [tags]

    items = []
    for tag in tags:
        items.append({
            "code": tag,
            "@type": "as.dto.tag.id.TagCode"
        })

    tagIds = {
        "actions": [
            {
                "items": items,
                "@type": "as.dto.common.update.ListUpdateAction{}".format(action.capitalize())
            }
        ],
        "@type": "as.dto.common.update.IdListUpdateValue"
    }
    return tagIds


def _list_update(ids=None, entity=None, action='Add'):
    """creates an action item to add, set or remove ids. 
    """
    if ids is None:
        return
    if not isinstance(ids, list):
        ids = [ids]

    items = []
    for ids in ids:
        items.append({
            "code": ids,
            "@type": "as.dto.{}.id.{}Code".format(entity.lower(), entity)
        })

    list_update = {
        "actions": [
            {
                "items": items,
                "@type": "as.dto.common.update.ListUpdateAction{}".format(action.capitalize())
            }
        ],
        "@type": "as.dto.common.update.IdListUpdateValue"
    }
    return list_update


def _create_typeId(type):
    return {
        "permId": type.upper(),
        "@type": "as.dto.entitytype.id.EntityTypePermId"
    }


def _create_projectId(ident):
    match = re.match('/', ident)
    if match:
        return {
            "identifier": ident,
            "@type": "as.dto.project.id.ProjectIdentifier"
        }
    else:
        return {
            "permId": ident,
            "@type": "as.dto.project.id.ProjectPermId"
        }


def _create_experimentId(ident):
    return {
        "identifier": ident,
        "@type": "as.dto.experiment.id.ExperimentIdentifier"
    }


def _common_search(search_type, value, comparison="StringEqualToValue"):
    sreq = {
        "@type": search_type,
        "fieldValue": {
            "value": value,
            "@type": "as.dto.common.search.{}".format(comparison)
        }
    }
    return sreq


def _criteria_for_code(code):
    return {
        "fieldValue": {
            "value": code.upper(),
            "@type": "as.dto.common.search.StringEqualToValue"
        },
        "@type": "as.dto.common.search.CodeSearchCriteria"
    }


def _subcriteria_for_type(code, entity):
    return {
        "@type": "as.dto.{}.search.{}TypeSearchCriteria".format(entity.lower(), entity),
        "criteria": [
            {
                "@type": "as.dto.common.search.CodeSearchCriteria",
                "fieldValue": {
                    "value": code.upper(),
                    "@type": "as.dto.common.search.StringEqualToValue"
                }
            }
        ]
    }


def _subcriteria_for_status(status_value):
    status_value = status_value.upper()
    valid_status = "AVAILABLE LOCKED ARCHIVED UNARCHIVE_PENDING ARCHIVE_PENDING BACKUP_PENDING".split()
    if not status_value in valid_status:
        raise ValueError("status must be one of the following: " + ", ".join(valid_status))

    return {
        "@type": "as.dto.dataset.search.PhysicalDataSearchCriteria",
        "operator": "AND",
        "criteria": [{
            "@type":
                "as.dto.dataset.search.StatusSearchCriteria",
            "fieldName": "status",
            "fieldType": "ATTRIBUTE",
            "fieldValue": status_value
        }]
    }


def _gen_search_criteria(req):
    sreq = {}
    for key, val in req.items():
        if key == "criteria":
            items = []
            for item in req['criteria']:
                items.append(_gen_search_criteria(item))
            sreq['criteria'] = items
        elif key == "code":
            sreq["criteria"] = [_common_search(
                "as.dto.common.search.CodeSearchCriteria", val.upper()
            )]
        elif key == "identifier":
            if is_identifier(val):
                # if we have an identifier, we need to search in Space and Code separately
                si = split_identifier(val)
                sreq["criteria"] = []
                if "space" in si:
                    sreq["criteria"].append(
                        _gen_search_criteria({"space": "Space", "code": si["space"]})
                    )
                if "experiment" in si:
                    pass

                if "code" in si:
                    sreq["criteria"].append(
                        _common_search(
                            "as.dto.common.search.CodeSearchCriteria", si["code"].upper()
                        )
                    )
            elif is_permid(val):
                sreq["criteria"] = [_common_search(
                    "as.dto.common.search.PermIdSearchCriteria", val
                )]
            else:
                # we assume we just got a code
                sreq["criteria"] = [_common_search(
                    "as.dto.common.search.CodeSearchCriteria", val.upper()
                )]

        elif key == "operator":
            sreq["operator"] = val.upper()
        else:
            sreq["@type"] = "as.dto.{}.search.{}SearchCriteria".format(key, val)
    return sreq


def _subcriteria_for_tags(tags):
    if not isinstance(tags, list):
        tags = [tags]

    criterias = []
    for tag in tags:
        criterias.append({
            "fieldName": "code",
            "fieldType": "ATTRIBUTE",
            "fieldValue": {
                "value": tag,
                "@type": "as.dto.common.search.StringEqualToValue"
            },
            "@type": "as.dto.common.search.CodeSearchCriteria"
        })

    return {
        "@type": "as.dto.tag.search.TagSearchCriteria",
        "operator": "AND",
        "criteria": criterias
    }


def _subcriteria_for_is_finished(is_finished):
    return {
        "@type": "as.dto.common.search.StringPropertySearchCriteria",
        "fieldName": "FINISHED_FLAG",
        "fieldType": "PROPERTY",
        "fieldValue": {
            "value": is_finished,
            "@type": "as.dto.common.search.StringEqualToValue"
        }
    }


def _subcriteria_for_properties(prop, val):
    return {
        "@type": "as.dto.common.search.StringPropertySearchCriteria",
        "fieldName": prop.upper(),
        "fieldType": "PROPERTY",
        "fieldValue": {
            "value": val,
            "@type": "as.dto.common.search.StringEqualToValue"
        }
    }


def _subcriteria_for_permid(permids, entity, parents_or_children=''):
    if not isinstance(permids, list):
        permids = [permids]

    criterias = []
    for permid in permids:
        criterias.append({
            "@type": "as.dto.common.search.PermIdSearchCriteria",
            "fieldValue": {
                "value": permid,
                "@type": "as.dto.common.search.StringEqualToValue"
            },
            "fieldType": "ATTRIBUTE",
            "fieldName": "code"
        })

    criteria = {
        "criteria": criterias,
        "@type": "as.dto.{}.search.{}{}SearchCriteria".format(
            entity.lower(), entity, parents_or_children
        ),
        "operator": "OR"
    }
    return criteria


def _subcriteria_for_code(code, object_type):
    if code is not None:
        if is_permid(code):
            fieldname = "permId"
            fieldtype = "as.dto.common.search.PermIdSearchCriteria"
        else:
            fieldname = "code"
            fieldtype = "as.dto.common.search.CodeSearchCriteria"

        criteria = {
            "criteria": [
                {
                    "fieldName": fieldname,
                    "fieldType": "ATTRIBUTE",
                    "fieldValue": {
                        "value": code.upper(),
                        "@type": "as.dto.common.search.StringEqualToValue"
                    },
                    "@type": fieldtype
                }
            ],
            "@type": search_criteria[object_type.lower()],
            "operator": "AND"
        }
        return criteria
    else:
        criteria = {"@type": search_criteria[object_type.lower()]}
        return criteria


class Openbis:
    """Interface for communicating with openBIS. 
    A recent version of openBIS is required (minimum 16.05.2).
    For creation of datasets, dataset-uploader-api needs to be installed.
    """

    def __init__(self, url, verify_certificates=True, token=None):
        """Initialize a new connection to an openBIS server.
        :param host:
        """
        url_obj = urlparse(url)
        if url_obj.netloc is None:
            raise ValueError("please provide the url in this format: https://openbis.host.ch:8443")
        if url_obj.hostname is None:
            raise ValueError("hostname is missing")

        self.url = url_obj.geturl()
        self.port = url_obj.port
        self.hostname = url_obj.hostname
        self.as_v3 = '/openbis/openbis/rmi-application-server-v3.json'
        self.as_v1 = '/openbis/openbis/rmi-general-information-v1.json'
        self.reg_v1 = '/openbis/openbis/rmi-query-v1.json'
        self.verify_certificates = verify_certificates
        self.token = token

        self.dataset_types = None
        self.sample_types = None
        self.files_in_wsp = []
        self.token_path = None

        # use an existing token, if available
        if self.token is None:
            self.token = self._get_cached_token()

    def __dir__(self):
        return [
            'url', 'port', 'hostname',
            'login()', 'logout()', 'is_session_active()', 'token', 'is_token_valid("")',
            "get_dataset('permId')",
            "get_datasets()",
            "get_dataset_type('raw_data')",
            "get_dataset_types()",
            "get_datastores()",
            "get_deletions()",
            "get_experiment('permId', withAttachments=False)",
            "get_experiments()",
            "get_experiment_type('type')",
            "get_experiment_types()",
            "get_external_data_management_system(permId)",
            "get_material_type('type')",
            "get_material_types()",
            "get_project('project')",
            "get_projects(space=None, code=None)",
            "get_sample('id')",
            "get_object('id')", # "get_sample('id')" alias
            "get_samples()",
            "get_objects()", # "get_samples()" alias
            "get_sample_type(type))",
            "get_object_type(type))", # "get_sample_type(type))" alias
            "get_sample_types()",
            "get_object_types()", # "get_sample_types()" alias
            "get_semantic_annotations()",
            "get_semantic_annotation(permId, only_data = False)",
            "get_space(code)",
            "get_spaces()",
            "get_tags()",
            "get_terms()",
            'new_space(name, description)',
            'new_project(space, code, description, attachments)',
            'new_experiment(type, code, project, props={})',
            'new_sample(type, space, project, experiment, parents)',
            'new_object(type, space, project, experiment, parents)', # 'new_sample(type, space, project, experiment)' alias
            'new_dataset(type, parent, experiment, sample, files=[], folder, props={})',
            'new_semantic_annotation(entityType, propertyType)',
            'update_sample(sampleId, space, project, experiment, parents, children, components, properties, tagIds, attachments)',
            'update_object(sampleId, space, project, experiment, parents, children, components, properties, tagIds, attachments)', # 'update_sample(sampleId, space, project, experiment, parents, children, components, properties, tagIds, attachments)' alias
        ]

    @property
    def spaces(self):
        return self.get_spaces()

    @property
    def projects(self):
        return self.get_projects()

    def _get_cached_token(self):
        """Read the token from the cache, and set the token ivar to it, if there, otherwise None.
        If the token is not valid anymore, delete it. 
        """
        token_path = self.gen_token_path()
        if not os.path.exists(token_path):
            return None
        try:
            with open(token_path) as f:
                token = f.read()
                if token == "":
                    return None
                if not self.is_token_valid(token):
                    os.remove(token_path)
                    return None
                else:
                    return token
        except FileNotFoundError:
            return None

    def gen_token_path(self, parent_folder=None):
        """generates a path to the token file.
        The token is usually saved in a file called
        ~/.pybis/hostname.token
        """
        if parent_folder is None:
            # save token under ~/.pybis folder
            parent_folder = os.path.join(
                os.path.expanduser("~"),
                '.pybis'
            )
        path = os.path.join(parent_folder, self.hostname + '.token')
        return path

    def save_token(self, token=None, parent_folder=None):
        """ saves the session token to the disk, usually here: ~/.pybis/hostname.token. When a new Openbis instance is created, it tries to read this saved token by default.
        """
        if token is None:
            token = self.token

        token_path = None;
        if parent_folder is None:
            token_path = self.gen_token_path()
        else:
            token_path = self.gen_token_path(parent_folder)

        # create the necessary directories, if they don't exist yet
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as f:
            f.write(token)
            self.token_path = token_path

    def delete_token(self, token_path=None):
        """ deletes a stored session token.
        """
        if token_path is None:
            token_path = self.token_path
        os.remove(token_path)

    def _post_request(self, resource, request):
        """ internal method, used to handle all post requests and serializing / deserializing
        data
        """
        return self._post_request_full_url(urljoin(self.url,resource), request)

    def _post_request_full_url(self, full_url, request):
        """ internal method, used to handle all post requests and serializing / deserializing
        data
        """
        if "id" not in request:
            request["id"] = "1"
        if "jsonrpc" not in request:
            request["jsonrpc"] = "2.0"
        if request["params"][0] is None:
            raise ValueError("Your session expired, please log in again")
        resp = requests.post(
            full_url,
            json.dumps(request),
            verify=self.verify_certificates
        )

        if resp.ok:
            resp = resp.json()
            if 'error' in resp:
                print(json.dumps(request))
                raise ValueError(resp['error']['message'])
            elif 'result' in resp:
                return resp['result']
            else:
                raise ValueError('request did not return either result nor error')
        else:
            raise ValueError('general error while performing post request')

    def logout(self):
        """ Log out of openBIS. After logout, the session token is no longer valid.
        """
        if self.token is None:
            return

        logout_request = {
            "method": "logout",
            "params": [self.token],
        }
        resp = self._post_request(self.as_v3, logout_request)
        self.token = None
        self.token_path = None
        return resp

    def login(self, username=None, password=None, save_token=False):
        """Log into openBIS.
        Expects a username and a password and updates the token (session-ID).
        The token is then used for every request.
        Clients may want to store the credentials object in a credentials store after successful login.
        Throw a ValueError with the error message if login failed.
        """

        if password is None:
            import getpass
            password = getpass.getpass()

        login_request = {
            "method": "login",
            "params": [username, password],
        }
        result = self._post_request(self.as_v3, login_request)
        if result is None:
            raise ValueError("login to openBIS failed")
        else:
            self.token = result
            if save_token:
                self.save_token()
            return self.token

    def create_permId(self):
        """Have the server generate a new permId"""
        # Request just 1 permId
        request = {
            "method": "createPermIdStrings",
            "params": [self.token, 1],
        }
        resp = self._post_request(self.as_v3, request)
        if resp is not None:
            return resp[0]
        else:
            raise ValueError("Could not create permId")

    def get_datastores(self):
        """ Get a list of all available datastores. Usually there is only one, but in some cases
        there might be multiple servers. If you upload a file, you need to specifiy the datastore you want
        the file uploaded to.
        """

        request = {
            "method": "listDataStores",
            "params": [self.token],
        }
        resp = self._post_request(self.as_v1, request)
        if resp is not None:
            return DataFrame(resp)[['code', 'downloadUrl', 'hostUrl']]
        else:
            raise ValueError("No datastore found!")

    def get_spaces(self, code=None):
        """ Get a list of all available spaces (DataFrame object). To create a sample or a
        dataset, you need to specify in which space it should live.
        """

        criteria = {}
        options = {}
        request = {
            "method": "searchSpaces",
            "params": [self.token,
                       criteria,
                       options,
                       ],
        }
        resp = self._post_request(self.as_v3, request)
        if resp is not None:
            spaces = DataFrame(resp['objects'])
            spaces['registrationDate'] = spaces['registrationDate'].map(format_timestamp)
            spaces['modificationDate'] = spaces['modificationDate'].map(format_timestamp)
            sp = Things(
                self,
                'space',
                spaces[['code', 'description', 'registrationDate', 'modificationDate']]
            )
            return sp
        else:
            raise ValueError("No spaces found!")

    def get_space(self, code, only_data=False):
        """ Returns a Space object for a given identifier.
        """

        code = str(code).upper()
        fetchopts = {"@type": "as.dto.space.fetchoptions.SpaceFetchOptions"}
        for option in ['registrator']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "getSpaces",
            "params": [
                self.token,
                [{
                    "permId": code,
                    "@type": "as.dto.space.id.SpacePermId"
                }],
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp) == 0:
            raise ValueError("No such space: %s" % code)

        for permid in resp:
            if only_data:
                return resp[permid]
            else:
                return Space(self, data=resp[permid])

    def get_samples(self, code=None, permId=None, space=None, project=None, experiment=None, type=None,
                    withParents=None, withChildren=None, tags=None, props=None, **properties):
        """ Get a list of all samples for a given space/project/experiment (or any combination)
        """

        sub_criteria = []
        if space:
            sub_criteria.append(_gen_search_criteria({
                "space": "Space",
                "operator": "AND",
                "code": space
            })
            )
        if project:
            exp_crit = _subcriteria_for_code(experiment, 'experiment')
            proj_crit = _subcriteria_for_code(project, 'project')
            exp_crit['criteria'] = []
            exp_crit['criteria'].append(proj_crit)
            sub_criteria.append(exp_crit)
        if experiment:
            sub_criteria.append(_subcriteria_for_code(experiment, 'experiment'))
        if properties is not None:
            for prop in properties:
                sub_criteria.append(_subcriteria_for_properties(prop, properties[prop]))
        if type:
            sub_criteria.append(_subcriteria_for_code(type, 'sample_type'))
        if tags:
            sub_criteria.append(_subcriteria_for_tags(tags))
        if code:
            sub_criteria.append(_criteria_for_code(code))
        if permId:
            sub_criteria.append(_common_search("as.dto.common.search.PermIdSearchCriteria", permId))
        if withParents:
            if not isinstance(withParents, list):
                withParents = [withParents]
            for parent in withParents:
                sub_criteria.append(
                    _gen_search_criteria({
                        "sample": "SampleParents",
                        "identifier": parent
                    })
                )
        if withChildren:
            if not isinstance(withChildren, list):
                withChildren = [withChildren]
            for child in withChildren:
                sub_criteria.append(
                    _gen_search_criteria({
                        "sample": "SampleChildren",
                        "identifier": child
                    })
                )

        criteria = {
            "criteria": sub_criteria,
            "@type": "as.dto.sample.search.SampleSearchCriteria",
            "operator": "AND"
        }

        # build the various fetch options
        fetchopts = fetch_option['sample']

        for option in ['tags', 'properties', 'registrator', 'modifier', 'experiment']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchSamples",
            "params": [self.token,
                       criteria,
                       fetchopts,
                       ],
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp['objects']) == 0:
            raise ValueError("no samples found!")

        objects = resp['objects']
        parse_jackson(objects)

        samples = DataFrame(objects)
        samples['registrationDate'] = samples['registrationDate'].map(format_timestamp)
        samples['modificationDate'] = samples['modificationDate'].map(format_timestamp)
        samples['registrator'] = samples['registrator'].map(extract_person)
        samples['modifier'] = samples['modifier'].map(extract_person)
        samples['identifier'] = samples['identifier'].map(extract_identifier)
        samples['permId'] = samples['permId'].map(extract_permid)
        samples['experiment'] = samples['experiment'].map(extract_nested_identifier)
        samples['sample_type'] = samples['type'].map(extract_nested_permid)

        attrs = ['identifier', 'permId', 'experiment', 'sample_type',
                 'registrator', 'registrationDate', 'modifier', 'modificationDate']

        if props is not None:
            for prop in props:
                samples[prop.upper()] = samples['properties'].map(lambda x: x.get(prop.upper(), ''))
                attrs.append(prop.upper())

        ss = samples[attrs]
        return Things(self, 'sample', ss, 'identifier')

    get_objects = get_samples # Alias

    def get_experiments(self, code=None, type=None, space=None, project=None, tags=None, is_finished=None, props=None,
                        **properties):
        """ Get a list of all experiment for a given space or project (or any combination)
        """

        sub_criteria = []
        if space:
            sub_criteria.append(_subcriteria_for_code(space, 'space'))
        if project:
            sub_criteria.append(_subcriteria_for_code(project, 'project'))
        if code:
            sub_criteria.append(_criteria_for_code(code))
        if type:
            sub_criteria.append(_subcriteria_for_type(type, 'Experiment'))
        if tags:
            sub_criteria.append(_subcriteria_for_tags(tags))
        if is_finished is not None:
            sub_criteria.append(_subcriteria_for_is_finished(is_finished))
        if properties is not None:
            for prop in properties:
                sub_criteria.append(_subcriteria_for_properties(prop, properties[prop]))

        criteria = {
            "criteria": sub_criteria,
            "@type": "as.dto.experiment.search.ExperimentSearchCriteria",
            "operator": "AND"
        }
        fetchopts = fetch_option['experiment']
        for option in ['tags', 'properties', 'registrator', 'modifier', 'project']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchExperiments",
            "params": [self.token,
                       criteria,
                       fetchopts,
                       ],
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp['objects']) == 0:
            raise ValueError("No experiments found!")

        objects = resp['objects']
        parse_jackson(objects)

        experiments = DataFrame(objects)
        experiments['registrationDate'] = experiments['registrationDate'].map(format_timestamp)
        experiments['modificationDate'] = experiments['modificationDate'].map(format_timestamp)
        experiments['project'] = experiments['project'].map(extract_code)
        experiments['registrator'] = experiments['registrator'].map(extract_person)
        experiments['modifier'] = experiments['modifier'].map(extract_person)
        experiments['identifier'] = experiments['identifier'].map(extract_identifier)
        experiments['permId'] = experiments['permId'].map(extract_permid)
        experiments['type'] = experiments['type'].map(extract_code)

        attrs = ['identifier', 'permId', 'project', 'type',
                 'registrator', 'registrationDate', 'modifier', 'modificationDate']

        if props is not None:
            for prop in props:
                experiments[prop.upper()] = experiments['properties'].map(lambda x: x.get(prop.upper(), ''))
                attrs.append(prop.upper())

        exps = experiments[attrs]
        return Things(self, 'experiment', exps, 'identifier')

    def get_datasets(self,
                     code=None, type=None, withParents=None, withChildren=None, status=None,
                     sample=None, experiment=None, project=None, tags=None, props=None, **properties
                     ):

        sub_criteria = []

        if code:
            sub_criteria.append(_criteria_for_code(code))
        if type:
            sub_criteria.append(_subcriteria_for_type(type, 'DataSet'))
        if withParents:
            sub_criteria.append(_subcriteria_for_permid(withParents, 'DataSet', 'Parents'))
        if withChildren:
            sub_criteria.append(_subcriteria_for_permid(withChildren, 'DataSet', 'Children'))

        if sample:
            sub_criteria.append(_subcriteria_for_code(sample, 'Sample'))
        if experiment:
            sub_criteria.append(_subcriteria_for_code(experiment, 'Experiment'))
        if project:
            exp_crit = _subcriteria_for_code(experiment, 'Experiment')
            proj_crit = _subcriteria_for_code(project, 'Project')
            exp_crit['criteria'] = []
            exp_crit['criteria'].append(proj_crit)
            sub_criteria.append(exp_crit)
        if tags:
            sub_criteria.append(_subcriteria_for_tags(tags))
        if status:
            sub_criteria.append(_subcriteria_for_status(status))
        if properties is not None:
            for prop in properties:
                sub_criteria.append(_subcriteria_for_properties(prop, properties[prop]))

        criteria = {
            "criteria": sub_criteria,
            "@type": "as.dto.dataset.search.DataSetSearchCriteria",
            "operator": "AND"
        }

        fetchopts = {
            "containers": {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
            "type": {"@type": "as.dto.dataset.fetchoptions.DataSetTypeFetchOptions"}
        }

        for option in ['tags', 'properties', 'sample', 'experiment', 'physicalData']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchDataSets",
            "params": [self.token,
                       criteria,
                       fetchopts,
                       ],
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp['objects']) == 0:
            raise ValueError("no datasets found!")

        objects = resp['objects']
        parse_jackson(objects)

        datasets = DataFrame(objects)
        datasets['registrationDate'] = datasets['registrationDate'].map(format_timestamp)
        datasets['modificationDate'] = datasets['modificationDate'].map(format_timestamp)
        datasets['experiment'] = datasets['experiment'].map(extract_nested_identifier)
        datasets['sample'] = datasets['sample'].map(extract_nested_identifier)
        datasets['type'] = datasets['type'].map(extract_code)
        datasets['permId'] = datasets['code']
        datasets['location'] = datasets['physicalData'].map(lambda x: x.get('location') if x else '')

        attrs = ['permId', 'properties', 'type', 'experiment', 'sample', 'registrationDate', 'modificationDate',
                 'location']
        if props is not None:
            for prop in props:
                datasets[prop.upper()] = datasets['properties'].map(lambda x: x.get(prop.upper(), ''))
                attrs.append(prop.upper())

        return Things(self, 'dataset', datasets[attrs], 'permId')

    def get_experiment(self, expId, withAttachments=False, only_data=False):
        """ Returns an experiment object for a given identifier (expId).
        """

        fetchopts = {
            "@type": "as.dto.experiment.fetchoptions.ExperimentFetchOptions",
            "type": {
                "@type": "as.dto.experiment.fetchoptions.ExperimentTypeFetchOptions",
            },
        }

        search_request = search_request_for_identifier(expId, 'experiment')
        for option in ['tags', 'properties', 'attachments', 'project', 'samples']:
            fetchopts[option] = fetch_option[option]

        if withAttachments:
            fetchopts['attachments'] = fetch_option['attachmentsWithContent']

        request = {
            "method": "getExperiments",
            "params": [
                self.token,
                [search_request],
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp) == 0:
            raise ValueError("No such experiment: %s" % expId)

        for id in resp:
            if only_data:
                return resp[id]
            else:
                return Experiment(
                    openbis_obj = self,
                    type = self.get_experiment_type(resp[expId]["type"]["code"]),
                    data = resp[id]
                )

    def new_experiment(self, type, code, project, props=None, **kwargs):
        """ Creates a new experiment of a given experiment type.
        """
        return Experiment(
            openbis_obj = self, 
            type = self.get_experiment_type(type), 
            project = project,
            data = None,
            props = props,
            code = code, 
            **kwargs
        )

    def update_experiment(self, experimentId, properties=None, tagIds=None, attachments=None):
        params = {
            "experimentId": {
                "permId": experimentId,
                "@type": "as.dto.experiment.id.ExperimentPermId"
            },
            "@type": "as.dto.experiment.update.ExperimentUpdate"
        }
        if properties is not None:
            params["properties"] = properties
        if tagIds is not None:
            params["tagIds"] = tagIds
        if attachments is not None:
            params["attachments"] = attachments

        request = {
            "method": "updateExperiments",
            "params": [
                self.token,
                [params]
            ]
        }
        self._post_request(self.as_v3, request)

    def create_sample(self, space_ident, code, type,
                      project_ident=None, experiment_ident=None, properties=None, attachments=None, tags=None):

        tagIds = _create_tagIds(tags)
        typeId = _create_typeId(type)
        projectId = _create_projectId(project_ident)
        experimentId = _create_experimentId(experiment_ident)

        if properties is None:
            properties = {}

        request = {
            "method": "createSamples",
            "params": [
                self.token,
                [
                    {
                        "properties": properties,
                        "code": code,
                        "typeId": typeId,
                        "projectId": projectId,
                        "experimentId": experimentId,
                        "tagIds": tagIds,
                        "attachments": attachments,
                        "@type": "as.dto.sample.create.SampleCreation",
                    }
                ]
            ],
        }
        resp = self._post_request(self.as_v3, request)
        return self.get_sample(resp[0]['permId'])

    create_object = create_sample # Alias

    def create_external_data_management_system(self, code, label, address, address_type='FILE_SYSTEM'):
        """Create an external DMS.
        :param code: An openBIS code for the external DMS.
        :param label: A human-readable label.
        :param address: The address for accessing the external DMS. E.g., a URL.
        :param address_type: One of OPENBIS, URL, or FILE_SYSTEM
        :return:
        """
        request = {
            "method": "createExternalDataManagementSystems",
            "params": [
                self.token,
                [
                    {
                        "code": code,
                        "label": label,
                        "addressType": address_type,
                        "address": address,
                        "@type": "as.dto.externaldms.create.ExternalDmsCreation",
                    }
                ]
            ],
        }
        resp = self._post_request(self.as_v3, request)
        return self.get_external_data_management_system(resp[0]['permId'])

    def update_sample(self, sampleId, space=None, project=None, experiment=None,
                      parents=None, children=None, components=None, properties=None, tagIds=None, attachments=None):
        params = {
            "sampleId": {
                "permId": sampleId,
                "@type": "as.dto.sample.id.SamplePermId"
            },
            "@type": "as.dto.sample.update.SampleUpdate"
        }
        if space is not None:
            params['spaceId'] = space
        if project is not None:
            params['projectId'] = project
        if properties is not None:
            params["properties"] = properties
        if tagIds is not None:
            params["tagIds"] = tagIds
        if attachments is not None:
            params["attachments"] = attachments

        request = {
            "method": "updateSamples",
            "params": [
                self.token,
                [params]
            ]
        }
        self._post_request(self.as_v3, request)

    update_object = update_sample # Alias

    def delete_entity(self, entity, permid, reason, capitalize=True):
        """Deletes Spaces, Projects, Experiments, Samples and DataSets
        """

        if capitalize:
            entity_capitalized = entity.capitalize()
        else:
            entity_capitalized = entity

        entity_type = "as.dto.{}.id.{}PermId".format(entity.lower(), entity_capitalized)
        request = {
            "method": "delete" + entity_capitalized + 's',
            "params": [
                self.token,
                [
                    {
                        "permId": permid,
                        "@type": entity_type
                    }
                ],
                {
                    "reason": reason,
                    "@type": "as.dto.{}.delete.{}DeletionOptions".format(entity.lower(), entity_capitalized)
                }
            ]
        }
        self._post_request(self.as_v3, request)

    def get_deletions(self):
        request = {
            "method": "searchDeletions",
            "params": [
                self.token,
                {},
                {
                    "deletedObjects": {
                        "@type": "as.dto.deletion.fetchoptions.DeletedObjectFetchOptions"
                    }
                }
            ]
        }
        resp = self._post_request(self.as_v3, request)
        objects = resp['objects']
        parse_jackson(objects)

        new_objs = []
        for value in objects:
            del_objs = extract_deletion(value)
            if len(del_objs) > 0:
                new_objs.append(*del_objs)

        return DataFrame(new_objs)

    def new_project(self, space, code, description=None, **kwargs):
        return Project(self, None, space=space, code=code, description=description, **kwargs)

    def _gen_fetchoptions(self, options):
        fo = {}
        for option in options:
            fo[option] = fetch_option[option]
        return fo

    def get_project(self, projectId, only_data=False):
        options = ['space', 'registrator', 'modifier', 'attachments']
        if is_identifier(projectId) or is_permid(projectId):
            request = self._create_get_request(
                'getProjects', 'project', projectId, options
            )
            resp = self._post_request(self.as_v3, request)
            if only_data:
                return resp[projectId]

            return Project(self, resp[projectId])

        else:
            search_criteria = _gen_search_criteria({
                'project': 'Project',
                'operator': 'AND',
                'code': projectId
            })
            fo = self._gen_fetchoptions(options)
            request = {
                "method": "searchProjects",
                "params": [self.token, search_criteria, fo]
            }
            resp = self._post_request(self.as_v3, request)
            if len(resp['objects']) == 0:
                raise ValueError("No such project: %s" % projectId)
            if only_data:
                return resp['objects'][0]

            return Project(self, resp['objects'][0])

    def get_projects(self, space=None, code=None):
        """ Get a list of all available projects (DataFrame object).
        """

        sub_criteria = []
        if space:
            sub_criteria.append(_subcriteria_for_code(space, 'space'))
        if code:
            sub_criteria.append(_criteria_for_code(code))

        criteria = {
            "criteria": sub_criteria,
            "@type": "as.dto.project.search.ProjectSearchCriteria",
            "operator": "AND"
        }

        fetchopts = {"@type": "as.dto.project.fetchoptions.ProjectFetchOptions"}
        for option in ['registrator', 'modifier', 'leader']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchProjects",
            "params": [self.token,
                       criteria,
                       fetchopts,
                       ],
        }

        resp = self._post_request(self.as_v3, request)
        if resp is not None:
            objects = resp['objects']
            parse_jackson(objects)

            projects = DataFrame(objects)
            if len(projects) is 0:
                raise ValueError("No projects found!")

            projects['registrationDate'] = projects['registrationDate'].map(format_timestamp)
            projects['modificationDate'] = projects['modificationDate'].map(format_timestamp)
            projects['leader'] = projects['leader'].map(extract_person)
            projects['registrator'] = projects['registrator'].map(extract_person)
            projects['modifier'] = projects['modifier'].map(extract_person)
            projects['permId'] = projects['permId'].map(extract_permid)
            projects['identifier'] = projects['identifier'].map(extract_identifier)

            pros = projects[['identifier', 'permId', 'leader', 'registrator', 'registrationDate',
                             'modifier', 'modificationDate']]
            return Things(self, 'project', pros, 'identifier')
        else:
            raise ValueError("No projects found!")

    def _create_get_request(self, method_name, entity, permids, options):

        if not isinstance(permids, list):
            permids = [permids]

        type = "as.dto.{}.id.{}".format(entity.lower(), entity.capitalize())
        search_params = []
        for permid in permids:
            # decide if we got a permId or an identifier
            match = re.match('/', permid)
            if match:
                search_params.append(
                    {"identifier": permid, "@type": type + 'Identifier'}
                )
            else:
                search_params.append(
                    {"permId": permid, "@type": type + 'PermId'}
                )

        fo = {}
        for option in options:
            fo[option] = fetch_option[option]

        request = {
            "method": method_name,
            "params": [
                self.token,
                search_params,
                fo
            ],
        }
        return request

    def get_terms(self, vocabulary=None):
        """ Returns information about vocabulary, including its controlled vocabulary
        """

        search_request = {}
        if vocabulary is not None:
            search_request = _gen_search_criteria({
                "vocabulary": "VocabularyTerm",
                "criteria": [{
                    "vocabulary": "Vocabulary",
                    "code": vocabulary
                }]
            })

        fetch_options = {
            "vocabulary": {"@type": "as.dto.vocabulary.fetchoptions.VocabularyFetchOptions"},
            "@type": "as.dto.vocabulary.fetchoptions.VocabularyTermFetchOptions"
        }

        request = {
            "method": "searchVocabularyTerms",
            "params": [self.token, search_request, fetch_options]
        }
        resp = self._post_request(self.as_v3, request)
        parse_jackson(resp)
        return Vocabulary(resp)

    def get_tags(self):
        """ Returns a DataFrame of all 
        """
        request = {
            "method": "searchTags",
            "params": [self.token, {}, {}]
        }
        resp = self._post_request(self.as_v3, request)
        parse_jackson(resp)
        objects = DataFrame(resp['objects'])
        objects['registrationDate'] = objects['registrationDate'].map(format_timestamp)
        return objects[['code', 'registrationDate']]
    
    def _search_semantic_annotations(self, criteria):

        fetch_options = {
            "@type": "as.dto.semanticannotation.fetchoptions.SemanticAnnotationFetchOptions",
            "entityType": {"@type": "as.dto.entitytype.fetchoptions.EntityTypeFetchOptions"},
            "propertyType": {"@type": "as.dto.property.fetchoptions.PropertyTypeFetchOptions"},
            "propertyAssignment": {
                "@type": "as.dto.property.fetchoptions.PropertyAssignmentFetchOptions",
                "entityType" : {
                    "@type" : "as.dto.entitytype.fetchoptions.EntityTypeFetchOptions"
                },
                "propertyType" : {
                    "@type" : "as.dto.property.fetchoptions.PropertyTypeFetchOptions"
                }
            }
        }

        request = {
            "method": "searchSemanticAnnotations",
            "params": [self.token, criteria, fetch_options]
        }

        resp = self._post_request(self.as_v3, request)
        
        if resp is not None:
            objects = resp['objects']
            
            if len(objects) is 0:
                raise ValueError("No semantic annotations found!")
            
            parse_jackson(objects)
            
            for object in objects:
                object['permId'] = object['permId']['permId']
                if object.get('entityType') is not None:
                    object['entityType'] = object['entityType']['code']
                elif object.get('propertyType') is not None:
                    object['propertyType'] = object['propertyType']['code']
                elif object.get('propertyAssignment') is not None:
                    object['entityType'] = object['propertyAssignment']['entityType']['code']
                    object['propertyType'] = object['propertyAssignment']['propertyType']['code']
                object['creationDate'] = format_timestamp(object['creationDate'])
                
            return objects
        else:
            raise ValueError("No semantic annotations found!")

    def get_semantic_annotations(self):
        """ Get a list of all available semantic annotations (DataFrame object).
        """

        objects = self._search_semantic_annotations({})
        attrs = ['permId', 'entityType', 'propertyType', 'predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId', 'creationDate']
        annotations = DataFrame(objects)
        return Things(self, 'semantic_annotation', annotations[attrs], 'permId')
    
    def get_semantic_annotation(self, permId, only_data = False):

        criteria = {
            "@type" : "as.dto.semanticannotation.search.SemanticAnnotationSearchCriteria",
            "criteria" : [{
                "@type" : "as.dto.common.search.PermIdSearchCriteria",
                "fieldValue" : {
                    "@type" : "as.dto.common.search.StringEqualToValue",
                    "value" : permId
                }
            }]
        }

        objects = self._search_semantic_annotations(criteria)
        object = objects[0]

        if only_data:
            return object
        else:
            return SemanticAnnotation(self, isNew=False, **object)    
    
    def get_sample_types(self, type=None):
        """ Returns a list of all available sample types
        """
        return self._get_types_of(
            "searchSampleTypes",
            "Sample",
            type,
            ["generatedCodePrefix"]
        )

    get_object_types = get_sample_types # Alias

    def get_sample_type(self, type):
        try:
            return self._get_types_of(
                "searchSampleTypes",
                "Sample",
                type,
                ["generatedCodePrefix"]
            )
        except Exception:
            raise ValueError("no such sample type: {}".format(type))

    get_object_type = get_sample_type # Alias

    def get_experiment_types(self, type=None):
        """ Returns a list of all available experiment types
        """
        return self._get_types_of(
            "searchExperimentTypes",
            "Experiment",
            type
        )

    def get_experiment_type(self, type):
        try:
            return self._get_types_of(
                "searchExperimentTypes",
                "Experiment",
                type
            )
        except Exception:
            raise ValueError("No such experiment type: {}".format(type))

    def get_material_types(self, type=None):
        """ Returns a list of all available material types
        """
        return self._get_types_of("searchMaterialTypes", "Material", type)

    def get_material_type(self, type):
        try:
            return self._get_types_of("searchMaterialTypes", "Material", type)
        except Exception:
            raise ValueError("No such material type: {}".format(type))

    def get_dataset_types(self, type=None):
        """ Returns a list (DataFrame object) of all currently available dataset types
        """
        return self._get_types_of("searchDataSetTypes", "DataSet", type, optional_attributes=['kind'])

    def get_dataset_type(self, type):
        try:
            return self._get_types_of("searchDataSetTypes", "DataSet", type, optional_attributes=['kind'])
        except Exception:
            raise ValueError("No such dataSet type: {}".format(type))

    def _get_types_of(self, method_name, entity, type_name=None, additional_attributes=[], optional_attributes=[]):
        """ Returns a list of all available types of an entity.
        If the name of the entity-type is given, it returns a PropertyAssignments object
        """

        search_request = {}
        fetch_options = {}

        if type_name is not None:
            search_request = _gen_search_criteria({
                entity.lower(): entity + "Type",
                "operator": "AND",
                "code": type_name
            })

            fetch_options = {
                "@type": "as.dto.{}.fetchoptions.{}TypeFetchOptions".format(
                    entity.lower(), entity
                )
            }
            fetch_options['propertyAssignments'] = fetch_option['propertyAssignments']

        request = {
            "method": method_name,
            "params": [self.token, search_request, fetch_options],
        }
        resp = self._post_request(self.as_v3, request)
        parse_jackson(resp)

        if type_name is not None and len(resp['objects']) == 1:
            return PropertyAssignments(self, resp['objects'][0])
        if len(resp['objects']) >= 1:
            types = DataFrame(resp['objects'])
            types['modificationDate'] = types['modificationDate'].map(format_timestamp)
            attributes = self._get_attributes(type_name, types, additional_attributes, optional_attributes)
            return Things(self, entity.lower() + '_type', types[attributes])

        else:
            raise ValueError("Nothing found!")

    def _get_attributes(self, type_name, types, additional_attributes, optional_attributes):
        attributes = ['code', 'description'] + additional_attributes
        attributes += [attribute for attribute in optional_attributes if attribute in types]
        attributes += ['modificationDate']
        if type_name is not None:
            attributes += ['propertyAssignments']
        return attributes

    def is_session_active(self):
        """ checks whether a session is still active. Returns true or false.
        """
        return self.is_token_valid(self.token)

    def is_token_valid(self, token=None):
        """Check if the connection to openBIS is valid.
        This method is useful to check if a token is still valid or if it has timed out,
        requiring the user to login again.
        :return: Return True if the token is valid, False if it is not valid.
        """
        if token is None:
            token = self.token

        if token is None:
            return False

        request = {
            "method": "isSessionActive",
            "params": [token],
        }
        resp = self._post_request(self.as_v1, request)
        return resp

    def get_dataset(self, permid, only_data=False):
        """fetch a dataset and some metadata attached to it:
        - properties
        - sample
        - parents
        - children
        - containers
        - dataStore
        - physicalData
        - linkedData
        :return: a DataSet object
        """

        criteria = [{
            "permId": permid,
            "@type": "as.dto.dataset.id.DataSetPermId"
        }]

        fetchopts = {
            "parents": {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
            "children": {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
            "containers": {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
            "type": {"@type": "as.dto.dataset.fetchoptions.DataSetTypeFetchOptions"},
        }

        for option in ['tags', 'properties', 'dataStore', 'physicalData', 'linkedData',
                       'experiment', 'sample']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "getDataSets",
            "params": [self.token,
                       criteria,
                       fetchopts,
                       ],
        }

        resp = self._post_request(self.as_v3, request)
        if resp is None or len(resp) == 0:
            raise ValueError('no such dataset found: ' + permid)

        parse_jackson(resp)

        for permid in resp:
            if only_data:
                return resp[permid]
            else:
                return DataSet(
                    self, 
                    type=self.get_dataset_type(resp[permid]["type"]["code"]),
                    data=resp[permid]
                )

    def get_sample(self, sample_ident, only_data=False, withAttachments=False):
        """Retrieve metadata for the sample.
        Get metadata for the sample and any directly connected parents of the sample to allow access
        to the same information visible in the ELN UI. The metadata will be on the file system.
        :param sample_identifiers: A list of sample identifiers to retrieve.
        """

        search_request = search_request_for_identifier(sample_ident, 'sample')

        fetchopts = {"type": {"@type": "as.dto.sample.fetchoptions.SampleTypeFetchOptions"}}
        for option in ['tags', 'properties', 'attachments', 'space', 'experiment', 'registrator', 'dataSets']:
            fetchopts[option] = fetch_option[option]

        if withAttachments:
            fetchopts['attachments'] = fetch_option['attachmentsWithContent']

        for key in ['parents','children','container','components']:
            fetchopts[key] = {"@type": "as.dto.sample.fetchoptions.SampleFetchOptions"}

        sample_request = {
            "method": "getSamples",
            "params": [
                self.token,
                [search_request],
                fetchopts
            ],
        }

        resp = self._post_request(self.as_v3, sample_request)
        parse_jackson(resp)

        if resp is None or len(resp) == 0:
            raise ValueError('no such sample found: ' + sample_ident)
        else:
            for sample_ident in resp:
                if only_data:
                    return resp[sample_ident]
                else:
                    return Sample(self, self.get_sample_type(resp[sample_ident]["type"]["code"]), resp[sample_ident])

    get_object = get_sample # Alias

    def get_external_data_management_system(self, permId, only_data=False):
        """Retrieve metadata for the external data management system.
        :param permId: A permId for an external DMS.
        :param only_data: Return the result data as a hash-map, not an object.
        """

        request = {
            "method": "getExternalDataManagementSystems",
            "params": [
                self.token,
                [{
                    "@type": "as.dto.externaldms.id.ExternalDmsPermId",
                    "permId": permId
                }],
                {},
            ],
        }

        resp = self._post_request(self.as_v3, request)
        parse_jackson(resp)

        if resp is None or len(resp) == 0:
            raise ValueError('no such external DMS found: ' + permId)
        else:
            for ident in resp:
                if only_data:
                    return resp[ident]
                else:
                    return ExternalDMS(self, resp[ident])

    def new_space(self, **kwargs):
        """ Creates a new space in the openBIS instance.
        """
        return Space(self, None, **kwargs)


    def new_analysis(self, name, description=None, sample=None, dss_code=None, result_files=None,
                     notebook_files=None, parents=None):

        """ An analysis contains the Jupyter notebook file(s) and some result files.
            Technically this method involves uploading files to the session workspace
            and activating the dropbox aka dataset ingestion service "jupyter-uploader-api"
        """

        if dss_code is None:
            dss_code = self.get_datastores()['code'][0]

        # if a sample identifier was given, use it as a string.
        # if a sample object was given, take its identifier
        sampleId = self.sample_to_sample_id(sample)

        parentIds = []
        if parents is not None:
            if not isinstance(parents, list):
                parants = [parents]
            for parent in parents:
                parentIds.append(parent.permId)

        datastore_url = self._get_dss_url(dss_code)
        folder = time.strftime('%Y-%m-%d_%H-%M-%S')

        # upload the files
        data_sets = []
        if notebook_files is not None:
            notebooks_folder = os.path.join(folder, 'notebook_files')
            self.upload_files(
                datastore_url=datastore_url,
                files=notebook_files,
                folder=notebooks_folder,
                wait_until_finished=True
            )
            data_sets.append({
                "dataSetType": "JUPYTER_NOTEBOOk",
                "sessionWorkspaceFolder": notebooks_folder,
                "fileNames": notebook_files,
                "properties": {}
            })
        if result_files is not None:
            results_folder = os.path.join(folder, 'result_files')
            self.upload_files(
                datastore_url=datastore_url,
                files=result_files,
                folder=results_folder,
                wait_until_finished=True
            )
            data_sets.append({
                "dataSetType": "JUPYTER_RESULT",
                "sessionWorkspaceFolder": results_folder,
                "fileNames": result_files,
                "properties": {}
            })

        # register the files in openBIS
        request = {
            "method": "createReportFromAggregationService",
            "params": [
                self.token,
                dss_code,
                PYBIS_PLUGIN,
                {
                    "sampleId": sampleId,
                    "parentIds": parentIds,
                    "containers": [{
                        "dataSetType": "JUPYTER_CONTAINER",
                        "properties": {
                            "NAME": name,
                            "DESCRIPTION": description
                        }
                    }],
                    "dataSets": data_sets,
                }
            ],
        }

        resp = self._post_request(self.reg_v1, request)
        try:
            if resp['rows'][0][0]['value'] == 'OK':
                return resp['rows'][0][1]['value']
        except:
            return resp

    def new_git_data_set(self, data_set_type, path, commit_id, repository_id, dms, sample=None, experiment=None, properties={},
                         dss_code=None, parents=None, data_set_code=None, contents=[]):
        """ Create a link data set.
        :param data_set_type: The type of the data set
        :param data_set_type: The type of the data set
        :param path: The path to the git repository
        :param commit_id: The git commit id
        :param repository_id: The git repository id - same for copies
        :param dms: An external data managment system object or external_dms_id
        :param sample: A sample object or sample id.
        :param dss_code: Code for the DSS -- defaults to the first dss if none is supplied.
        :param properties: Properties for the data set.
        :param parents: Parents for the data set.
        :param data_set_code: A data set code -- used if provided, otherwise generated on the server
        :param contents: A list of dicts that describe the contents:
            {'file_length': [file length],
             'crc32': [crc32 checksum],
             'directory': [is path a directory?]
             'path': [the relative path string]}
        :return: A DataSet object
        """
        return pbds.GitDataSetCreation(self, data_set_type, path, commit_id, repository_id, dms, sample, experiment,
                                       properties, dss_code, parents, data_set_code, contents).new_git_data_set()

    def new_content_copy(self, path, commit_id, repository_id, edms_id, data_set_id):
        """
        Create a content copy in an existing link data set.
        :param path: path of the new content copy
        "param commit_id: commit id of the new content copy
        "param repository_id: repository id of the content copy
        "param edms_id: Id of the external data managment system of the content copy
        "param data_set_id: Id of the data set to which the new content copy belongs
        """
        return pbds.GitDataSetUpdate(self, path, commit_id, repository_id, edms_id, data_set_id).new_content_copy()

    @staticmethod
    def sample_to_sample_id(sample):
        """Take sample which may be a string or object and return an identifier for it."""
        return Openbis._object_to_object_id(sample, "as.dto.sample.id.SampleIdentifier", "as.dto.sample.id.SamplePermId");

    @staticmethod
    def experiment_to_experiment_id(experiment):
        """Take experiment which may be a string or object and return an identifier for it."""
        return Openbis._object_to_object_id(experiment, "as.dto.experiment.id.ExperimentIdentifier", "as.dto.experiment.id.SamplePermId");

    @staticmethod
    def _object_to_object_id(obj, identifierType, permIdType):
        object_id = None
        if isinstance(obj, str):
            if (is_identifier(obj)):
                object_id = {
                    "identifier": obj,
                    "@type": identifierType
                }
            else:
                object_id = {
                    "permId": obj,
                    "@type": permIdType
                }
        else:
            object_id = {
                "identifier": obj.identifier,
                "@type": identifierType
            }
        return object_id

    @staticmethod
    def data_set_to_data_set_id(data_set):
        if isinstance(data_set, str):
            code = data_set
        else:
            code = data_set.permId
        return {
            "permId": code,
            "@type": "as.dto.dataset.id.DataSetPermId"
        }

    def external_data_managment_system_to_dms_id(self, dms):
        if isinstance(dms, str):
            dms_id = {
                "permId": dms,
                "@type": "as.dto.externaldms.id.ExternalDmsPermId"
            }
        else:
            dms_id = {
                "identifier": dms.code,
                "@type": "as.dto.sample.id.SampleIdentifier"
            }
        return dms_id

    def new_sample(self, type, props=None, **kwargs):
        """ Creates a new sample of a given sample type.
        """
        return Sample(self, self.get_sample_type(type), None, props, **kwargs)

    new_object = new_sample # Alias

    def new_dataset(self, type=None, files=None, props=None, folder=None, **kwargs):
        """ Creates a new dataset of a given sample type.
        """
        if files is None:
            raise ValueError('please provide at least one file')
        elif isinstance(files, str):
            files = [files]

        type_obj = self.get_dataset_type(type.upper())

        return DataSet(self, type=type_obj, files=files, folder=folder, props=props, **kwargs)
    
    def new_semantic_annotation(self, entityType=None, propertyType=None, **kwargs):
        return SemanticAnnotation(openbis_obj=self, isNew=True, entityType=entityType, propertyType=propertyType, **kwargs)    

    def _get_dss_url(self, dss_code=None):
        """ internal method to get the downloadURL of a datastore.
        """
        dss = self.get_datastores()
        if dss_code is None:
            return dss['downloadUrl'][0]
        else:
            return dss[dss['code'] == dss_code]['downloadUrl'][0]

    def upload_files(self, datastore_url=None, files=None, folder=None, wait_until_finished=False):

        if datastore_url is None:
            datastore_url = self._get_dss_url()

        if files is None:
            raise ValueError("Please provide a filename.")

        if folder is None:
            # create a unique foldername
            folder = time.strftime('%Y-%m-%d_%H-%M-%S')

        if isinstance(files, str):
            files = [files]

        self.files = files
        self.startByte = 0
        self.endByte = 0

        # define a queue to handle the upload threads
        queue = DataSetUploadQueue()

        real_files = []
        for filename in files:
            if os.path.isdir(filename):
                real_files.extend(
                    [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(filename)) for f in fn])
            else:
                real_files.append(os.path.join(filename))

        # compose the upload-URL and put URL and filename in the upload queue 
        for filename in real_files:
            file_in_wsp = os.path.join(folder, filename)
            self.files_in_wsp.append(file_in_wsp)
            upload_url = (
                datastore_url + '/session_workspace_file_upload'
                + '?filename=' + os.path.join(folder, quote(filename))
                + '&id=1'
                + '&startByte=0&endByte=0'
                + '&sessionID=' + self.token
            )
            queue.put([upload_url, filename, self.verify_certificates])

        # wait until all files have uploaded
        if wait_until_finished:
            queue.join()

        # return files with full path in session workspace
        return self.files_in_wsp


class DataSetUploadQueue():
    def __init__(self, workers=20):
        # maximum files to be uploaded at once
        self.upload_queue = Queue()

        # define number of threads and start them
        for t in range(workers):
            t = Thread(target=self.upload_file)
            t.daemon = True
            t.start()

    def put(self, things):
        """ expects a list [url, filename] which is put into the upload queue
        """
        self.upload_queue.put(things)

    def join(self):
        """ needs to be called if you want to wait for all uploads to be finished
        """
        self.upload_queue.join()

    def upload_file(self):
        while True:
            # get the next item in the queue
            upload_url, filename, verify_certificates = self.upload_queue.get()

            filesize = os.path.getsize(filename)

            # upload the file to our DSS session workspace
            with open(filename, 'rb') as f:
                resp = requests.post(upload_url, data=f, verify=verify_certificates)
                resp.raise_for_status()
                data = resp.json()
                assert filesize == int(data['size'])

            # Tell the queue that we are done
            self.upload_queue.task_done()


class DataSetDownloadQueue():
    def __init__(self, workers=20):
        # maximum files to be downloaded at once
        self.download_queue = Queue()

        # define number of threads
        for t in range(workers):
            t = Thread(target=self.download_file)
            t.daemon = True
            t.start()

    def put(self, things):
        """ expects a list [url, filename] which is put into the download queue
        """
        self.download_queue.put(things)

    def join(self):
        """ needs to be called if you want to wait for all downloads to be finished
        """
        self.download_queue.join()

    def download_file(self):
        while True:
            url, filename, file_size, verify_certificates = self.download_queue.get()
            # create the necessary directory structure if they don't exist yet
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # request the file in streaming mode
            r = requests.get(url, stream=True, verify=verify_certificates)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

            assert os.path.getsize(filename) == int(file_size)
            self.download_queue.task_done()


class OpenBisObject():
    def __init__(self, openbis_obj, type, data=None, props=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['type'] = type
        self.__dict__['p'] = PropertyHolder(openbis_obj, type)
        self.__dict__['a'] = AttrHolder(openbis_obj, 'DataSet', type)

        # existing OpenBIS object
        if data is not None:
            self._set_data(data)

        if props is not None:
            for key in props:
                setattr(self.p, key, props[key])

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def _set_data(self, data):
        # assign the attribute data to self.a by calling it
        # (invoking the AttrHolder.__call__ function)
        self.a(data)
        self.__dict__['data'] = data

        # put the properties in the self.p namespace (without checking them)
        if 'properties' in data:
            for key, value in data['properties'].items():
                self.p.__dict__[key.lower()] = value

    @property
    def attrs(self):
        return self.__dict__['a']

    @property
    def space(self):
        try:
            return self.openbis.get_space(self._space['permId'])
        except Exception:
            pass

    @property
    def project(self):
        try:
            return self.openbis.get_project(self._project['identifier'])
        except Exception:
            pass

    @property
    def experiment(self):
        try:
            return self.openbis.get_experiment(self._experiment['identifier'])
        except Exception:
            pass

    @property
    def sample(self):
        try:
            return self.openbis.get_sample(self._sample['identifier'])
        except Exception:
            pass

    object = sample # Alias

    def __getattr__(self, name):
        return getattr(self.__dict__['a'], name)

    def __setattr__(self, name, value):
        if name in ['set_properties', 'set_tags', 'add_tags']:
            raise ValueError("These are methods which should not be overwritten")

        setattr(self.__dict__['a'], name, value)

    def _repr_html_(self):
        """Print all the assigned attributes (identifier, tags, etc.) in a nicely formatted table. See
        AttributeHolder class.
        """
        return self.a._repr_html_()

    def __repr__(self):
        """same thing as _repr_html_() but for IPython
        """
        return self.a.__repr__()


class LinkedData():
    def __init__(self, data=None):
        self.data = data if data is not None else []
        self.attrs = ['externalCode', 'contentCopies']

    def __dir__(self):
        return self.attrs

    def __getattr__(self, name):
        if name in self.attrs:
            if name in self.data:
                return self.data[name]
        else:
            return ''


class PhysicalData():
    def __init__(self, data=None):
        if data is None:
            data = []
        self.data = data
        self.attrs = ['speedHint', 'complete', 'shareId', 'size',
                      'fileFormatType', 'storageFormat', 'location', 'presentInArchive',
                      'storageConfirmation', 'locatorType', 'status']

    def __dir__(self):
        return self.attrs

    def __getattr__(self, name):
        if name in self.attrs:
            if name in self.data:
                return self.data[name]
        else:
            return ''

    def _repr_html_(self):
        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in self.attrs:
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, getattr(self, attr, '')
            )

        html += """
            </tbody>
            </table>
        """
        return html

    def __repr__(self):

        headers = ['attribute', 'value']
        lines = []
        for attr in self.attrs:
            lines.append([
                attr,
                getattr(self, attr, '')
            ])
        return tabulate(lines, headers=headers)


class DataSet(OpenBisObject):
    """ DataSet are openBIS objects that contain the actual files.
    """

    def __init__(self, openbis_obj, type=type, data=None, files=None, folder=None, props=None, **kwargs):
        super(DataSet, self).__init__(openbis_obj, type, data, props, **kwargs)

        # existing DataSet
        if data is not None:
            if data['physicalData'] is None:
                self.__dict__['shareId'] = None
                self.__dict__['location'] = None
            else:
                self.__dict__['shareId'] = data['physicalData']['shareId']
                self.__dict__['location'] = data['physicalData']['location']
        
        # new DataSet
        if files is not None:
            self.__dict__['files'] = files

        self.__dict__['folder'] = folder


    def __str__(self):
        return self.data['code']

    def __dir__(self):
        return [
            'props', 'get_parents()', 'get_children()', 
            'add_parents()', 'add_children()', 'del_parents()', 'del_children()',
            'sample', 'experiment', 'physicalData', 'linkedData',
            'tags', 'set_tags()', 'add_tags()', 'del_tags()',
            'add_attachment()', 'get_attachments()', 'download_attachments()',
            "get_files(start_folder='/')", 'file_list',
            'download(files=None, destination=None, wait_until_finished=True)', 
            'status', 'archive()', 'unarchive()', 'data'
        ]

    def __setattr__(self, name, value):
        if name in ['folder']:
            self.__dict__[name] = value
        else:
            super(DataSet, self).__setattr__(name, value)

    @property
    def props(self):
        return self.__dict__['p']

    @property
    def type(self):
        return self.__dict__['type']

    @type.setter
    def type(self, type_name):
        dataset_type = self.openbis.get_dataset_type(type_name.upper())
        self.p.__dict__['_type'] = dataset_type
        self.a.__dict__['_type'] = dataset_type

    @property
    def physicalData(self):
        if 'physicalData' in self.data:
            return PhysicalData(self.data['physicalData'])

    @property
    def linkedData(self):
        if 'linkedData' in self.data:
            return LinkedData(self.data['linkedData'])

    @property
    def status(self):
        ds = self.openbis.get_dataset(self.permId)
        self.data['physicalData'] = ds.data['physicalData']
        try:
            return self.data['physicalData']['status']
        except Exception:
            return None

    def archive(self, remove_from_data_store=True):
        fetchopts = {
            "removeFromDataStore": remove_from_data_store,
            "@type": "as.dto.dataset.archive.DataSetArchiveOptions"
        }
        self.archive_unarchive('archiveDataSets', fetchopts)
        print("DataSet {} archived".format(self.permId))

    def unarchive(self):
        fetchopts = {
            "@type": "as.dto.dataset.unarchive.DataSetUnarchiveOptions"
        }
        self.archive_unarchive('unarchiveDataSets', fetchopts)
        print("DataSet {} unarchived".format(self.permId))

    def archive_unarchive(self, method, fetchopts):
        dss = self.get_datastore
        payload = {}

        request = {
            "method": method,
            "params": [
                self.openbis.token,
                [{
                    "permId": self.permId,
                    "@type": "as.dto.dataset.id.DataSetPermId"
                }],
                dict(fetchopts)
            ],
        }
        resp = self.openbis._post_request(self._openbis.as_v3, request)
        return

    def set_properties(self, properties):
        self.openbis.update_dataset(self.permId, properties=properties)

    def download(self, files=None, destination=None, wait_until_finished=True, workers=10):
        """ download the actual files and put them by default in the following folder:
        __current_dir__/destination/dataset_permId/
        If no files are specified, all files of a given dataset are downloaded.
        If no destination is specified, the hostname is chosen instead.
        Files are usually downloaded in parallel, using 10 workers by default. If you want to wait until
        all the files are downloaded, set the wait_until_finished option to True.
        """

        if files == None:
            files = self.file_list
        elif isinstance(files, str):
            files = [files]

        if destination is None:
            destination = self.openbis.hostname

        base_url = self.data['dataStore']['downloadUrl'] + '/datastore_server/' + self.permId + '/'

        queue = DataSetDownloadQueue(workers=workers)

        # get file list and start download
        for filename in files:
            file_info = self.get_file_list(start_folder=filename)
            file_size = file_info[0]['fileSize']
            download_url = base_url + filename + '?sessionID=' + self.openbis.token
            filename_dest = os.path.join(destination, self.permId, filename)
            queue.put([download_url, filename_dest, file_size, self.openbis.verify_certificates])

        # wait until all files have downloaded
        if wait_until_finished:
            queue.join()

        print("Files downloaded to: %s" % os.path.join(destination, self.permId))

    @property
    def folder(self):
        return self.__dict__['folder']

    @property
    def file_list(self):
        """returns the list of files including their directories as an array of strings. Just folders are not
        listed.
        """
        files = []
        for file in self.get_file_list(recursive=True):
            if file['isDirectory']:
                pass
            else:
                files.append(file['pathInDataSet'])
        return files

    def get_files(self, start_folder='/'):
        """Returns a DataFrame of all files in this dataset
        """

        def createRelativePath(pathInDataSet):
            if self.shareId is None:
                return ''
            else:
                return os.path.join(self.shareId, self.location, pathInDataSet)

        def signed_to_unsigned(sig_int):
            """openBIS delivers crc32 checksums as signed integers.
            If the number is negative, we just have to add 2**32
            We display the hex number to match with the classic UI
            """
            if sig_int < 0:
                sig_int += 2 ** 32
            return "%x" % (sig_int & 0xFFFFFFFF)

        files = self.get_file_list(start_folder=start_folder)
        df = DataFrame(files)
        df['relativePath'] = df['pathInDataSet'].map(createRelativePath)
        df['crc32Checksum'] = df['crc32Checksum'].fillna(0.0).astype(int).map(signed_to_unsigned)
        return df[['isDirectory', 'pathInDataSet', 'fileSize', 'crc32Checksum']]

    def get_file_list(self, recursive=True, start_folder="/"):
        """Lists all files of a given dataset. You can specifiy a start_folder other than "/".
        By default, all directories and their containing files are listed recursively. You can
        turn off this option by setting recursive=False.
        """
        request = {
            "method": "listFilesForDataSet",
            "params": [
                self.openbis.token,
                self.permId,
                start_folder,
                recursive,
            ],
            "id": "1"
        }

        resp = requests.post(
            self.data["dataStore"]["downloadUrl"] + '/datastore_server/rmi-dss-api-v1.json',
            json.dumps(request),
            verify=self.openbis.verify_certificates
        )

        if resp.ok:
            data = resp.json()
            if 'error' in data:
                raise ValueError('Error from openBIS: ' + data['error']['message'])
            elif 'result' in data:
                return data['result']
            else:
                raise ValueError('request to openBIS did not return either result nor error')
        else:
            raise ValueError('internal error while performing post request')


    def _generate_plugin_request(self, dss):
        """generates a request to activate the dataset-uploader ingestion plugin to
        register our files as a new dataset
        """

        sample_identifier = None
        if self.sample is not None:
            sample_identifier = self.sample.identifier

        experiment_identifier = None
        if self.experiment is not None:
            experiment_identifier = self.experiment.identifier

        parentIds = self.parents

        dataset_type = self.type.code
        properties = self.props.all_nonempty()

        request = {
            "method": "createReportFromAggregationService",
            "params": [
                self.openbis.token,
                dss,
                PYBIS_PLUGIN,
                {
                    "method" : "insertDataSet",
                    "sampleIdentifier" : sample_identifier,
                    "experimentIdentifier" : experiment_identifier,
                    "dataSetType" : dataset_type,
                    "folderName" : self.folder,
                    "fileNames" : self.files,
                    "isZipDirectoryUpload" : False,
                    "properties" : properties,
                    "parentIdentifiers": parentIds
                }
            ],
        }
        return request


    def save(self):
        if self.is_new:
            if self.files is None or len(self.files) == 0:
                raise ValueError('Cannot register a dataset without a file. Please provide at least one file')

            if self.sample is None and self.experiment is None:
                raise ValueError('A DataSet must be either connected to a Sample or an Experiment')

            # upload the data to the user session workspace
            datastores = self.openbis.get_datastores()

            self.openbis.upload_files(
                datastore_url= datastores['downloadUrl'][0],
                files=self.files,
                folder='',
                wait_until_finished=True
            )

            # activate the ingestion plugin, as soon as the data is uploaded
            request = self._generate_plugin_request(dss=datastores['code'][0])

            resp = self.openbis._post_request(self.openbis.reg_v1, request)

            if resp['rows'][0][0]['value'] == 'OK':
                permId = resp['rows'][0][2]['value']
                if permId is None or permId == '': 
                    self.__dict__['is_new'] = False
                    print("DataSet successfully created. Because you connected to an openBIS version older than 16.05.04, you cannot update the object.")
                else:
                    new_dataset_data = self.openbis.get_dataset(permId, only_data=True)
                    self._set_data(new_dataset_data)
                    print("DataSet successfully created.")
            else:
                raise ValueError('Error while creating the DataSet: ' + resp['rows'][0][1]['value'])

            self.__dict__['_is_new'] = False

            
        else:
            request = self._up_attrs()
            props = self.p._all_props()
            request["params"][1][0]["properties"] = props
            request["params"][1][0].pop('parentIds')
            request["params"][1][0].pop('childIds')

            self.openbis._post_request(self.openbis.as_v3, request)
            print("DataSet successfully updated.")


class AttrHolder():
    """ General class for both samples and experiments that hold all common attributes, such as:
    - space
    - project
    - experiment (sample)
    - samples (experiment)
    - dataset
    - parents (sample, dataset)
    - children (sample, dataset)
    - tags
    """

    def __init__(self, openbis_obj, entity, type=None):
        self.__dict__['_openbis'] = openbis_obj
        self.__dict__['_entity'] = entity

        if type is not None:
            self.__dict__['_type'] = type.data

        self.__dict__['_allowed_attrs'] = _definitions(entity)['attrs']
        self.__dict__['_identifier'] = None
        self.__dict__['_is_new'] = True
        self.__dict__['_tags'] = []

    def __call__(self, data):
        """This internal method is invoked when an existing object is loaded.
        Instead of invoking a special method we «call» the object with the data
           self(data)
        which automatically invokes this method.
        Since the data comes from openBIS, we do not have to check it (hence the
        self.__dict__ statements to prevent invoking the __setattr__ method)
        Internally data is stored with an underscore, e.g.
            sample._space --> { '@id': 4,
                                '@type': 'as.dto.space.id.SpacePermId',
                                'permId': 'MATERIALS' }
        but when fetching the attribute without the underscore, we only return
        the relevant data for the user:
            sample.space  --> 'MATERIALS'
        """
        self.__dict__['_is_new'] = False
        for attr in self._allowed_attrs:
            if attr in ["code", "permId", "identifier",
                        "type", "container", "components"]:
                self.__dict__['_' + attr] = data.get(attr, None)

            elif attr in ["space"]:
                d = data.get(attr, None)
                if d is not None:
                    d = d['permId']
                self.__dict__['_' + attr] = d

            elif attr in ["sample", "experiment", "project"]:
                d = data.get(attr, None)
                if d is not None:
                    d = d['identifier']
                self.__dict__['_' + attr] = d

            elif attr in ["parents", "children", "samples"]:
                self.__dict__['_' + attr] = []
                for item in data[attr]:
                    if 'identifier' in item:
                        self.__dict__['_' + attr].append(item['identifier'])
                    elif 'permId' in item:
                        self.__dict__['_' + attr].append(item['permId'])

            elif attr in ["tags"]:
                tags = []
                for item in data[attr]:
                    tags.append({
                        "code": item['code'],
                        "@type": "as.dto.tag.id.TagCode"
                    })
                self.__dict__['_tags'] = tags
                self.__dict__['_prev_tags'] = copy.deepcopy(tags)
            else:
                self.__dict__['_' + attr] = data.get(attr, None)

    def _new_attrs(self):
        """Returns the Python-equivalent JSON request when a new object is created.
        It is used internally by the save() method of a newly created object.
        """
        defs = _definitions(self.entity)
        attr2ids = _definitions('attr2ids')

        new_obj = {
            "@type": "as.dto.{}.create.{}Creation".format(self.entity.lower(), self.entity)
        }

        for attr in defs['attrs_new']:
            items = None

            if attr == 'type':
                new_obj['typeId'] = self._type['permId']
                continue

            elif attr == 'attachments':
                attachments = getattr(self, '_new_attachments')
                if attachments is None:
                    continue
                atts_data = [attachment.get_data() for attachment in attachments]
                items = atts_data

            elif attr in defs['multi']:
                # parents, children, components, container, tags, attachments
                items = getattr(self, '_' + attr)
                if items is None:
                    items = []
            else:
                items = getattr(self, '_' + attr)

            key = None
            if attr in attr2ids:
                # translate parents into parentIds, children into childIds etc.
                key = attr2ids[attr]
            else:
                key = attr

            new_obj[key] = items

        # create a new entity
        request = {
            "method": "create{}s".format(self.entity),
            "params": [
                self.openbis.token,
                [new_obj]
            ]
        }
        return request


    def _up_attrs(self):
        """Returns the Python-equivalent JSON request when a new object is updated.
        It is used internally by the save() method of an object to be updated.
        """
        defs = _definitions(self._entity)
        attr2ids = _definitions('attr2ids')

        up_obj = {
            "@type": "as.dto.{}.update.{}Update".format(self.entity.lower(), self.entity),
            defs["identifier"]: self._permId
        }

        # look at all attributes available for that entity
        # that can be updated
        for attr in defs['attrs_up']:
            items = None

            if attr == 'attachments':
                # v3 API currently only supports adding attachments
                attachments = self.__dict__.get('_new_attachments', None)
                if attachments is None:
                    continue
                atts_data = [attachment.get_data() for attachment in attachments]

                up_obj['attachments'] = {
                    "actions": [{
                        "items": atts_data,
                        "@type": "as.dto.common.update.ListUpdateActionAdd"
                    }],
                    "@type": "as.dto.attachment.update.AttachmentListUpdateValue"
                }

            elif attr == 'tags':
                # look which tags have been added or removed and update them
                if getattr(self, '_prev_tags') is None:
                    self.__dict__['_prev_tags'] = []
                actions = []
                for tagId in self._prev_tags:
                    if tagId not in self._tags:
                        actions.append({
                            "items": [tagId],
                            "@type": "as.dto.common.update.ListUpdateActionRemove"
                        })

                for tagId in self._tags:
                    if tagId not in self._prev_tags:
                        actions.append({
                            "items": [tagId],
                            "@type": "as.dto.common.update.ListUpdateActionAdd"
                        })

                up_obj['tagIds'] = {
                    "@type": "as.dto.common.update.IdListUpdateValue",
                    "actions": actions
                }

            elif '_' + attr in self.__dict__:
                # handle multivalue attributes (parents, children, tags etc.)
                # we only cover the Set mechanism, which means we always update 
                # all items in a list
                if attr in defs['multi']:
                    items = self.__dict__.get('_' + attr, [])
                    if items == None:
                        items = []
                    up_obj[attr2ids[attr]] = {
                        "actions": [
                            {
                                "items": items,
                                "@type": "as.dto.common.update.ListUpdateActionSet",
                            }
                        ],
                        "@type": "as.dto.common.update.IdListUpdateValue"
                    }
                else:
                    # handle single attributes (space, experiment, project, container, etc.)
                    value = self.__dict__.get('_' + attr, {})
                    if value is None:
                        pass
                    elif len(value) == 0:
                        # value is {}: it means that we want this attribute to be
                        # deleted, not updated.
                        up_obj[attr2ids[attr]] = {
                            "@type": "as.dto.common.update.FieldUpdateValue",
                            "isModified": True,
                        }
                    elif 'isModified' in value and value['isModified'] == True:
                        val = {}
                        for x in ['identifier','permId','@type']:
                            if x in value:
                                val[x] = value[x]

                        up_obj[attr2ids[attr]] = {
                            "@type": "as.dto.common.update.FieldUpdateValue",
                            "isModified": True,
                            "value": val
                        }

        # update a new entity
        request = {
            "method": "update{}s".format(self.entity),
            "params": [
                self.openbis.token,
                [up_obj]
            ]
        }
        return request

    def __getattr__(self, name):
        """ handles all attribute requests dynamically. Values are returned in a sensible way,
            for example the identifiers of parents, children and components are returned
            as an array of values.
        """

        int_name = '_' + name
        if int_name in self.__dict__:
            if int_name in ['_attachments']:
                return [
                    {
                        "fileName": x['fileName'],
                        "title": x['title'],
                        "description": x['description']
                    } for x in self._attachments
                    ]
            if int_name in ['_registrator', '_modifier', '_dataProducer']:
                return self.__dict__[int_name].get('userId', None)
            elif int_name in ['_registrationDate', '_modificationDate', '_accessDate', '_dataProductionDate']:
                return format_timestamp(self.__dict__[int_name])
            # if the attribute contains a list, 
            # return a list of either identifiers, codes or
            # permIds (whatever is available first)
            elif isinstance(self.__dict__[int_name], list):
                values = []
                for item in self.__dict__[int_name]:
                    if "identifier" in item:
                        values.append(item['identifier'])
                    elif "code" in item:
                        values.append(item['code'])
                    elif "permId" in item:
                        values.append(item['permId'])
                    else:
                        pass
                return values
            # attribute contains a dictionary: same procedure as above.
            elif isinstance(self.__dict__[int_name], dict):
                if "identifier" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['identifier']
                elif "code" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['code']
                elif "permId" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['permId']
            else:
                return self.__dict__[int_name]
        else:
            return None

    def __setattr__(self, name, value):
        """This method is always invoked whenever we assign an attribute to an
        object, e.g.
            new_sample.space = 'MATERIALS'
            new_sample.parents = ['/MATERIALS/YEAST747']
        """
        if name in ["parents", "parent", "children", "child", "components"]:
            if name == "parent":
                name = "parents"
            if name == "child":
                name = "children"

            if not isinstance(value, list):
                value = [value]
            objs = []
            for val in value:
                if isinstance(val, str):
                    # fetch objects in openBIS, make sure they actually exists
                    obj = getattr(self._openbis, 'get_' + self._entity.lower())(val)
                    objs.append(obj)
                elif getattr(val, '_permId'):
                    # we got an existing object
                    objs.append(val)

            permids = []
            for item in objs:
                permid = item._permId
                # remove any existing @id keys to prevent jackson parser errors
                if '@id' in permid: permid.pop('@id')
                permids.append(permid)

            # setting self._parents = [{ 
            #    '@type': 'as.dto.sample.id.SampleIdentifier',
            #    'identifier': '/SPACE_NAME/SAMPLE_NAME'
            # }]
            self.__dict__['_' + name] = permids
        elif name in ["tags"]:
            self.set_tags(value)

        elif name in ["attachments"]:
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.add_attachment(**item)
                    else:
                        self.add_attachment(item)

            else:
                self.add_attachment(value)

        elif name in ["space"]:
            obj = None
            if isinstance(value, str):
                # fetch object in openBIS, make sure it actually exists
                obj = getattr(self._openbis, "get_" + name)(value)
            else:
                obj = value

            self.__dict__['_' + name] = obj.data['permId']

            # mark attribute as modified, if it's an existing entity
            if self.is_new:
                pass
            else:
                self.__dict__['_' + name]['isModified'] = True

        elif name in ["sample", "experiment", "project"]:
            obj = None
            if isinstance(value, str):
                # fetch object in openBIS, make sure it actually exists
                obj = getattr(self._openbis, "get_" + name)(value)
            elif value is None:
                self.__dict__['_'+name] = {}
                return
            else:
                obj = value

            self.__dict__['_' + name] = obj.data['identifier']

            # mark attribute as modified, if it's an existing entity
            if self.is_new:
                pass
            else:
                self.__dict__['_' + name]['isModified'] = True


        elif name in ["identifier"]:
            raise KeyError("you can not modify the {}".format(name))
        elif name == "code":
            try:
                if self._type['autoGeneratedCode']:
                    raise KeyError("This {}Type has auto-generated code. You cannot set a code".format(self.entity))
            except KeyError:
                pass
            except TypeError:
                pass

            self.__dict__['_code'] = value

        elif name == "description":
            self.__dict__['_description'] = value
        else:
            raise KeyError("no such attribute: {}".format(name))

    def get_type(self):
        return self._type

    def _ident_for_whatever(self, whatever):
        if isinstance(whatever, str):
            # fetch parent in openBIS, we are given an identifier
            obj = getattr(self._openbis, 'get_'+self._entity.lower())(whatever)
        else:
            # we assume we got an object
            obj = whatever

        ident = None
        if getattr(obj, '_identifier'):
            ident = obj._identifier
        elif getattr(obj, '_permId'):
            ident = obj._permId

        if '@id' in ident: ident.pop('@id')
        return ident

    def get_parents(self, **kwargs):
        identifier = self.identifier
        if identifier is None:
            identifier = self.permId

        if identifier is None:
            # TODO: if this is a new object, return the list of the parents which have been assigned
            pass
        else:
            return getattr(self._openbis, 'get_' + self._entity.lower() + 's')(withChildren=identifier, **kwargs)

    def add_parents(self, parents):
        if getattr(self, '_parents') is None:
            self.__dict__['_parents'] = []
        if not isinstance(parents, list):
            parents = [parents]
        for parent in parents:
            self.__dict__['_parents'].append(self._ident_for_whatever(parent))

    def del_parents(self, parents):
        if getattr(self, '_parents') is None:
            return
        if not isinstance(parents, list):
            parents = [parents]
        for parent in parents:
            ident = self._ident_for_whatever(parent)
            for i, item in enumerate(self.__dict__['_parents']):
                if 'identifier' in ident and 'identifier' in item and ident['identifier'] == item['identifier']:
                    self.__dict__['_parents'].pop(i)
                elif 'permId' in ident and 'permId' in item and ident['permId'] == item['permId']:
                    self.__dict__['_parents'].pop(i)

    def get_children(self, **kwargs):
        identifier = self.identifier
        if identifier is None:
            identifier = self.permId

        if identifier is None:
            # TODO: if this is a new object, return the list of the children which have been assigned
            pass
        else:
            # e.g. self._openbis.get_samples(withParents=self.identifier)
            return getattr(self._openbis, 'get_' + self._entity.lower() + 's')(withParents=identifier, **kwargs)

    def add_children(self, children):
        if getattr(self, '_children') is None:
            self.__dict__['_children'] = []
        if not isinstance(children, list):
            children = [children]
        for child in children:
            self.__dict__['_children'].append(self._ident_for_whatever(child))

    def del_children(self, children):
        if getattr(self, '_children') is None:
            return
        if not isinstance(children, list):
            children = [children]
        for child in children:
            ident = self._ident_for_whatever(child)
            for i, item in enumerate(self.__dict__['_children']):
                if 'identifier' in ident and 'identifier' in item and ident['identifier'] == item['identifier']:
                    self.__dict__['_children'].pop(i)
                elif 'permId' in ident and 'permId' in item and ident['permId'] == item['permId']:
                    self.__dict__['_children'].pop(i)

    @property
    def tags(self):
        if getattr(self, '_tags') is not None:
            return [x['code'] for x in self._tags]

    def set_tags(self, tags):
        if getattr(self, '_tags') is None:
            self.__dict__['_tags'] = []

        tagIds = _create_tagIds(tags)

        # remove tags that are not in the new tags list
        for tagId in self.__dict__['_tags']:
            if tagId not in tagIds:
                self.__dict__['_tags'].remove(tagId)

        # add all new tags that are not in the list yet
        for tagId in tagIds:
            if tagId not in self.__dict__['_tags']:
                self.__dict__['_tags'].append(tagId)

    def add_tags(self, tags):
        if getattr(self, '_tags') is None:
            self.__dict__['_tags'] = []

        # add the new tags to the _tags and _new_tags list,
        # if not listed yet
        tagIds = _create_tagIds(tags)
        for tagId in tagIds:
            if not tagId in self.__dict__['_tags']:
                self.__dict__['_tags'].append(tagId)

    def del_tags(self, tags):
        if getattr(self, '_tags') is None:
            self.__dict__['_tags'] = []

        # remove the tags from the _tags and _del_tags list,
        # if listed there
        tagIds = _create_tagIds(tags)
        for tagId in tagIds:
            if tagId in self.__dict__['_tags']:
                self.__dict__['_tags'].remove(tagId)

    def get_attachments(self):
        if getattr(self, '_attachments') is None:
            return None
        else:
            return DataFrame(self._attachments)[['fileName', 'title', 'description', 'version']]

    def add_attachment(self, fileName, title=None, description=None):
        att = Attachment(filename=fileName, title=title, description=description)
        if getattr(self, '_attachments') is None:
            self.__dict__['_attachments'] = []
        self._attachments.append(att.get_data_short())

        if getattr(self, '_new_attachments') is None:
            self.__dict__['_new_attachments'] = []
        self._new_attachments.append(att)

    def download_attachments(self):
        method = 'get' + self.entity + 's'
        entity = self.entity.lower()
        request = {
            "method": method,
            "params": [self._openbis.token,
                       [self._permId],
                       dict(
                           attachments=fetch_option['attachmentsWithContent'],
                           **fetch_option[entity]
                       )
                       ]
        }
        resp = self._openbis._post_request(self._openbis.as_v3, request)
        attachments = resp[self.permId]['attachments']
        file_list = []
        for attachment in attachments:
            filename = os.path.join(
                self._openbis.hostname,
                self.permId,
                attachment['fileName']
            )
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as att:
                content = base64.b64decode(attachment['content'])
                att.write(content)
            file_list.append(filename)
        return file_list

    def _repr_html_(self):
        def nvl(val, string=''):
            if val is None:
                return string
            return val

        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in self._allowed_attrs:
            if attr == 'attachments':
                continue
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, nvl(getattr(self, attr, ''), '')
            )
        if getattr(self, '_attachments') is not None:
            html += "<tr><td>attachments</td><td>"
            html += "<br/>".join(att['fileName'] for att in self._attachments)
            html += "</td></tr>"

        html += """
            </tbody>
            </table>
        """
        return html

    def __repr__(self):

        headers = ['attribute', 'value']
        lines = []
        for attr in self._allowed_attrs:
            if attr == 'attachments':
                continue
            lines.append([
                attr,
                nvl(getattr(self, attr, ''))
            ])
        return tabulate(lines, headers=headers)


class Sample():
    """ A Sample is one of the most commonly used objects in openBIS.
    """

    def __init__(self, openbis_obj, type, data=None, props=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['type'] = type
        self.__dict__['p'] = PropertyHolder(openbis_obj, type)
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Sample', type)

        if data is not None:
            self._set_data(data)

        if props is not None:
            for key in props:
                setattr(self.p, key, props[key])

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def _set_data(self, data):
        # assign the attribute data to self.a by calling it
        # (invoking the AttrHolder.__call__ function)
        self.a(data)
        self.__dict__['data'] = data

        # put the properties in the self.p namespace (without checking them)
        for key, value in data['properties'].items():
            self.p.__dict__[key.lower()] = value

    def __dir__(self):
        return [
            'props', 'get_parents()', 'get_children()', 
            'add_parents()', 'add_children()', 'del_parents()', 'del_children()',
            'get_datasets()', 'get_experiment()',
            'space', 'project', 'experiment', 'tags',
            'set_tags()', 'add_tags()', 'del_tags()',
            'add_attachment()', 'get_attachments()', 'download_attachments()',
            'save()', 'delete()'
        ]

    @property
    def props(self):
        return self.__dict__['p']

    @property
    def type(self):
        return self.__dict__['type']

    @type.setter
    def type(self, type_name):
        sample_type = self.openbis.get_sample_type(type_name)
        self.p.__dict__['_type'] = sample_type
        self.a.__dict__['_type'] = sample_type

    def __getattr__(self, name):
        return getattr(self.__dict__['a'], name)

    def __setattr__(self, name, value):
        if name in ['set_properties', 'set_tags', 'add_tags']:
            raise ValueError("These are methods which should not be overwritten")

        setattr(self.__dict__['a'], name, value)

    def _repr_html_(self):
        return self.a._repr_html_()

    def __repr__(self):
        return self.a.__repr__()

    def set_properties(self, properties):
        self.openbis.update_sample(self.permId, properties=properties)

    def save(self):
        props = self.p._all_props()

        if self.is_new:
            request = self._new_attrs()
            request["params"][1][0]["properties"] = props
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            print("Sample successfully created.")
            new_sample_data = self.openbis.get_sample(resp[0]['permId'], only_data=True)
            self._set_data(new_sample_data)
            return self

        else:
            request = self._up_attrs()
            request["params"][1][0]["properties"] = props
            self.openbis._post_request(self.openbis.as_v3, request)
            print("Sample successfully updated.")
            new_sample_data = self.openbis.get_sample(self.permId, only_data=True)
            self._set_data(new_sample_data)

    def delete(self, reason):
        self.openbis.delete_entity('sample', self.permId, reason)

    def get_datasets(self, **kwargs):
        return self.openbis.get_datasets(sample=self.permId, **kwargs)

    def get_projects(self, **kwargs):
        return self.openbis.get_project(withSamples=[self.permId], **kwargs)

    def get_experiment(self):
        try:
            return self.openbis.get_experiment(self._experiment['identifier'])
        except Exception:
            pass

    @property
    def experiment(self):
        try:
            return self.openbis.get_experiment(self._experiment['identifier'])
        except Exception:
            pass


class Space(OpenBisObject):
    """ managing openBIS spaces
    """

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Space' )

        if data is not None:
            self.a(data)
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return [
            'code', 'permId', 'description', 'registrator', 'registrationDate', 'modificationDate', 
            'get_projects()', 
            "new_project(code='', description='', attachments)", 
            'get_samples()', 
            'delete()'
        ]

    def __str__(self):
        return self.data.get('code', None)

    def get_samples(self, **kwargs):
        return self.openbis.get_samples(space=self.code, **kwargs)

    get_objects = get_samples #Alias

    def get_sample(self, sample_code):
        if is_identifier(sample_code) or is_permid(sample_code):
            return self.openbis.get_sample(sample_code)
        else:
            # we assume we just got the code
            return self.openbis.get_sample('/{}/{}'.format(self.code,sample_code) )


    def get_projects(self, **kwargs):
        return self.openbis.get_projects(space=self.code, **kwargs)

    def new_project(self, code, description=None, **kwargs):
        return self.openbis.new_project(self.code, code, description, **kwargs)

    def new_sample(self, **kwargs):
        return self.openbis.new_sample(space=self, **kwargs)

    def delete(self, reason):
        self.openbis.delete_entity('Space', self.permId, reason)
        print("Space {} has been sucessfully deleted.".format(self.permId))

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)
            print("Space successfully created.")
            new_space_data = self.openbis.get_space(resp[0]['permId'], only_data=True)
            self._set_data(new_space_data)
            return self

        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            print("Space successfully updated.")
            new_space_data = self.openbis.get_space(self.permId, only_data=True)
            self._set_data(new_space_data)


class ExternalDMS():
    """ managing openBIS external data management systems
    """

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj

        if data is not None:
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __getattr__(self, name):
        return self.__dict__['data'].get(name)

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return ['code', 'label', 'urlTemplate', 'address', 'addressType', 'openbis']

    def __str__(self):
        return self.data.get('code', None)


class Things():
    """An object that contains a DataFrame object about an entity  available in openBIS.
       
    """

    def __init__(self, openbis_obj, entity, df, identifier_name='code'):
        self.openbis = openbis_obj
        self.entity = entity
        self.df = df
        self.identifier_name = identifier_name

    def __repr__(self):
        return tabulate(self.df, headers=list(self.df))

    def __len__(self):
        return len(self.df)

    def _repr_html_(self):
        return self.df._repr_html_()

    def get_parents(self, **kwargs):
        if self.entity not in ['sample', 'dataset']:
            raise ValueError("{}s do not have parents".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                # get all objects that have this object as a child == parent
                try:
                    parents = getattr(self.openbis, 'get_' + self.entity.lower() + 's')(withChildren=ident, **kwargs)
                    dfs.append(parents.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, self.entity, pd.concat(dfs), self.identifier_name)
            else:
                return Things(self.openbis, self.entity, DataFrame(), self.identifier_name)

    def get_children(self, **kwargs):
        if self.entity not in ['sample', 'dataset']:
            raise ValueError("{}s do not have children".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                # get all objects that have this object as a child == parent
                try:
                    parents = getattr(self.openbis, 'get_' + self.entity.lower() + 's')(withParent=ident, **kwargs)
                    dfs.append(parents.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, self.entity, pd.concat(dfs), self.identifier_name)
            else:
                return Things(self.openbis, self.entity, DataFrame(), self.identifier_name)

    def get_samples(self, **kwargs):
        if self.entity not in ['space', 'project', 'experiment']:
            raise ValueError("{}s do not have samples".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                args = {}
                args[self.entity.lower()] = ident
                try:
                    samples = self.openbis.get_samples(**args, **kwargs)
                    dfs.append(samples.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, 'sample', pd.concat(dfs), 'identifier')
            else:
                return Things(self.openbis, 'sample', DataFrame(), 'identifier')

    get_objects = get_samples # Alias

    def get_datasets(self, **kwargs):
        if self.entity not in ['sample', 'experiment']:
            raise ValueError("{}s do not have datasets".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                args = {}
                args[self.entity.lower()] = ident
                try:
                    datasets = self.openbis.get_datasets(**args, **kwargs)
                    dfs.append(datasets.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, 'dataset', pd.concat(dfs), 'permId')
            else:
                return Things(self.openbis, 'dataset', DataFrame(), 'permId')

    def __getitem__(self, key):
        if self.df is not None and len(self.df) > 0:
            row = None
            if isinstance(key, int):
                # get thing by rowid
                row = self.df.loc[[key]]
            elif isinstance(key, list):
                # treat it as a normal dataframe
                return self.df[key]
            else:
                # get thing by code
                row = self.df[self.df[self.identifier_name] == key.upper()]

            if row is not None:
                # invoke the openbis.get_entity() method
                return getattr(self.openbis, 'get_' + self.entity)(row[self.identifier_name].values[0])

    def __iter__(self):
        for item in self.df[[self.identifier_name]][self.identifier_name].iteritems():
            yield getattr(self.openbis, 'get_' + self.entity)(item[1])

            # return self.df[[self.identifier_name]].to_dict()[self.identifier_name]


class Experiment(OpenBisObject):
    """ 
    """

    def __init__(self, openbis_obj, type, project=None, data=None, props=None, code=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['type'] = type
        self.__dict__['p'] = PropertyHolder(openbis_obj, type)
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Experiment', type)

        if data is not None:
            self._set_data(data)

        if project is not None:
            setattr(self, 'project', project)

        if props is not None:
            for key in props:
                setattr(self.p, key, props[key])

        if code is not None:
            self.code = code

        if kwargs is not None:
            defs = _definitions('Experiment')
            for key in kwargs:
                if key in defs['attrs']:
                    setattr(self, key, kwargs[key])
                else:
                    raise ValueError("{attr} is not a known attribute for an Experiment".format(attr=key))


    def _set_data(self, data):
        # assign the attribute data to self.a by calling it
        # (invoking the AttrHolder.__call__ function)
        self.a(data)
        self.__dict__['data'] = data

        # put the properties in the self.p namespace (without checking them)
        for key, value in data['properties'].items():
            self.p.__dict__[key.lower()] = value

    def __str__(self):
        return self.data['code']

    def __dir__(self):
        # the list of possible methods/attributes displayed
        # when invoking TAB-completition
        return [
            'code', 'permId', 'identifier',
            'type', 'project',
            'props.', 
            'project', 'tags', 'attachments', 'data',
            'get_datasets()', 'get_samples()',
            'set_tags()', 'add_tags()', 'del_tags()',
            'add_attachment()', 'get_attachments()', 'download_attachments()',
            'save()'
        ]

    @property
    def props(self):
        return self.__dict__['p']

    @property
    def type(self):
        return self.__dict__['type']

    @type.setter
    def type(self, type_name):
        experiment_type = self.openbis.get_experiment_type(type_name)
        self.p.__dict__['_type'] = experiment_type
        self.a.__dict__['_type'] = experiment_type

    def __getattr__(self, name):
        return getattr(self.__dict__['a'], name)

    def __setattr__(self, name, value):
        if name in ['set_properties', 'add_tags()', 'del_tags()', 'set_tags()']:
            raise ValueError("These are methods which should not be overwritten")

        setattr(self.__dict__['a'], name, value)

    def _repr_html_(self):
        html = self.a._repr_html_()
        return html

    def set_properties(self, properties):
        self.openbis.update_experiment(self.permId, properties=properties)

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            props = self.p._all_props()
            request["params"][1][0]["properties"] = props
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            print("Experiment successfully created.")
            new_exp_data = self.openbis.get_experiment(resp[0]['permId'], only_data=True)
            self._set_data(new_exp_data)
            return self
        else:
            request = self._up_attrs()
            props = self.p._all_props()
            request["params"][1][0]["properties"] = props
            self.openbis._post_request(self.openbis.as_v3, request)
            print("Experiment successfully updated.")
            new_exp_data = self.openbis.get_experiment(resp[0]['permId'], only_data=True)
            self._set_data(new_exp_data)

    def delete(self, reason):
        if self.permId is None:
            return None
        self.openbis.delete_entity('experiment', self.permId, reason)

    def get_datasets(self, **kwargs):
        if self.permId is None:
            return None
        return self.openbis.get_datasets(experiment=self.permId, **kwargs)

    def get_projects(self, **kwargs):
        if self.permId is None:
            return None
        return self.openbis.get_project(experiment=self.permId, **kwargs)

    def get_samples(self, **kwargs):
        if self.permId is None:
            return None
        return self.openbis.get_samples(experiment=self.permId, **kwargs)

    get_objects = get_samples # Alias

    def add_samples(self, *samples):

        for sample in samples:
            if isinstance(sample, str):
                obj = self.openbis.get_sample(sample)
            else:
                # we assume we got a sample object
                obj = sample

            # a sample can only belong to exactly one experiment
            if obj.experiment is not None:
                raise ValueError(
                    "sample {} already belongs to experiment {}".format(
                        obj.code, obj.experiment
                    )
                )
            else:
                if self.is_new:
                    raise ValueError("You need to save this experiment first before you can assign any samples to it")
                else:
                    # update the sample directly
                    obj.experiment = self.identifier
                    obj.save()
                    self.a.__dict__['_samples'].append(obj._identifier)

    add_objects = add_samples # Alias

    def del_samples(self, samples):
        if not isinstance(samples, list):
            samples = [samples]

        
        for sample in samples:
            if isinstance(sample, str):
                obj = self.openbis.get_sample(sample)
                objects.append(obj)
            else:
                # we assume we got an object
                objects.append(obj)
        
        self.samples = objects

    del_objects = del_samples # Alias

class Attachment():
    def __init__(self, filename, title=None, description=None):
        if not os.path.exists(filename):
            raise ValueError("File not found: {}".format(filename))
        self.fileName = filename
        self.title = title
        self.description = description

    def get_data_short(self):
        return {
            "fileName": self.fileName,
            "title": self.title,
            "description": self.description,
        }

    def get_data(self):
        with open(self.fileName, 'rb') as att:
            content = att.read()
            contentb64 = base64.b64encode(content).decode()
        return {
            "fileName": self.fileName,
            "title": self.title,
            "description": self.description,
            "content": contentb64,
            "@type": "as.dto.attachment.create.AttachmentCreation",
        }


class Project(OpenBisObject):
    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Project')

        if data is not None:
            self.a(data)
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def _modifiable_attrs(self):
        return

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return ['code', 'permId', 'identifier', 'description', 'space', 'registrator',
                'registrationDate', 'modifier', 'modificationDate', 'add_attachment()',
                'get_attachments()', 'download_attachments()',
                'get_experiments()', 'get_samples()', 'get_datasets()',
                'save()', 'delete()'
                ]

    def get_samples(self, **kwargs):
        return self.openbis.get_samples(project=self.permId, **kwargs)

    def get_sample(self, sample_code):
        if is_identifier(sample_code) or is_permid(sample_code):
            return self.openbis.get_sample(sample_code)
        else:
            # we assume we just got the code
            return self.openbis.get_sample(project=self, code=sample_code)

    get_objects = get_samples # Alias

    def get_experiments(self):
        return self.openbis.get_experiments(project=self.permId)

    def get_datasets(self):
        return self.openbis.get_datasets(project=self.permId)

    def delete(self, reason):
        self.openbis.delete_entity('project', self.permId, reason)

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)
            self.a.__dict__['_is_new'] = False
            print("Project successfully created.")
            new_project_data = self.openbis.get_project(resp[0]['permId'], only_data=True)
            self._set_data(new_project_data)
            return self
        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            print("Project successfully updated.")


class SemanticAnnotation():
    def __init__(self, openbis_obj, isNew=True, **kwargs):
        self._openbis = openbis_obj
        self._isNew = isNew;
        
        self.permId = kwargs.get('permId')
        self.entityType = kwargs.get('entityType')
        self.propertyType = kwargs.get('propertyType')
        self.predicateOntologyId = kwargs.get('predicateOntologyId')
        self.predicateOntologyVersion = kwargs.get('predicateOntologyVersion')
        self.predicateAccessionId = kwargs.get('predicateAccessionId')
        self.descriptorOntologyId = kwargs.get('descriptorOntologyId')
        self.descriptorOntologyVersion = kwargs.get('descriptorOntologyVersion')
        self.descriptorAccessionId = kwargs.get('descriptorAccessionId')
        self.creationDate = kwargs.get('creationDate')

    def __dir__(self):
        return ['permId', 'entityType', 'propertyType', 'predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId', 'creationDate', 'save()', 'delete()' ]

    def save(self):
        if self._isNew:
            self._create()
        else:
            self._update()
            
    def _create(self):
        
        creation = {
            "@type": "as.dto.semanticannotation.create.SemanticAnnotationCreation"
        }

        if self.entityType is not None and self.propertyType is not None:
            creation["propertyAssignmentId"] = {
                "@type": "as.dto.property.id.PropertyAssignmentPermId",
                "entityTypeId" : {
                    "@type": "as.dto.entitytype.id.EntityTypePermId",
                    "permId" : self.entityType,
                    "entityKind" : "SAMPLE"
                },
                "propertyTypeId" : {
                    "@type" : "as.dto.property.id.PropertyTypePermId",
                    "permId" : self.propertyType
                }
            }
        elif self.entityType is not None:
            creation["entityTypeId"] = {
                "@type": "as.dto.entitytype.id.EntityTypePermId",
                "permId" : self.entityType,
                "entityKind" : "SAMPLE"
            }
        elif self.propertyType is not None:
            creation["propertyTypeId"] = {
                "@type" : "as.dto.property.id.PropertyTypePermId",
                "permId" : self.propertyType
            }
            
        for attr in ['predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId']:
            creation[attr] = getattr(self, attr)

        request = {
            "method": "createSemanticAnnotations",
            "params": [
                self._openbis.token,
                [creation]
            ]
        }
        
        self._openbis._post_request(self._openbis.as_v3, request)
        self._isNew = False
        
        print("Semantic annotation successfully created.")
    
    def _update(self):
        
        update = {
            "@type": "as.dto.semanticannotation.update.SemanticAnnotationUpdate",
            "semanticAnnotationId" : {
                "@type" : "as.dto.semanticannotation.id.SemanticAnnotationPermId",
                "permId" : self.permId
            }
        }
        
        for attr in ['predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId']:
            update[attr] = {
                "@type" : "as.dto.common.update.FieldUpdateValue",
                "isModified" : True,
                "value" : getattr(self, attr)
            }
            
        request = {
            "method": "updateSemanticAnnotations",
            "params": [
                self._openbis.token,
                [update]
            ]
        }
        
        self._openbis._post_request(self._openbis.as_v3, request)
        print("Semantic annotation successfully updated.")
    
    def delete(self, reason):
        self._openbis.delete_entity('SemanticAnnotation', self.permId, reason, False)
        print("Semantic annotation successfully deleted.")
