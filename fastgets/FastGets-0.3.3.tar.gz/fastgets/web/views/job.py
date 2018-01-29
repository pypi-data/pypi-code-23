# coding: utf8
import json
import uuid
import random

from flask import Blueprint, jsonify, request, redirect, abort
from fastgets.core.errors import ApiError
from fastgets.template import Template
from fastgets.job import Job
from fastgets.process import Process


job_blueprint = Blueprint('job', __name__, url_prefix='/job')


@job_blueprint.route('/add')
def job_add_view():
    name = request.args.get('name')
    trigger = request.args.get('trigger')
    type = request.args.get('type')
    if type not in ['template', 'script']:
        raise ApiError('type is error')

    job = Job.get_by_name(name, type)
    if job:
        job.delete()

    Job.add(name, trigger, type)
    return jsonify()


@job_blueprint.route('/delete')
def job_delete_view():
    id = request.args.get('id')
    type = request.args.get('type')

    job = Job.get(id, type)
    if not job:
        raise ApiError('ID 不存在')

    job.delete()
    return jsonify()
