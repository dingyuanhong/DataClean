#coding=utf-8
import os
import time
import hashlib
import Util

def ChechCacheFileExpress(file,express):
    if not os.path.exists(file):
        return None;
    if int(express) == 0:
        return None;
    #print file
    if (os.path.isfile(file)):
        if int(express) < 0:
            return file;
        #创建时间
        # os.path.getctime(file)
        #修改时间
        mtime = os.path.getmtime(file)
        ticks = time.time()
        # mtime = time.ctime(mtime)
        # print mtime
        #过期
        if int(mtime) + int(express) > int(ticks):
            return file
    else:
        os.remove(file);
    return None

def ReadCacheFile(file):
    data=None
    if not os.path.exists(file):
        return data;
    file_object = open(file, 'rb')
    try:
        data = file_object.read()
    finally:
        file_object.close()
    return data

def WriteCacheFile(file,content):
    with open(file, "wb") as code:
        code.write(content)
        code.close()
        return;
    if os.path.exists(file):
        os.remove(file);

def GetCahceFile(md5):
    return str(CACHE(str(md5) + ".cache"));

def GetCacheName(url):
    md5string = hashlib.md5(str(url).encode('utf-8')).hexdigest()
    return md5string;

def GetCacheFile(url):
    md5string = GetCacheName(url);
    return GetCahceFile(md5string);

def ChechCacheExpress(md5,express):
    file = GetCahceFile(md5);
    return ChechCacheFileExpress(file,express);