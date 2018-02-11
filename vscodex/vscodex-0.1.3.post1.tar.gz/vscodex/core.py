import json
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
import semver
from bs4 import BeautifulSoup

from .config import VSCODE_EXECUTABLE


def fetch_info(extension_id):
    print(f"Fetching info for '{extension_id}'")
    r = requests.get('https://marketplace.visualstudio.com/items',
                     params={'itemName': extension_id})

    if r.status_code == 404:
        raise KeyError('Invalid extension id')

    soup = BeautifulSoup(r.text, 'html.parser')
    info = soup.find('script', class_='vss-extension')
    return json.loads(info.get_text())


def run(args):
    p = subprocess.run(args, stdout=subprocess.PIPE)
    return p.stdout.decode().strip()


def current_versions():
    args = [VSCODE_EXECUTABLE, '--list-extensions', '--show-versions']
    return dict(line.split('@') for line in run(args).splitlines())


def fetch_latest_version(extension_id):
    info = fetch_info(extension_id)
    latest = max(info['versions'], key=lambda x: x['version'])

    for file in latest['files']:
        if file['assetType'] == 'Microsoft.VisualStudio.Services.VSIXPackage':
            url = file['source']
            break
    else:
        raise LookupError('VSIX Package not found for'
                          f'latest version of {extension_id}')

    return latest['version'], url


def download_and_install(extension_id, url):
    print(f'Downloading {url}')
    vsix = requests.get(url)

    with NamedTemporaryFile(suffix=f'-{extension_id}.vsix') as f:
        f.write(vsix.content)

        args = [VSCODE_EXECUTABLE, '--install-extension', f.name]
        output = run(args)
        output = output.replace(Path(f.name).name, extension_id)
        print(output)


def install(extension_id):
    latest_version, url = fetch_latest_version(extension_id)
    return download_and_install(extension_id, url)


def uninstall(extension_id):
    args = [VSCODE_EXECUTABLE, '--uninstall-extension', extension_id]
    print(run(args))


def update(extension_ids):
    current = current_versions()

    for extension_id in extension_ids or current.keys():
        try:
            current_version = current[extension_id]
        except KeyError:
            print(f"Extension '{extension_id}' is not installed.")
            return

        latest_version, url = fetch_latest_version(extension_id)

        if semver.compare(latest_version, current_version) == 1:
            download_and_install(extension_id, url)
            print(f"Extension '{extension_id}' was updated "
                  f'({current_version} -> {latest_version})')
        else:
            print(f"Extension '{extension_id}' is up to date "
                  f'({current_version})')


def list_installed(show_versions=False):
    if show_versions:
        print('\n'.join('@'.join(x) for x in current_versions().items()))
    else:
        print('\n'.join(current_versions().keys()))
