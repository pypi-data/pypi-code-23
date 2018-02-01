import logging
from collections import OrderedDict

import rethinkdb as R
import repool_forked

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


def migrate_to_v_0_8_anjilib_core(connection_pool: repool_forked.ConnectionPool, logger: logging.Logger) -> None:
    """
    Rename anjilib.core module to anji_core
    """
    with connection_pool.connect() as conn:
        table_list = R.table_list().run(conn)
        for table in table_list:
            logger.info('Processing table %s', table)
            data = R.table(table).has_fields('__python_info').filter(lambda doc: doc['__python_info']['module_name'].match('anjilib\.core.*')).get_field('id').run(conn)
            counter = 0
            for record_id in data:
                counter += 1
                python_info = R.table(table).get(record_id).get_field('__python_info').run(conn)
                R.table(table).get(record_id).update({'__python_info': {'module_name': python_info['module_name'].replace('anjilib.core', 'anji_core')}}).run(conn)
            if counter:
                logger.info('Updated %d records', counter)
            else:
                logger.info('Nothing to update')


def migrate_to_v_0_8_anjilib_rest(connection_pool: repool_forked.ConnectionPool, logger: logging.Logger) -> None:
    """
    Rename anjilib.submodule module to anji_core.submodule
    """
    with connection_pool.connect() as conn:
        table_list = R.table_list().run(conn)
        for table in table_list:
            logger.info('Processing table %s', table)
            data = R.table(table).has_fields('__python_info').filter(lambda doc: doc['__python_info']['module_name'].match('anjilib.*')).get_field('id').run(conn)
            counter = 0
            for record_id in data:
                counter += 1
                python_info = R.table(table).get(record_id).get_field('__python_info').run(conn)
                R.table(table).get(record_id).update({'__python_info': {'module_name': python_info['module_name'].replace('anjilib', 'anji_core')}}).run(conn)
            if counter:
                logger.info('Updated %d records', counter)
            else:
                logger.info('Nothing to update')


def migrate_to_v_0_8_anjilib_addons(connection_pool: repool_forked.ConnectionPool, logger: logging.Logger) -> None:
    """
    Rename anji_core.addons module to anji_common_addons
    """
    with connection_pool.connect() as conn:
        table_list = R.table_list().run(conn)
        for table in table_list:
            logger.info('Processing table %s', table)
            data = R.table(table).has_fields('__python_info').filter(lambda doc: doc['__python_info']['module_name'].match('anji_core.addons.*')).get_field('id').run(conn)
            counter = 0
            for record_id in data:
                counter += 1
                python_info = R.table(table).get(record_id).get_field('__python_info').run(conn)
                R.table(table).get(record_id).update({'__python_info': {'module_name': python_info['module_name'].replace('anji_core.addons', 'anji_common_addons')}}).run(conn)
            if counter:
                logger.info('Updated %d records', counter)
            else:
                logger.info('Nothing to update')


def migrate_to_v_0_8_anji_core_services(connection_pool: repool_forked.ConnectionPool, logger: logging.Logger) -> None:
    """
    Rename service modules
    """
    with connection_pool.connect() as conn:
        logger.info('Update docker services')
        logger.info(
            R.table('services').filter(
                R.row['_python_info']['module_name'] == 'anji_core.services.docker'
            ).replace(
                lambda doc: doc.merge(dict(_python_info=dict(module_name='anji_core.services.docker_service')))
            ).run(conn)
        )
        logger.info('Update systemd services')
        logger.info(
            R.table('services').filter(
                R.row['_python_info']['module_name'] == 'anji_core.services.systemd'
            ).replace(
                lambda doc: doc.merge(dict(_python_info=dict(module_name='anji_core.services.systemd_service')))
            ).run(conn)
        )


MIGRATION_ORDER = OrderedDict(**{
    'v0.8': [
        migrate_to_v_0_8_anjilib_core, migrate_to_v_0_8_anjilib_rest,
        migrate_to_v_0_8_anjilib_addons, migrate_to_v_0_8_anji_core_services
    ]
})
