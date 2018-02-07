import logging.config

from amaascore.tools.csv_tools import csv_stream_to_objects
from amaasutils.logging_utils import DEFAULT_LOGGING
from amaascore.csv_upload.utils import process_normal, interface_direct_csvpath


class Uploader(object):

    @staticmethod
    def json_handler(orderedDict, params):
        Dict = dict(orderedDict)
        for key, var in params.items():
            Dict[key]=var
        data_class = Dict.get('amaasclass', None)
        Dict = process_normal(Dict)
        obj = globals()[data_class](**dict(Dict))
        return obj

    @staticmethod
    def upload(csvpath, asset_manager_id=None, client_id=None):
        """convert csv file rows to objects and insert;
           asset_manager_id and possibly client_id from the UI (login)"""
        interface = interface_direct_csvpath(csvpath)
        logging.config.dictConfig(DEFAULT_LOGGING)
        logger = logging.getLogger(__name__)
        if asset_manager_id is None:
            params = dict()
        elif client_id is None:
            params = {'asset_manager_id': asset_manager_id}
        else:
            params = {'asset_manager_id': asset_manager_id, 'client_id': client_id}
        with open(csvpath) as csvfile:
            objs = csv_stream_to_objects(stream=csvfile, json_handler=Uploader.json_handler, params=params)
        for obj in objs:
            interface.new(obj)
            logger.info('Creating this object and upload to database successfully')

    @staticmethod
    def download(csvpath, asset_manager_id, data_id_type, data_id_list):
        """retrieve the objs mainly for test purposes"""
        interface = interface_direct_csvpath(csvpath)
        logging.config.dictConfig(DEFAULT_LOGGING)
        logger = logging.getLogger(__name__)
        objs = []
        for data_id in data_id_list:
            Dict = dict()
            Dict[data_id_type] = data_id
            objs.append(interface.retrieve(asset_manager_id=asset_manager_id, **Dict))
        return objs
