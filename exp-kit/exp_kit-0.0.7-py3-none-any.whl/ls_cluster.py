# coding: utf-8
from halo import Halo
from tabulate import tabulate
import click

from . import utils


def doc2entry(doc):
    return [ doc['name'], len(doc['instance_id_list']), doc['request_id'] ]

def ls_all():
    with Halo(text='Loading cluster information ...', spinner='dots'):
        clusters = utils.load_all_clusters()
    table = tabulate([ [ 'name', 'size', 'request-id' ] ] + list(map(doc2entry, clusters)))
    click.echo(table)

def ls(cluster_name, ip_only):
    cluster_name = utils.match_cluster_name(cluster_name)
    with (utils.null_context() if ip_only else Halo(text='Loading cluster information ...', spinner='dots')):
        instances = utils.load_cluster_instances(cluster_name)
        entries = [ [ i.public_ip_address, i.instance_type, i.state['Name'] ] for i in instances ]
    if ip_only:
        click.echo('\n'.join(e[0] for e in entries))
    else:
        table = tabulate( [ [ 'ip', 'type', 'status' ] ] + entries)
        click.echo(table)
