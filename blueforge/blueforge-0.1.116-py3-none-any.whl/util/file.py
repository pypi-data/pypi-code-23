import json
import logging
import os
import shutil
import zipfile

from blueforge import BLUEFORGE_ROOT

logger = logging.getLogger(__name__)


def check_and_create_directories(paths):
    """
        Check and create directories.

        If the directory is exist, It will remove it and create new folder.

        :type paths: Array of string or string
        :param paths: the location of directory
    """
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)


def delete_directories(paths):
    """
        Delete directories.

        If the directory is exist, It will delete it including files.

        :type paths: Array of string or string
        :param paths: the location of directory
    """
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)


def delete_files(paths):
    """
        Delete files.

        If the file is exist, It will delete it.

        :type paths: Array of string or string
        :param paths: the location of file
    """
    for path in paths:
        if os.path.exists(path):
            os.remove(path)


def write_file(file_path, data):
    """
        Write file.

        :type file_path: str
        :param file_path: Path of file to be saved

        :type data: Any
        :param data: Data
    """
    with open(file_path, 'wb') as file:
        file.write(data)


def move_file(originals, destination):
    """
        Move file from original path to destination path.

        :type originals: Array of str
        :param originals: The original path

        :type destination: str
        :param destination: The destination path
    """
    for original in originals:
        if os.path.exists(original):
            shutil.move(original, destination)


def uncompress_files(original, destination):
    """
        Move file from original path to destination path.

        :type original: str
        :param original: The location of zip file

        :type destination: str
        :param destination: The extract path
    """
    with zipfile.ZipFile(original) as zips:
        extract_path = os.path.join(destination)
        zips.extractall(extract_path)


def compress_files(original, destination):
    empty_dirs = []
    with zipfile.ZipFile(destination, 'w') as zips:
        for folder, subfolders, files in os.walk(original):
            empty_dirs.extend([os.path.relpath(os.path.join(folder, dirs), original) for dirs in subfolders if
                               not os.listdir(os.path.join(folder, dirs))])
            for file in files:
                zips.write(os.path.join(folder, file),
                           os.path.relpath(os.path.join(folder, file), original),
                           compress_type=zipfile.ZIP_DEFLATED)
        for dirs in empty_dirs:
            zif = zipfile.ZipInfo(dirs + "/")
            zips.writestr(zif, '')

    return destination


def exclude_extension(file_name):
    return os.path.splitext(file_name)[0]


def load_json_file(file_path):
    if not os.path.isfile(file_path):
        return

    with open(file_path, 'rb') as fp:
        payload = fp.read().decode('utf-8')
        logger.debug("Loading JSON file: " + file_path)
        return json.loads(payload)


def get_latest_api_json_file(service_name):
    full_path = os.path.join(BLUEFORGE_ROOT, os.path.join('data', service_name))
    list_of_service_version = os.listdir(full_path)

    # TODO: Swagger JSON도 파싱이 되도록한다
    # 서브디렉토리가 존재할 경우, 해당 디렉토리 중 최신의 json을 가져온다
    if len(list_of_service_version):
        path_latest_version = sorted(os.listdir(full_path))[-1]
        return load_json_file(os.path.join(os.path.join(full_path, path_latest_version), 'api.json'))
