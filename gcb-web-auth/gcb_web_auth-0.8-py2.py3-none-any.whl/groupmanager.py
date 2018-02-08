from __future__ import absolute_import
import requests


def user_belongs_to_group(group_manager_connection, duke_unique_id, group_name):
    """
    Returns True if the user associated with duke_unique_id is in a particular GroupManager group
    :param group_manager_connection: GroupManagerConnection: settings used to talk to group manager
    :param duke_unique_id: str: unique id (number) of the user we want to check
    :param group_name: str: name of the group to check (eg. 'duke:group-manager:roles:bespin-users')
    :return: boolean: True if the user belongs to that agroup
    """
    return group_name in get_users_group_names(group_manager_connection, duke_unique_id)


def get_users_group_names(group_manager_connection, duke_unique_id):
    """
    Returns list of GroupManager group names associated with a duke user
    :param group_manager_connection: GroupManagerConnection: settings used to talk to group manager
    :param duke_unique_id: str: unique id (number) of the user we want to check
    :return: [str]: list of group names (eg. ['duke:group-manager:roles:bespin-users'] )
    """
    response_payload = _fetch_users_groups(group_manager_connection, duke_unique_id)
    group_data = response_payload['WsGetGroupsLiteResult']['wsGroups']
    return [data['name'] for data in group_data]


def _fetch_users_groups(group_manager_connection, duke_unique_id):
    auth = (group_manager_connection.account_id, group_manager_connection.password)
    url = make_users_groups_url(group_manager_connection.base_url, duke_unique_id)
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    return resp.json()


def make_users_groups_url(base_url, duke_unique_id):
    """
    Create url for fetching a users groups.
    :param base_url: base group manager url (eg. 'https://groups.oit.duke.edu/grouper-ws/servicesRest/json/v2_1_500/')
    :param duke_unique_id: str: unique id (number) of the user we want to build a url for
    :return: str: url we created
    """
    return "{}/subjects/{}/groups".format(base_url, duke_unique_id)



