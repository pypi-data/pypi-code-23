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

        except project.ConfigurationError as ex:
            print(str(ex))
            sys.exit(0)

        except project.VersionMissMatchError as ex:
            print(str(ex))
            sys.exit(0)

        except Exception as ex:  # pylint: disable:broad-exception
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

    if cargs['--major']:
        part = 'major'
    elif cargs['--minor']:
        part = 'minor'
    elif cargs['--patch']:
        part = 'patch'
    else:
        raise Exception('No valid version segment selected.')

    new_version.increment(part)

    print('Current Version: {}'.format(current_version))
    print('New Version:     {}'.format(new_version))
    print('Files:')
    project.print_versioned_updates(vfiles, str(new_version))

    if cargs['--apply'] is True:
        for vfile in vfiles:
            vfile.update(str(new_version))
            vfile.save()
        print('Version updates applied.')
