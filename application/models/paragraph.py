#-*- coding: UTF-8 -*- 

from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from datetime import datetime
from pymongo.errors import *

from . import db

class Paragraph:
    # {
    #     id: 'xxx',
    #     author_id: 'xx',
    #     story_id: 'xx'
    #     create_time: 'xxx',
    #     favour_users: ['xxxuid', ...],
    #     content: 'xxx',
    #     pictures: ['urlxxx', ...]
    # }


    def __init__(self, author_id, story_id, content):
        self._id = ObjectId()
        self.author_id = author_id
        self.story_id = story_id
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.favour_users = []
        self.content = content
        self.pictures = []
    
    #return the class as json
    def get_as_json(self):
        return self.__dict__

    #@params Paragraph class
    #@return success return "", else return reasons
    @staticmethod
    def insert_paragraph(i_paragraph):
        collection =  db['paragraph']
        if i_paragraph is not None:
            try:
                collection.insert_one(i_paragraph)
                return ""
            except DuplicateKeyError as e:
                return "Insert fail due to duplicate key."
            except PyMongoError as e:
                return "Insert fail due to unkown reason."
        else:
            return "Insert fail due to unvalid parameter." 

    #@params Paragraph id
    #json type: list or dict
    @staticmethod
    def get_paragraph(id = None):
        collection =  db['paragraph']
        if id is None:
            return dumps(collection.find({}))
        else:
            return dumps(collection.find_one({"_id":id}))

    #@params story_id
    #json type: list 
    @staticmethod
    def get_paragraph_by_story_id(story_id):
        collection =  db['paragraph']
        return dumps(collection.find({"story_id":story_id}))

    #@params offset limit sort_field
    #json type: list
    @staticmethod
    def get_paragraph_by_fields(offset, limit, sort_field='_id'):
        collection =  db['paragraph']
        #desc order by sort_field
        return dumps(collection.find().sort(sort_field, -1).skip(offset).limit(limit))

    #@params u_paragraph
    #@return success return "", else return reasons
    @staticmethod
    def update_paragraph(u_paragraph):
        collection =  db['paragraph']
        if u_paragraph is not None:
            try:
                # m_json = u_paragraph.get_as_json()
                result = collection.replace_one({'_id':u_paragraph['_id']}, u_paragraph)
                if result.modified_count == 0:
                    return "Update fail due to not existing id."
                else:
                    return ""
            except PyMongoError as e:
                return "Update fail due to unkown reason."
        else:
            return "Update fail due to unvalid parameter."