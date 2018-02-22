# -*- coding: utf8 -*-
import json
import logging
import os
import uuid
from traceback import format_exception_only
import six
import click
import requests
import yaml
from click import exceptions

from mali_commands.commons import output_result
from .utilities import source_tracking


@click.group('run', help='runs an experiment on a cluster. By defaults run on a local cluster ')
def run_commands():
    pass


def _load_recipe(r_path):
    if not os.path.isfile(r_path):
        return {}
    else:
        print('loading defaults from recipe: %s' % r_path)
        with open(r_path) as f:
            return yaml.safe_load(f)


DEFAULT_RECIPE_PATH = '.ml_recipe'


def _source_tracking_data(path_='.'):
    repo_obj = None
    src_data = {}
    try:
        repo_obj = source_tracking.get_repo(path_)
        src_data = _export_repo_state(repo_obj)
    # noinspection PyBroadException
    except Exception as ex:
        src_data['error'] = export_exception(ex)
    return src_data, repo_obj


def export_exception(ex):
    return ('\n'.join(format_exception_only(ex.__class__, ex))).strip()


def _export_repo_state(repo_obj):
    src_data = {}
    try:
        src_data['branch'] = repo_obj.branch.name
        src_data['remote'] = repo_obj.remote_url
        src_data['sha_local'] = repo_obj.head_sha
        src_data['sha_local_url'] = repo_obj.head_sha_url
        src_data['is_dirty'] = not repo_obj.is_clean
        if repo_obj.has_head:
            commit_data = repo_obj.export_commit(repo_obj.repo.head.commit)
        if commit_data is not None:
            src_data.update(commit_data)
    # noinspection PyBroadException
    except Exception as ex:
        src_data['error'] = export_exception(ex)

    return src_data


def get_tracking_repo(repo_obj):
    repo_path = os.path.join(repo_obj.repo.working_dir, '.ml_tracking_repo')
    if os.path.isfile(repo_path):
        with open(repo_path) as f:
            return f.read().strip()
    # TODO: ADD QUERY to track server
    # return "git@github.com:missinglinkai/sim-test-remote-run.git"
    return None


def _sync_working_dir_if_needed(repo_obj, invocation_id):
    try:
        tracking_repository_url = get_tracking_repo(repo_obj)
        if tracking_repository_url is None:
            return {'error': 'no tracking repository found.'}
        logging.info('There is repository tracking enabled. Tracking to repository: {}'.format(tracking_repository_url))
        source_tracking_repo = source_tracking.GitRepoSyncer.clone_tracking_repo(tracking_repository_url)
        commit_tag = source_tracking.GitRepoSyncer.merge_src_to_tracking_repository(repo_obj.repo, source_tracking_repo, br_tag=invocation_id)
        shadow_repo_obj = source_tracking.get_repo(repo=source_tracking_repo)
        cur_br = source_tracking_repo.active_branch
        source_tracking_repo.git.checkout(commit_tag)
        shadow_repo_obj.refresh()
        src_data = _export_repo_state(shadow_repo_obj)
        source_tracking_repo.git.checkout(cur_br)
        if 'error' not in src_data:
            logging.info('Tracking repository sync completed. This experiment source code is available here: {}'.format(src_data['sha_local_url']))
        else:
            logging.info('Tracking repository sync Failed. The Error was: {}'.format(src_data['error']))
        return src_data
    except Exception as ex:
        ex_txt = export_exception(ex)
        logging.error("Failed to init repository tracking. This experiment may not be tracked. Got: " + ex_txt)
        return {'error': ex_txt}


def parse_env_array_to_dict(env_array):
    if env_array is None:
        return {}
    res = {}
    for env_tuple in env_array:
        key, value = env_tuple.split('=')
        key = key.strip()
        value = value.strip()

        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
        res[key] = value
    return res


@run_commands.command('xp')
@click.pass_context
@click.option('--org', type=str, help='organization to use')
@click.option('--project', type=int if six.PY3 else long)
@click.option('--image', type=str, required=False, help='Docker image to use, defaults to keras 1.2.2 (gw000)')
@click.option('--git-repo', type=str, required=False, help='Git repository to pull the code from')
@click.option('--git-tag', type=str, required=False, help='Git branch/tag for the git repository. defaults to master. The cloned code will be available under `/code`')
@click.option('--source-dir', type=str, required=False, help='source directory for the experiment.')
@click.option('--command', type=str, required=False, help='command to execute')
@click.option('--gpu/--cpu', required=False, default=None, help='Use GPU for this instance. Your image will need to support this as well. Defaults to --cpu')
@click.option('--data-volume', type=str, required=False, help='data volume to clone data from')
@click.option('--data-query', type=str, required=False, help='query to execute on the data volume')
@click.option('--data-dest', type=str, required=False, help='destination folder and format for cloning data. If provided, must begin with /data')
@click.option('--data-iterator', type=bool, required=False, help='When set to True, data will not be cloned before the experiment and the quarry will be available for the SDK iterator')
@click.option('--recipe', '-r', type=str, required=False, help='recipe file. recipe file is yaml file with the `flag: value` that allows you to specify default values for all params for this function')
@click.option('--save-recipe', type=str, required=False, help='Saves a recipe for this call to the target file and quits. Note the default values are not encoded into the recipe')
@click.option('--env', multiple=True, required=False, help='Environment variables to pass for the invocation in key=value format. You can use this flag multiple times')
@click.option('--output-paths', multiple=True, required=False, help='Paths that will be exported to the Data management at the end of the invocation job. The paths will be available to the the running code under `/path_name` by defaults to `/output`')
def run_experiment(ctx, org, project, image, git_repo, git_tag, source_dir, command, gpu, data_volume, data_iterator, data_dest, data_query, recipe, save_recipe, env, output_paths):
    # try:

    input_data = {
        'org': org,
        'project': project,
        'image': image,
        'git_repo': git_repo,
        'git_tag': git_tag,
        'source_dir': source_dir,
        'command': command,
        'data_query': data_query,
        'data_volume': data_volume,
        'data_use_iterator': data_iterator,
        'data_dest_folder': data_dest,
        'gpu': gpu,
        'output_paths': output_paths,
        'env': parse_env_array_to_dict(env)
    }
    if data_dest is not None and not data_dest.startswith('/data'):
        raise click.BadOptionUsage('`--data_dest` must begin with /data')

    recipe_data = _load_recipe(recipe or DEFAULT_RECIPE_PATH)

    for k, v in recipe_data.items():
        if k in input_data and input_data[k] is None:
            input_data[k] = v

    # Apply Defauls
    input_data['gpu'] = False if input_data['gpu'] is None else input_data['gpu']
    input_data['data_use_iterator'] = False if input_data['data_use_iterator'] is None else input_data['data_use_iterator']

    if save_recipe is not None:
        with open(save_recipe, 'w') as f:
            save_data = {}
            for k, v in input_data.items():
                if v is not None:
                    save_data[k] = v
            yaml.safe_dump(save_data, f, default_flow_style=False)
            print('Configuration saved to ', save_recipe)
        return

    if input_data.get('image') is None and input_data.get('command') is None:
        raise exceptions.BadOptionUsage('No command nor image provided')

    # apply defaults:
    default_image = 'gw000/keras:1.2.2-cpu' if not input_data.get('gpu') else 'gw000/keras:1.2.2-gpu'
    input_data['image'] = input_data.get('image') or default_image

    exp_id = uuid.uuid4().hex
    if input_data['git_repo'] is None and input_data['git_tag'] is None:
        src_repo, x = _source_tracking_data(input_data['source_dir'])
        sync_res = _sync_working_dir_if_needed(x, exp_id)
        if 'error' in sync_res:
            logging.error(sync_res['error'])
        else:
            input_data['git_repo'] = sync_res['remote']
            input_data['git_tag'] = sync_res['branch']
    if input_data['git_repo'] is None and input_data['git_tag'] is None:  # still
        raise exceptions.BadOptionUsage('Failed to obtain git point to use fo the experiment. please provide --git-repo, or --source-dir if you have remote tracking enabled')
        # todo: find the current git path and get tracing path from the server if we don't have git point
        # todo better handling of ignoring
    org = input_data['org']
    project = input_data['project']
    recipe_keys = ['source-dir', 'org', 'project']
    for dep_key in recipe_keys:
        if dep_key in input_data:
            del (input_data[dep_key])
    print(input_data)
    input_data['env'] = json.dumps(input_data.get('env', {}))
    result = ctx.obj.handle_api(ctx.obj, requests.put, '{}/{}/invoke'.format(org, project), input_data)
    output_result(ctx, result, ['ok', 'invocation'])
