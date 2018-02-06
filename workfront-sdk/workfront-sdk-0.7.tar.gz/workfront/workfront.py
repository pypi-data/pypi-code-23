from __future__ import absolute_import
from requests import session
from workfront.exceptions import WFException
import datetime as dt


class WFEventType:
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    SHARE = "SHARE"


class Workfront(object):
    '''
    @summary: A workfront service object that is used to interact with the
    Workfront API.
    '''
    url_base = "https://thebridgecorp.my.workfront.com/attask/api/v7.0/"

    def __init__(self, user, passw):
        '''
        @param user: user used to login into WF (probably email)
        @param passw: password for the given user
        '''
        self.sess = session()
        self.user = user
        self.passw = passw
        self._wf_last_connect = dt.datetime.now() - dt.timedelta(weeks=65)
        self.sess_id = None

    @property
    def sess_id(self):
        # Force the service to reconnect after 25 minutes to avoid expired
        # sessions
        tdiff = dt.datetime.now() - self._wf_last_connect
        if tdiff > dt.timedelta(minutes=25) or self._sess_id is None:
            self.login()
        return self._sess_id

    @sess_id.setter
    def sess_id(self, value):
        self._sess_id = value

    def login(self):
        '''
        @summary: login against the WF API and save the session id for future
        requests
        '''
        url = self.url_base + "login?username=%s&password=%s"
        r = self.sess.post(url % (self.user, self.passw))
        if r.status_code is not 200:
            e = "Could not log in to Workfront: {}".format(r.json())
            raise WFException(e)
        self.sess_id = r.json()["data"]["sessionID"]
        self._wf_last_connect = dt.datetime.now()

    def logout(self):
        '''
        @summary: logout, invalidating the current session id
        '''
        u = self.url_base + "logout"
        self.sess.get(u)
        self.sess_id = None

    def _post(self, url, js):
        '''
        @param url: url part of the object being posted (not the url base)
        @param js: json body to be send
        '''
        u = self.url_base + url
        hs = {"SessionID": self.sess_id}
        r = self.sess.post(u, json=js, headers=hs)
        return r

    def _put(self, url, **kwargs):
        '''
        @param url: url part of the object being put (not the url base)
        '''
        u = self.url_base + url
        hs = {"SessionID": self.sess_id}
        r = self.sess.put(u, headers=hs, **kwargs)
        return r

    def _get(self, url):
        '''
        @param url: url part of the object being get (not the url base)
        '''
        u = self.url_base + url
        hs = {"SessionID": self.sess_id}
        r = self.sess.get(u, headers=hs)
        return r

    def _delete(self, url):
        '''
        @param url: url part of the object being put (not the url base)
        '''
        u = self.url_base + url
        hs = {"SessionID": self.sess_id}
        r = self.sess.delete(u, headers=hs)
        return r

    def search_objects(self, obj, param_dict, fields=[]):
        '''
        @summary: Do a search of the objects restricted by the fields given in
        the param_dict
        @param obj: object code being searched
        @param param_dict: dictionary of query strings (key = value)
        @param fields: fields being retrieved for the object
        '''
        url = "%s/search" % obj
        if len(param_dict) > 0:
            qs = ["{}={}".format(k, v) for k, v in param_dict.items()]
            if len(fields) > 0:
                qs.append("fields={}".format(",".join(fields)))
            qs = "&".join(qs)
            url = url + "?" + qs
        return self._get(url)

    def get_object(self, obj, idd, fields=[]):
        '''
        @param obj: object code being retrieved
        @param idd: WF id of the object
        @param fields: list of fields being retrieved for the given object. If
        not given, the fields retrieved will be the custom one.
        '''
        url = "%s/%s" % (obj, idd)
        if len(fields):
            url = url + "?fields=%s" % ",".join(fields)
        return self._get(url)

    def put_object(self, obj, idd, param_dict={}):
        '''
        @summary: Do a put object
        @param obj: obj code
        @param idd: WF id of the object being put
        @param param_dict: dictionary of query strings (key = value)
        '''
        url = "%s/%s" % (obj, idd)
        qs = ["{}={}".format(k, v) for k, v in param_dict.items()]
        qs = "&".join(qs)
        url = url + "?" + qs
        return self._put(url)

    def post_object(self, obj, param_dict={}):
        '''
        @summary: Do a post object
        @param obj: obj code
        @param param_dict: dictionary of query strings (key = value)
        '''
        return self._post(obj, param_dict).json()["data"]

    def action(self, obj, idd, action, param_dict):
        '''
        @summary: Perform an action for the object given.
        @param obj: obj code
        @param idd: WF id of the object being put
        @param action: action being done for the given object
        @param param_dict: dictionary of query strings (key = value)
        '''
        param_dict["action"] = action
        return self.put_object(obj, idd, param_dict)

    def get_api_key(self):
        '''
        @summary: Get a Workfront API key.
        '''
        u = self.url_base + "USER?action=getApiKey&username=%s&password=%s"
        u = u % (self.user, self.passw)
        hs = {"SessionID": self.sess_id}
        return self.sess.put(u, hs).json()["data"]["result"]

    def gen_api_key(self):
        '''
        @summary: Generate a Workfront API key.
        '''
        u = self.url_base + "USER/generateApiKey?username=%s&password=%s"
        u = u % (self.user, self.passw)
        hs = {"SessionID": self.sess_id}
        return self.sess.put(u, hs).json()["data"]["result"]
