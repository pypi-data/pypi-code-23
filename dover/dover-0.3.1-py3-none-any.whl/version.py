import re


_FORMATING_ = {
    'M': '{0.major}',
    'Mm': '{0.major}.{0.minor}',
    'Mmp': '{0.major}.{0.minor}.{0.patch}'
}


class VersionError(Exception):
    pass


class PreRelease(object):

    _names = (None, 'alpha', 'beta', 'rc')

    def __init__(self):
        self.name = None 
        self.number = 0 

    def initialize(self, name=None, number=0):
        self.name = name
        self.number = number

    def reset(self):
        self.initialize()

    @property
    def exists(self):
        return self.name is not None

    def increment(self, name):

        if not name in self._names:
            raise VersionError('Unrecognized pre-release name: `{}`.'.format(name))

        if name is None:
            self.reset()
        elif not self.name:
            # this will set the pre-relase to 
            # whatever the name is and skip the natural sequence 
            self.name = name
            self.number = 0
        elif name == self.name:
            self.increment_number()
        elif self.name == 'alpha' and name in ('beta', 'rc'):
            self.initialize(name, 0)
        elif self.name == 'beta' and name == 'rc':
            self.initialize(name, 0)
        else:
            err_msg = ('Invalid pre-release sequence requested: '
                       '`{}` release preceeds `{}`.')
            raise VersionError(err_msg.format(name, self.name))

    def increment_number(self):
        self.number += 1

    def __str__(self):
        if not self.exists:
            return ''
        if self.number == 0:
            number_str = ''
        else:
            number_str = '.{}'.format(self.number)
        return '-{}{}'.format(self.name, number_str)


class Version(object):

    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'
    ALPHA = 'alpha'
    BETA = 'beta'
    RC = 'rc'

    _names = (None, 'major', 'minor', 'patch')

    _vers_regex = re.compile((r'^(?P<major>\d+)'
                              r'(\.(?P<minor>\d+))?'
                              r'(\.(?P<patch>\d+))?'
                              r'(-(?P<pre_release>(alpha|beta|rc))(\.(?P<pre_number>\d+))?)?$'))

    def __init__(self, version_string='0.1.0'):
        vmatch = self._vers_regex.match(version_string)
        if not vmatch:
            msg = '"{}" is an invalid version string.'
            raise VersionError(msg.format(version_string))

        vstr = vmatch.groupdict()

        self.major = int(0 if not vstr['major'] else vstr['major'])
        self.minor = int(0 if not vstr['minor'] else vstr['minor'])
        self.patch = int(0 if not vstr['patch'] else vstr['patch'])
        # pre-release 
        self.pre_release = PreRelease()
        _pre_name = None if not vstr['pre_release'] else vstr['pre_release']
        _pre_number = int(0 if not vstr['pre_number'] else vstr['pre_number'])
        self.pre_release.initialize(_pre_name, _pre_number)

    def copy(self):
        return Version(str(self))

    def increment(self, part, pre_release=None):
        if part not in self._names:
            raise VersionError('`{}` is not a valid version part.'.format(part))

        if not part and not pre_release:
            raise VersionError('No version section has been selected.')

        if part == 'major':
            self.increment_major()
        elif part == 'minor':
            self.increment_minor()
        elif part == 'patch':
            self.increment_patch()

        if not pre_release or (part and pre_release):
            self.pre_release.reset()

        if pre_release:
            self.pre_release.increment(pre_release)

    def increment_major(self):
        self.major += 1
        self.minor = 0
        self.patch = 0

    def increment_minor(self):
        self.minor += 1
        self.patch = 0

    def increment_patch(self):
        self.patch += 1

    def to_tuple(self):
        if self.pre_release.exists:
            return (self.major, self.minor, self.patch, self.pre_release)
        return (self.major, self.minor, self.patch)

    def __eq__(self, obj):
        return str(self) == str(obj)

    def __str__(self):
        version = self.to_tuple()
        ver_str = '.'.join([str(i) for i in version[:3]])
        if len(version) > 3:
            ver_str += str(version[3])
        return ver_str

    def __repr__(self):
        return '<Version {0}>'.format(self)

    def __format__(self, fmt):
        default = _FORMATING_['Mmp']
        return _FORMATING_.get(fmt, default).format(self)
