# coding: utf8

import json
from flask import Flask, request, jsonify
from fastgets.core import config_parse


def create_app():
    from fastgets import env
    app = Flask(
        __name__,
        static_url_path='',
        template_folder='{}fastgets/web/static'.format(env.FASTGETS_DIR)
    )

    from fastgets.web.views.cluster import cluster_blueprint
    from fastgets.web.views.unknown_error import unknown_error_blueprint
    from fastgets.web.views.instance import instance_blueprint
    from fastgets.web.views.job import job_blueprint
    from fastgets.web.views.process import process_blueprint
    from fastgets.web.views.script import script_blueprint
    from fastgets.web.views.task import task_blueprint
    from fastgets.web.views.template import template_blueprint
    from fastgets.web.views.index import index_blueprint

    app.register_blueprint(cluster_blueprint)
    app.register_blueprint(unknown_error_blueprint)
    app.register_blueprint(instance_blueprint)
    app.register_blueprint(job_blueprint)
    app.register_blueprint(process_blueprint)
    app.register_blueprint(script_blueprint)
    app.register_blueprint(task_blueprint)
    app.register_blueprint(template_blueprint)
    app.register_blueprint(index_blueprint)

    return app


def run():
    from fastgets import env
    env.mode = env.API
    config_parse()

    app = create_app()

    @app.before_request
    def before_request():
        request.start = int(request.args.get('start') or 0)
        request.limit = int(request.args.get('limit') or 20)

    @app.after_request
    def after_request(response):
        if request.path in ['/', '/task/page_raw'] or request.path.startswith('/dist'):
            return response
        elif response.status_code in [200, 304]:
            data = response.get_data()
            if isinstance(data, bytes):
                data = data.decode('utf8')

            dct = json.loads(data)
            if 'error_code' not in dct:
                dct['error_code'] = 0
            response = jsonify(dct)

        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST')

        return response

    app.run(env.WEB_CONFIG['host'], env.WEB_CONFIG['port'], debug=env.WEB_CONFIG.get('debug', False))


if __name__ == '__main__':
    run()

