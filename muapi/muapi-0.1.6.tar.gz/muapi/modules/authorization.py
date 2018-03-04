"""
Authorization module
"""
import json
from flask import request

from muapi import auth
from muapi.Module import Module
from muapi.Auth import AuthException
from muapi.user import User

AU = Module('authorization', __name__, url_prefix='/authorization', no_version=True)


@AU.route('', methods=['POST'])
def login():
    """
    Authorize user using their username and password
    @return user's document from the DB including config
    """
    user_data = request.get_json()

    if not user_data:
        raise AuthException("Missing user data")

    user = User(user_data['username'], password=user_data['password'])

    auth_user = auth.login(user)

    user = User.from_dict(auth_user)

    session_id = auth.store_session(user)

    return json.dumps({"session_id" : session_id, "user" : auth_user})


@AU.route('', methods=['DELETE'])
@auth.required()
def logout():
    """
    Logout a user by deleting its session from session manager
    """
    session_id = request.headers.get('Authorization', None)
    auth.delete(session_id)
    return json.dumps({"success": True})


@AU.route('', methods=['GET'])
@auth.required()
def check_session():
    """
    Checks validity of session using only required() decorator
    """
    return '{}'
