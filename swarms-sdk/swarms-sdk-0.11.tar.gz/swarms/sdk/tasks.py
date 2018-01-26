import requests
from .utils.hal import get_link
from . import CrudService
import os.path
import magic

class Tasks(CrudService, object):
    path = "tasks"

    def __upload_from_url(self, url):
        file_name = url.split('/')[-1]

        if os.path.isfile(url):
            f = open(url, 'rb')
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(url)

        else:
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception("Could not retrieve file: %s" % url)

            mimetype = response.headers['Content-Type']

            f = response.content

        return self.client.post_file("/upload", file_name, f, mimetype)

    def __upload_files(self, objects):
        for o in objects:
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "url":
                        o[k] = self.__upload_from_url(v)
                    elif isinstance(v, list):
                        self.__upload_files(v)
                    else:
                        self.__upload_files([v])

    def create(self, resource):
        self.__upload_files(resource["components"])

        return super(Tasks, self).create(resource)

    # copy a task
    def copy(self, task):
        return self.client.post(get_link(task, "copy"))
