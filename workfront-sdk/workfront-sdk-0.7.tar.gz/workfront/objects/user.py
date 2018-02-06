from workfront.objects.fields import user as user_fields
from workfront.objects.codes import WFObjCode
from workfront.objects.generic_objects import WFObject


def from_id(wf, idd):
    '''
    @summary: Construct a WFUser object from a valid workfront user id.
    @param wf: A Workfront service object
    @param idd: workfront id of the existing user
    '''
    r = wf.search_objects(WFObjCode.user, {"ID": idd}, user_fields)
    js = r.json()["data"][0]
    u = WFUser(wf, js)
    return u


def from_email(wf, email):
    '''
    @summary: Construct a WFUser object from a workfront user that has the
    given email.
    @param wf: A Workfront service object
    @param email: email of an existing workfront user
    '''
    r = wf.search_objects(WFObjCode.user, {"emailAddr": email}, user_fields)
    js = r.json()["data"][0]
    u = WFUser(wf, js)
    return u


class WFUser(WFObject):
    '''
    @summary: a Workfront user helper class
    '''

    def __init__(self, wf, js=None):
        '''
        @param wf: A Workfront service object
        @param js: a  json object representing a workfront user.
        '''
        super(WFUser, self).__init__(wf, WFObjCode.user, None)
        self.wf = wf
        self.name = None
        self.emailAddr = None
        if js is not None:
            self._init_from_js(js)

    def _init_from_js(self, js):
        self.wf_id = js["ID"]
        self.name = js["name"]
        self.emailAddr = js["emailAddr"]
