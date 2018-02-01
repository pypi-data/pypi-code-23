# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# Simulagora-client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

"""
Simulagora-client: HTTP client for Simulagora Web Services.

The main class of this module is `Simulagora` which is the Simulagora client.

"""

import os
import os.path as osp
import errno
import logging
import json
import hashlib
from base64 import b64encode, b64decode
from urlparse import urlparse

import requests

from cwclientlib import (
    cwproxy,
    cwproxy_for,
    builders,
)


def _compute_md5_as_b64(path):
    """Compute the md5 of the file at `path` and return it b64 encoded.
    """
    md5 = hashlib.md5()
    chunksize = 128 * md5.block_size  # pylint: disable=no-member
    with open(path, 'rb') as fdesc:
        for chunk in iter(lambda: fdesc.read(chunksize), ''):
            md5.update(chunk)
    return b64encode(md5.digest())


def _s3_upload_file(fpath, dest_url, form):
    """Upload a file on S3.

    fpath: str
       filepath
    dest_url: str
       Amazon S3 url (e.g. https://s3.amazonaws.com/uploads/EID/)
    form: dict
       Form including authorizations to post (from Simulagora)
    """
    form['Content-MD5'] = _compute_md5_as_b64(fpath)
    parsed_url = urlparse(dest_url)
    fname = osp.basename(fpath)
    form['key'] = parsed_url.path[1:] + '/' + fname + '.0'
    s3_url = '%s://%s' % (parsed_url.scheme, parsed_url.netloc)
    with open(fpath) as fdesc:
        return requests.post(
            s3_url, data=form, files={'file': ('file', fdesc)})


def _get_s3_base_url(post_form):
    """Return the S3 base_url an upload must be posted to, from the
    authorization form Simulagora delivers for this purpose.
    """
    policy = json.loads(b64decode(post_form['policy']))
    key = 'success_action_redirect'
    for cond in policy['conditions']:
        if isinstance(cond, dict):
            value = cond.get(key)
            if value is not None:
                url = urlparse(value)
                return '://'.join([url.scheme, url.netloc])
    raise ValueError("Policy does not have the key 'success_action_redirect'")


def _todicts(data, *keys):
    """Return the `data` list of list as a list of dict, each value of the inner
    list being the value of the key in `keys` which as the same index.
    """
    return [dict(zip(keys, row)) for row in data]


class Simulagora(cwproxy.CWProxy):
    """Client for the Simulagora web services.
    """
    _store_keyring_cache = None

    @classmethod
    def for_instance(cls, instance, **kwargs):
        """Instantiate a Simulagora client for `instance`.

        `instance` should match the name of a section in cwclientlib's
        configuration file.
        """
        return cwproxy_for(instance, proxycls=cls, **kwargs)

    def studies(self):
        """Get the list of readable studies.
        """
        rql = 'Any SEID, N WHERE X is Study, X eid SEID, X name N'
        response = self.rql(rql)
        response.raise_for_status()
        return _todicts(response.json(), 'eid', 'name')

    def runs(self, study=None):
        """Display the list of runs.

        Show run eids, name of the executable and the state.
        """
        rql = ('Any R, EXN, RST, PARAMS'
               ' WHERE R is Run, R in_state S, S name RST,'
               ' R executable X, X name EXN, R parameters_json PARAMS')
        if study is not None:
            rql += ', R in_study ST, ST eid %d' % study
        runs = _todicts(self.rql(rql).json(),
                        'eid', 'executable_name', 'state', 'parameters')
        # Expand "parameters" (a JSON String) as a dict.
        for run in runs:
            params = run['parameters']
            if params is not None:
                run['parameters'] = json.loads(params)
        return runs

    def executables(self):
        """Return the list of available executables.
        """
        query = 'Any X,N WHERE X is Executable, X name N'
        return _todicts(self.rql(query).json(), 'eid', 'name')

    def server_types(self):
        """Return the list of available virtual machines which can be launched.
        """
        rql = ('Any X, N, CPU, RAM, CPNAME '
               'WHERE X is CloudServerType, X name N, X cpu_core_nb CPU, '
               'X ram RAM, X provided_by Y, Y name CPNAME')
        return _todicts(self.rql(rql).json(),
                        'eid', 'name', 'cpu', 'ram', 'cloud provider')

    def images(self):
        """Return the list of available machine images.
        """
        query = 'Any X, T WHERE X is CloudServerImage, X title T'
        return _todicts(self.rql(query).json(), 'eid', 'title')

    @property
    def last_image(self):
        """Return the more recent machine image.
        """
        query = ('Any X, T ORDERBY X DESC LIMIT 1'
                 ' WHERE X is CloudServerImage, X title T')
        return _todicts(self.rql(query).json(), 'eid', 'title')[0]

    def files_in_folder(self, folder):
        """Return a list of dicts describing the files under the folder which
        eid is ``folder``.
        The keys of the dict are: eid, md5_hash, mimetype, name, size, uri.
        """
        query = ('Any X,U,S,H,T WHERE X is DistantFile, X uri U, X size S, '
                 'X md5_hash H, X mimetype T, X filed_under F, F eid %d')
        descrs = _todicts(self.rql(query % folder).json(),
                          'eid', 'uri', 'size', 'md5_hash', 'mimetype')
        for descr in descrs:
            descr['name'] = descr['uri'].rsplit('/')[-1]
        return descrs

    def state(self, eid):
        """Return the current state of a specific Entity. Mostly useful to get
        the state of a run.
        """
        rql = 'Any ST WHERE X eid %d, X in_state S, S name ST' % eid
        return self.rql(rql).json()[0][0]

    # Entity creation (folders, studies, runs) and manipulation

    def _create_single_entity(self, etype, **kwargs):
        """Create an entity of type `etype` and attribute/ relation values
        `kwargs`. Returns its unique identifier (eid).
        """
        query = builders.create_entity(etype, **kwargs)
        resp = self.rqlio([query])
        resp.raise_for_status()
        return resp.json()[-1][0][0]

    def create_folder(self, name):
        """Create a folder which name is the one passed as an argument.
        Return its unique identifier (an integer).
        """
        return self._create_single_entity('Folder', name=name)

    def create_study(self, name):
        """Create a study which name is the one passed as an argument.
        Return its unique identifier (an integer).
        """
        return self._create_single_entity('Study', name=name)

    def create_run(self, in_study, executable, server_type,
                   input_files=None, parameters=None, image=None):
        """Create a run and return its unique identifier (an integer).

        All entities arguments should be pass by there eid (e.g. in_study,
        executable, server_type, image).
        ``input_files`` should be a list of eids.
        ``parameters`` should be a dictionnary (like {'p2': 12, 'p1': 0.3}).
        """
        if parameters is None:
            parameters = {}
        if image is None:
            image = self.last_image['eid']
        queries = []
        # create run
        rql = ('INSERT Run R:'
               ' R in_study S, R executable E, R store_keyring K,'
               ' R run_on M, R use_image I, R parameters_json %(params)s '
               'WHERE S eid %(s)s, E eid %(e)s, M eid %(m)s, I eid %(i)s,'
               ' K eid %(k)s')
        args = {'k': self._store_keyring,
                's': in_study,
                'e': executable,
                'm': server_type,
                'i': image,
                'params': json.dumps(parameters).decode('utf-8'),
                }
        queries.append((rql, args))
        # attaching files
        if input_files:
            rql = ('SET R input_file F WHERE R eid %%(r)s, F eid IN (%s)'
                   % ', '.join([str(ifile) for ifile in input_files]))
            queries.append((rql, {'r': '__r0'}))
        return self.rqlio(queries).json()[0][0][0]

    def start_run(self, run):
        """Start the given Run. Return the unique identifier of the transition
        between the previous and the new state of the run.
        """
        query = [builders.build_trinfo(run, 'wft_run_queue')]
        resp = self.rqlio(query)
        resp.raise_for_status()
        # Eid of the transition.
        eid = resp.json()[-1][0][0]
        return eid

    # Input/ output data file related methods

    def download_results(self, run, dest_path='.'):
        """Download all result files of `run` into `dest_path` (which defaults
        to the current working directory).

        Use log level INFO (at least) to know what file is being downloaded.
        """
        urls = self._ajax_controller('results_url', run).json()
        for url in urls:
            tmp_path = urlparse(url)
            local_filename = '/'.join(tmp_path.path.split('/')[5:])
            try:
                os.makedirs(osp.join(dest_path, osp.dirname(local_filename)))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
            logging.info("downloading %s", local_filename)
            req = requests.get(url, stream=True)
            with open(local_filename, 'wb') as fdesc:
                for chunk in req.iter_content(chunk_size=4096):
                    if chunk:  # filter out keep-alive new chunks
                        fdesc.write(chunk)
                        fdesc.flush()

    def upload_files(self, folder, *filepaths):
        """Given the destination `folder` by eid, upload the files which paths
        are passed afterwards into this folder.

        folder: int (None by default)
           The eid of the destination Simulagora Folder.
        filepaths: str or list
           The paths of the files to be uploaded
        """
        # 0. Create an Upload instance
        upload_name = '_'.join([osp.basename(filepaths[0]), 'upload'])
        upload_eid = self._create_upload(upload_name, folder)
        logging.debug("uploading files: upload eid is %s", upload_eid)
        # 1. Get the form to have the permission to POST to S3
        post_form = self._ajax_controller('upload_form', upload_eid).json()
        logging.debug("uploading files: received upload form %s", post_form)
        base_s3_url = _get_s3_base_url(post_form)
        dest_url = base_s3_url + '/uploads/%s' % upload_eid
        # 2. Upload the file to S3
        description = []
        for fpath in filepaths:
            fpath = osp.expanduser(fpath)
            _s3_upload_file(fpath, dest_url, post_form)
            filesize = osp.getsize(fpath)
            description.append({'name': osp.basename(fpath),
                                'total': filesize,
                                'chunks': 1})
        # 3. Post the upload description to Simulagora
        self._ajax_controller('upload_description', upload_eid,
                              description).raise_for_status()
        logging.debug("uploading files: description posted: %s", description)
        # 4. Make the finished upload Simulagora dedicated controller call
        response = self._ajax_controller('upload_successful_files',
                                         upload_eid)
        response.raise_for_status()
        file_eids = response.json()
        logging.debug("uploading files: upload eid %s successful (%d files)",
                      upload_eid, len(file_eids))
        return file_eids

    # Lower level read-only helpers

    def find(self, etype, **kwargs):
        """This low level request aims at getting the list of unique
        identifiers (integers) of Simulagora entities of type `type` which also
        match the conditions on their attributes described by `kwargs`, of the
        form "attribute_name=attribute_value".
        """
        # XXX to be moved to cwclientlib
        rql = ['Any X WHERE X is %s' % etype]
        args = {}
        for key, value in kwargs.items():
            if isinstance(value, dict) and 'eid' in value:
                value = value['eid']
            args[key] = value
            rql.append('X %s %%(%s)s' % (key, key))
        rql = ','.join(rql)
        result = self.rqlio([(rql, args)]).json()
        return result[0]

    def find_one(self, etype, **kwargs):
        """This low level request aims at getting the unique identifier
        (an integers) of a single Simulagora entity of type `type` supposed to
        match the conditions on its attributes described by `kwargs` (of the
        form "attribute_name=attribute_value").

        An AssertionError is raised if the number of entities found is not
        exactly 1.
        """
        # XXX to be moved to cwclientlib
        data = self.find(etype, **kwargs)
        assert len(data) != 0, 'no such entity found in the database'
        assert len(data) == 1, ('more than one entity matches your request '
                                '(%d found)' % len(data))
        return data[0][0]

    # Internal helpers: do not use, they can disappear or change!

    @property
    def _store_keyring(self):
        """Cached helper that returns the CloudStoreKeyring first instance.
        """
        if self._store_keyring_cache is None:
            self._store_keyring_cache = self.rql(
                'Any X WHERE X is CloudStoreKeyring').json()[0][0]
        return self._store_keyring_cache

    def _create_upload(self, name, folder):
        """Create an Upload entity with name `name` which files will be filed
        under folder `folder`. Return the eid of the new Upload entity.
        """
        queries = [('INSERT Upload U: U name %(name)s, U upload_folder F,'
                    ' U keyring K WHERE K eid %(k)s, F eid %(f)s',
                    {'name': name, 'k': self._store_keyring, 'f': folder})]
        rset = self.rqlio(queries).json()[0]
        if not rset:
            raise ValueError(
                'Upload creation failed. Are you sure folder id %r'
                ' really exists ?' % folder)
        return rset[0][0]

    def _ajax_controller(self, fname, *args):
        """Helper to call an ajax function named `fname` with arguments `args`.
        """
        params = {'url': self.build_url('/ajax'),
                  'headers': cwproxy.build_request_headers(),
                  'verify': self._ssl_verify,
                  'auth': self.auth,
                  'data': {'fname': fname,
                           'arg': [json.dumps(x) for x in args]}}
        return requests.post(**params)  # pylint: disable=star-args
