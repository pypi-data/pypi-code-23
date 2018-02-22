from flask import jsonify, request
import NodeDefender
from NodeDefender.frontend.api import user_api

@user_api.route("/user/<email>", methods=["GET"])
def get_user(email):
    user = NodeDefender.db.user.get_sql(email)
    return jsonify(user.to_json()), 200

@user_api.route("/user/create", methods=["POST"])
def create_user():
    user = request.get_json()
    try:
        email = user['email']
    except KeyError:
        jsonify(user), 400
    try:
        firstname = user['firstname']
    except KeyError:
        firstname = None
    try:
        lastname = user['lastname']
    except KeyError:
        lastname = None

    NodeDefender.db.user.create(email, firstname, lastname)
    
    try:
        password = user['password']
        NodeDefender.db.user.set_password(email, password)
        NodeDefender.db.user.enable(email)
    except KeyError:
        pass
    
    try:
        group = user['group']
        NodeDefender.db.group.add_user(group, email)
    except KeyError:
        pass

    try:
        role = user['role']
        NodeDefender.db.user.set_role(email, role)
    except KeyError:
        pass

    return jsonify(user), 200
