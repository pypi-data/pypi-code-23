import os.path

__conrad_url = "https://www5.cs.fau.de/fileadmin/user_upload/CONRAD_1.0.8.zip"
__conrad_release = __conrad_url.split('/')[-1].rstrip(".zip")
__conrad_jar = __conrad_release.lower() + ".jar"
__conrad_download_dir = os.path.dirname(__file__)


def conrad_jar_filename():
    return __conrad_jar


def conrad_jar_dir():
    return os.path.join(__conrad_download_dir, __conrad_release.replace('_', ' '))


def conrad_jar_file():
    return os.path.join(conrad_jar_dir(), __conrad_jar)


def download_conrad(dest_dir=__conrad_download_dir):
    import sys
    import os

    __conrad_download_dir = dest_dir

    if sys.version_info[0] == 3:
        from urllib.request import urlopen
    else:
        from urllib import urlopen

    file_name = __conrad_url.split('/')[-1]
    zip_path = os.path.join(__conrad_download_dir, __conrad_url.split('/')[-1])
    u = urlopen(__conrad_url)
    f = open(zip_path, 'wb')

    file_size_dl = 0
    block_sz = 8192
    print("Downloading %s..." % file_name)
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        # status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        # status = status + chr(8)*(len(status)+1)

    f.close()

    print("Extracting %s..." % file_name)
    import zipfile
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(__conrad_download_dir)
    zip_ref.close()
    os.remove(zip_path)
    print("Finished extracting.")
