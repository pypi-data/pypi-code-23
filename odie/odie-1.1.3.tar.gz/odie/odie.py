#!/usr/bin/env python

import os
import sys
import re

import json
import requests
import tempfile
import datetime
import getpass
from ruamel.yaml import YAML
from StringIO import StringIO

from subprocess import call
from requests.auth import HTTPBasicAuth


def questions(Question = None):
    x = raw_input(Question)
    y = "Y|y|Yes|yes"
    lists = y.split('|')

    if x in lists:
        return True
    else:
        return False


class Odie:
    def __init__(self, base_url=None, username=None, password=None):
        """
        Uses default RESTHeart creds if none given

        :keyword base_url: URL to query. (Mandatory)
        :type            : string
        """

        if base_url is None:
            raise Exception("Keyword base_url required")

        self.base_url = base_url
        self.username = username
        self.password = password

        self.headers = {'Content-Type': 'application/json'}
        self.yaml = YAML()
        self.stream = StringIO()
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def get_json(self, url):
        """
        HTTP GET JSON Data

        :keyword url: HTTP GET URL
        :type         : string

        :return: dict
        :rtype: dict
        """
        r = requests.get(url=url, headers=self.headers, auth=(self.username, self.password))
        if r.status_code not in (200,201,202,203,204,205,206,207,208,226):
            return None
        try:
            return json.loads(r.content)
        except:
            raise Exception("Unable to load json from url: {}".format(url))

    def put_json(self, url, data):
        """
        HTTP PUT JSON Data

        :keyword url: HTTP PUT URL
        :type         : string

        :keyword data: HTTP PUT data
        :type         : dict

        :return: True
        :rtype: boolean
        """
        r = requests.put(url=url, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password))
        # 201 > Created
        if r.status_code in (200,201,202,203,204,205,206,207,208,226):
            return True
        else:
            raise Exception("Unable to put json to url: {} Got HTTP code {}".format(url, r.status_code))

    def get_object(self, table=None, name=None):
        """
        Get an object and return json
        :keyword table: Type to get. global, object, or role (Mandatory)
        :type         : string
        :keyword name: Name of object. (Mandatory)
        :type        : string
        :return: json
        :rtype: string
        """

        if table is None and name is None:
            raise Exception("Keyword table and name required")

        url = "%s/%s/%s" % ( self.base_url, table, name )

        r = requests.get(url, headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))

        try:
            json_data = json.loads(r.content)
        except:
            raise Exception("Unable to load json data from %s/%s" % ( table, name ))

        json_data.pop('_id',None)
        json_data.pop('_etag',None)

        return json_data

    def list_object(self, table=None):
        """
        List all objects in an table

        :keyword table: Type to get. global, object, or role (Mandatory)
        :type         : string

        :return: json
        :rtype: string
        """

        if table is None:
            raise Exception("Keyword table required")

        payload = { 'keys': "{\"_id\":1}", 'pagesize': '1000' }

        url = "%s/%s" % ( self.base_url, table )

        json_data = {}
        try:
            json_data['_embedded'] = self.get_json_pages(url)
        except Exception, e:
            print(e)
            raise Exception("Unable to load json data from table %s" % ( table ))

        item_list = json_data['_embedded']

        return self.filter_indexes(item_list)

    def filter_indexes(self, item_list):
        '''
        Remove .index and .rev items from a list

        :keyword item_list  : Item list to redact
        :type               : list

        :return:    filtered_list
        :rtype:     list
        '''
        filtered_list = []

        # Filter out .index and .number records
        index_finder = re.compile('.*\.index$')
        number_finder = re.compile('.*\d+$')
        for i in item_list:
            if type(i['_id']) == unicode:
                if len(index_finder.findall(i['_id'])) == 0 and  len(number_finder.findall(i['_id'])) == 0:
                    filtered_list.append(i)

        return filtered_list

    def get_json_pages(self, url):
        """
        Get all paginated results for a collection

        :keyword url    : Url to get all objects from
        :type           : string

        :return: objects
        :rtype: list
        """
        objects = []
        r = requests.get('{}?count&pagesize=1000'.format(url), auth=(self.username, self.password))
        data = json.loads(r.content)
        # Append first 1000
        for doc in data['_embedded']:
            objects.append(doc)

        total_pages = data['_total_pages']
        if total_pages > 1:
            for page in range(2, data['_total_pages']+1):
                r = requests.get('{}?count&pagesize=1000&page={}'.format(url, page), auth=(self.username, self.password))
                data = json.loads(r.content)
                for doc in data['_embedded']:
                    objects.append(doc)
        return objects

    def list_object_role(self, role=None):
        """
        List all objects associated with a specific role

        :keyword role: role (Mandatory)
        :type        : string

        :return: json
        :rtype: string
        """
        if role is None:
            raise Exception("Keyword role required")

        payload = {'filter': "{\"pillar_data.roles\":\"%s\"}" % role, 'keys': "{\"_id\":1}" , 'pagesize': '1000' }

        url = "%s/object" %  self.base_url

        r = requests.get(url, headers=self.headers, params=payload, auth=HTTPBasicAuth(self.username, self.password))

        try:
            json_data = json.loads(r.content)
        except:
            raise Exception("Unable to load json data from object table with role" % role)

        json_data.pop('_id',None)
        json_data.pop('_etag',None)
        json_data.pop('_returned',None)

        return self.filter_indexes(json_data['_embedded'])

    def dump_yaml(self, raw_data=None):
        """
        return a yaml string given a dict

        :keyword raw_data: the raw data to dump (mandatory)
        :type:           : dictonary

        :return: yaml of given dict
        :rtype: string
        """
        self.yaml.dump(raw_data, self.stream)
        serialized_data = self.stream.getvalue()
        self.stream.truncate()
        return serialized_data

    def dump_list(self, raw_data=None):
        """
        return a raw list of items given a dict

        :keyword raw_data: the raw data to dump (mandatory)
        :type:           : dictonary

        :return: yaml of given dict
        :rtype: string
        """

        x = ""

        for i in raw_data:
            x += str(i['_id']) + "\n"

        return x

    def put_object(self, table=None, name=None, data=None):
        """
        Put an object and return True if succesful. Raise with HTTP Status if error
        https://docs.python.org/3/library/http.html
        :keyword table: Type to put. global, object, or role (Mandatory)
        :type         : string

        :keyword name: Name of object. (Mandatory)
        :type        : string

        :keyword data: Data to put
        :type        : dict

        :return: True if succesful
        :rtype: boolean
        """

        if table is None or name is None or data is None:
            raise Exception("Keyword table, name, and data required")

        url = "%s/%s/%s" % ( self.base_url, table, name )
        epoch_time = str(datetime.datetime.utcnow().strftime("%s"))
        user = getpass.getuser()

        # Does index exist?
        index = None
        try:
            index = self.get_json(url+".index")
        except:
            print("Index does not exist, creating {}".format(url+".index"))
        if index == None:
            # If no index, create index
            r = {
            "_id": name+".index",
            "latest": epoch_time,
            "revisions": {
                epoch_time: {
                    "author": user,
                },
            },
            "checked_out": False,
            }
            self.put_json(url=url+".index", data=r)
        # If index, update index
        else:
            index['latest'] = epoch_time
            index['revisions'][epoch_time] = {"author": user}
            self.put_json(url=url+".index", data=index)
        # Add document
        try:
            # Put the versioned object
            self.put_json(url=''.join([url, ".", epoch_time]), data=data)
            # Put the unversioned object
            self.put_json(url=url, data=data)
        except Exception, e:
            print(e)
            raise Exception("Unable to PUT document {}".format(''.join([url, ".", epoch_time])))
        return True

    def convert_yaml(self, yaml_data):
        """
        Return a dict based on a given yaml string

        :keyword yaml_data: String of Yaml data
        :type             : string

        :return: Converted YAML to dict
        :rtype: dict
        """

        try:
            return self.yaml.load(yaml_data)
        except:
            raise Exception("Unable to convert YAML")


    def editor(self, raw_data=None, suffix=".yaml"):
        """
        Runs an external editor

        :keyword raw_data: Data to edit (Mandatory)
        :type            : string

        :keyword suffix: Suffix of the file, usefull for editors
        :type          : string

        :return: Edited string
        :rtype: string
        """
        EDITOR = os.environ.get('EDITOR','vim')

        with tempfile.NamedTemporaryFile(suffix=".yaml") as tf:
            tf.write(raw_data)
            tf.flush()
            call([EDITOR,tf.name])

            tf.seek(0)
            edited_message = tf.read()

        return edited_message

    def copy_object(self, source_object=None, dest_object=None, table=None):
        """
        Copy one object to a new name

        :keyword source_object: Name of the source object (Mandatory)
        :type:                : string

        :keyword dest_object: Name of the destination object
        :type:              : string

        :return: True if succesful
        :rtype: boolean
        """
        # Does the source exist?
    	if self.checker(table=table,name=source_object) is True:
    	   source_data = self.get_object(table=table, name=source_object)
    	else:
            raise Exception("Unable to retrieve the source object. Does {} exist?".format(source_object))
    	    return False
        # Does the destination exist?
        if self.checker(table=table,name=dest_object) is False:
           try:
               ret = self.put_object(table=table, name=dest_object, data=source_data)
               return ret
           except RuntimeError as e:
               print "Unable to write copy, %s" % e.message
               return False

    def convert_error(self, raw_data=None):
        """
        Dumps the original YAML when something goes wrong

        NOTE: This should most likely be re-written as a standalone class

        :keyword raw_yaml: The bad raw_yaml (Mandtory)
        :type            : string

        :return: Pretty message to dump
        :rtype: string
        """

        error_msg = "\nSomething wrong w/the format. Check your syntax"
        error_msg +=  "\n---------------------------------\n"
        error_msg += raw_data
        error_msg +=  "\n---------------------------------"
        return error_msg

    def checker(self,table=None,name=None):
        '''
        checker
        NOTE : double check if the role exists

        :keyword table  : role, object, or config
        :type           : string

        :keyword name   : name of role, object, or config
        :type           : string

        :return: True (if exists), False (else)
        :rtype : boolean
        '''
        url = "%s/%s/%s" %(self.base_url,table,name)
        r = requests.get(url, headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))
        #print r.status_code
        if r.status_code == 200:
            return True
        else:
            return False

    def delete_odie_record(self, delete_data=False, table=None, name=None):
        """
        Delete role or object entry from odie

        :keyword table: role or object (mandatory)
        :type         : string

        :keyword name: object or something (mandatory)
        :type        : string

        :return: True if succeed
        :rtype: boolean
        """
        if table is None and name is None:
            raise Exception("Keyword table and name required")

       	url = "%s/%s/%s" % (self.base_url, table, name)

        answer = False
        if delete_data == True:
            answer = True
        elif delete_data == False:
            answer = questions("Please confirm removal of item: {}/{} (y/n)".format(table, name))

        if answer is True:
            try:
                # Get all revisions
                index = self.get_json(url + ".index")
                # Delete each revision document
                for i in index['revisions'].keys():
                    r = requests.delete(url + "." + i, headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))
                # Delete index
                r = requests.delete(url + ".index", headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))
                # Delete object
                r = requests.delete(url, headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))
                return True
            except Exception, e:
                print(e)
                print("unable to delete record: %s") % url
        else:
            print('Deletion aborted. Exiting.')

    def get_revisions(self, table, name):
        """
        Get a revisions dictionary from the index

        :keyword table: role or object (mandatory)
        :type         : string

        :keyword name: object or something (mandatory)
        :type        : string

        :return: Revision dict
        :rtype: dict
        """
        url = '/'.join([self.base_url, table, name])
        index_url = url + ".index"
        index = self.get_json(index_url)
        return index['revisions']

    def restore_revision(self, table, name, revision_id):
        """
        Restore previous version of odie document

        :keyword table: role or object (mandatory)
        :type         : string

        :keyword name: object or something (mandatory)
        :type        : string

        :keyword revision_id: The revision id
        :type          : string

        :return: True if succeed
        :rtype: boolean
        """
        url = '/'.join([self.base_url, table, name])
        index_url = url + ".index"
        index = self.get_json(index_url)

        rev_string = str(revision_id)
        if revision_id in index['revisions']:
            # Set that revision as latest
            try:
                index['latest'] = rev_string
                self.put_json(url=index_url, data=index)
            except:
                raise Exception('Unable to set the "latest" key in the index')
            # Load revision
            try:
                document = self.get_json(url=url + "." + rev_string)
                # Set the _id field to be correct in the key
                document['_id'] = name
                # Overwrite object
                self.put_json(url=url, data=document)
            except:
                raise Exception("Unable to overwrite current document. Data may be in an inconsistent state.")
        else:
            raise Exception("Revision id not found in history")
        return True
