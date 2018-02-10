# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

_package_data = dict(
    full_package_name='nim_install',
    version_info=(0, 4, 1),
    __version__='0.4.1',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    description='install nim compiler in Linux virtualenv assumes gcc',
    # keywords="",
    entry_points='nim_install',
    # entry_points=None,
    license='MIT',
    since=2016,
    # data_files="",
    universal=True,
    extras_require={':python_version<="3.3"': ['backports.lzma']},
    tox=dict(
        env='23',
    ),
)


version_info = _package_data['version_info']
__version__ = _package_data['__version__']

######


def main():
    import sys
    import os
    import tarfile
    if sys.version_info < (3, ):
        from backports import lzma
        import urllib2
    else:
        import lzma
        from urllib.request import FancyURLopener

        class MyURLOpener(FancyURLopener):
            version = 'Mozilla/5.0'

    try:
        nim_version_string = sys.argv[1]
    except IndexError:
        nim_version = (0, 17, 2)
        nim_version_string = '.'.join([str(x) for x in nim_version])
    nim_download = 'http://nim-lang.org/download/nim-{}.tar.xz'.format(
        nim_version_string)
    print('getting', nim_download)
    inst_dir = os.path.dirname(os.path.dirname(sys.executable))
    print('inst_dir', inst_dir)
    os.chdir(inst_dir)
    if True:
        from io import BytesIO
        if sys.version_info < (3, ):
            # request = urllib2.Request(nim_download)
            # request.add_header('User-Agent', "Mozilla/5.0")
            opener = urllib2.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        else:
            opener = MyURLOpener()
        response = opener.open(nim_download)
        data = BytesIO()
        data.write(lzma.decompress(response.read()))
        data.seek(0)
        with tarfile.open(fileobj=data, mode='r') as tar:
            for tarinfo in tar:
                if '/' not in tarinfo.name:
                    continue
                name = tarinfo.name.split('/', 1)[1]
                if tarinfo.isdir():
                    if not os.path.exists(name):
                        os.mkdir(name)
                    continue
                # print('tarinfo', tarinfo.name, name, tarinfo.isdir())
                with open(name, 'wb') as fp:
                    fp.write(tar.extractfile(tarinfo).read())

    os.system('make -j8')
    os.system('./bin/nim c koch')
    os.system('./koch tools')


if __name__ == '__main__':
    main()
