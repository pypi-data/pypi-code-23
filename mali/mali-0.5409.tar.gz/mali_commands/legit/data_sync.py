# -*- coding: utf8 -*-
import collections
import importlib
import json
import logging
try:
    import cPickle as pickle
except ImportError:
    import pickle
import random
import string
import tempfile
from contextlib import closing
import sys
import os
from uuid import uuid4
import datetime
import requests
from six import wraps

from .api import default_api_retry
from .config import Config
from .data_volume import with_repo
from .json_utils import multi_line_json_from_data, normalize_item, dict_normalize
from . import MetadataOperationError
from .multi_process_control import get_multi_process_control
from .path_utils import get_batch_of_files_from_paths, safe_make_dirs, DestPathEnum, enumerate_paths_with_info
from .print_status import PrintStatus
from .eprint import eprint


def wrap_exceptions(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AssertionError:
            raise
        except Exception as ex:
            eprint('\n' + str(ex))
            sys.exit(1)

    return decorated


epoch = datetime.datetime.utcfromtimestamp(0)


class InvalidJsonFile(Exception):
    def __init__(self, filename):
        self.filename = filename


def _download_entity(config_init_dict, volume_id, metadata):
    return DataSync.download_entity(config_init_dict, volume_id, metadata)


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def status_with_timing(message, callback):
    start_time = datetime.datetime.utcnow()
    status_line = PrintStatus()
    with closing(status_line):
        status_line.print_status(message)
        result = callback()
        total_time = datetime.datetime.utcnow() - start_time
        total_time = chop_microseconds(total_time)
        status_line.print_status('%s Done (%s)' % (message, total_time))

    return result


def disk_result(resume_token, method, result_callback=None):
    def wrap_f(f):
        def wrap(*args, **kwargs):
            import tempfile

            def loader():
                cache_result = pickle.load(cache_file)
                if result_callback is not None:
                    result_callback(cache_result)

                return cache_result

            name = '{func_name}_{python_version}'.format(func_name=method, python_version=sys.hexversion)
            full_path = os.path.join(tempfile.gettempdir(), 'ml_cache', resume_token, name)

            try:
                with open(full_path, 'rb') as cache_file:
                    return status_with_timing('Loading cache file', loader)
            except Exception as ex:
                logging.info('failed to load %s %s', full_path, ex)

            result = f(*args, **kwargs)

            full_path_tmp = full_path + '.tmp'
            try:
                safe_make_dirs(os.path.dirname(full_path_tmp))
                with open(full_path_tmp, 'wb') as cache_file:
                    pickle.dump(result, cache_file, pickle.HIGHEST_PROTOCOL)
                    os.rename(full_path_tmp, full_path)
            except Exception as ex:
                logging.info('failed to save %s %s', full_path_tmp, ex)

            return result

        return wrap

    return wrap_f


class DiskStorage(object):
    def __init__(self, dest_pattern, save_meta):
        self.__dest_pattern = dest_pattern
        self.__save_meta = save_meta

    def close(self):
        pass

    def add_item(self, metadata, data):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        safe_make_dirs(os.path.dirname(full_filename))

        if self.__save_meta:
            item_meta = {key: val for key, val in metadata.items() if not key.startswith('@')}
            with open(full_filename + '.metadata.json', 'w') as f:
                json.dump(item_meta, f)

        with open(full_filename, 'wb') as f:
            f.write(data)

    def has_item(self, metadata):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        return os.path.isfile(full_filename)

    @property
    def storage_params(self):
        return {
            'dest_pattern': self.__dest_pattern,
            'save_meta': self.__save_meta,
        }

    @classmethod
    def init_from_config(cls, dest_pattern, save_meta, **kwargs):
        return cls(dest_pattern, save_meta)


class DataSync(object):
    metadata_ext = '.metadata.json'
    resume_prefix = 'resume-'

    def __init__(self, ctx, repo, no_progressbar, resume_token=None):
        self.__ctx = ctx
        self.__repo = repo
        self.__no_progressbar = no_progressbar

        self.__resume_token = resume_token or self.generate_resume_token()

        if not self.__resume_token.startswith(self.resume_prefix):
            self.__resume_token = self.resume_prefix + self.__resume_token

    @property
    def repo(self):
        return self.__repo

    @property
    def resume_token(self):
        return self.__resume_token

    def __upload_file_for_processing(self, file_obj, file_description):
        from .gcs_utils import do_upload
        from tqdm import tqdm

        volume_id = self.__repo.data_volume_config.volume_id

        data_object_name = '%s/temp/%s_%s.json' % (volume_id, file_description, uuid4().hex)

        url = 'data_volumes/{volume_id}/gcs_urls'.format(volume_id=volume_id)

        headers = {'Content-Type': 'application/json'}

        msg = {
            'methods': 'PUT',
            'paths': [data_object_name],
            'content_type': 'application/json',
            'temp': True,
        }

        result = self.__ctx.obj.handle_api(self.__ctx.obj, requests.post, url, msg, retry=default_api_retry())

        put_url = result['put'][0]

        gcs_auth = self.__repo.data_volume_config.object_store_config.get('auth')

        def update_bar(c):
            bar.update(c)

        logging.debug('uploading %s', data_object_name)
        with tqdm(total=file_obj.tell(), desc="Uploading {}".format(file_description), unit=' KB', ncols=80,
                  disable=self.__no_progressbar, unit_scale=True) as bar:
            do_upload(gcs_auth, None, data_object_name, file_obj, headers, head_url=None, put_url=put_url,
                      callback=update_bar)

        return data_object_name

    def __process_index(self, object_name):
        index = self.__repo.open_index()

        change_set = status_with_timing('Server process index', lambda: index.get_changeset(data='gs://' + object_name))

        total_modify_files = 0
        total_new_files = 0

        files_to_upload = tempfile.TemporaryFile('w+')

        for name, op in change_set:
            if op == 'm':
                total_modify_files += 1
            elif op == 'i':
                total_new_files += 1
            else:
                continue

            data = name + '\n'

            files_to_upload.write(data)

        total_files_to_upload = total_modify_files + total_new_files
        files_to_upload.seek(0)

        return files_to_upload, total_files_to_upload

    def upload_and_update_index(self, index_entities_file):
        object_name = self.__upload_file_for_processing(index_entities_file, 'Index')

        files_to_upload, total_files_to_upload = self.__process_index(object_name)

        return files_to_upload, total_files_to_upload

    def upload_and_update_metadata(self, file_obj):
        object_name = self.__upload_file_for_processing(file_obj, 'Metadata')

        status_with_timing('Server process metadata', lambda: self.__repo.metadata.add_data(data='gs://' + object_name))

    @classmethod
    def __meta_companion_file_name(cls, metadata_file_name):
        return metadata_file_name[:-len(cls.metadata_ext)]

    def __get_metadata_info(self, rel_metadata_file_name):
        full_path_metadata = os.path.join(self.__repo.data_path, rel_metadata_file_name)

        rel_path_key = rel_metadata_file_name[:-len(self.metadata_ext)]

        with open(full_path_metadata) as metadata_file:
            try:
                data = json.load(metadata_file)
                for key, val in data.items():
                    if isinstance(val, (dict, list)):
                        data[key] = json.dumps(val)
            except ValueError:
                raise InvalidJsonFile(rel_metadata_file_name)

            return rel_path_key, data

    def __append_index_file(self, file_info, combined_index_files):
        file_name = file_info['path']

        mtime = file_info['mtime']
        ctime = file_info.get('ctime', mtime)

        mtime = (mtime - epoch).total_seconds()
        ctime = (ctime - epoch).total_seconds()

        if file_info['sys'] == 'local':
            rel_path = os.path.relpath(file_name, self.__repo.data_path)

            params = {
                'ctime': ctime,
                'mtime': mtime,
                'size': file_info['size'],
                'sha': file_info['sha'],
                'mode': 0,
            }
        else:  # file_info['sys'] == 's3':
            rel_path = file_name

            params = {
                'ctime': mtime,
                'mtime': ctime,
                'size': file_info['size'],
                'sha': file_info['sha'],
                'mode': 0,
            }

        multi_line_json_from_data({rel_path: params}, combined_index_files)

    def __load_all_metadata(self, data_files_info, metadata_files_list):
        from tqdm import tqdm

        files_metadata = {}
        for rel_file_name in tqdm(metadata_files_list, desc="Read metadata", unit=' files', ncols=80, disable=self.__no_progressbar):
            if self.__meta_companion_file_name(rel_file_name) in data_files_info:
                key, val = self.__get_metadata_info(rel_file_name)

                files_metadata[key] = val
            else:
                logging.debug("file %s doesn't have a data point file", rel_file_name)

        return files_metadata

    def __create_combined_index_and_metadata(self, data_path):
        import humanize
        status_line = PrintStatus()

        def on_result(result):
            data_files_info, metadata_files_list = result

            total_files_size = sum(x['size'] for x in data_files_info.values())

            status_line.print_status(
                'Total files {:,} ({}) (metadata found: {:,})', len(data_files_info),
                humanize.naturalsize(total_files_size), len(metadata_files_list))

        @disk_result(self.resume_token, '__create_combined_index_and_metadata', on_result)
        def with_disk_result():
            total_files = 0
            total_files_size = 0
            total_metadata = 0

            data_files_list = set()
            metadata_files_list = set()
            data_files_info = {}

            with closing(status_line):
                for file_info in enumerate_paths_with_info(data_path):
                    rel_file_name = self.repo.rel_path(file_info['path'])
                    total_files_size += file_info['size']

                    if rel_file_name.endswith(self.metadata_ext):
                        total_metadata += 1
                        metadata_files_list.add(rel_file_name)
                    else:
                        total_files += 1
                        data_files_list.add(rel_file_name)
                        data_files_info[rel_file_name] = file_info

                    status_line.print_status(
                        'Total files {:,} ({}) (metadata found: {:,})', total_files,
                        humanize.naturalsize(total_files_size), total_metadata)

            return data_files_info, metadata_files_list

        return with_disk_result()

    def create_combined_index_and_metadata(self, data_path):
        @disk_result(self.resume_token, 'create_combined_index_and_metadata')
        def with_disk_result():
            data_files_info, metadata_files_list = self.__create_combined_index_and_metadata(data_path)

            files_metadata = self.__load_all_metadata(data_files_info, metadata_files_list)

            return files_metadata, data_files_info

        return with_disk_result()

    @wrap_exceptions
    def upload_in_batches(self, files_info, total_files=None, callback=None):
        total_files = total_files or len(files_info)
        batch_size = max(min(total_files // 100, 250), 250)  # FIXME: hardcoded

        for files_info_batch in get_batch_of_files_from_paths(files_info, batch_size):
            self.__repo.stage(files_info_batch, callback=callback)

    @classmethod
    def download_entity(cls, config_init_dict, volume_id, metadata):
        config = Config(**config_init_dict)

        item_id = metadata['@id']

        def get_item_data():
            try:
                _, data = repo.object_store.get_raw(item_id)
                return data
            except requests.exceptions.HTTPError as ex:
                if ex.response.status_code == 404:
                    return

                raise

        def get_storage(storage_class):
            module_name, class_name = storage_class.rsplit('.', 1)
            m = importlib.import_module(module_name)
            return getattr(m, class_name)

        storage_config = config.items('storage')
        storage = get_storage(storage_config['class']).init_from_config(**storage_config)

        with with_repo(config, volume_id, read_only=True) as repo:
            with closing(storage):
                if storage.has_item(metadata):
                    return

                storage.add_item(metadata, get_item_data())

    def download_all(self, query, root_folder, dest_pattern, batch_size, processes, save_meta=True):
        multi_process_control = get_multi_process_control(processes)
        return self.__download_all(multi_process_control, query, root_folder, dest_pattern, batch_size, save_meta=save_meta)

    def __download_results(self, process_control, storage, results, callback=None):
        volume_id = self.__repo.data_volume_config.volume_id

        def wrap_callback_func(current_item):
            def wrapper(_):
                if callback is not None:
                    callback(current_item)

            return wrapper

        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__

        config_init_dict = self.__ctx.obj.config.init_dict
        storage_params = storage.storage_params
        storage_params['class'] = fullname(storage)
        config_init_dict['storage'] = storage_params

        for normalized_item in results:
            task_async = process_control.execute(
                _download_entity,
                args=(config_init_dict, volume_id, normalized_item),
                callback=wrap_callback_func(normalized_item))

            yield task_async, normalized_item

    class DownloadIterResults(collections.Iterator):
        def __init__(self, repo, query, batch_size):
            self.__query = query
            self.__batch_size = batch_size
            self.__repo = repo
            self.__query_index = 0
            self.__total_data_points = None

        def __get_next_results(self):
            current_results, current_total_data_points = self.__repo.metadata.query(
                self.__query, max_results=self.__batch_size, start_index=self.__query_index)

            return [normalize_item(metadata) for metadata in current_results], current_total_data_points

        def __len__(self):
            return self.__total_data_points

        def __next__(self):
            results, self.__total_data_points = self.__get_next_results()
            self.__query_index += len(results)

            if len(results) == 0:
                raise StopIteration()

            return results

        next = __next__

    def create_download_iter(self, query, batch_size):
        return self.DownloadIterResults(self.__repo, query, batch_size)

    def download_items(self, metadata_items, storage, multi_process_control):
        if len(metadata_items) == 0:
            return

        futures = []
        for async_result, normalized_item in self.__download_results(multi_process_control, storage, metadata_items):
            futures.append((async_result, normalized_item))

        for async_result, normalized_item in futures:
            async_result.wait()

    def __download_all(self, multi_process_control, query, root_folder, dest_pattern, batch_size, save_meta=True):
        from tqdm import tqdm

        def handle_item(item):
            file_name = DestPathEnum.get_full_path(dest_pattern, item)
            rel_path = os.path.relpath(file_name, root_folder)
            phase = item.get('phase', 'all')
            phase_meta.setdefault(phase, {})[rel_path] = item

            bar.update()

        download_iter = self.create_download_iter(query, batch_size)

        results = next(download_iter)
        phase_meta = {}

        storage = DiskStorage(dest_pattern, save_meta)

        with tqdm(total=len(download_iter), desc="Downloading", unit=' data point', ncols=80, disable=self.__no_progressbar) as bar:
            with closing(multi_process_control):
                try:
                    while True:
                        for _ in self.__download_results(multi_process_control, storage, results, handle_item):
                            pass  # no need to wait for the feature becouse the closing context above will wait for the entire pool

                        if len(results) != batch_size:
                            break

                        results = next(download_iter)
                except MetadataOperationError as ex:
                    eprint(str(ex))
                except KeyboardInterrupt:
                    multi_process_control.terminate()
                    multi_process_control.close()

        return phase_meta

    def save_metadata(self, root_dest, metadata):
        from tqdm import tqdm

        with tqdm(total=len(metadata), desc="saving metadata", unit=' files', ncols=80, disable=self.__no_progressbar) as bar:
            for key, val in metadata.items():
                if key is None:
                    key = 'unknown'

                json_metadata_file = os.path.join(root_dest, key + '.metadata.json')

                with open(json_metadata_file, 'w') as f:
                    json.dump(val, f)

                bar.update()

    def create_index_file_from_data(self, f, files_info):
        for val in files_info.values():
            self.__append_index_file(val, f)

    @classmethod
    def create_metadata_file_from_data(cls, f, metadata_files):
        dict_normalize(metadata_files)

        for rel_file_name, file_metadata in metadata_files.items():
            multi_line_json_from_data({rel_file_name: file_metadata}, f)

    def upload_index_and_metadata(self, data_path):
        def with_disk_result():
            metadata_files, files_info = self.create_combined_index_and_metadata(data_path)

            if len(files_info) == 0:
                return []

            if len(metadata_files) > 0:
                combined_meta_files = tempfile.TemporaryFile('wb+')
                self.create_metadata_file_from_data(combined_meta_files, metadata_files)
                self.upload_and_update_metadata(combined_meta_files)

            combined_index_files = tempfile.TemporaryFile('wb+')
            self.create_index_file_from_data(combined_index_files, files_info)
            files_to_upload, total_files_to_upload = self.upload_and_update_index(combined_index_files)

            def switch_to_full_path(params):
                rel_path = params['path']

                params['path'] = self.repo.full_path(rel_path)

                return params

            def enum_file_names():
                for file_name in files_to_upload:
                    file_name = file_name.strip()

                    yield file_name

            files_to_upload = [switch_to_full_path(files_info[rel_file_name]) for rel_file_name in enum_file_names()]

            return files_to_upload

        return with_disk_result()

    @classmethod
    def generate_resume_token(cls):
        size = 6
        chars = string.digits
        result = ''.join(random.choice(chars) for _ in range(size))

        return result
