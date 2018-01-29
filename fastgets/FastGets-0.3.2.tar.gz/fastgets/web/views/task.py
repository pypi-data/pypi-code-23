# coding: utf8

from flask import Blueprint, jsonify, request, make_response, render_template_string
from fastgets.pool import ProcessErrorPool

task_blueprint = Blueprint('task', __name__, url_prefix='/task')


@task_blueprint.route('/page_raw')
def task_page_raw_view():

    task_id = request.args.get('task_id')
    instance_id = request.args.get('instance_id')

    tasks = ProcessErrorPool.get_tasks(instance_id)
    task = None
    for _task in tasks:
        if _task.id == task_id:
            task = _task

    return render_template_string(task.page_raw)
