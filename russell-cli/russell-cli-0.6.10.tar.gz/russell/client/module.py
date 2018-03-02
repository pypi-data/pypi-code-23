import json
import sys

from russell.client.base import RussellHttpClient
from russell.cli.utils import get_files_in_directory
from russell.exceptions import DuplicateException, NotFoundException
from russell.log import logger as russell_logger
from russell.model.module import Module


class ModuleClient(RussellHttpClient):
    """
    Client to interact with modules api

    files upload transfer to fs
    """
    def __init__(self):
        self.url = "/modules"
        super(ModuleClient, self).__init__()

    def create(self, module):
        # try:
        #     upload_files, total_file_size_fmt, total_file_size = get_files_in_directory(path='.', file_type='code')
        # except OSError:
        #     sys.exit("Directory contains too many files to upload. Add unused directories to .russellignore file."
        #              "Or download data directly from the internet into RussellHub")
        json_dict = module.to_dict()
        # russell_logger.info("Creating project run. Total upload size: {}".format(total_file_size_fmt))
        # russell_logger.debug("Creating module. Uploading: {} files".format(len(upload_files)))
        # russell_logger.info("Syncing code ...")
        try:
            response = self.request("PUT",
                                    url="/module",
                                    data=json.dumps(json_dict),
                                    # files=upload_files,
                                    timeout=3600)
        except NotFoundException:
            return False
        except DuplicateException:
            return False
        return response

    def delete(self, id):
        self.request("DELETE",
                     url="/module",
                     params={'id': id})
        return True

    def update_codehash(self, id, codehash):
        self.request("POST",
                     url="/module",
                     data=json.dumps({'id': id,
                                      'codehash': codehash}))
        return True

    def get(self, id):
        module_dict = self.request("GET",
                     url="/module",
                     params={'id': id})
        return Module.from_dict(module_dict)

    def get_by_entity_id_version(self, entity_id, version):
        module_dict = self.request("GET",
                                   url="/module",
                                   params={
                                       "entity_id": entity_id,
                                       "version": version,
                                   })
        return module_dict

    def get_by_codehash_entity_id(self, hash_code, entity_id):
        try:
            module_dict = self.request("GET",
                                       url="/module",
                                       params={
                                           "entity_id": entity_id,
                                           "codehash": hash_code,
                                       })
            return module_dict
        except NotFoundException:
            return None
