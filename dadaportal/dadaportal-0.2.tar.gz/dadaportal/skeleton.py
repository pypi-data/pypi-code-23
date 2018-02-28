import horetu
from pathlib import Path
from . import config

IMAGE = {'.png', '.jpg', '.jpeg', '.gif'}
VIDEO = {'.webm', '.mp4'}
AUDIO = {'.ogg'}
OTHER_BINARY = { 
    '.gz',
    '.docx',
    '.geojson', '.json',
    '.maff', '.mht',
    '.svg', '.pdf',
    '.mkv',
    '.xcf',
}
IGNORE = {'.checked', '.bak', '.orig', '.new'}

LISTING_FORMATS = {
    'rst': (
        '`%(title)s <%(href)s>`_',
        '.. image:: %(href)s\n    :alt: %(title)s\n',
        '.. raw:: html\n\n    <audio src="%(href)s" autoplay>%(title)s</audio>\n',
        '.. raw:: html\n\n    <video src="%(href)s" controls width="100%%">%(title)s</video>\n'
    ),
    'md': (
        '[%(title)s](%(href)s)',
        '![%(title)s](%(href)s)',
        '<audio src="%(href)s" autoplay>%(title)s</audio>',
        '<video src="%(href)s" controls width="100%%">%(title)s</video>',
    ),
    'html': (
        '<a href="%(href)s">%(title)s</a>',
        '<img src="%(href)s">%(title)s>',
        '<audio src="%(href)s" autoplay>%(title)s</audio>',
        '<video src="%(href)s" controls width="100%%">%(title)s</video>',
    ),
}
def listing(directory: Path,
            format: LISTING_FORMATS=LISTING_FORMATS['rst']):
    '''
    Write a directory listing file in ReStructured Text.

    :param directory: Directory to write the listing for
    :param format: File format of the resulting listing
    '''
    page, image, audio, video = format
    for child in sorted(directory.glob('*')):
        if child.is_dir() or child.with_suffix('').name != 'index':
            if child.suffix.lower() in IGNORE:
                continue
            elif child.suffix.lower() in IMAGE:
                subformat = image
                slash = ''
            elif child.suffix.lower() in AUDIO:
                subformat = audio
                slash = ''
            elif child.suffix.lower() in VIDEO:
                subformat = video
                slash = ''
            else:
                subformat = page
                slash = '/'
            yield (subformat) % {
                'title': child.with_suffix('').name.replace('-', ' ').title(),
                'href': child.name + slash,
            }

INSTALLER = '''\
#!/bin/sh
cd /tmp
wget https://www.fossil-scm.org/fossil/uv/fossil-src-2.1.tar.gz
tar xzf fossil-src-2.1.tar.gz
cd fossil-2.1
./configure
make
cp fossil %(fossil-executable)s
mkdir -p %(fossil-repositories)s
chown -R :web %(fossil-repositories)s
'''

def sdf():
    '''
    Write an installation script for SDF.
    '''
    return INSTALLER % {
        'fossil-executable': '~/fossil',
        'fossil-repositories': '~/r',
    }

def nfsn(configuration: Path):
    '''
    Write an installation script for NFSN.

    :param configuration: Configuration file
    '''
    tpl = INSTALLER + '''\
echo '#!%(fossil-executable)s
directory: %(fossil-repositories)s' > %(web-directory)s/%(fossil-route)s
chmod a+x %(web-directory)s/%(fossil-route)s
'''
    with configuration.open() as fp:
        c = config.configuration_file(fp)
    c['web-directory'] = '/home/public'
    return tpl % c

def permissions(configuration: Path):
    '''
    Set permissions to protect against accidental deletion.

    :param configuration: Configuration file
    '''
    binary = IMAGE.union(VIDEO).union(AUDIO).union(OTHER_BINARY)
    with configuration.open() as fp:
        c = config.configuration_file(fp)
    if c['root-directory']:
        root = configuration.parent / c['root-directory']
        for path in root.glob('**/*'):
            if path.suffix.lower() in binary:
                path.chmod(0o444)

def configure(configuration: Path, force=False):
    '''
    Write a new configuration file.

    :param configuration: Where to put the configuration file
    :param force: Overwrite if a file already exists at the
        configuration file output location
    '''
    if not force and configuration.exists():
        raise horetu.Error('File already exists: %s' % configuration)

    with configuration.open('w') as fp:
        for key, default in config.CONFIGURATION_DEFAULTS.items():
            value = input('%s [%s]: ' % (key, default)).strip()
            if value:
                fp.write('%s: %s\n' % (key, value))
