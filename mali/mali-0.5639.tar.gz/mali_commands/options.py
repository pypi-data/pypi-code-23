# -*- coding: utf8 -*-
import json

import requests
import click
import click.types
from .legit.context import init_context


class DataVolumeIdParamType(click.types.IntParamType):
    def complete(self, ctx, incomplete):
        if ctx.obj is None:
            init_context(ctx)

        projects = ctx.obj.handle_api(ctx.obj, requests.get, 'data_volumes')

        result = []
        for project in projects.get('volumes', []):
            project_id = str(project['id'])

            display_name = project.get('display_name')

            org = project.get('org') or 'me'

            display_name += ' @' + org

            result.append((project_id, display_name))

        return result


class ProjectIdParamType(click.types.IntParamType):
    def complete(self, ctx, incomplete):
        if ctx.obj is None:
            init_context(ctx)

        projects = ctx.obj.handle_api(ctx.obj, requests.get, 'projects')

        result = []
        for project in projects.get('projects', []):
            project_id = str(project['project_id'])

            display_name = project.get('display_name')

            org = project.get('org') or 'me'

            display_name += ' @' + org

            result.append((project_id, display_name))

        return result


def processes_option():
    def decorator(f):
        return click.option('--processes', default=-1, type=int, required=False)(f)

    return decorator


def no_progressbar_option():
    def decorator(f):
        return click.option('--no_progressbar/--enable_progressbar', default=False, is_flag=True, required=False)(f)

    return decorator


def data_volume_id_argument():
    def decorator(f):
        return click.argument(
            'volumeId', type=DataVolumeIdParamType(), envvar='VOLUMEID')(f)

    return decorator


def alert_type_option(required=False, multiple=False):
    all_options = ['started', 'stopped', 'ended', 'failed', 'dataWarning']

    def validate_alert_type(ctx, option, value):
        value = list(value)

        for alert_type in value:
            if alert_type == 'all':
                value.extend(all_options)

        value = [v for v in value if v in all_options]

        return list(set(value))

    def decorator(f):
        return click.option(
            '--alertType', '-a', callback=validate_alert_type, type=click.Choice(['all'] + all_options), required=required, multiple=multiple,
            help='Alert type for project subscription')(f)

    return decorator


def project_id_option(required=False, multiple=False):
    def decorator(f):
        return click.option(
            '--projectId', '-p', type=ProjectIdParamType(), required=required, multiple=multiple,
            help='The project Id. Use `mali projects list` to find your project Ids')(f)

    return decorator


def experiment_id_option(required=False):
    def decorator(f):
        return click.option(
            '--experimentId', '-e', type=int, metavar='<int>', required=required,
            help='The experiment ID. Use `mali experiments list` to find your experiment IDs')(f)

    return decorator


def chart_scope_option(required=False):
    def decorator(f):
        return click.option(
            '--chartScope', '-cs', type=click.Choice(['test', 'validation', 'train']), required=required,
            default='test', help='Scope type.')(f)

    return decorator


def chart_type_option(required=False):
    def decorator(f):
        return click.option(
            '--chartType', '-ct', type=click.Choice(['line']), required=required,
            default='line', help='Graph type.')(f)

    return decorator


def chart_name_option(required=False):
    def decorator(f):
        return click.option(
            '--chartName', '-c', metavar='<str>', required=required,
            help='The name of the chart. The name is used in order to identify the chart against different '
                 'experiments and through the same experiment.')(f)

    return decorator


def chart_x_option(required=False):
    def decorator(f):
        return click.option(
            '--chartX', '-cx', metavar='<json_string>', required=required,
            help='Array of m data points (X axis), Can be Strings, Integers or Floats.')(f)

    return decorator


def chart_y_option(required=False):
    def decorator(f):
        return click.option(
            '--chartY', '-cy', metavar='<json_string>', required=required,
            help='Array/Matrix of m data values. Can be either array m of Integers/Floats or a matrix (m arrays having n Ints/Floats each),  a full matrix describing the values of every chart in every data point')(f)

    return decorator


def chart_y_name_option(required=False):
    def decorator(f):
        return click.option(
            '--chartYName', '-cyn', metavar='<json_str>', required=required, default='Y',
            help='Display name for chart(s) Y axis')(f)

    return decorator


def chart_x_name_option(required=False):
    def decorator(f):
        return click.option(
            '--chartXName', '-cxn', metavar='<str>', required=required, default='X',
            help='Display name for charts X axis')(f)

    return decorator


def metrics_option(required=False):
    def decorator(f):
        return click.option(
            '--metrics', '-m', metavar='<json_string>', required=required,
            help='The metrics of the experiment as a jsonified string. The key should be the metric '
                 'name with "ex" prefix e.g. "ex_cost". The value is the metric value in String, Float, '
                 'Integer or Boolean.')(f)

    return decorator


def model_weights_hash_option(required=False):
    def decorator(f):
        return click.option(
            '--weightsHash', '-wh', metavar='<sha1_hex>', required=required,
            help="The hexadecimal sha1 hash of the model's weights")(f)

    return decorator


def validate_json(ctx, param, value):
    try:
        if value is None:
            return None

        return json.loads(value)
    except ValueError:
        raise click.BadParameter('not valid json', param=param, ctx=ctx)
