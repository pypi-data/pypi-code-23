# -*- coding: utf8 -*-
import os
import click
import requests
import sys

from mali_commands.legit.data_sync import DataSync, InvalidJsonFile
from mali_commands.legit.json_utils import multi_line_json_from_data, newline_json_file_from_json_file, \
    json_data_from_files, normalize_item
from mali_commands.legit import MetadataOperationError
from tqdm import tqdm
from mali_commands.commons import add_to_data_if_not_none, output_result
from mali_commands.legit.data_volume import create_data_volume, with_repo, default_data_volume_path, with_repo_dynamic, \
    map_volume
from mali_commands.options import data_volume_id_argument, no_progressbar_option, processes_option, validate_json
from mali_commands.legit.path_utils import expend_and_validate_path, safe_make_dirs, safe_rm_tree, \
    DestPathEnum, has_moniker, bucket_print_name, enumerate_paths_with_info


@click.group('data')
def data_commands():
    pass


def __expend_and_validate_path(path, expand_vars=True, validate_path=True, abs_path=True):
    try:
        return expend_and_validate_path(path, expand_vars, validate_path, abs_path)
    except IOError:
        click.echo('Folder not found %s' % path, err=True)
        sys.exit(1)


@data_commands.command('map')
@data_volume_id_argument()
@click.option('--dataPath', required=True)
@click.pass_context
def _cmd_add_data_path(ctx, volumeid, datapath):
    config = map_volume(ctx, volumeid, datapath)

    display_name = config.general_config.get('display_name', 'No display name provided')
    click.echo('Initialized data volume %s (%s)' % (config.volume_id, display_name))


@data_commands.command('create')
@click.option('--displayName', required=True)
@click.option('--description', required=False)
@click.option('--org', required=True)
@click.option('--dataPath', required=True)
@click.option('--bucket')
@click.pass_context
def _cmd_create_data_volume(ctx, displayname, description, org, datapath, bucket):
    data = {}

    if org == 'me':
        org = None

    linked = False

    add_to_data_if_not_none(data, displayname, "display_name")
    add_to_data_if_not_none(data, org, "org")
    add_to_data_if_not_none(data, description, "description")
    add_to_data_if_not_none(data, not linked, "embedded")

    expiration = ctx.obj.config.readonly_items('data_volumes').get('expiration')
    if expiration:
        data['expiration'] = expiration

    result = ctx.obj.handle_api(ctx.obj, requests.post, "data_volumes", data)

    data_volume_id = result['id']

    datapath = __expend_and_validate_path(datapath)

    params = {}
    if bucket is not None:
        params['object_store'] = {'bucket_name': bucket}

    create_data_volume(data_volume_id, datapath, linked, displayname, description, **params)

    output_result(ctx, result)


@data_commands.command('config')
@data_volume_id_argument()
@click.option('--edit', is_flag=True)
def edit_config_file(volumeid, edit):
    import subprocess

    path = os.path.join(default_data_volume_path(volumeid), 'config')

    if edit:
        subprocess.call(['edit', path])
        return

    with open(path) as f:
        click.echo(f.read())


@data_commands.command('commit')
@data_volume_id_argument()
@click.option('--message', '-m', required=False)
@click.pass_context
def commit_data_volume(ctx, volumeid, message):
    with with_repo(ctx.obj.config, volumeid) as repo:
        result = repo.commit(message)

        if 'commit_id' not in result:
            click.echo('no changeset detected', err=True)
            sys.exit(1)

        output_result(ctx, result)


def process_moniker_data_path(data_path):
    from six.moves.urllib.parse import urlparse, urlunparse

    if not has_moniker(data_path):
        return data_path

    parts = urlparse(data_path)

    return urlunparse((parts.scheme, parts.netloc, '', '', '', ''))


def __print_transfer_info(repo):
    bucket_name = repo.data_volume_config.object_store_config.get('bucket_name')

    if bucket_name:
        click.echo('transfer files from %s to %s' % (bucket_print_name(repo.data_path), bucket_print_name(bucket_name)))
    else:
        click.echo('transfer files from %s to MissingLink secure bucket' % (bucket_print_name(repo.data_path),))


@data_commands.command('sync')
@data_volume_id_argument()
@click.option('--dataPath', required=True)
@click.option('--commit', required=False)
@processes_option()
@no_progressbar_option()
@click.option('--resume', required=False)
@click.pass_context
def sync_to_data_volume(ctx, volumeid, datapath, commit, processes, no_progressbar, resume):
    data_path = __expend_and_validate_path(datapath, expand_vars=False, validate_path=True)

    repo_data_path = process_moniker_data_path(data_path)

    with with_repo_dynamic(ctx, volumeid, repo_data_path) as repo:
        __repo_validate_data_path(repo, volumeid)

        data_sync = DataSync(ctx, repo, no_progressbar, resume)

        try:
            files_to_upload = data_sync.upload_index_and_metadata(data_path)
        except InvalidJsonFile as ex:
            click.echo('Invalid json file %s' % ex.filename, err=True)
            sys.exit(1)

        total_files_to_upload = len(files_to_upload)

        if total_files_to_upload > 0:
            __print_transfer_info(repo)

            with tqdm(total=total_files_to_upload, desc='Syncing files', unit=' files', ncols=80, disable=no_progressbar) as bar:
                if processes != -1:
                    repo.data_volume_config.object_store_config['processes'] = processes

                data_sync.upload_in_batches(files_to_upload, callback=lambda _: bar.update())
        else:
            click.echo('No change detected, nothing to upload (metadata only change).')

        if commit is not None:
            repo.commit(commit)


@data_commands.command('add')
@data_volume_id_argument()
@click.option('--files', '-f', multiple=True)
@click.option('--commit', is_flag=True, required=False)
@processes_option()
@no_progressbar_option()
@click.pass_context
def add_to_data_volume(ctx, volumeid, files, commit, processes, no_progressbar):
    all_files = list(enumerate_paths_with_info(files))
    total_files = len(all_files)

    with tqdm(total=total_files, desc="Adding files", unit=' files', ncols=80, disable=no_progressbar) as bar:
        with with_repo(ctx.obj.config, volumeid) as repo:
            data_sync = DataSync(ctx, repo, no_progressbar)
            if processes != -1:
                repo.data_volume_config.object_store_config['processes'] = processes

            data_sync.upload_in_batches(all_files, total_files, callback=lambda x: bar.update())

            if commit:
                repo.commit(commit)


@data_commands.command('clone')
@data_volume_id_argument()
@click.option('--destFolder', '-d', required=True)
@click.option('--destFile', '-df')
@click.option('--query', '-q', required=False)
@click.option('--delete', is_flag=True, required=False)
@click.option('--batchSize', required=False, default=500)
@processes_option()
@no_progressbar_option()
@click.pass_context
def clone_data(ctx, volumeid, destfolder, destfile, query, delete, batchsize, processes, no_progressbar):
    if delete and (destfolder in ('.', './', '/', os.path.expanduser('~'), '~', '~/')):
        raise click.BadParameter("for protection --dest can't point into current directory while using delete")

    dest_folder = __expend_and_validate_path(destfolder, expand_vars=False, validate_path=False)

    root_dest = DestPathEnum.find_root(destfolder)
    dest_pattern = DestPathEnum.get_dest_path(dest_folder, destfile)

    if delete:
        safe_rm_tree(root_dest)

    safe_make_dirs(root_dest)

    with with_repo_dynamic(ctx, volumeid) as repo:
        data_sync = DataSync(ctx, repo, no_progressbar)
        phase_meta = data_sync.download_all(query, root_dest, dest_pattern, batchsize, processes)

        data_sync.save_metadata(root_dest, phase_meta)


@data_commands.group('metadata')
def metadata_commands():
    pass


def stats_from_json(now, json_data):
    return os.stat_result((
        0,  # mode
        0,  # inode
        0,  # device
        0,  # hard links
        0,  # owner uid
        0,  # gid
        len(json_data),  # size
        0,  # atime
        now,
        now,
    ))


@data_commands.command('query')
@data_volume_id_argument()
@click.option('--query', '-q')
@click.option('--batchSize', required=False, default=500)
@click.pass_context
def query_metadata(ctx, volumeid, query, batchsize):
    def get_all_results():
        def get_next_results():
            current_results, current_total_data_points = repo.metadata.query(
                query, max_results=batchsize, start_index=start_index)

            return list(current_results), current_total_data_points

        total_results = []

        start_index = 0

        results, total_data_points = get_next_results()
        while True:
            total_results.extend([normalize_item(item) for item in results])

            if len(results) != batchsize:
                break

            start_index += len(results)

            results, total_data_points = get_next_results()

        return total_results

    try:
        with with_repo_dynamic(ctx, volumeid) as repo:
            all_results = get_all_results()
    except MetadataOperationError as ex:
        click.echo(str(ex), err=True)
        sys.exit(1)

    output_result(ctx, all_results)


def chunks(l, n):
    result = []
    for item in l:
        result.append(item)

        if len(result) == n:
            yield result
            result = []

    if result:
        yield result


class File2(click.File):
    def convert(self, value, param, ctx):
        value = os.path.expanduser(value)

        return super(File2, self).convert(value, param, ctx)


def __repo_validate_data_path(repo, volume_id):
    if repo.data_path:
        return

    msg = 'Data volume {0} was not mapped on this machine, ' \
          'you should call "mali data map {0} --dataPath [root path of data]" ' \
          'in order to work with the volume locally'.format(volume_id)
    click.echo(msg, err=True)
    sys.exit(1)


@metadata_commands.command('add')
@data_volume_id_argument()
@click.option('--files', '-f', multiple=True)
@click.option('--data', '-d', required=False, callback=validate_json)
@click.option('--dataPoint', '-dp', multiple=True)
@click.option('--dataFile', '-df', required=False, type=File2())
@click.option('--property', '-p', required=False, type=(str, str), multiple=True)
@click.option('--propertyInt', '-pi', required=False, type=(str, int), multiple=True)
@click.option('--propertyFloat', '-pf', required=False, type=(str, float), multiple=True)
@click.option('--update/--replace', is_flag=True, default=True, required=False)
@no_progressbar_option()
@click.pass_context
def add_to_metadata(
        ctx, volumeid, files, data, datapoint, datafile, property, propertyint, propertyfloat, update, no_progressbar):

    def get_per_data_entry():
        data_per_entry = data or {}

        for props in (property, propertyint, propertyfloat):
            if not props:
                continue

            for prop_name, prop_val in props:
                data_per_entry[prop_name] = prop_val

        return data_per_entry

    def get_current_data_file():
        if datafile:
            return newline_json_file_from_json_file(datafile)

        entries = datapoint or []
        entries.extend(files or [])

        __repo_validate_data_path(repo, volumeid)

        data_list = json_data_from_files(repo.data_path, entries, get_per_data_entry())

        return multi_line_json_from_data(data_list)

    with with_repo_dynamic(ctx, volumeid) as repo:
        file_obj = get_current_data_file()
        data_sync = DataSync(ctx, repo, no_progressbar)
        data_sync.upload_and_update_metadata(file_obj)


@data_commands.command('list')
@click.pass_context
def list_data_volumes(ctx):
    projects = ctx.obj.handle_api(ctx.obj, requests.get, 'data_volumes')

    output_result(ctx, projects.get('volumes', []), ['id', 'display_name', 'description', 'org'])
