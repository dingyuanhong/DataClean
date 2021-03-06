#coding=utf-8

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

class SinaDefault(object):
    db = None;
    collection_ = None;
    collection = None;
    def __init__(self,name):
        self.db = MongoDB(db.Config.mongo());
        self.collection_ = self.db.get("dataclean",name);
        self.collection = Collection(self.collection_);
    
    def getDefault(self,param):
        params = {
            "__s":[],
            "callback":'var a='
        };
        params["__s"].append(param);
        params = Tool.urlEncode(params);
        return params;

    def getPage(self,url,params):
        result = UrlContent(url,params);
        if result["status_code"] != 200:
            return {"code":result["status_code"],"source":"UrlContent"};
        
        ret = self.process(result["content"]);
        
        # print ret;
        if not isinstance(ret,(list)):
            error = str(ret).decode("unicode-escape");
            print error;
            return {"code":ret["code"],"source":"sina"};
        ret = ret[0];
        if ret["code"] != 0:
            return {"code":ret["code"],"source":"sina"};

        ret = self.result(ret);
        return ret;
    def __compile(self,content):
        try:
            js = content;
            parser = execjs.compile(js);
            ret = parser._eval("a");
            return ret;
        # except:
        #     pass
        finally:
            pass;
        return False;
    def process(self,content):
        ret = self.__compile(content);
        if(ret != False):
            return ret;
        content = str(content).decode("unicode-escape");
        ret = self.__compile(content);
        if(ret != False):
            return ret;
        content = content.encode("unicode-escape").decode("string-escape");
        ret = self.__compile(content);
        if(ret != False):
            return ret;
        raise RuntimeError("解析失败");
    def result(self,value):
        other = {};
        for (k,v) in value.items():
            if(k not in ['count','fields','items','code']):
                other[k] = v;
                pass;
        fields = value["fields"];
        items = value["items"];
        for share in items:
            obj = {};
            l  = len(share);
            for i in range( 0,len(fields) ):
                if i < l:
                    obj[fields[i]] = share[i];
            obj.update(other);
            filter = {"code":obj['code']};
            r = self.collection.update(filter,{'$setOnInsert':obj},{'upsert':True});
            if r == False:
                raise IOError("update db error");
        count = len(value["items"]);
        value["fields"] = len(value["fields"]);
        value["items"] = count;
        value["total"] = int(value["count"]);
        value["count"] = count;
        return value;

class SinaAPI(SinaDefault):
    db = None;
    collection_ = None;
    collection = None;
    pagesize = 80;
    index = 'code';
    day = 'Add';
    def getParam(self,param,page,pagesize):
        pa = [];
        pa.extend(param);
        pa.append(0);
        pa.append(page);
        pa.append(pagesize);
        return super(SinaAPI,self).getDefault(pa);

    def getAllPage(self,url,param):
        page = 1;
        params = self.getParam(param,page,self.pagesize);
        ret = self.getPage(url,params);
        if ret['code'] != 0:
            return ret;
        result = ret;
        while True:
            if result['count'] >= ret['total']:
                break;
            page+=1;
            params = self.getParam(param,page,self.pagesize);
            ret = self.getPage(url,params);
            if ret['code'] != 0:
                return ret;
            result['count'] += ret['count'];
            print result;
        return result;

    def result(self,value):
        # print value;
        other = {};
        for (k,v) in value.items():
            if(k not in ['count','fields','items','code']):
                other[k] = v;
                pass;
        if(self.day != None):
            if not hasattr(other,'day'):
                other['day'] =  time.strftime("%Y-%m-%d", time.localtime());
        
        fields = value["fields"];
        items = value["items"];
        for share in items:
            obj = {};
            l  = len(share);
            for i in range( 0,len(fields) ):
                if i < l:
                    obj[fields[i]] = share[i];
            obj.update(other);
            # r = self.collection.insert(obj);
            if(self.day != None):
                if hasattr(obj,'ticktime'):
                    filter = {self.index:obj[self.index],'day':obj['day'],'ticktime':obj['ticktime']};
                else:
                    filter = {self.index:obj[self.index],'day':obj['day']};
            else:
                if hasattr(obj,'ticktime'):
                    filter = {self.index:obj[self.index],'ticktime':obj['ticktime']};
                else:
                    filter = {self.index:obj[self.index]};
            r = self.collection.update(filter,{'$setOnInsert':obj},{'upsert':True});
            if r == False:
                raise IOError("update db error");
        count = len(value["items"]);
        value["fields"] = len(value["fields"]);
        value["items"] = count;
        value["total"] = int(value["count"]);
        value["count"] = count;
        return value;


class SinaAPI2(SinaAPI):
    def getParam(self,param,page,pagesize):
        pa = [];
        pa.append(param[0]);
        pa.append(page);
        pa.append(pagesize);
        for i in range(1,len(param)):
            pa.append(param[i]);
        return super(SinaAPI,self).getDefault(pa);

url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/";

def lushen():
    #A股
    #__s=[[%22hq%22,%22hs_a%22,%22%22,0,2,40]]&callback=FDC_DC.theTableData
    #__s:[["hq","hs_a","",0,2,40]]

    param =  ['"hq"','"hs_a"','""'];
    sina = SinaAPI('a');
    print sina.getAllPage(url,param);

    #中小板
    #__s=[[%22hq%22,%22zxqy%22,%22%22,0,2,40]]&callback=FDC_DC.theTableData
    #__s:[["hq","zxqy","",0,2,40]]

    param =  ['"hq"','"zxqy"','""'];
    sina = SinaAPI('zxqy');
    print sina.getAllPage(url,param);

    #创业板
    #__s=[[%22hq%22,%22cyb%22,%22%22,0,2,40]]&callback=FDC_DC.theTableData
    #__s:[["hq","cyb","",0,2,40]]

    param =  ['"hq"','"cyb"','""'];
    sina = SinaAPI('cyb');
    print sina.getAllPage(url,param);

    #新浪行业板块
    #__s=[[%22bkshy%22,%22%22,0]]&callback=FDC_DC.theTableData
    #__s:[["bkshy","",0]]

    param =  ['"bkshy"','""',0]
    sina = SinaDefault('bkshy');
    param = sina.getDefault(param);
    print sina.getPage(url,param);

    #概念板块
    #__s=[[%22bknode%22,%22gainianbankuai%22,%22%22,0]]&callback=FDC_DC.theTableData
    #__s:[["bknode","gainianbankuai","",0]]

    param =  ['"bknode"','"gainianbankuai"','""',0];
    sina = SinaDefault('gainianbankuai');
    param = sina.getDefault(param);
    print sina.getPage(url,param);

    #地域板块
    #__s=[[%22bknode%22,%22diyu%22,%22%22,0]]&callback=FDC_DC.theTableData
    #__s:[["bknode","diyu","",0]]

    param =  ['"bknode"','"diyu"','""',0];
    sina = SinaDefault('diyu');
    param = sina.getDefault(param);
    print sina.getPage(url,param);

    #指数
    #__s=[[%22hq%22,%22dpzs%22,%22%22,0,1,40]]&callback=FDC_DC.theTableData
    #__s:[["hq","dpzs","",0,1,40]]

    param =  ['"hq"','"dpzs"','""'];
    sina = SinaAPI('dpzs');
    print sina.getAllPage(url,param);

    #上证指数
    #__s:[["jjhq",1,40,"",0,"zhishu_000001"]]

    param =  ['"jjhq"','""',0,'"zhishu_000001"'];
    sina = SinaAPI2('jjhq');
    print sina.getAllPage(url,param);

    #深证指数
    #__s=[[%22jjhq%22,1,40,%22%22,0,%22zhishu_399001%22]]&callback=FDC_DC.theTableData
    #__s:[["jjhq",1,40,"",0,"zhishu_399001"]]

    param =  ['"jjhq"','""',0,'"zhishu_399001"'];
    sina = SinaAPI2('zhishu_399001');
    print sina.getAllPage(url,param);

    #泸深指数
    #__s=[[%22jjhq%22,1,40,%22%22,0,%22hs300%22]]&callback=FDC_DC.theTableData
    #__s:[["jjhq",1,40,"",0,"hs300"]]

    param =  ['"jjhq"','""',0,'"hs300"'];
    sina = SinaAPI2('hs300');
    print sina.getAllPage(url,param);



def lugang():
    #泸港通
    #__s:[["hgtnode","hgt_hk","",0,2,40]]
    param =  ['"hgtnode"','"hgt_hk"','""'];
    sina = SinaAPI('hgt_hk');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #泸股通
    #__s:[["bkshy_node","hgt_sh","",0,1,40]]
    param =  ['"bkshy_node"','"hgt_sh"','""'];
    sina = SinaAPI('hgt_sh');
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

def honkon():
    #全部港股
    #__s:[["hk","qbgg_hk","",0,1,40]]
    param =  ['"hk"','"qbgg_hk"','""'];
    sina = SinaAPI('qbgg_hk');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);
    
    #蓝筹股
    #__s:[["hk","lcg_hk","",0,1,40]]
    param =  ['"hk"','"lcg_hk"','""'];
    sina = SinaAPI('lcg_hk');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #红筹股
    #__s:[["hk","hcg_hk","",0,1,40]]
    param =  ['"hk"','"hcg_hk"','""'];
    sina = SinaAPI('hcg_hk');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #国企股
    #__s:[["hk","gqg_hk","",0,1,40]]
    param =  ['"hk"','"gqg_hk"','""'];
    sina = SinaAPI('gqg_hk');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #创业板
    #__s:[["hk","cyb_hk","",0,1,40]]
    param =  ['"hk"','"cyb_hk"','""'];
    sina = SinaAPI('cyb_hk');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #指数
    # __s:[["hk","zs_hk","",0,1,40]]
    param =  ['"hk"','"zs_hk"','""'];
    sina = SinaAPI('zs_hk');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

def mei():
    #美股
    #__s:[["us_c",0,"","",0,1,40]]
    param =  ['"us_c"', 0,'""','""'];
    sina = SinaAPI('us_c');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #知名美股

    #中国概念股
    #__s:[["us_z",0,"","",0,1,40]]
    param =  ['"us_z"', 0,'""','""'];
    sina = SinaAPI('us_z');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #道琼斯
    #__s:[["us_cf",3,"","",0,1,40]]
    param =  ['"us_cf"', 3,'""','""'];
    sina = SinaAPI('us_cf_3');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #纳斯达克
    #__s:[["us_cf",1,"","",0,1,40]]
    param =  ['"us_cf"', 1,'""','""'];
    sina = SinaAPI('us_cf_1');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

    #标普500
    #__s:[["us_cf",2,"","",0,1,40]]
    param =  ['"us_cf"', 2,'""','""'];
    sina = SinaAPI('us_cf_2');
    sina.day = None;
    sina.index = 'symbol';
    print sina.getAllPage(url,param);

lushen();
# mei();