
from pymongo import MongoClient
from pymongo import ReadPreference
from pymongo import ReturnDocument
from pymongo import write_concern

class MongoDB:
    def __init__(self,config):
        if config["options"].has_key('auth') and config["options"]["auth"] :
            client = MongoClient(host = config["member"]
            ,replicaset=config["options"]["replicaSet"]
            ,username=config["options"]["username"]
            ,password=config["options"]["password"]
            ,authSource=config["options"]["authSource"]
            );
        else:
            client = MongoClient(host = config["member"]
            ,replicaset=config["options"]["replicaSet"]
            );
        self.client = client;

    def close(self):
        self.client.close();
        self.client = None;
    
    def get(self,db,collection):
        db_ = self.client.get_database(db);
        collection_ = db_.get_collection(collection);
        return collection_;
    
    def getRead(self,db,collection):
        # ReadPreference.PRIMARY_PREFERRED;
        db_ = self.client.get_database(db,read_preference=ReadPreference.SECONDARY);
        collection_ = db_.get_collection(collection);
        return collection_;

    def getWrite(self,db,collection):
        db_ = self.client.get_database(db,write_concern=write_concern.WriteConcern());
        collection_ = db_.get_collection(collection);
        return collection_;
    
    def insert(self,db,collection,data):
        collection_ = self.getWrite(db,collection);
        result = collection_.insert_one(data);
        if result.acknowledged == True:
            return {"result":True,"id":result.inserted_id};
        else:
            return {"result":False,"id":result.inserted_id};
    
    def delete(self,db,collection,filter):
        collection_ = self.getWrite(db,collection);
        result = collection_.delete_many(filter);
        if result.deleted_count > 0:
            return {"result":True};
        else:
            return {"result":False};

    def update(self,db,collection,filter,update,option = None):
        upsert=False;
        array_filters=None;
        if(option != None):
            if option.has_key("upsert"):
                upsert=option["upsert"];
            if option.has_key("array_filters"):
                array_filters=option["array_filters"];
        collection_ = self.getWrite(db,collection);
        result = collection_.update_many(filter,update,upsert = upsert,array_filters = array_filters);
        if result.deleted_count > 0:
            return {"result":True};
        else:
            return {"result":False};

    def find(self,db,collection,filter={},option=None):
        collection_ = self.getRead(db,collection);
        result = collection_.find(filter);
        result.count();
        ret = [];
        for item in result:
            ret.append(item);
        result.close();
        return ret;

    def findAndModify(self,db,collection,filter,update,option=None):
        return self.update(filter,update,option);

    def count(self,db,collection,filter=''):
        collection_ = self.getRead(db,collection);
        result = collection_.count(filter);
        return result;