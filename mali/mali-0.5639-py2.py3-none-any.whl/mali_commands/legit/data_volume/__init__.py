# -*- coding: utf8 -*-
import os
import errno
import requests
from contextlib import closing

from ..eprint import eprint
from ..dulwich.errors import NotGitRepository
from ..data_volume_config import DataVolumeConfig
from ..path_utils import expend_and_validate_path
from .repo import MlRepo


def default_data_volume_path(volume_id):
    return os.path.join(os.path.expanduser('~'), '.MissingLinkAI', 'data_volumes', str(volume_id))


def update_config_file(volume_id, params):
    path = default_data_volume_path(volume_id)

    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    config = DataVolumeConfig(path)

    config.update_and_save(params)

    return config


def create_data_volume(volume_id, data_path, linked, display_name, description, **kwargs):
    params = {
        'general': {
            'id': volume_id,
            'embedded': not linked,
            'datapath': data_path,
            'display_name': display_name,
            'description': description
        }
    }

    params.update(**kwargs)
    return update_config_file(volume_id, params)


def map_volume(ctx, volume_id, data_path):
    result = ctx.obj.handle_api(ctx.obj, requests.get, "data_volumes/{volume_id}".format(volume_id=volume_id))

    if data_path is not None:
        data_path = expend_and_validate_path(data_path)

    bucket_name = result.get('bucket_name')

    params = {}
    if bucket_name is not None:
        params['object_store'] = {'bucket_name': bucket_name}

    config = create_data_volume(
        result['id'],
        data_path,
        not result['embedded'],
        result.get('display_name'),
        result.get('description'),
        **params)

    if bucket_name is None:
        config.remove_option('object_store', 'bucket_name')
        config.save()

    return config


def repo_dynamic(ctx, volume_id, data_path=None):
    repo_root = default_data_volume_path(volume_id)

    config = ctx.obj.config

    try:
        repo = MlRepo(config, repo_root)
        if data_path is not None:
            repo.data_path = data_path

        return repo
    except NotGitRepository:
        data_volume_config = map_volume(ctx, volume_id, data_path)
        return MlRepo(
            config, repo_root, read_only=True, require_path=False, data_volume_config=data_volume_config)


def with_repo_dynamic(ctx, volume_id, data_path=None):
    return closing(repo_dynamic(ctx, volume_id, data_path))


def create_repo(config, repo_root, read_only=False, require_map=True):
    return MlRepo(config, repo_root, read_only=read_only, require_path=require_map)


def with_repo(config, volume_id, read_only=False, require_map=True):
    repo_root = default_data_volume_path(volume_id)

    try:
        return closing(create_repo(config, repo_root, read_only=read_only, require_map=require_map))
    except NotGitRepository:
        msg = 'Data volume {0} was not mapped on this machine, you should call "mali data map {0} --dataPath [root path of data]" in order to work with the volume locally'.format(volume_id)
        eprint(msg, err=True)
        exit(1)
