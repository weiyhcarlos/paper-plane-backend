#-*- coding: UTF-8 -*- 

from bson.objectid import ObjectId
from bson.json_util import dumps
from datetime import datetime
from pymongo.errors import *
# from pymongo import ASCENDING, DESCENDING

from . import db

class Story:
    # {
    #     id: 'xxx',
    #     title: 'xxx',
    #     create_time: 'xxx',
    #     total_favours: Number,
    #     total_collections: Number,
    #     paragraph_ids: ['xx', ...],
    #     state: Number,
    #     lock_time: 'xxx',
    #     current_owner: 'xxxuid'
    # }
    def __init__(self, title):
        self._id = ObjectId()
        self.title = title
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_favours = 0
        self.total_collections = 0
        self.paragraph_ids = []
        self.state = 0
        self.lock_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_owner =""

    #return the class as json
    def get_as_json(self):
        return self.__dict__

    #@params Paragraph class
    #@return success return "", else return reasons
    @staticmethod
    def insert_story(i_story):
        collection =  db['story']
        if i_story is not None:
            try:
                collection.insert_one(i_story)
                return ""
            except DuplicateKeyError as e:
                return "Insert fail due to duplicate key."
            except PyMongoError as e:
                return "Insert fail due to unkown reason."
        else:
            return "Insert fail due to unvalid parameter." 

    #@params story id
    #json type: dict
    @staticmethod
    def get_story_by_id(id):
        collection =  db['story']
        return dumps(collection.find_one({"_id":id})) 

    #@params current_owner
    #json type: list
    @staticmethod
    def get_story_by_current_owner(current_owner):
        collection =  db['story']
        return dumps(collection.find({"current_owner":current_owner})) 

    #@params offset limit sort_field
    #json type: list
    @staticmethod
    def get_story_by_fields(offset, limit, sort_field='total_favours'):
        collection =  db['story']
        #desc order by sort_field
        return dumps(collection.find().sort(sort_field, -1).skip(offset).limit(limit))

    #@params 
    #@json type: list
    @staticmethod
    def get_story_id_by_state(value):
        collection = db['story']
        return dumps(collection.find({'state':value}, {'_id':1}))

    #@params u_story
    #@return success return "", else return reasons
    @staticmethod
    def update_story(u_story):
        collection =  db['story']
        if u_story is not None:
            try:
                # m_json = u_story.get_as_json()
                result = collection.replace_one({'_id':u_story['_id']}, u_story)
                if result.modified_count == 0:
                    return "Update fail due to not existing id."
                else:
                    return ""
            except PyMongoError as e:
                return "Update fail due to unkown reason."
        else:
            return "Update fail due to unvalid parameter."