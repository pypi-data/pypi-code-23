"""project.py contains the project class that contains resources
in steno3d
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import properties

from .base import (CompositeResource, ProjectQuotaExceeded,
                   ProjectResourceLimitExceeded,
                   ProjectSizeLimitExceeded, UploadError, UserContent)
from .client import Comms, needs_login, plot


QUOTA_REACHED = """
Uploading this {priv} project will put you over your quota
of {num} {priv} project(s). For more projects and space, consider
upgrading your account: {base_url}settings/plan
"""

QUOTA_IMPENDING = """
After this project, you may upload {remaining} more {priv} project(s) before
reaching your {priv} project quota. For more projects and space
consider upgrading your account: {base_url}settings/plan
"""


class Project(UserContent):
    """Steno3D top-level project"""
    _model_api_location = 'project/steno3d'

    resources = properties.List(
        doc='Project Resources',
        prop=CompositeResource,
        coerce=True,
        default=list,
    )

    public = properties.Boolean(
        doc='Public visibility of project',
        default=False
    )

    _public_online = None

    @classmethod
    def _url_view_from_uid(cls, uid):
        """Get full url from a uid"""
        url = '{base}{mapi}/{uid}'.format(
            base=Comms.base_url,
            mapi='app',
            uid=uid)
        return url

    @needs_login
    def upload(self, **kwargs):
        """Upload the project"""
        verbose = kwargs.get('verbose', True)
        if getattr(self, '_upload_data', None) is None:
            assert self.validate()
            self._check_project_quota(verbose)
            self._public_online = self.public
        elif verbose and self._public_online:
            print('This project is PUBLIC. It is viewable by everyone.')
        if verbose and not self._public_online == self.public:
            print('Local privacy changes cannot be applied to '
                  'projects that are already uploaded. To make '
                  'these changes, please use the dashboard on '
                  '{base_url}'.format(base_url=Comms.base_url))
        if verbose:
            print('\rStarting upload: {}'.format(self.title), end='')
        UserContent._upload_size = 1
        UserContent._upload_total_size = self._nbytes() + 1
        UserContent._upload_count = 0
        UserContent._upload_total_count = len(self.resources) + 1
        self._upload(**kwargs)
        self._trigger_ACL_fix()
        if verbose:
            print('\nComplete!')
        if verbose and kwargs.get('print_url', True):
            print(self._url)
        return self._upload_data['uid']

    def _post(self, datadict=None, files=None):
        try:
            return super(Project, self)._post(datadict, files)
        except UploadError:
            if getattr(self, '_upload_data', None) is None:
                self._check_project_quota(False)
            raise

    def _trigger_ACL_fix(self):
        self._put({})

    @properties.validator
    def _validate_resources(self):
        """Check if project resource pointers are correct"""
        for res in self.resources:
            if self not in res.project:
                raise ValueError('Project/resource pointers misaligned: '
                                 'Ensure that resources point to containing '
                                 'project.')
        self._validate_project_size()
        return True

    def _nbytes(self):
        return sum(r._nbytes() for r in self.resources)

    def _validate_project_size(self, res=None):
        if Comms.user.logged_in:
            if res is None:
                res = self.resources
            res_limit = Comms.user.project_resource_limit
            if len(res) > res_limit:
                raise ProjectResourceLimitExceeded(
                    'Total number of resources in project ({res}) '
                    'exceeds limit: {lim}'.format(res=len(self.resources),
                                                  lim=res_limit)
                )
            size_limit = Comms.user.project_size_limit
            sz = self._nbytes()
            if sz > size_limit:
                raise ProjectSizeLimitExceeded(
                    'Total project size ({file} bytes) exceeds limit: '
                    '{lim} bytes'.format(file=sz,
                                         lim=size_limit)
                )
        return True

    @properties.observer('resources')
    def _fix_proj_res(self, change):
        before = change['previous']
        after = change['value']
        if before in (None, properties.undefined):
            before = []
        if after in (None, properties.undefined):
            after = []
        for res in after:
            if res not in before and self not in res.project:
                res.project += [self]
        for res in before:
            if res not in after and self in res.project:
                res.project = [p for p in res.project
                               if p is not self]
        if len(set(after)) != len(after):
            post_post = []
            for r in after:
                if r not in post_post:
                    post_post += [r]
            self.resources = post_post

    def _upload_dirty(self, **kwargs):
        dirty = self._dirty
        if 'resources' in dirty:
            [r._upload(**kwargs) for r in self.resources]

    def _get_dirty_data(self, force=False, initialize=False):
        datadict = super(Project, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if 'public' in dirty or force:
            datadict['public'] = self.public
        if ('resources' in dirty or force) and not initialize:
            datadict['resourceUids'] = ','.join(
                (r._json['longUid'] for r in self.resources)
            )
        return datadict

    def _check_project_quota(self, verbose=True):
        if self.public:
            privacy = 'public'
        else:
            privacy = 'private'
        if verbose:
            print('Verifying your quota for ' + privacy + ' projects...')
        resp = Comms.get('api/check/quota?test=ProjectSteno3D')
        resp = resp['json']
        mode = resp.get('mode', None)
        if not mode or mode == 'split':
            key = privacy
        else:
            key = mode
        resp = resp.get(key, None)
        if not resp or 'quota' not in resp or 'count' not in resp:
            pass
        elif resp['quota'] == 'Unlimited':
            pass
        elif resp['count'] >= resp['quota']:
            quota_message = resp.get('message', QUOTA_REACHED)
            raise ProjectQuotaExceeded(quota_message.format(
                priv=privacy,
                num=resp['quota'],
                base_url=Comms.base_url,
            ))
        elif verbose and (resp['quota'] - resp['count'] - 1) < 4:
            print(QUOTA_IMPENDING.format(
                remaining=resp['quota'] - resp['count'] - 1,
                priv=privacy,
                base_url=Comms.base_url,
            ))
        if verbose and self.public:
            print('This PUBLIC project will be viewable by everyone.')

    @property
    def _url(self):
        if getattr(self, '_upload_data', None) is not None:
            return self._url_view_from_uid(self._upload_data['uid'])

    @property
    @needs_login
    def url(self):
        """url of project if uploaded"""
        if getattr(self, '_upload_data', None) is None:
            print('Project not uploaded: Please upload() '
                  'before accessing the URL.')
        return self._url

    @needs_login
    def plot(self):
        """Display the 3D representation of the content

        You must be logged in to steno3d.com for the plot to display
        """
        if getattr(self, '_upload_data', None) is None:
            print('Project not uploaded: Please upload() '
                  'before plotting.')
            return
        url = '{base}{mapi}/{uid}'.format(
            base=Comms.base_url,
            mapi='embed',
            uid=self._upload_data['uid'],
        )
        return plot(url)

    @classmethod
    def _build(cls, uid, copy=True, tab_level='', verbose=True):
        if verbose:
            print('Downloading project', end=': ')
        json = cls._json_from_uid(uid)
        title = '' if json['title'] is None else json['title']
        desc = '' if json['description'] is None else json['description']
        if verbose:
            print(title)
        pub = False
        for a in json['access']:
            if a['user'] == 'Special:PUBLIC':
                pub = True
                break
        is_owner = Comms.user.username == json['owner']['uid']
        if copy is None:
            copy = not is_owner
        elif not copy and not is_owner:
            copy = True
        if copy and verbose:
            print('This is a copy of the {pub} project'.format(
                pub='PUBLIC' if pub else 'private'
            ))
        elif verbose:
            print('This is the original version of the {pub} project'.format(
                pub='PUBLIC' if pub else 'private'
            ))
            print('>> NOTE: Any changes you upload will overwrite the '
                  'project online')
            print('>> ', end='')
            if len(json['perspectiveUids']) > 0:
                print('and existing perspectives may be invalidated. ', end='')
            print('Please upload with caution.')

        proj = Project(
            public=pub,
            title=title,
            description=desc,
            resources=[]
        )
        for longuid in json['resourceUids']:
            res_string = longuid.split('Resource')[-1].split(':')[0]
            res_class = UserContent._REGISTRY[res_string]
            proj.resources += [res_class._build(
                src=longuid.split(':')[1],
                copy=copy,
                tab_level=tab_level + '    ',
                project=proj,
                using='ProjectSteno3D:{}'.format(uid),
            )]
        if not copy:
            proj._public_online = pub
            proj._upload_data = json
            proj._mark_clean()
        if verbose:
            print('... Complete!')
        return proj

    @classmethod
    def from_omf(cls, omf_input):
        if isinstance(omf_input, six.string_types):
            from omf import OMFReader
            omf_input = OMFReader(omf_input).get_project()
        if omf_input.__class__.__name__ != 'Project':
            raise ValueError('input must be omf file or Project')
        return cls._build_from_omf(omf_input)

    @classmethod
    def _build_from_omf(cls, omf_project):
        proj = Project(
            title=omf_project.name,
            description=omf_project.description,
            resources=[]
        )
        resource_map = {
            'PointSetElement': 'Point',
            'LineSetElement': 'Line',
            'SurfaceElement': 'Surface',
            'VolumeElement': 'Volume'
        }
        for elem in omf_project.elements:
            res_class = UserContent._REGISTRY[
                resource_map[elem.__class__.__name__]
            ]
            proj.resources += [
                res_class._build_from_omf(elem, omf_project, proj)
            ]
        return proj

CompositeResource._props['project'].prop.instance_class = Project


__all__ = ['Project']
