from flask import jsonify, request
import NodeDefender
from NodeDefender.frontend.api import api_view

@api_view.route("/config/write", methods=["POST"])
def write_config():
    NodeDefender.config.general.write()
    NodeDefender.config.database.write()
    NodeDefender.config.redis.write()
    NodeDefender.config.mail.write()
    NodeDefender.config.logging.write()
    NodeDefender.config.celery.write()
    return "OK", 200

@api_view.route("/config/default", methods=["POST"])
def default_config():
    pass

@api_view.route("/config/general", methods=["GET", "POST"])
def config_general():
    if request.method == "POST":
        config = request.get_json()
        NodeDefender.config.general.set(**config)
        return jsonify(config), 200
    config = NodeDefender.config.general.config
    return jsonify(config), 200

@api_view.route("/config/database", methods=["GET", "POST"])
def config_database():
    if request.method == "POST":
        config = request.get_json()
        NodeDefender.config.database.set(**config)
        return jsonify(config), 200
    config = NodeDefender.config.database.config
    return jsonify(config), 200

@api_view.route("/config/cache", methods=["GET", "POST"])
def config_cache():
    if request.method == "POST":
        config = request.get_json()
        NodeDefender.config.redis.set(**config)
        return jsonify(config), 200
    config = NodeDefender.config.redis.config
    return jsonify(config), 200

@api_view.route("/config/mail", methods=["GET", "POST"])
def config_mail():
    if request.method == "POST":
        config = request.get_json()
        NodeDefender.config.mail.set(**config)
        return jsonify(config), 200
    config = NodeDefender.config.mail.config
    return jsonify(config), 200

@api_view.route("/config/logging", methods=["GET", "POST"])
def config_logging():
    if request.method == "POST":
        config = request.get_json()
        NodeDefender.config.logging.set(**config)
        return jsonify(config), 200
    config = NodeDefender.config.logging.config
    return jsonify(config), 200

@api_view.route("/config/celery", methods=["GET", "POST"])
def config_celery():
    if request.method == "POST":
        config = request.get_json()
        NodeDefender.config.celery.set(**config)
        return jsonify(config), 200
    config = NodeDefender.config.celery.config
    return jsonify(config), 200

