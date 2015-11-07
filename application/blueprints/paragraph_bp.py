#-*- coding: UTF-8 -*- 

from flask import Blueprint, session, request, jsonify,render_template
from bson.objectid import ObjectId
from bson.json_util import loads, dumps

from ..models.message import Message
from ..models.paragraph import Paragraph
from ..models.story import Story
from ..models.user import User

from . import convert_id, is_login,get_current_user

paragraph_bp= Blueprint('paragraph_bp', __name__)

#点赞(已点赞则为取消点赞)
@paragraph_bp.route('/toggle', methods=['POST'])
def toggle():
    if not is_login():
        return jsonify({
                'status':401,
                'data':'user not log in'
            })
    paragraph_id = json.loads(request.data).get('paragraph_id')
    user_id = loads(get_current_user())['_id']
    #获得目标段落对象
    target_paragraph = Paragraph.get_paragraph(ObjectId(paragraph_id))
    if target_paragraph != 'null':
        target_paragraph = loads(target_paragraph)
        #获得段落所属故事对象
        target_story = loads(Story.get_story_by_id(target_paragraph['story_id']))
        #如果用户点赞过则取消点赞
        if user_id in target_paragraph['favour_users']:
            target_paragraph['favour_users'].remove(user_id)
            target_story['total_favours'] -= 1
            return_data = 'disfavour'
        #如果用户没点赞过则点赞
        else:
            target_paragraph['favour_users'].append(user_id)
            target_story['total_favours'] += 1
            return_data = 'favour'
        update_paragraph_result = Paragraph.update_paragraph(target_paragraph) 
        update_story_result = Story.update_story(target_story)
        #更新成功,返回200,失败返回403
        if update_paragraph_result == "" and update_story_result == "":
            return jsonify({
                    'status':200,
                    'data':return_data
                })
        else:
            return jsonify({
                    'status':403,
                    'data':update_paragraph_result+ " " +update_story_result
                })
    #目标段落不存在,返回403
    else:
        return jsonify({
                'status':403,
                'data':'invalid paragraph_id'
            })

#根据每页显示数量以及页数返回故事段落
@paragraph_bp.route('/story-paragraphs')
def story_paragraphs():
    story_id = request.args.get('story_id', '')
    offset = request.args.get('offset', '')
    amount = request.args.get('amount', '')

    if story_id == '' or offset == '' or amount == '':
        return jsonify({
                'status':403,
                'data':'unvalid params'
            })

    story = Story.get_story_by_id(ObjectId(story_id))
    #如果传入的story_id存在对应的story,则进行处理
    if story != 'null':
        story = loads(story)
        paragraphs = story['paragraph_ids']
        p_length = len(paragraphs)
        offset = (int(offset)-1)*int(amount)
        start = offset
        #如果页数的位移超出了段落数量,返回空
        if  p_length - start <= 0:
            return jsonify({
                    'status':200,
                    'data':''
                })
        else:
            #如果该页显示的数量大于段落数量,则设置结束位置为段落数
            if start + int(amount) < p_length:
                end = start + int(amount)
            else:
                end = p_length
        return_para_id = paragraphs[start:end]
        return_para = []
        #将选中的段落信息加入返回的段落列表中
        for p_id in return_para_id:
            p = loads(Paragraph.get_paragraph(p_id))
            author = loads(User.get_user(p['author_id']))
            del p['author_id']
            del p['story_id']
            del p['pictures']
            p['favour_users'] = len(p['favour_users'])
            p['author'] = {
                'id':str(author['_id']),
                'nickname':author['nickname'],
                'avatar':author['avatar']
            }
            return_para.append(convert_id(p))
        return jsonify({
                'status':200,
                'data':return_para
            })
    else:
        return jsonify({
                'status':403,
                'data':'unvalid story id'
            })

