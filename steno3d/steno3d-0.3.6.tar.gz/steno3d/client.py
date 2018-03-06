"""client.py contains the functionality to link the python steno3d
client with the steno3d website
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps
from os import mkdir
from os import path
from time import sleep

import requests
from six import string_types
from six.moves import input
from six.moves.urllib.parse import urlparse

from .user import User


__version__ = '0.3.6'

PRODUCTION_BASE_URL = 'https://steno3d.com/'
SLEEP_TIME = .75

DEVKEY_PROMPT = "If you have a Steno3D developer key, please enter it here > "

WELCOME_MESSAGE = """
>> Welcome to the Python client library for Steno3D!
"""

FIRST_LOGIN = """
If you do not have a Steno3D developer key, you need to request
one from the Steno3D website in order to access the API. Please
log in to the application (if necessary) and request a new key.

{base_url}settings/developer

If you are not yet signed up, you can do that here:

{base_url}signup

When you are ready, please enter the key above, or reproduce this
prompt by calling steno3d.login().

"""

LOGIN_FAILED = """
>> Oh no! We could not log you in. The API developer key that you provided
could not be validated. If your current API key has been lost or
invalidated, please request a new one at:

{base_url}settings/developer

Then, try `steno3d.login('YOUR-NEW-DEVEL-KEY')`

If the problem persists:

1) Restart your Python kernel and try again
2) Update steno3d with `pip install --upgrade steno3d`
3) Ask for <support@steno3d.com>
4) Open an issue https://github.com/aranzgeo/steno3dpy/issues

"""

NOT_CONNECTED = """
>> Oh no! We could not connect to the server. Please ensure that you are:

1) Connected to the Internet
2) Can connect to {base_url}
3) If you are getting an InsecurePlatformWarning while using pip try:
    a) Upgrading to Python 2.7.9 or above
    b) Or `pip install --upgrade requests[security]`
4) Ask for <support@steno3d.com>
5) Open an issue https://github.com/aranzgeo/steno3dpy/issues

"""

BAD_API_KEY = """
>> Oh no! Your API developer key format is incorrect.

It should be your username followed by '//' then 36 characters.
You may also use only your username if you have access to local saved
credentials. If you have not requested an API key or if you have lost
your API key, please request a new one at:

{base_url}settings/developer

"""

INVALID_VERSION = """
Oh no! Your version of steno3d is out of date.

{your_version}
{current_version}

Please update steno3d with `pip install --upgrade steno3d`.

"""

BETA_TEST = """
It looks like you are using a beta version of steno3d. Thank you for
trying it out!

Please, if you run into any problems or have any feedback, open an
issue at https://github.com/aranzgeo/steno3dpy/issues

If you would like to switch to the most recent stable version:
> pip uninstall steno3d
> pip install steno3d

"""

ALREADY_LOGGED_IN = """
You are already logged in as @{user}. To log in as a different user
please `steno3d.logout()`, then login specifying a different
username or API developer key.

"""


def needs_login(func):
    """Wrapper used around functions that need you to be logged in"""
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if Comms.user.logged_in:
            return func(*args, **kwargs)
        elif kwargs.get('verbose', True):
            print("Please login: 'steno3d.login()'")
    return func_wrapper


def pause():
    """Brief pause on localhost to simulate network delay"""
    if 'localhost' in Comms.base_url:
        sleep(SLEEP_TIME)


class _Comms(object):
    """Comms controls the interaction between the python client and the
    Steno3D website.
    """

    def __init__(self):
        self.user = User()
        self._base_url = PRODUCTION_BASE_URL
        self._hard_devel_key = None

    @property
    def host(self):
        """hostname of url"""
        parseresult = urlparse(self.base_url)
        return parseresult.hostname

    @property
    def base_url(self):
        """base url endpoint for uploading"""
        return getattr(self, '_base_url', PRODUCTION_BASE_URL)

    @base_url.setter
    def base_url(self, value):
        assert isinstance(value, string_types), \
            'Endpoint path must be a string'
        # Patch '/' onto bare URL endpoints
        if not value[-1] == '/':
            value += '/'
        # Check for HTTPS
        parsed = urlparse(value)
        if '.com' in parsed.hostname and parsed.scheme != 'https':
            raise ValueError('Live endpoints require HTTPS.')

        self._base_url = value

    def login(self, devel_key=None, credentials_file=None,
              skip_credentials=False, endpoint=None, verbose=True):
        """Login to steno3d.com to allow uploading resources. To obtain an
        API developer key, you need a Steno3D account:

        https://steno3d.com/signup

        Then, you can request a devel key:

        https://steno3d.com/settings/developer

        Unless you choose to 'skip_credentials', your API key will be
        saved locally and read next time you call `steno3d.login()`.
        You can always login using a different devel key (or username if
        the corresponding devel key is saved in the credentials file).

        Optional arguments:
            devel_key        - API key from steno3d.com. Prompt will appear if
                               this is not provided or saved in credential
                               file. This may also be a username corresponding
                               to a devel key saved in the credentials file
            credentials_file - Local file where devel keys are stored.
                               (Default: ~/.steno3d_client/credentials)
            skip_credentials - If False (default), devel key will be read
                               from and written to local credentials file.
                               If True, only uses the provided devel key or
                               prompts for a new key.
            endpoint         - Target site (Default: steno3d.com)
        """

        # Check user
        if self.user.logged_in:
            if verbose:
                print(ALREADY_LOGGED_IN.format(user=self.user.username))
            return

        # Set endpoint
        if endpoint is not None:
            self.base_url = endpoint

        # Check client version
        if not self._version_ok(verbose):
            if verbose:
                print('Login failed.')
            return

        if verbose:
            print(WELCOME_MESSAGE)

        # Assess credential file options.
        if skip_credentials:
            self._login_with(devel_key, verbose)
            return

        # Extract credential file
        if credentials_file is None:
            credentials_file = path.sep.join([path.expanduser('~'),
                                              '.steno3d_client',
                                              'credentials'])
            cred_dir = path.sep.join(credentials_file.split(path.sep)[:-1])
            if not path.isdir(cred_dir):
                mkdir(cred_dir)
        elif isinstance(credentials_file, string_types):
            credentials_file = path.realpath(path.expanduser(
                credentials_file
            ))
            cred_dir = path.sep.join(credentials_file.split(path.sep)[:-1])
        else:
            raise ValueError('credentials_file: must be the name of a file')

        if not path.isdir(cred_dir):
            raise ValueError(
                '{}: credentials file directory must exist'.format(cred_dir)
            )
        if path.exists(credentials_file) and not path.isfile(credentials_file):
            raise ValueError(
                '{}: credentials file must be a file'.format(credentials_file)
            )
        if path.isfile(credentials_file):
            if verbose:
                print('Credentials file found: {}'.format(credentials_file))
            with open(credentials_file, 'r') as cred:
                devel_keys = cred.readlines()
            devel_keys = [dk.strip() for dk in devel_keys
                          if self.is_key(dk.strip())]
            usernames = [dk.split('//')[0] for dk in devel_keys]
        else:
            if verbose:
                print('Creating new credentials file: {}'.format(credentials_file))
            devel_keys = []
            usernames = []

        # Get key from credential file
        if devel_key in usernames:
            if verbose:
                print('Accessing API developer key for @{}'.format(devel_key))
            devel_key = devel_keys[usernames.index(devel_key)]

        if devel_key is None and len(devel_keys) > 0:
            if verbose:
                print('Accessing API developer key for @{}'.format(usernames[0]))
            devel_key = devel_keys[0]

        self._login_with(devel_key, verbose)

        # Update credential file
        if self.user.logged_in:
            updated_devel_keys = [self.user.devel_key]
            for i, key in enumerate(devel_keys):
                if (key == self.user.devel_key or
                        usernames[i] == self.user.username):
                    continue
                updated_devel_keys += [key]
            with open(credentials_file, 'w') as cred:
                cred.writelines(['{}\n'.format(k) for k in updated_devel_keys])

    def _version_ok(self, verbose=True):
        """Check current Steno3D client version in the database"""
        try:
            resp = requests.post(
                self.base_url + 'api/client/steno3dpy',
                dict(version=__version__),
                timeout=120,
            )
        except requests.ConnectionError:
            if verbose:
                print(NOT_CONNECTED.format(base_url=self.base_url))
            return False
        if resp.status_code == 200:
            resp_json = resp.json()
            your_ver_str = resp_json['your_version']
            your_ver = [int(v) for v in your_ver_str.split('.')]
            curr_ver_str = resp_json['current_version']
            curr_ver = [int(v) for v in curr_ver_str.split('.')]
            if resp_json['valid'] or curr_ver_str == '0.0.0':
                return True
            elif your_ver[0] == curr_ver[0] and your_ver[1] == curr_ver[1]:
                if verbose:
                    print(INVALID_VERSION.format(
                        your_version='Your version: ' + your_ver_str,
                        current_version='Current version: ' + curr_ver_str
                    ))
                return True
            else:
                if verbose:
                    print(INVALID_VERSION.format(
                        your_version='Your version: ' + your_ver_str,
                        current_version='Required version: ' + curr_ver_str
                    ))
                if your_ver[0] < curr_ver[0]:
                    return False
                if your_ver[0] == curr_ver[0] and your_ver[1] < curr_ver[1]:
                    return False
                return True
        elif resp.status_code == 400 and verbose:
            resp_json = resp.json()
            if 'b' in __version__.split('.')[2]:
                print(BETA_TEST)
            else:
                print(INVALID_VERSION.format(
                    your_version='Your version: ' + __version__,
                    current_version='Error: ' + resp_json['reason']
                ))
        return True

    def _login_with(self, devel_key, verbose=True):
        """Login with devel_key"""
        if devel_key is None:
            if verbose:
                print(FIRST_LOGIN.format(base_url=self.base_url))
            devel_key = input(DEVKEY_PROMPT)
        if not self.is_key(devel_key):
            if verbose:
                print(BAD_API_KEY.format(base_url=self.base_url))
            return
        try:
            resp = requests.get(
                self.base_url + 'api/me',
                headers={'sshKey': devel_key,
                         'client': 'steno3dpy:{}'.format(__version__)},
                timeout=120,
            )
        except requests.ConnectionError:
            if verbose:
                print(NOT_CONNECTED.format(base_url=self.base_url))
            return
        if resp.status_code is not 200:
            if verbose:
                print(LOGIN_FAILED.format(base_url=self.base_url))
            self.logout()
            return
        self.user.login_with_json(resp.json())
        self.user.set_key(devel_key)
        self._cookies = dict(resp.cookies)
        if verbose:
            print(
                'Welcome to Steno3D! You are logged in as @{name}'.format(
                    name=self.user.username
                )
            )

    @staticmethod
    def is_key(devel_key):
        """Checks if devel_key is a valid API key string"""
        if not isinstance(devel_key, string_types):
            return False
        split_key = devel_key.split('//')
        return len(split_key) == 2 and len(split_key[1]) == 36

    def logout(self, verbose=True):
        """Logout current user"""
        if self.user.logged_in:
            if verbose:
                print('Logging out of steno3d...')
            headers = {'sshKey': Comms.user.devel_key,
                       'client': 'steno3dpy:{}'.format(__version__)}
            requests.get(
                Comms.base_url + 'signout',
                headers=headers,
                cookies=Comms._cookies,
                timeout=120,
            )

            if verbose:
                print('Goodbye, @{}.'.format(self.user.username))
        self._base_url = PRODUCTION_BASE_URL
        self.user.logout()

    @staticmethod
    def post(url, data=None, files=None):
        """Post data and files to the steno3d online endpoint"""
        return _Comms._communicate(requests.post, url, data, files)

    @staticmethod
    def put(url, data=None, files=None):
        """Put data and files to the steno3d online endpoint"""
        return _Comms._communicate(requests.put, url, data, files)

    @staticmethod
    def get(url):
        """Make a get request from a steno3d online endpoint"""
        return _Comms._communicate(requests.get, url, None, None)

    @staticmethod
    def _communicate(request_fcn, url, data, files):
        """Post data and files to the steno3d online endpoint"""
        data = {} if data is None else data
        files = {} if files is None else files
        filedict = {}
        for filename in files:
            if hasattr(files[filename], 'dtype'):
                filedict[filename] = files[filename].file
                filedict[filename + 'Type'] = files[filename].dtype
            else:
                filedict[filename] = files[filename]
        headers = {'sshKey': Comms.user.devel_key,
                   'client': 'steno3dpy:{}'.format(__version__)}
        if getattr(Comms, 'extra_headers', None):
            headers.update(Comms.extra_headers)
        req = request_fcn(
            Comms.base_url + url,
            data=data,
            files=filedict,
            headers=headers,
            cookies=Comms._cookies,
            timeout=120,
        )
        if req.status_code < 210:
            Comms._cookies.update(req.cookies)
        for key in files:
            files[key].file.close()

        try:
            resp = req.json()
        except ValueError:
            resp = req
        return {"status_code": req.status_code, "json": resp}


Comms = _Comms()


def plot(url):
    """Return an IFrame plot"""
    from IPython.display import IFrame
    return IFrame(url, width='100%', height=500)
