import os
import hashlib

def isbasestring(obj):
    return isinstance(obj,basestring)

ROOT_PATH='.';

def setROOT(path =None):
    if path == None:
        return;
    ROOT_PATH = path;

def ROOT():
    return ROOT_PATH;

def __makedir(path):
    dirname, basename = os.path.split(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return path

def TEMP(file = None):
    path = ROOT() + '/temp/'
    if isbasestring(file):
        path = path + file
    return __makedir(path);

def DATA(file = None):
    path = ROOT() + '/data/'
    if isbasestring(file):
        path = path + file
    return __makedir(path);

def CACHE(file = None):
    path= ROOT() + "/cache/"
    if isbasestring(file):
        path = path + file
    return __makedir(path);

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
    