from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError
from tornado.escape import url_escape
from hashlib import md5
from datetime import datetime
from os.path import expanduser
try:
    import json
    from json.decoder import JSONDecodeError
except ImportError:
    import simplejson as json
    from simplejson import JSONDecodeError

from swdl.matches import Match
from swdl.labels import Label
import numpy as np
from getpass import getpass
import os
from builtins import input
from subprocess import call


def to_md5(password):
    """
    Hashes a password to md5

    # Arguments
    password(str): The password to be hashed

    # Returns
    str: Password MD5-hash
    """
    return md5(password.encode()).hexdigest()

def save_password():
    """
    Asks for username and password and stores the credentials in ~/.swdlrc
    """
    username = input("Username: ")
    password = to_md5(getpass("Password: "))
    user_file = expanduser("~/.swdlrc")
    user_config = {}
    if os.path.exists(user_file):
        user_config = json.loads(open(user_file).read())
    user_config.update({"username":username,"password":password})
    call("chmod 600 {}".format(user_file).split())
    open(user_file,"w").write(json.dumps(user_config))


class DataService:
    """
    Helper service to download soccerwatch data

    # Attributes
    username (str): Name of the user to connect to the service
    password_hashed (str): MD5 hashed password required to login. Use #to_md5()
    """
    def __init__(self, username=None, password_hashed=None):
        if not username:
            user_file = expanduser("~/.swdlrc")
            if os.path.exists(user_file):
                user_config = json.loads(open(user_file).read())
                username = user_config["username"]
                password_hashed = user_config["password"]
        self.username=username
        self.password = password_hashed
        self.api_stream_url = "https://api-stream-interface-soccerwatch.azurewebsites.net/intern/rest/v1/streamInterface"
        self.user_escaped=None
        if username:
            self.user_escaped = url_escape(username)

        self.client = HTTPClient()

    def get(self, url):
        """
        Performs a get request on the given URL. See alse #DataService.post()

        # Arguments
        url (str): URL to perform get request

        # Retrurns
        str: Dictionary created from JSON dump of the response

        # Example
        ```python
        ds = DataService()
        ds.get("www.google.de")
        ```
        """
        request = HTTPRequest(url, "GET",connect_timeout=120,request_timeout=120)
        try:
            ret = self.client.fetch(request).body
            return json.loads(ret)
        except JSONDecodeError:
            print("could not parse result")
        except HTTPError as e:
            print("Failed to connect to {}".format(url))

    def post(self, url, **kwargs):
        """
        Performs a post request on the given URL

        # Arguments
        url (str): URL to perform get request
        kwargs: Parameters that will be dumped as JSON

        #Return
        dict: Dictionary created from JSON dump of the response
        """
        header = {"Content-Type": "application/json"}
        request = HTTPRequest(url, "POST", header, json.dumps(kwargs),connect_timeout=120,request_timeout=120)
        try:
            ret = self.client.fetch(request).body
            return json.loads(ret)
        except JSONDecodeError:
            print("could not parse result")
        except HTTPError as e:
            print("Failed to connect to {}".format(url))

    def get_matches(self):
        """
        Lists all matches

        # Returns
        list: All matches in type #Match`
        """
        url = "{}/match/all/{}/{}".format(self.api_stream_url, self.user_escaped,self.password)
        matches = self.get(url)
        if not matches:
            return []
        match_list =  [Match(**x).set_data_service(self) for x in self.get(url)]
        return match_list

    def get_match(self, match_id):
        """
        Returns a single #Match for a given match id

        # Arguments
        match_id (int,str): Match id

        #Returns
        Match: The requested match
        """
        url = "{}/match/single/{}/{}/{}".format(self.api_stream_url, match_id, self.user_escaped, self.password)
        response = self.get(url)
        if not response:
            return Match(match_id)
        ret = response[0]

        return Match(**ret).set_data_service(self)

    def get_events(self, match_id):
        """
        Returns all Events from azure

        # Arguments
        match_id (str,int): Matchid

        # Returns
        list: Events as got as dictionaries
        """
        url = "{}/tags/{}/{}/{}".format(self.api_stream_url, match_id, self.user_escaped, self.password)
        return self.get(url)

    def get_positions(self, match_id, time=None, virtual_camera_id="-1", source="human"):
        """
        Get the camera positions of a match

        # Arguments
        match_id (str,int): Match id
        time (datetime): Datetime to limit the data given back. Will only return data later than time
        virtual_camera_id (str): The camera id of the positions
        source (str): Should be human or machine

        # Returns
        list: Dictionaries of the positions

        # Example
        """
        if not time:
            last_modified = 0
        elif type(time) == int:
            last_modified = time
        elif type(time) == datetime:
            last_modified = int(time.strftime("%s")) * 1000
        else:
            raise TypeError

        virtual_camera_id = str(virtual_camera_id)
        source = str (source)

        url = "{}/positions/request/{}/{}/{}".format(self.api_stream_url, match_id, self.user_escaped, self.password)
        return self.post(url, virtualCameraId=virtual_camera_id, lastModified=last_modified, source=source)

    def pull_info(self, match):
        """
        Updates the information about a match

        # Arguments
        match (Match): A match

        # Returns
        Match: Updated match

        # Raises
        ValueError: If input is not a match
        """
        if not isinstance(match, Match):
            raise ValueError("Argument must be a valid match")
        return self.get_match(match.match_id)

    def push_labels(self, match, start_index=0, virtual_camera_id="-1", source="human"):
        """
        Uploads the positions greater than the given #start_index to the cloud service

        # Arguments
        match (str): The match
        start_index (int): only positions greater than start index will be pushed
        virtual_camera_id (str): Camera id the positions belongs to
        source (str): Should be "human" or "machine"
        """

        message_body= self._create_label_body(match.match_id, match.labels.positions, start_index, virtual_camera_id, source)
        url = "{}/positions/insert/{}/{}/{}".format(self.api_stream_url,
                                                    match.match_id,
                                                    self.user_escaped,
                                                    self.password)
        self.post(url,**message_body)

    @staticmethod
    def _create_label_body(match_id,  position_list, start_index=0, virtual_camera_id="-1" ,source="human"):

        #ToDo push events and status
        message_body =  dict()
        message_body["virtualCameraId"] = str(virtual_camera_id)
        message_body["matchId"] = str(match_id)
        message_body["source"] = str(source)
        message_body["positions"] = list()
        for i in range(start_index, len(position_list)):
            timestamp = int(position_list[i,0]/100.0)
            if timestamp==0:
                continue
            message_body["positions"].append(dict())
            message_body["positions"][-1]["timestamp"]= timestamp
            message_body["positions"][-1]["x"]= str(position_list[i,1])
            message_body["positions"][-1]["y"]= str(position_list[i,2])
            message_body["positions"][-1]["zoom"]= str(position_list[i,3])
            message_body["positions"][-1]["source"]= str(source)
        return message_body

    def pull_labels(self, match, time_from=None, virtual_camera_id="-1", source="human"):
        """
        Updates the labels of a match. May clear all locally created labels.

        # Arguments
        match (Match): A match
        time_from (datetime,int): Will only get labels later than this time, Must be msecs after 1970 or datetime
        virtual_camera_id (str): Camera Id
        source (str): "human" or "machine"

        #Returns
        Match: Updated match

        # Raises
        ValueError: If input is not a match
        """
        if not isinstance(match, Match):
            raise ValueError("Argument must be a valid match")

        if time_from == None:
            time_from = match.last_label_update

        match_id = match.match_id

        label = Label()
        # Get events
        label.events = np.zeros((0,3), dtype=np.float32)
        label.status = np.zeros((0,2), dtype=np.float32)
        events = self.get_events(match_id)
        for i, e in enumerate(events):
            e_mapped = self.map_events_from_azure(e)
            if len(e_mapped) == 2:
                label.status = np.append(label.status, [e_mapped], axis=0).astype(np.uint32)
            else:
                label.events = np.append(label.events, [e_mapped], axis=0).astype(np.uint32)
        # Get positions
        pos_unsorted = self.get_positions(match_id, time_from, virtual_camera_id, source)
        if not pos_unsorted and len(pos_unsorted) > 0:
            positions = sorted(pos_unsorted, key=lambda k: k['timestamp'])
            highest_timestamp = int(positions[-1]["timestamp"])
            if highest_timestamp + 1 > label.positions.shape[0]:
                label.positions.resize((highest_timestamp + 1 , 7))
            latest_date=datetime.fromtimestamp(0)
            for p in positions:
                timestamp = (p["timestamp"])
                x = float(p["x"])
                y = float(p["y"])
                zoom = float(p["zoom"])
                temp = [timestamp * 100, x, y, zoom, x, y, zoom]
                label.positions[timestamp] = temp
                date = datetime.fromtimestamp(float(p["lastModified"])/1000)
                if (date > latest_date):
                    latest_date=date
            match.last_label_update = latest_date
        match.labels = label
        return match

    @staticmethod
    def map_events_from_azure(event):
        """
        Maps a event dictionary to a list

        # Arguments
        event (dict): Event dictionary

        # Returns
        list: With either 2 or 3 entries
        """
        e = int(event["eventType"])
        timestamp = int(event["timestamp"])
        if e == 0:
            return [timestamp, 0, 0]
        if e == 1:
            return [timestamp, 0, 1]
        if e == 2:
            return [timestamp, 6, 0]
        if e == 3:
            return [timestamp, 6, 1]
        if e == 4:
            return [timestamp, 5, 0]
        if e == 5:
            return [timestamp, 5, 1]
        if e == 6:
            return [timestamp, 4, 0]
        if e == 7:
            return [timestamp, 4, 1]
        if e == 35:
            return [timestamp, 2, 0]
        if e == 36:
            return [timestamp, 2, 1]
        # For status
        if e == 12:
            return [timestamp * 1000, 1]
        if e == 13:
            return [timestamp * 1000, 2]
        if e == 14:
            return [timestamp * 1000, 3]
        if e == 15:
            return [timestamp * 1000, 4]
        return [timestamp, 7, 0]
