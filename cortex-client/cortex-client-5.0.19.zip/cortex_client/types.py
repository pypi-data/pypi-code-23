"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from collections import namedtuple
from typing import Dict, Any, List, Union

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class Model:
    """
    A Model holds information related to a train request. 

    :param agentId: The agent instance ID.
    :param processorId: The unique id of the processor.
    :param name: The name of the new Model.
    :param description: An arbitrary textual description.
    """

    def __init__(self, agentId, processorId, name, description, _id=None):
        self.agent_id = agentId
        self.processor_id = processorId
        self.name = name
        self.description = description
        self._id = _id

    ## TODO: rename to from_params
    @classmethod
    def _make(cls, json):
        return cls(json['agentId'], 
                   json['processorId'], 
                   json['name'], 
                   json['description'], 
                   json['_id'])

ModelEvent = namedtuple('ModelEvent', ['trainedModelId', 'key', 'value'])
ModelEvent.__doc__ = """\
    An event associated with a specific Model.

    :param trainedModelId: the unique ID of the Model to which this event belongs.
    :param key: A string that labels the event. e.g., 'train.status'.
    :param value: An arbitrary string with the information this event carries.
"""


class InputMessage:
    """The message structure that Cortex sends when making request across its APIs.

        :param instance_id: The Agent instance ID.
        :param session_id: Cortex's session ID.
        :param channel_id: This is the Skill/Processor ID.
        :param type_name: The name of the type associated with this message.
        :param payload: The payload of an HTTP request made to a Cortex service. 
        :param properties: The Skill properties associated with this message.
        :param api_endpoint:  The Cortex URL.
        :param token: The JWT token necessary to make HTTP request to Cortex REST APIs.
    """
    
    def __init__(self, instance_id, 
                       session_id, 
                       channel_id, 
                       type_name, 
                       payload, 
                       properties, 
                       api_endpoint, 
                       token):
        self.instance_id = instance_id
        self.session_id = session_id
        self.channel_id = channel_id
        self.type_name = type_name
        self.payload = payload
        self.properties = properties
        self.api_endpoint = api_endpoint
        self.token = token

    @property
    def instance_id(self):
        return self._instance_id

    @instance_id.setter
    def instance_id(self, id):
        if not id: raise ValueError('instance_id not set')
        self._instance_id = id

    @property
    def session_id(self):
        return self._session_id

    @session_id.setter
    def session_id(self, id):
        if not id: raise ValueError('session_id not set')
        self._session_id = id

    @property
    def channel_id(self):
        return self._channel_id

    @channel_id.setter
    def channel_id(self, id):
        if not id: raise ValueError('channel_id not set')
        self._channel_id = id

    @property
    def type_name(self):
        return self._type_name

    @type_name.setter
    def type_name(self, name):
        if not name: raise ValueError('type_name not set')
        self._type_name = name

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, p):
        self._payload = p or {}

    @property
    def api_endpoint(self):
        return self._api_endpoint

    @api_endpoint.setter
    def api_endpoint(self, ep):
        if not ep: raise ValueError('api_endpoint not set')
        self._api_endpoint = ep

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, t):
        if not t: raise ValueError('token not set')
        self._token = t

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, props):
        self._properties = props or {}

    @staticmethod
    def from_params(params):
        return InputMessage(
            params.get('instanceId'), 
            params.get('sessionId'), 
            params.get('channelId'), 
            params.get('typeName'), 
            params.get('payload'),
            params.get('properties'),
            params.get('apiEndpoint'),
            params.get('token'))
 
    def to_params(self):
        return {'instanceId':   self.instance_id,
                'sessionId':    self.session_id,
                'channelId':    self.channel_id,
                'typeName':     self.type_name,
                'payload':      self.payload,
                'properties':   self.properties,
                'apiEndpoint':  self.api_endpoint,
                'token':        self.token}


## TODO: deprecate in favor of just InputMessage.from_params
def mk_inputMessage(params: Dict[str, object]):
    return InputMessage.from_params(params)


class OutputMessage:
    """The message structure to send back to Cortex as response to Cortex Agent Serivce calls. 

    :param payload: The payload to send to Cortex.
    :param type_name: The name of the Cortex Type of this message.
    """

    def __init__(self, payload, type_name):
        self.payload = payload
        self.type_name = type_name

    @staticmethod
    def create():
        return OutputMessage({}, 'cortex/Any')

    def with_payload(self, payload):
        self.payload = payload
        return self

    def with_type(self, type_name):
        self.type_name = type_name
        return self

    def to_params(self):
        return {'payload': self.payload, 'typeName': self.type_name}
