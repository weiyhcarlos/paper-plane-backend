#-*- coding: UTF-8 -*- 

from flask import Blueprint, session, request, jsonify,render_template
from bson.objectid import ObjectId
from bson.json_util import loads,dumps
import json

from ..models.user import User
from ..models.story import Story
from . import is_login, convert_id,get_current_user

user_bp= Blueprint('user_bp', __name__)

#用户登陆
@user_bp.route('/login', methods = ['POST'])
def login():
    user_phone = json.loads(request.data).get('phone')
    user_password = json.loads(request.data).get('password')
    user_token = json.loads(request.data).get('token')
    user_avatar = json.loads(request.data).get('avatar')
    #存在user_token字段,则使用user_token登陆
    if user_token != None:
        user = User.get_user_by_token(user_token)

        if user != 'null':
            session['token'] = user_token
            return jsonify({
                    'status':200,
                    'data':'success'
                })
        #如果该token用户未存在,则注册并登陆
        else:
            new_user = User("", "", user_avatar, user_token)
            if User.insert_user(new_user) == "":
                session['token'] = user_token
                return jsonify({
                        'status':200,
                        'data':'token register user success'
                    })
            return jsonify({
                    'status':403,
                    'data':'fail'
                })
    #使用手机以及密码登陆
    user = User.get_user_by_phone(user_phone)
    if user != 'null' and loads(user)['password']==user_password:
        session['phone'] = user_phone
        data = {
            'status':200,
            'data': 'success'
        }
        resp = jsonify(data)
    else:
        data = {
            'status':403,
            'data': 'fail'
        }
        resp = jsonify(data)
    return resp

#用户登出
@user_bp.route('/logout')
def logout():
    if is_login():
        session.pop('phone', None)
        session.pop('token', None)
        return jsonify( {
            'status':200,
            'data':'success'
        })
    else:
        return jsonify( {
            'status':401,
            'data':'user not log in'
        })


#用户注册
@user_bp.route('/register', methods = ['POST'])
def register():
    user_phone = json.loads(request.data)['phone']
    user_password = json.loads(request.data)['password']
    user_avatar = json.loads(request.data)['avatar']
    if User.get_user_by_phone(user_phone) != 'null':
        data = {
            'status':403,
            'data':'user exit!'
        }
        resp = jsonify(data)
    else:
        r_user = User(user_phone, user_password, user_avatar)
        result = User.insert_user(r_user) 
        if not result:
            data = {
                'status':200,
                'data':'success'
            }
            resp = jsonify(data)
        else:
            data = {
                'status':500,
                'data':'create user fail'
            }
            resp = jsonify(data)
    return resp

#收藏用户
@user_bp.route('/collect-user', methods = ['POST'])
def collect_user():
    if is_login():
        user = get_current_user()
        user_id = loads(user)['_id']
        collect_user_id = ObjectId(json.loads(request.data)['user_id'])
        result = User.add_focus_user(user_id, collect_user_id)
        if result == '':
           return jsonify( {
                'status':200,
                'data':'success'
            })
        else:
            return jsonify( {
                'status':403,
                'data':result
            })
    else:
        return jsonify( {
                'status':401,
                'data':'user not log in'
            })

#收藏飞机
@user_bp.route('/collect-plane', methods = ['POST'])
def collect_plane():
    if is_login():
        user = get_current_user()
        user_id = loads(user)['_id']
        collect_story_id = ObjectId(json.loads(request.data)['story_id'])
        story = Story.get_story_by_id(collect_story_id)
        if story == 'null':
            return jsonify({
                    'status':403,
                    'data':'invalid story id'
                })
        story = loads(story)
        story['total_collections'] += 1
        result = User.add_focus_story(user_id, collect_story_id)
        if result == '':
            result_story = Story.update_story(story)
            return jsonify( {
                'status':200,
                'data':'success'
            })
        else:
            return jsonify({
                'status':403,
                'data':result
            })
    else:
        return jsonify( {
                'status':401,
                'data':'user not log in'
            })

#显示收藏用户列表
@user_bp.route('/show-focus-users')
def show_foucs_users():
    if not is_login():
        return jsonify({
                'status':401,
                'data':'user not log in'
            })
    user = get_current_user()
    focus_users = loads(user)['focus_users']
    if not focus_users:
        return jsonify({
                'status':200,
                'data':""
            })
    else:
        return_users = []
        for single_user_id in focus_users:
            single_user = User.get_user(single_user_id)
            if single_user != 'null':
                single_user = loads(single_user)
                del single_user['focus_stories']
                del single_user['focus_users']
                del single_user['phone']
                del single_user['password']
                return_users.append(single_user)
        return jsonify({
                'status':200,
                'data':convert_id(return_users)
            })

#显示收藏故事列表
@user_bp.route('/show-focus-stories')
def show_foucs_stories():
    if not is_login():
        return jsonify({
                'status':401,
                'data':'user not log in'
            })
    user = get_current_user()
    focus_stories = loads(user)['focus_stories']
    if not focus_stories:
        return jsonify({
                'status':200,
                'data':""
            })
    else:
        return_stories = []
        for single_story_id in focus_stories:
            single_story = Story.get_story_by_id(single_story_id)
            if single_story != 'null':
                single_story = loads(single_story)
                del single_story['paragraph_ids']
                del single_story['current_owner']
                return_stories.append(single_story)
        return jsonify({
                'status':200,
                'data':convert_id(return_stories)
            })
