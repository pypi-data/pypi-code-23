from .version import Version  
from . import project


@project.command
def version(vfiles, *args, **kwargs):
    '''
    Return just the version number string.

    '''
    print(kwargs['current_version'])


@project.command
def display(vfiles, *args, **kwargs):
    '''
    Return the version number sting, as well as a listing
    of all the files with version strings and what that
    version number is.

    '''
    print('Current Version: {}'.format(kwargs['current_version']))
    print('Files:')
    for vfile in vfiles:
        print(vfile.show_version_lines(indent=4))


@project.command
def increment(vfiles, *args, **kwargs):
    
    cli_args = kwargs['cli_args']
    current_version = kwargs['current_version']
    version = Version(current_version)

    if cli_args['--major']:
        part = 'major' 
    elif cli_args['--minor']:
        part = 'minor'
    elif cli_args['--patch']:
        part = 'patch'
    else:
        raise Exception('No valid version segment selected.')
    
    version.increment(part)
    version_str = str(version)

    print('Current Version: {}'.format(kwargs['current_version']))
    print('New Version:     {}'.format(version_str))
    print('Files:')

    for vfile in vfiles:
        vfile.update(version_str)
        print(vfile.show_version_update(version_str, indent=4))

    if cli_args['--apply'] is True:
        for vfile in vfiles: 
            vfile.save()
        print('Version updates applied.')
