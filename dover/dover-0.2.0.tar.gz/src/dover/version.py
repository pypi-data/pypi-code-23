import re


_formating_ = {
    'M': '{0.major}',
    'Mm': '{0.major}.{0.minor}',
    'Mmp': '{0.major}.{0.minor}.{0.patch}'
}


class Version(object):

    _vers_regex = re.compile((r'^(?P<major>\d+)'
                              r'(\.(?P<minor>\d+))?'
                              r'(\.(?P<patch>\d+))?$'))

    def __init__(self, version_string='0.1.0'):
        vmatch = self._vers_regex.match(version_string)
        if not vmatch:
            msg = '"{}" is an invalid version string.'
            raise Exception(msg.format(version_string))

        vstr = vmatch.groupdict()

        self.major = int(0 if not vstr['major'] else vstr['major'])
        self.minor = int(0 if not vstr['minor'] else vstr['minor'])
        self.patch = int(0 if not vstr['patch'] else vstr['patch'])

    def copy(self):
        return Version(str(self))

    def increment(self, part):
        if part == 'major':
            self.increment_major()
        elif part == 'minor':
            self.increment_minor()
        elif part == 'patch':
            self.increment_patch()
        else:
            raise Exception('`{}` is not a valid version part.'.format(part))

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
        return (self.major, self.minor, self.patch)

    def __str__(self):
        version = self.to_tuple()

        return '.'.join([str(i) for i in version])

    def __repr__(self):
        return '<Version {0}>'.format(self)

    def __format__(self, format):
        default = _formating_['Mmp']
        return _formating_.get(format, default).format(self)
