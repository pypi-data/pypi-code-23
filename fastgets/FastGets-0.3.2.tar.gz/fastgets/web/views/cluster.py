# coding: utf8
import json
import uuid
import random

from flask import Blueprint, jsonify, request, redirect, abort
from fastgets.core.errors import ApiError
from fastgets.job import Job
from fastgets.utils import datetime2utc
from fastgets.stats import ClusterStats


cluster_blueprint = Blueprint('cluster', __name__, url_prefix='/cluster')


@cluster_blueprint.route('/second_stats')
def cluster_second_stats_view():
    process_error_num_list = []
    crawl_error_num_list = []
    success_num_list = []
    time_list = []

    for i, (k, v) in enumerate(ClusterStats.get_recent_stats(num=60)):
        process_error_num_list.append(v.get('process_error') or 0)
        crawl_error_num_list.append(v.get('crawl_error') or 0)
        success_num_list.append(v.get('success') or 0)
        time_list.append('{}s'.format(-60+i))

    return jsonify(dict(
        process_error_num_list=process_error_num_list,
        crawl_error_num_list=crawl_error_num_list,
        success_num_list=success_num_list,
        time_list=time_list,
    ))


@cluster_blueprint.route('/current')
def cluster_current_view():
    server_num = ClusterStats.get_current_server_num()
    thread_num = ClusterStats.get_current_thread_num()
    success_num = ClusterStats.get_today_success_num()
    error_num = ClusterStats.get_today_error_num()
    return jsonify(dict(server_num=server_num, thread_num=thread_num, success_num=success_num, error_num=error_num))
