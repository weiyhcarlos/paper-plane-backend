#-*- coding: UTF-8 -*- 

from flask import Blueprint, session, request, jsonify,render_template
from bson.objectid import ObjectId
from bson.json_util import loads
from datetime import datetime
import json
import random

from ..models.message import Message
from ..models.paragraph import Paragraph
from ..models.story import Story
from ..models.user import User

from . import convert_id, is_login,get_current_user
plane_bp= Blueprint('plane_bp', __name__)

#如果story_id为空则为叠飞机，story_id如果不为空则判断content是否为空，
#不空则为完成续写飞机(title为空)，空的话就是扔回飞机
@plane_bp.route('/fly', methods = ['POST'])
def fly():
    if not is_login():
        return jsonify({
            'status':403,
            'data':'user not log in'
            })
    story_id = json.loads(request.data).get('story_id')
    title = json.loads(request.data).get('title')
    content = json.loads(request.data).get('content')
    fly_user = loads(get_current_user())
    user_id = fly_user['_id']
    #story_id为空,为叠飞机
    if story_id == '':
        #叠飞机内容为空,返回错误信息
        if content == '':
            return jsonify(
                {
                    'status':403,
                    'data':"empty content"
                })
        #创建新story对象
        story = Story(title).get_as_json()
        new_story_id = story['_id']
        #创建第一段段落对象
        first_paragraph = Paragraph(user_id, new_story_id, content).get_as_json()
        #将第一段段落id插入新story对象
        story['paragraph_ids'].append(first_paragraph['_id'])
        #插入story对象和paragraph对象
        if Story.insert_story(story) == "" and Paragraph.insert_paragraph(first_paragraph)=="":
            #叠飞机成功,增加经验值
            fly_user['experience_value'] += 3
            fly_user['degree'] = fly_user['experience_value'] /50
            User.update_user(fly_user)
            return jsonify({
                    'status':200,
                    'data':'success'
                })
        else:
            return jsonify({
                    'status':403,
                    'data':'fail to create a plane'
                })
    #story_id不为空,为续写飞机
    else:
        story = Story.get_story_by_id(ObjectId(story_id))
        if story == 'null':
            return jsonify({
                    'status':403,
                    'data':'invalid story id'
                })
        else:
            story = loads(story)
            story['status'] = 0
            story['current_owner'] = ""
            #内容为空,不增加新段落,扔回飞机
            if content == '':
                result = Story.update_story(story) 
                if result == '':
                    return jsonify({
                            'status':200,
                            'data':'success'
                        })
                else:
                    return jsonify({
                            'status':403,
                            'data':result
                        })
            #增加新段落
            new_paragraph = Paragraph(user_id, ObjectId(story_id), content).get_as_json()
            #将新段落Id插入故事
            story['paragraph_ids'].append(new_paragraph['_id'])
            #更新故事和插入段落
            if Story.update_story(story) == "" and Paragraph.insert_paragraph(new_paragraph) == "":
                #续写飞机成功增加经验值
                fly_user['experience_value'] += 5
                fly_user['degree'] = fly_user['experience_value'] /50
                User.update_user(fly_user)
                return jsonify({
                        'status':200,
                        'data':'success'
                    })
            else:
                return jsonify({
                        'status':403,
                        'data':'fail to continue a plane'
                    })

#返回热门飞机
@plane_bp.route('/hot')
def hot():
    amount = request.args.get('amount', '')
    offset = request.args.get('offset', '')
    if amount == '' or offset == '':
        return jsonify({
                'status':403,
                'data':'invalid parameters'
            })
    #将页数转为offset
    offset = (int(offset)-1)*int(amount)
    result = Story.get_story_by_fields(offset, int(amount))
    if result == 'null':
        return jsonify({
                'status':200,
                'data':''
            })
    else:
        #返回故事相应字段给前端
        result = loads(result)
        for r in result:
            del r['paragraph_ids']
            del r['current_owner']
            del r['lock_time']
        return jsonify({
                'status':200,
                'data':convert_id(result)
            })

#如果story_id为空,则为捡飞机,否则为续写飞机
@plane_bp.route("/occupy", methods = ['POST'])
def occupy():
    if not is_login():
        return jsonify({
                'status':401,
                'data':'user not log in'
            })
    story_id = json.loads(request.data).get('story_id')
    #story_id为空,随机返回一个未被占用的故事
    if story_id == "":
        result = Story.get_story_id_by_state(0)
        if result:
            #从列表中随机选取一个故事
            return_story_id = random.choice(loads(result))
            result_story = Story.get_story_by_id(return_story_id['_id'])
            if result_story == 'null':
                return jsonify({
                        'status':403,
                        'data':'not existing target story'
                    })
            else:
                result_story = loads(result_story)
                del result_story['paragraph_ids']
                del result_story['current_owner']
                return jsonify({
                    'status':200,
                    'data':convert_id(result_story)
                    })
        else:
            return jsonify({
                    'status':200,
                    'data':""
                })
    #story_id不为空,续写飞机,进行锁定
    else:
        story = Story.get_story_by_id(ObjectId(story_id))
        if story != 'null':
            story = loads(story)
            story['lock_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story['state'] = 1
            story['current_owner'] = loads(get_current_user())['_id']
            result = Story.update_story(story)
            if result == "":
                del story['current_owner']
                del story['paragraph_ids']
                return jsonify({
                        'status':200,
                        'data':convert_id(story)
                    })
            else:
                return jsonify({
                        'status':403,
                        'data':'update fail'
                    })
        else:
            return jsonify({
                    'status':403,
                    'data':'invalid story id'
                })


