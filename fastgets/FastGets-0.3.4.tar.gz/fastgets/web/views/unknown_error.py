# coding: utf8
import json
import uuid
import random

from flask import Blueprint, jsonify, request, redirect, abort
from fastgets.core.errors import ApiError
from fastgets.utils import datetime2utc
from fastgets.models import UnknownError


unknown_error_blueprint = Blueprint('unknown_error', __name__, url_prefix='/unknown_error')


@unknown_error_blueprint.route('/list')
def unknown_error_list_view():

    errors = UnknownError.objects.order_by('-create_at').limit(100)

    errors = [
        error.to_api_json()
        for error in errors
    ]

    return jsonify(dict(
        errors=errors
    ))


@unknown_error_blueprint.route('/flushall')
def unknown_error_flushall_view():
    UnknownError.drop_collection()
    return jsonify()
