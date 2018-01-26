#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# print sys.getdefaultencoding()

import requests
import re
from bs4 import BeautifulSoup
import HTMLParser
import urllib
import execjs
import os
os.environ["NODE_PATH"] = os.getcwd()+"/../node_modules";

from module.Content import *
from module.mongo import MongoDB
from module import *

dbConfig = {
    "member":[
        "192.168.127.128:27017"
        ,"192.168.127.128:27018"
        ,"192.168.127.128:27019"
    ],
    "options":{
        "replicaSet":"testset"
    }
}
db = MongoDB(dbConfig);
sina = db.get("dataclean","sina");

def getWrapContent(url):
    result = UrlContent(url);
    if result["status_code"] == 200:
        soup = BeautifulSoup(result["content"],"lxml");
        wrap = soup.find_all("div",attrs={"class":"wrap"});
        wrap = soup.select("div.wrap");
        print str(wrap).decode('unicode_escape');

def getShares(id):
    url = "http://hq.sinajs.cn/?func=getData._hq_cron();&list=" + id;
    result = UrlContent(url);
    if result["status_code"] == 200:
        content = str(result["content"]).decode("gbk");
        content = content.encode('unicode-escape').decode('string-escape');
        js = "var getData = {'_hq_cron':function(){}};" + content;
        parser = execjs.compile(js);
        ret = parser._eval("hq_str_" + id);
        Util.writeBinary(ret.encode('gbk'),tempPath(id+".dat"));

def getValue(value):
    if isinstance(value, (bool)):
        return str(value);
    elif isinstance(value,(float)):
        return str(value);
    elif isinstance(value,(int)):
        return str(value);
    elif isinstance(value,(str)):
        return "" + str(value) + "";
    elif isinstance(value,(unicode)):
        return str(value);
    elif isinstance(value,(list)):
        result = "[";
        for a in value:
            if result != "[":
                result += ",";
            result += getValue(a);
        return  result + ']' ;
    elif isinstance(value,(dict)):
        result = "{";
        for a in value.__dict__:
            if hasattr(param,property):
                result += getValue(getattr(value,a));
            else:
                result += getValue(value[a]);
        return  result + '}' ;

def Escape(str):
    str = str.replace("'","%27");
    str = str.replace("\"","%22");
    str = str.replace(" ","%20");
    str = str.replace("=","%3D");
    return str;

def urlEncode(param):
    result = "";
    for property in param:
        if result != "":
            result += "&";
        if hasattr(param,property):
            value = getValue(getattr(param,property));
        else:
            value =  getValue(param[property]);
        value = Escape(value);
        result += property + "=" + value;
    return result;

def sharesIDS(page):
    url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/";
    # "__s=[[%22hq%22,%22hs_a%22,%22%22,0,1,40]]&callback=FDC_DC.theTableData";

    param = [];
    param.append('"hq"');
    param.append('"hs_a"');
    param.append('""');
    param.append(0);
    param.append(page);
    param.append(80);

    params = {
        "__s":[],
        "callback":'var a='
    };
    params["__s"].append(param);
    params = urlEncode(params);
    # print params;
    result = UrlContent(url,params);
    if result["status_code"] != 200:
        return {"code":result["status_code"],"src":"url"};
    content = str(result["content"]).decode("unicode-escape");
    # print content;
    content = content.encode("unicode-escape").decode("string-escape");
    js = content;
    parser = execjs.compile(js);
    ret = parser._eval("a");
    
    # print type(ret);
    if isinstance(ret,(list)):
        if ret[0]["code"] != 0:
            return {"code":ret[0]["code"],"src":"sina"};
    else:
        data = str(ret).decode("unicode-escape");
        print data;
        return {"code":ret["code"],"src":"sina"};

    fields = ret[0]["fields"];
    items = ret[0]["items"];
    for share in items:
        obj = {};
        for i in range( 0,len(fields) ):
            obj[fields[i]] = share[i];
        acknowledged = False
        if acknowledged != True:
            acknowledged = sina.insert_one(obj).acknowledged;
    
    count =  ret[0]["count"];
    if ((page-1) * 80 + len(items)) >= count:
        # print page;
        return count;
    page+=1;
    return sharesIDS(page);

print sharesIDS(1);

db.close();

if __name__ == '__main__':
    print('')
    
