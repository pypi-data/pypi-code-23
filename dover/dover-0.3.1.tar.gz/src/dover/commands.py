import sys
from functools import wraps
from .version import Version
from . import project


def command(func):

    @wraps(func)
    def _command(cargs, *args, **kwargs):
        try:

            cfg = project.find_config_file()
            vfiles = project.collect_versioned_files(cfg)
            current_version = project.assert_versions(vfiles)
            kwargs['current_version'] = current_version

            return func(vfiles, cargs, *args, **kwargs)

        except project.ConfigurationError as config_err:
            print(str(config_err))

        except project.VersionMissMatchError as version_err:  # pragma: no cover
            print(str(version_err))

        except Exception as ex:  # pylint: disable:broad-exception  # pragma: no cover
            print("Error: {}".format(ex))

            if cargs['--debug'] is True:
                import traceback
                exc = sys.exc_info()
                traceback.print_tb(exc[2])

            sys.exit(1)

    return _command


@command
def version(*args, **kwargs):
    '''
    Return the raw version number string.

    '''
    print(kwargs['current_version'])


@command
def display(vfiles, cargs, *args, **kwargs):
    '''
    Return the version number sting, as well as a listing
    of all the files with version strings and what that
    version number is.

    '''
    print('Current Version: {}'.format(kwargs['current_version']))
    print('Files:')
    project.print_versioned_lines(vfiles)


@command
def increment(vfiles, cargs, *args, **kwargs):

    current_version = kwargs['current_version']
    new_version = Version(current_version)
    
    part = None

    if cargs['--major']:
        part = Version.MAJOR
    elif cargs['--minor']:
        part = Version.MINOR
    elif cargs['--patch']:
        part = Version.PATCH
    
    prerelease = None

    if cargs['--alpha']:
        prerelease = Version.ALPHA
    elif cargs['--beta']:
        prerelease = Version.BETA
    elif cargs['--rc']:
        prerelease = Version.RC

    new_version.increment(part, prerelease)

    print('Current Version: {}'.format(current_version))
    print('New Version:     {}'.format(str(new_version)))

    if not cargs['--no-list']: 
        print('Files:')
        project.print_versioned_updates(vfiles, str(new_version))

    if cargs['--apply'] is True:
        for vfile in vfiles:
            vfile.update(str(new_version))
            vfile.save()
        print('Version updates applied.')
