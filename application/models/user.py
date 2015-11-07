#-*- coding: UTF-8 -*- 

from bson.objectid import ObjectId
from bson.json_util import dumps
from datetime import datetime
from pymongo.errors import *

from . import db

class User:
    # {
    #     id: 'xxx',
    #     token: 'xxx',
    #     phone: 'xxx',
    #     password: 'xxx',
    #     nickname: 'xxx',
    #     avatar: 'urlxxx',
    #     degree: Number,
    #     experience_value: Number,
    #     focus_stories: [story_ids],
    #     focus_users: [user_ids]
    # }
    def __init__(self, phone,password,avatar, token=""):
        self._id = ObjectId()
        #self.token=""
        self.phone = phone
        self.password = password
        self.nickname = ""
        self.avatar =avatar
        self.degree = 0
        self.experience_value = 0
        self.focus_stories = []
        self.focus_users = []
        self.token = token

    #return the class as json
    def get_as_json(self):
        return self.__dict__

    #insert user
    @staticmethod
    def insert_user(i_user):
        collection =  db['user']
        if i_user is not None:
            try:
                collection.insert_one(i_user.get_as_json())
                return ""
            except DuplicateKeyError as e:
                return "Insert fail due to duplicate key."
            except PyMongoError as e:
                return "Insert fail due to unkown reason."
        else:
            return "Insert fail due to unvalid parameter."   

    #@params user id
    #json type: list or dict
    @staticmethod
    def get_user(id = None):
        collection =  db['user']
        if id is None:
            return dumps(collection.find({}))
        else:
            return dumps(collection.find_one({"_id":id}))

    #@params phone
    #json type: list
    @staticmethod
    def get_user_by_phone(phone):
        collection =  db['user']
        return dumps(collection.find_one({"phone":phone}))

    #@params token
    #json type: list
    @staticmethod
    def get_user_by_token(token):
        collection =  db['user']
        return dumps(collection.find_one({"token":token}))

    #@params u_user
    #@return success return "", else return reasons
    @staticmethod
    def update_user(u_user):
        collection =  db['user']
        if u_user is not None:
            try:
                # m_json = u_user.get_as_json()
                result = collection.replace_one({'_id':u_user['_id']}, u_user)
                if result.modified_count == 0:
                    return "Update fail due to not existing id."
                else:
                    return ""
            except PyMongoError as e:
                return "Update fail due to unkown reason."
        else:
            return "Update fail due to unvalid parameter."

    #@params user_id , story_id
    #@return success return "", else return reasons
    @staticmethod
    def add_focus_story(user_id, story_id):
        collection = db['user']
        try:
            result = collection.update_one({'_id':user_id}, {
                '$push': {
                    'focus_stories':story_id
                } 
                })
            if result.modified_count == 0:
                return "add focus to story fail due to not existing user id."
            else:
                return ""
        except PyMongoError as e:
            return "add focus to story fail due to unkown reason."

    #@params user_id , focus_user_id
    #@return success return "", else return reasons
    @staticmethod
    def add_focus_user(user_id, focus_user_id):
        collection = db['user']
        try:
            result = collection.update_one({'_id':user_id}, {
                '$push': {
                    'focus_users':focus_user_id
                } 
                })
            if result.modified_count == 0:
                return "add focus to story fail due to not existing user id."
            else:
                return ""
        except PyMongoError as e:
            return "add focus to story fail due to unkown reason."