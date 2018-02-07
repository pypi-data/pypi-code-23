from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
from abs import AbstractApi
from util import fetch_post
from util import get_filename


class File(AbstractApi):
    auth = None
    domain = None
    cookie = None

    def __init__(self, auth):
        self.auth = auth
        self.domain = auth.domain
        self.cookie = auth.cookie

    def delete(self, filename):
        headers = self.get_headers()
        url = 'http://%s/fs/hdfs/delete.json' % self.domain

        data = json.dumps({
            'currentPath': '/',
            'deleteList': [{
                'fullyQualifiedPath': filename,
                'directory': False
            }]
        })

        r = fetch_post(url, data=data, headers=headers)

        return json.loads(r.content)['success']

    def permission(self, filename, group="hdfs", owner="hdfs", permission="644"):
        headers = self.get_headers()
        url = 'http://%s/fs/hdfs/setPermission' % self.domain

        data = json.dumps({
            'currentPath': filename,
            'fileNames': get_filename(filename),
            'fileStatus': 'FILE',
            'files': filename,
            'group': group,
            'owner': owner,
            'permission': permission,
            'recursiveOwner': 0,
            'recursivePermission': 0
        })

        r = fetch_post(url, data=data, headers=headers)

        return json.loads(r.content)['success']

    def upload_file(self, filename, dest_filename, overwrite=False):
        if overwrite:
            self.delete(dest_filename)

        headers = self.get_headers()
        url = 'http://%s/fs/hdfs/upload.json' % self.domain

        dstPath = '/'.join(dest_filename.split('/')[0:-1])
        fileName = get_filename(dest_filename)

        form_data = MultipartEncoder(fields={
            'dstPath': dstPath,
            'fileName': (fileName, open(filename, 'rb'))
        })

        headers['Content-Type'] = form_data.content_type

        r = fetch_post(url, data=form_data, headers=headers)

        return json.loads(r.content)['success']
