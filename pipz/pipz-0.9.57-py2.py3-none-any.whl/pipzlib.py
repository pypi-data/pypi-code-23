import os
import zipfile
from tempfile import NamedTemporaryFile, mkdtemp
import requests
import re
import ctypes
import tempfile
import uuid

def isAdmin():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def projectPath(localdata=None):
    parents = os.getcwd().split(os.sep)
    for i in range(len(parents)):
        if i == 0:
            parents_list = parents
        else:
            parents_list = parents[:-i]

        config_path = os.sep.join(parents_list + ['config.json'])

        if os.path.exists(config_path):
            if localdata is None:
                return os.sep.join(parents_list)

            return os.sep.join(parents_list + [localdata])
    return None

def unzip(key, directory):
    f = NamedTemporaryFile(delete=False)
    f.close()
    fn = f.name

    url = 'https://s3.amazonaws.com/whl/{location}'.format(location=key)
    r = requests.get(url, allow_redirects=True)
    with open(fn, 'wb') as f:
        f.write(r.content)

    file_name = os.path.abspath(fn)  # get full path of files
    zip_ref = zipfile.ZipFile(file_name)  # create zipfile object

    if not os.path.exists(directory):
        os.mkdir(directory)

    zip_ref.extractall(directory)  # extract file to dir
    zip_ref.close()  # close file
    os.unlink(file_name)  # delete zipped file

def install_powershell_module(module, secret):
    ps_dirs = os.environ['PSMODULEPATH'].split(';')
    existing_locations = []
    upgrade_locations = []
    for ps_dir in ps_dirs:
        if os.path.exists(ps_dir):
            ss_dir = os.path.join(ps_dir, module)
            existing_locations.append(ps_dir)
            if os.path.exists(ss_dir):
                upgrade_locations.append(ps_dir)

    upgrade_locations = list(set(upgrade_locations))
    if any(upgrade_locations):
        location, = upgrade_locations
    elif any(existing_locations):
        location = existing_locations[0]
    else:
        raise Exception("No existing PSMODULEPATH")

    module_location = os.path.join(location, module)

    if secret is None:
        unzip('{module}/{module}.zip'.format(module=module), module_location)
    else:
        unzip('{secret}/{module}/{module}.zip'.format(secret=secret, module=module), module_location)


def install_data(name=None, target=None):
    project_fn = projectPath()
    if name is None:
        name = os.path.basename(project_fn)

    zipfn = os.path.join(tempfile.gettempdir(), 'z'+str(uuid.uuid4()).replace('-','')+'.zip')
    import urllib.request

    url = "https://s3.amazonaws.com/whl/data/{name}/data.zip".format(name=name)
    urllib.request.urlretrieve(url, zipfn)

    zip_ref = zipfile.ZipFile(zipfn, 'r')
    if target is None:
        target = 'localdata'
    zip_ref.extractall(os.path.join(projectPath(), target))
    zip_ref.close()
    os.unlink(zipfn)



def install_private_package(package, secret):
    if secret is None:
        os.system("pip install {lib} --no-cache-dir --upgrade --extra-index-url http://s3.amazonaws.com/whl/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package))
    else:
        os.system("pip install {lib} --no-cache-dir --upgrade --extra-index-url http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package, secret=secret))

    os.system("pipz install-requirements {lib}".format(lib=package))


def download_private_package(package, secret):
    if secret is None:
        os.system("pip download {lib} --no-cache-dir --no-deps --index-url http://s3.amazonaws.com/whl/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package))
    else:
        os.system("pip download {lib} --no-cache-dir --no-deps  --index-url http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package, secret=secret))
