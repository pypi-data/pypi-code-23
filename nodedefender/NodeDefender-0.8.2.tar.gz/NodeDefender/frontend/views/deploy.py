from flask import request, redirect, url_for, render_template, flash, jsonify
from datetime import datetime
from NodeDefender.frontend.views import deploy_view
import NodeDefender

@deploy_view.route('/deploy', methods=['GET'])
def deploy():
    return render_template('frontend/deploy.html')


class GeneralConfig(Resource):
    def get(self):
        config = NodeDefender.config.general.config()
        return config
    def put(self, config):
        NodeDefender.config.general.set_config(**config)


