# coding: utf8
import json
import uuid
import random

from flask import Blueprint, jsonify, request, redirect, abort
from fastgets.core.errors import ApiError
from fastgets.template import Template
from fastgets.job import Job
from fastgets.process import Process


process_blueprint = Blueprint('process', __name__, url_prefix='/process')


@process_blueprint.route('/add')
def process_add_view():
    name = request.args.get('name')
    type = request.args.get('type')

    Process.add(name, type)
    return jsonify()


@process_blueprint.route('/kill')
def process_kill_view():
    id = request.args.get('id')
    process = Process.get(id)
    process.kill()
    return jsonify()


@process_blueprint.route('/list')
def process_list_view():
    process_list = Process.get_list('script')
    process_list = [
        process.to_api_json()
        for process in process_list
    ]
    return jsonify(dict(process_list=process_list))
