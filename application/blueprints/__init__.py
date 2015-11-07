from flask import Blueprint, session, request, jsonify
from bson.json_util import loads,dumps

from ..models.user import User

def is_login():
    if 'phone' in session or 'token' in session:
        return True
    else:
        return False

def convert_id(data):
    if isinstance(data, list):
        for single_data in data:
            single_data['_id'] = str(single_data['_id'])
        return dumps(data)
    data['_id'] = str(data['_id'])
    return dumps(data)

def get_current_user():
    if 'phone' in session:
        return User.get_user_by_phone(session['phone'])
    elif 'token' in session:
        return User.get_user_by_token(session['token'])
