#coding:utf-8
import urllib
import requests
import re
from bs4 import BeautifulSoup

from module.mongo import MongoDB,Collection
from module import *
from module.Content import *
import db
from Tool import *

import execjs
import os
os.environ["NODE_PATH"] = os.getcwd()+"/../node_modules";

import time


class Yingke(object):
    db = None;
    collection_ = None;
    collection = None;
    def __init__(self,name):
        self.db = MongoDB(db.Config.mongo());
        self.collection_ = self.db.get("dataclean",name);
        self.collection = Collection(self.collection_);
        pass
    
    def getPage(self,url,params):
        result = UrlContent(url,params);
        if result["status_code"] != 200:
            return {"code":result["status_code"],"source":"UrlContent"};

        # print result['content'].encode('gbk','ignore')
        # print result['content'].encode('GB18030')
        ret = self.process(result["content"]);

        if not isinstance(ret,(list)):
            error = str(ret).decode("unicode-escape");
            print error;
            return {"code":ret["code"],"source":"yinke"};

        ret = self.result(ret);
        return ret;
    def process(self,content):
        # print content
        soup = BeautifulSoup(content,"lxml");
        wrap = soup.find_all("div",attrs={"class":"list_box"});
        list_ = [];
        for div in wrap:
            a = div.find('a');
            name = div.find('span',attrs={"class":"list_user_name"})

            item = {
                "href":a["href"],
                "image":a.img["src"],
                'attention':a.p.span.string,
                "name":name.string
            }
            list_.append(item);
        return list_;
    def result(self,value):
        for obj in value:
            filter = {"name":obj['name']};
            r = self.collection.update(filter,{'$setOnInsert':obj},{'upsert':True});
            if r == False:
                raise IOError("update db error");
        return value;

url = "http://www.inke.cn/hotlive_list.html";

a = Yingke("yinke");
print a.getPage(url,{"page":1});