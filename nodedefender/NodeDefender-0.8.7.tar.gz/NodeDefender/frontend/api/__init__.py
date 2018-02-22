import NodeDefender
from flask import Blueprint, make_response, jsonify

api_view = Blueprint("api_view", __name__)
user_api = Blueprint("user_api", __name__)

def load_api(app):
    global api
    NodeDefender.app.register_blueprint(api_view, url_prefix="/api/v1")
    NodeDefender.app.register_blueprint(user_api, url_prefix="/api/v1")
    return True

import NodeDefender.frontend.api.config
import NodeDefender.frontend.api.user
