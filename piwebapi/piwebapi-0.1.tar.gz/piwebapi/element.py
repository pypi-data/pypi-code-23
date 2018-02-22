from .piobject import PIObject
from .attribute import Attribute
from .config import webapi_server

class Element(PIObject):

    def __init__(self, path=False, webid=False, persistence=None):

        if webid:
            response = self.request("elements/"+webid, {}, persistence)

        elif not isinstance(path, dict):
            if "https" not in path:
                response = self.request("elements", {"path": path}, persistence)
            else:
                response = self.request(path, {}, persistence)
        else:
            response = path

        self.persistence = persistence
        # assign information
        self.web_id = response["WebId"]
        self.name = response["Name"]
        self.has_children = response["HasChildren"]
        self.links = response["Links"]
        self._attributes = None
        self._children = None

    def __getitem__(self, key):
        return self.children[key]

    def add_child(self, name, description=None, template=None):
        url = webapi_server + 'elements/' + self.web_id + '/elements'
        payload = {
                'Name': name,
                'Description': description,
                'TemplateName': template
                }
        self._children = None
        response = self.post(url, payload)
        try:
            return Element(path=response.headers['location'])
        except:
            raise ValueError(response.text)

    def add_attribute(self, name, description=None, attribute_type=None, **kwargs):
        url = webapi_server + 'elements/' + self.web_id + '/attributes'

        payload = {
                "Name": name,
                "Description": description,
                "Type": attribute_type,
                }
        for key in kwargs:
            payload[key.title().replace("_", "")] = kwargs[key]

        self._attributes = None
        response = self.post(url, payload)
        try:
            return Attribute(path=response.headers['location'])
        except:
            raise ValueError(response.text)



    def _delete(self):
        url = webapi_server + 'elements/' + self.web_id
        self.req_delete(url).text
        del self

    def delete_child(self, childname):
        self.children[childname]._delete()
        del self._children[childname]

    def rename(self, to_name):
        payload = {
            "Name": to_name
        }
        url = webapi_server + 'elements/' + self.web_id
        self.patch(url, payload)
        self.name = to_name

    @property
    def children(self):
        if not self._children:
            request = self.request(self.links["Elements"], {}, persistence=self.persistence)

            self._children = {}

            for item in request["Items"]:
                self._children[item["Name"]] = Element(item)

        return self._children

    @property
    def attributes(self):
        if not self._attributes:
            request = self.request(self.links["Attributes"])

            self._attributes = {}

            for item in request["Items"]:
                self._attributes[item["Name"]] = Attribute(item, persistence=self.persistence)

        return self._attributes

    @property
    def parent(self):
        return Element(self.links["Parent"], persistence=self.persistence)
