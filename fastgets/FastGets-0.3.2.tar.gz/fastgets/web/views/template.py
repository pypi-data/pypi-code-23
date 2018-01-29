# coding: utf8
import json
import uuid
import random

from flask import Blueprint, jsonify, request, redirect, abort
from fastgets.core.errors import ApiError
from fastgets.template import Template
from fastgets.job import Job
from fastgets.process import Process


template_blueprint = Blueprint('template', __name__, url_prefix='/template')


@template_blueprint.route('/list')
def template_list_view():

    templates = Template.get_list()

    job_dict = {
        name: job.to_api_json()
        for name, job in Job.get_dict('template').items()
    }
    process_dict = {
        name: process.to_api_json()
        for name, process in Process.get_dict('template').items()
    }

    templates = [
        template.to_api_json(
            job=job_dict.get(template.name),
            process=process_dict.get(template.name)
        )
        for template in templates
    ]

    return jsonify(dict(templates=templates))
