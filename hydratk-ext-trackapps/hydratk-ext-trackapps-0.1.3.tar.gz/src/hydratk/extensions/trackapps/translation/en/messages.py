# -*- coding: utf-8 -*-

"""This code is a part of Hydra Toolkit

.. module:: hydratk.extensions.testenv.translation.en
   :platform: Unix
   :synopsis: English language translation for TestEnv extension
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

language = {
    'name': 'English',
    'ISO-639-1': 'en'
}

msg = {
    'track_connecting': ["Connecting to server with params: {0}"],
    'track_connected': ["Connected successfully"],
    'track_missing_cookie': ["Cookie missing in response"],
    'track_missing_token': ["Token missing in response"],
    'track_missing_project': ["Project {0} not found"],
    'track_error': ["Error occured status:'{0}', error: {1}"],
    'track_disconnecting': ["Disconnecting from server"],
    'track_disconnected': ["Disconnected from server"],
    'track_not_connected': ["Not connected to server"],
    'track_reading': ["Reading records with params: {0}"],
    'track_read': ["Records read: '{0}'"],
    'track_creating': ["Creating record entity:'{0}', params: {1}"],
    'track_created': ["Record with id:'{0}' created"],
    'track_updating': ["Updating record entity:'{0}', id:'{1}', params: {2}"],
    'track_updated': ["Record with id:'{0}' updated"],
    'track_deleting': ["Deleting record entity:'{0}', id:'{1}'"],
    'track_deleted': ["Record with id:'{0}' deleted"],
    'track_unknown_record': ["Unknown record with id:'{0}'"],
    'track_unknown_entity': ["Unknown entity:'{0}'"],
    'track_unknown_folder': ["Unknown test folder:'{0}'"],
    'track_reading_folder': ["Reading test folder: '{0}', entity:'{1}'"],
    'track_folder_read': ["Tests in folder read: '{0}'"],
    'track_missing_hier': ["Missing hierarchical path in test folder:'{0}'"],
    'track_reading_set': ["Reading test set: '{0}'"],
    'track_set_read': ["Tests in set read: '{0}'"]
}
