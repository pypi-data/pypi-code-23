# -*- coding: utf-8 -*-

import os
import argparse
from jinja2 import Environment, FileSystemLoader, meta
import yaml
import json
from pathlib import Path


template_filename_pool = []


def main():
    args = parse_args()
    render_templates(**args)


def parse_args():
    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('--config', dest='config_filename', metavar='<config>',
                        type=str, required=True, help='the config filename')
    parser.add_argument('--templates-dir', metavar='templates_dir', type=str,
                        nargs='?', help='the templates dir path')
    parser.add_argument('--target-dir', metavar='target_dir', type=str,
                        nargs='?', help='the target dir')

    return vars(parser.parse_args())


def render_templates(config_filename=None, templates_dir=None, target_dir=None,
                     **kwargs):
    config_filename = os.path.realpath(config_filename)
    if not os.path.exists(config_filename):
        raise Exception("Config file \"{}\" does not exists".format(
            config_filename))

    # load all configs
    f = open(config_filename, 'r')
    config = yaml.load(f)
    f.close()

    variables = convert_config_variables(**config)
    # print(variables)

    if templates_dir and target_dir:
        templates_dir = os.path.realpath(templates_dir)
        target_dir = os.path.realpath(target_dir)

        render_one_task(templates_dir, target_dir, variables)
    elif templates_dir:
        raise Exception(
            "\"--target-dir\" is needed when using \"--templates-dir\"")
    elif target_dir:
        raise Exception(
            "\"--templates-dir\" is needed when using \"--target-dir\"")
    else:
        for task in config['tasks']:
            if 'templates_dir' not in task:
                raise Exception("\"templates_dir\" is needed")
            templates_dir = os.path.realpath(task['templates_dir'])

            if 'target_dir' not in task:
                raise Exception("\"target_dir\" is needed")
            target_dir = os.path.realpath(task['target_dir'])

            file_list = []
            if 'files' in task:
                if isinstance(task['files'], str):
                    file_list = [] if task['files'] == '*' else task['files']
                elif isinstance(task['files'], list):
                    file_list = task['files']

            render_one_task(templates_dir, target_dir, variables,
                            file_list=file_list)

    print('DONE')


def render_one_task(templates_dir, target_dir, variables, file_list=[]):
    global template_filename_pool

    filter_func = None
    extensions = None
    if isinstance(file_list, list):
        template_filename_pool = file_list
        filter_func = template_filter
    else:
        template_filename_pool = []
        extensions = file_list

    if not Path(templates_dir).is_dir():
        raise Exception("{} is not a valid directory.".format(templates_dir))
    target_dir_path = Path(target_dir)
    if target_dir_path.is_file():
        raise Exception("target_dir({}) cannot be a file. ".format(target_dir))
    if not target_dir_path.exists():
        target_dir_path.mkdir(parents=True)

    # prepare template env
    env = Environment(
        loader=FileSystemLoader([templates_dir])
    )

    # list all templates
    templates = env.list_templates(extensions=extensions,
                                   filter_func=filter_func)
    # print(templates)

    # for f in target_dir_path.iterdir():
    #     f.is_file() and f.unlink()

    for template_filename in templates:
        rendered = render_one_template(env, variables, template_filename)
        rendered = rendered.rstrip(" \t\n\r") + "\n"
        with open(os.path.join(target_dir, template_filename), "wb") as f:
            f.write(rendered.encode("utf-8"))
        print("{} rendered to {}.".format(
            Path(templates_dir).joinpath(template_filename),
            Path(target_dir).joinpath(template_filename)))


def render_one_template(env, variables, template_filename):
    # check variables
    template_source = env.loader.get_source(env, template_filename)
    parsed_content = env.parse(template_source)
    keys = meta.find_undeclared_variables(parsed_content)

    for v in keys:
        if v not in variables:
            raise Exception("\"{}\" is not defined".format(v))

    template = env.get_template(template_filename)
    return template.render(variables)


def convert_config_variables(**config):
    convert_variables = {}
    for k, v in config['variables'].items():
        if isinstance(v, dict):
            if 'type' in v:
                if (v['type'] == 'list' and
                        'vars' in v and
                        isinstance(v['vars'], list)):
                    seperator = ','
                    if 'seperator' in v:
                        seperator = v['seperator']
                    convert_variables[k] = seperator.join(v['vars'])
                if (v['type'] == 'json' and 'vars' in v):
                    convert_variables[k] = json.dumps(v['vars'])
        elif isinstance(v, list):
            jump_out = False
            for kk in range(0, len(v)):
                if not is_scalar(v[kk]):
                    jump_out = True
                    break
            if jump_out:
                continue
            convert_variables[k] = ','.join(v)
        elif isinstance(v, bool):
            convert_variables[k] = 'true' if v else 'false'
        elif is_scalar(v):
            convert_variables[k] = v
        elif v is None:
            convert_variables[k] = ''

    return convert_variables


def is_scalar(var):
    return isinstance(var, (str, int, float))


def template_filter(template_name):
    global template_filename_pool

    if not template_filename_pool:
        return True
    elif template_name in template_filename_pool:
        return True
    else:
        return False


if __name__ == "__main__":
    main()
