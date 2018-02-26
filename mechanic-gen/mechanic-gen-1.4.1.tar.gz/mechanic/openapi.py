import os

import yaml
import flask

openapi_blueprint = flask.Blueprint('mechanic', __name__,
                                    template_folder='templates',
                                    static_folder='static',
                                    static_url_path='/static/mechanic')


@openapi_blueprint.route('/openapi')
def openapi():
    with open(os.path.abspath(os.path.curdir) + '/openapi.yaml') as f:
        contents = f.read()
        yaml_contents = yaml.load(contents)
    return flask.render_template('swagger-ui-index.html', title=yaml_contents.get('info', {}).get('title', 'Swagger UI'))


@openapi_blueprint.route('/openapi.yaml')
def openapi_docs():
    with open(os.path.abspath(os.path.curdir) + '/openapi.yaml') as f:
        contents = f.read()

    return flask.render_template_string(contents)
