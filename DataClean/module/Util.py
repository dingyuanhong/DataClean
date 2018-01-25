import os
import hashlib

def isAString(obj):
    return isinstance(obj,basestring)

ROOT_PATH='.';

def setRootPath(path =None):
    if path == None:
        return;
    ROOT_PATH = path;

def rootPath():
    return ROOT_PATH;

def tempPath(file = None):
    path = rootPath() + '/temp/'
    if isAString(file):
        path = path + file

    dirname, basename = os.path.split(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return path

def dataPath(file = None):
    path = rootPath() + '/data/'
    if isAString(file):
        path = path + file

    dirname, basename = os.path.split(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return path

def cachePath():
    path= rootPath() + "/cache/"
    dirname, basename = os.path.split(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return path

def FileMd5(filename):
    if not os.path.isfile(filename):
        return None;
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def writeContent(line, path):
    fd = os.open(path, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    os.write(fd, str(line))
    os.close(fd)

def writeBinary(line,path):
    fd = open(path,'wb')
    fd.write(line)
    fd.close()

def printModule(module):
    for property in module.__dict__:
        print property + ':', getattr(module,property);
    