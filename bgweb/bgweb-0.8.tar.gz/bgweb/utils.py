import json
import logging
import os
from datetime import datetime
from cherrypy.lib.static import serve_file


def copy_file(input_file, output_file):
    """
    Make a copy of a file into another

    Args:
        input_file:
        output_file:

    """
    with open(output_file, 'wb') as fd:
        size = 0
        while True:
            # The size is limited to avoid issues while reading large
            # files.
            data = input_file.file.read(8192)
            if not data:
                break
            size += len(data)
            fd.write(data)


def errors_to_json(**kwargs):
    return json.dumps({
        'error_code': int(kwargs['status'].split()[0]),
        'message':kwargs['message']
    })


def download(file_path, download_name=None):

    if not os.path.exists(file_path):
        logging.getLogger(__name__).warning('Non existing download path %s' % file_path)
        raise FileNotFoundError

    if download_name is None:
        download_name = "{}_{}".format(datetime.now().strftime('%Y-%m-%d'), os.path.basename(file_path))

    if file_path.endswith("png"):
        ct = "image/png"
        disp = "attachment; filename=\"{}\";".format(download_name)
    elif file_path.endswith("tsv") or file_path.endswith("txt"):
        ct = "text/tab-separated-values"
        disp = "attachment; filename=\"{}\";".format(download_name)
    elif file_path.endswith("html"):
        ct = "text/html"
        disp = None
    elif file_path.endswith("zip"):
        ct = "application/zip"
        disp = "attachment; filename=\"{}\";".format(download_name)
    else:
        ct = None
        disp = None

    return serve_file(file_path, ct, disp)

