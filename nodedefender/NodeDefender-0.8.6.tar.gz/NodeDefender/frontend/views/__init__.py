from flask_login import login_required, current_user
import NodeDefender
from itsdangerous import URLSafeSerializer
from flask import Blueprint, render_template
from flask_login import login_required

admin_view = Blueprint('admin_view', __name__, template_folder="templates/admin",
                      static_folder="templates/frontend/static")
auth_view = Blueprint('auth_view', __name__, template_folder="templates/auth",
                     static_folder="templates/frontend/static")
data_view = Blueprint('data_view', __name__, template_folder="templates/data",
                      static_folder="templates/frontend/static")
node_view = Blueprint('node_view', __name__, template_folder="templates",
                      static_folder="templates/frontend/static",
                      static_url_path="/")
user_view = Blueprint('user_view', __name__, template_folder="templates/user",
                      static_folder="templates/frontend/static")

def load_user(id):
    return NodeDefender.db.sql.UserModel.query.get(id)

def inject_user():      # Adds general data to base-template
    if current_user:
        # Return Message- inbox for user if authenticated
        return dict(current_user = current_user)
    else:
        # If not authenticated user get Guest- ID(That cant be used).
        return dict(current_user = None)

def inject_serializer():
    def serialize(name):
        return NodeDefender.serializer.dumps(name)
    def serialize_salted(name):
        return NodeDefender.serializer.dumps_salted(name)
    return dict(serialize = serialize, serialize_salted = serialize_salted)

def inject_deployed():
    return dict(deployed = NodeDefender.config.deployed)

def trim_string(string):
    return string.replace(" ", "")

@login_required
def index():
    return render_template('frontend/dashboard/index.html')

def load_views(app):
    NodeDefender.app.jinja_env.globals.update(trim=trim_string)
    NodeDefender.app.context_processor(inject_user)
    NodeDefender.app.context_processor(inject_serializer)
    NodeDefender.app.context_processor(inject_deployed)

    NodeDefender.app.add_url_rule('/', 'index',
                                   NodeDefender.frontend.views.index)
    
    NodeDefender.login_manager.user_loader(load_user)

    # Register Blueprints
    NodeDefender.app.register_blueprint(admin_view)
    NodeDefender.app.register_blueprint(auth_view)
    NodeDefender.app.register_blueprint(data_view)
    NodeDefender.app.register_blueprint(node_view)
    NodeDefender.app.register_blueprint(user_view)
    return True

import NodeDefender.frontend.views.admin
import NodeDefender.frontend.views.auth
import NodeDefender.frontend.views.data
import NodeDefender.frontend.views.nodes
import NodeDefender.frontend.views.user
