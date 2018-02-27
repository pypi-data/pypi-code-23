from first import first
import click
import re

pattern = re.compile(r"((?:__)?version(?:__)? ?= ?[\"'])(.+?)([\"'])")


class SemVer(object):

    def __init__(self, major=0, minor=0, patch=0, pre=None, local=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre = pre
        self.local = local

    def __repr__(self):
        # TODO: this is broken
        return '<SemVer {}>'.format(
            ', '.join([
                '{}={}'.format(n, getattr(self, n))
                for n in self.__slots__
            ])
        )

    def __str__(self):
        version_string = '.'.join(map(
            str,
            [self.major, self.minor, self.patch]
        ))
        if self.pre:
            version_string += '-' + self.pre
        if self.local:
            version_string += '+' + self.local
        return version_string

    @classmethod
    def parse(cls, version):
        major = minor = patch = 0
        local = pre = None
        local_split = version.split('+')
        if len(local_split) > 1:
            version, local = local_split
        pre_split = version.split('-', 1)
        if len(pre_split) > 1:
            version, pre = pre_split
        major_split = version.split('.', 1)
        if len(major_split) > 1:
            major, version = major_split
            minor_split = version.split('.', 1)
            if len(minor_split) > 1:
                minor, version = minor_split
                if version:
                    patch = version
            else:
                minor = version
        else:
            major = version
        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            pre=pre,
            local=local,
        )

    def bump(self, major=False, minor=False, patch=False, pre=None, local=None):
        if major:
            self.major += 1
        if minor:
            self.minor += 1
        if patch:
            self.patch += 1
        if pre:
            self.pre = pre
        if local:
            self.local = local
        if not (major or minor or patch or pre or local):
            self.patch += 1


def find_version(input_string):
    return first(pattern.findall(input_string))[1]


@click.command()
@click.option(
    '--major', '-M', 'major', flag_value=True, default=False,
    help='Bump major number',
)
@click.option(
    '--minor', '-m', 'minor', flag_value=True, default=False,
    help='Bump minor number',
)
@click.option(
    '--patch', '-p', 'patch', flag_value=True, default=True,
    help='Bump patch number',
)
@click.option('--pre', help='Set the pre-release identifier')
@click.option('--local', help='Set the local version segment')
@click.argument('input', type=click.File('rb'), default='setup.py')
@click.argument('output', type=click.File('wb'), default='setup.py')
def main(input, output, **kwargs):
    contents = input.read().decode('utf-8')
    version_string = find_version(contents)
    version = SemVer.parse(version_string)
    version.bump(**kwargs)
    new = pattern.sub('\g<1>{}\g<3>'.format(version), contents)
    output.write(new.encode())
    click.echo(version)


if __name__ == '__main__':
    main()
