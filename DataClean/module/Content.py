import requests
import re
from UserAgent import getUserAgent as UserAgent
from Util import *;

Charsets = [
["gb2312","gbk"],
["gbk","gbk"],
["utf","utf"],
["big5","unicode"],
["unicode","unicode"],
];

def Charset(name):
    name = name.lower()
    for item in Charsets:
        if name.find(item[0]) != -1:
            return item[1];
    return None;


# <meta charset="gb2312">
# <meta http-equiv="Content-Type" content="text/html;charset=utf-8">

def FindCharset(content):
    regs = [
        '(?:\<meta[\s]*?charset[ ="\']*?([\w_-]+)[ "\'/>]*?)',
        '(?:\<meta[\s]*?charset[ ="\']*?([\w_-]+)[ "\'\s/>]*?)',
        '(?:\<meta[\s\S]*charset[ \=\"\']*?([\w_-]+)[ "\'\s]*?)'
    ]
    for reg in regs:
        pattern = re.compile(reg);
        body = re.findall(pattern, str(content));
        # print body;
        if body.__len__() > 0:
            break;
    if body.__len__() == 0:
        return None;
    return Charset(body[0]);

def UrlContent(url,params=None,options=None):
    try:
        header = {"User-Agent":UserAgent()};
        if options == None:
            response=requests.get(url=url,headers=header,params=params);
        else :
            option = options;
            if hasattr(option,"header"):
                option["header"] = dict(option["header"].items + header.items);
            else:
                option["header"] = header;
            if  not hasattr(option,'proxy') and not hasattr(option,'timeout'):
                response=requests.get(url=url,headers=option["header"],params=params);
            elif not hasattr(option,'timeout'):
                response=requests.get(url=url,headers=option["header"],params=params,proxies = option["proxy"]);
            else:
                response=requests.get(url=url,headers=option["header"],params=params,proxies = option["proxy"],timeout = option["timeout"]);
    except Exception as e:
        return {'status_code':404,'url':url};
    if response.status_code != 200:
        return {'status_code':response.status_code,'url':url};
    result = {"status_code":response.status_code,'url':url,'content':response.content};
    charset = FindCharset(response.content);
    if charset != None:
        result['content'] = response.content.decode(charset);
    return result;

def CacheContent(url,file,params=None,options = None):
    result = GetContent(url,options)
    if result['status_code'] == 200 :
        writeBinary(result['content'],file);
        result['file'] = file;
    return result;

if __name__ == '__main__':
    result = UrlContent("https://www.baidu.com/",{'timeout':1});
    result = CacheContent("https://www.baidu.com/",dataPath("baidu.txt"),{'timeout':1});
    
