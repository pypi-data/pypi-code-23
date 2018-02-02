# coding: utf-8
import boto3
import click

from . import utils


def rm(cluster_name):
    client = boto3.client('ec2')
    cluster_name = utils.match_cluster_name(cluster_name)
    styled_name = click.style(cluster_name, bold=True)
    request_id = utils.get_request_id(cluster_name)
    res = client.cancel_spot_fleet_requests(SpotFleetRequestIds=[ request_id ], TerminateInstances=True)
    for output in res['UnsuccessfulFleetRequests']:
        utils.warn('Error cancelling fleet request {}.'.format(output['SpotFleetRequestId']))
    if not any(res['UnsuccessfulFleetRequests']):
        utils.info('Deleted cluster with name {}.'.format(styled_name))
        utils.delete_cluster_information(cluster_name)
