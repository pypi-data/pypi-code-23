import concurrent.futures
import logging
import os
import tempfile
import threading
import uuid

from flask import Flask, request
from flask_cors import CORS
from flask_jsonpify import jsonpify

from lib import DppRunner


app = Flask(__name__)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

runner = DppRunner()

def initialize_app(flask_app):
    CORS(flask_app)

    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    flask_app.logger.handlers.extend(gunicorn_error_logger.handlers)


@app.route('/', methods=['POST'])
def create_runner():
    data = request.get_data()
    kind = request.values.get('kind')

    def status_cb(pipeline_id, status):
        logging.info('STATUS for %s: %s', pipeline_id, status)

    uid = runner.start(kind, data, status_cb=status_cb)
    return jsonpify({'uid': uid})


@app.route('/', methods=['GET'])
def get_status():
    uid = request.values.get('uid')
    return jsonpify(runner.status(uid))


initialize_app(app)
logging.info('DPP-Server Running')

if __name__ == '__main__':
    app.run()