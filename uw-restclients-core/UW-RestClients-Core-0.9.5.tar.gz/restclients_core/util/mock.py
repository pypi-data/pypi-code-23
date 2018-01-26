import re
import os
from os.path import isfile, join, dirname
import json

from restclients_core.exceptions import DataFailureException

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote
from restclients_core.models import MockHTTP


def load_resource_from_path(resource_dir, service_name,
                            implementation_name,
                            url, headers):

    RESOURCE_ROOT = os.path.join(resource_dir,
                                 service_name,
                                 implementation_name)

    if url == "///":
        # Just a placeholder to put everything else in an else.
        # If there are things that need dynamic work, they'd go here
        pass
    else:
        orig_file_path = RESOURCE_ROOT + url
        handle = open_file(orig_file_path)
        header_handle = open_file(orig_file_path + ".http-headers")

        # attempt to open query permutations even on success
        # so that if there are multiple files we throw an exception
        if "?" in url:
            handle = attempt_open_query_permutations(url, orig_file_path,
                                                     False)

        if "?" in url:
            header_handle = attempt_open_query_permutations(url,
                                                            orig_file_path,
                                                            True)

        if handle is None and header_handle is None:
            return None

        if handle is not None:
            data = handle.read()
            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                pass

        response = MockHTTP()
        response.status = 200
        if handle is not None:
            response.data = data
        response.headers = {"X-Data-Source": service_name + " file mock data",
                            }

        if header_handle is not None:
            try:
                data = header_handle.read()
                data = data.decode('utf-8')
                file_values = json.loads(data)

                if "headers" in file_values:
                    response.headers.update(file_values['headers'])

                    if 'status' in file_values:
                        response.status = file_values['status']

                else:
                    response.headers.update(file_values)
            except UnicodeDecodeError:
                pass
            except IOError:
                pass

        return response


def convert_to_platform_safe(dir_file_name):
    """
    :param dir_file_name: a string to be processed
    :return: a string with all the reserved characters replaced
    """
    return re.sub('[\?|<>=:*,;+&"@$]', '_', dir_file_name)


def open_file(orig_file_path):
    """
    Taking in a file path, attempt to open mock data files with it.
    """
    unquoted = unquote(orig_file_path)
    paths = [
        convert_to_platform_safe(orig_file_path),
        "%s/index.html" % (convert_to_platform_safe(orig_file_path)),
        orig_file_path,
        "%s/index.html" % orig_file_path,
        convert_to_platform_safe(unquoted),
        "%s/index.html" % (convert_to_platform_safe(unquoted)),
        unquoted,
        "%s/index.html" % unquoted,
        ]

    file_path = None
    handle = None
    for path in paths:
        try:
            file_path = path
            handle = open(path, "rb")
            break
        except IOError as ex:
            pass

    return handle


def attempt_open_query_permutations(url, orig_file_path, is_header_file):
    """
    Attempt to open a given mock data file with different permutations of the
    query parameters
    """
    directory = dirname(convert_to_platform_safe(orig_file_path)) + "/"

    # get all filenames in directory
    try:
        filenames = [f for f in os.listdir(directory)
                     if isfile(join(directory, f))]
    except OSError:
        return

    # ensure that there are not extra parameters on any files
    if is_header_file:
        filenames = [f for f in filenames if ".http-headers" in f]
        filenames = [f for f in filenames if
                     _compare_file_name(orig_file_path + ".http-headers",
                                        directory,
                                        f)]
    else:
        filenames = [f for f in filenames if ".http-headers" not in f]
        filenames = [f for f in filenames if _compare_file_name(orig_file_path,
                                                                directory,
                                                                f)]

    url_parts = url.split("/")
    url_parts = url_parts[len(url_parts) - 1].split("?")

    base = url_parts[0]
    params = url_parts[1]

    params = params.split("&")

    # check to ensure that the base url matches
    filenames = [f for f in filenames if f.startswith(base)]

    params = [convert_to_platform_safe(unquote(p)) for p in params]

    # ensure that all parameters are there
    for param in params:
        filenames = [f for f in filenames if param in f]

    # if we only have one file, return it
    if len(filenames) == 1:
        path = join(directory, filenames[0])
        return open_file(path)

    # if there is more than one file, raise an exception
    if len(filenames) > 1:
        raise DataFailureException(url,
                                   "Multiple mock data files matched the " +
                                   "parameters provided!",
                                   404)


def _compare_file_name(orig_file_path, directory, filename):
    return (len(unquote(orig_file_path)) - len(unquote(directory)) ==
            len(unquote(filename)))
