# -*- coding: utf-8 -*-
from contacthub.node import Node
from contacthub._parsers._config_parser import _GeneralConfigParser


class Workspace(object):
    """
    Workspace class for authenticating on the specified base url APIs.
    This class is the first step for accessing the Contacthub APIs, the higher level.
    """

    def __init__(self, workspace_id, token, base_url='https://api.contactlab.it/hub/v1/workspaces'):
        """
        :param workspace_id: The ID associated at the unique workspace on Contacthub. This parameter is given by Contacthub
        :param token: Authentication token. This parameter is given by Contacthub
        :param base_url: Optional base URL for accessing the APIs
        """
        self.workspace_id = str(workspace_id)
        self.token = str(token)
        self.base_url = str(base_url)

    @classmethod
    def from_ini_file(cls, file_path):
        """
        Create a new Workspace object, taking the Workspace id, the token and the base URL from a INI configuration file

        :param file_path: The path of the INI file for the parameters
        :return: a new Workspace object
        """
        options = _GeneralConfigParser(file_path).get_options()
        workspace_id = options.get('workspace_id', '')
        token = options.get('token', '')
        base_url = options.get('base_url', '')
        if workspace_id and token:
            if base_url:
                return Workspace(workspace_id=workspace_id, token=token, base_url=base_url)
            else:
                return Workspace(workspace_id=workspace_id, token=token)
        raise KeyError("workspace_id or token parameter not found in INI file")

    def get_node(self, node_id):
        """
        Retrieve the node associated at the specified node id

        :param node_id: The ID of the node to retrieve
        :return: a Node object with the Workspace object specified
        """
        return Node(self, node_id)



