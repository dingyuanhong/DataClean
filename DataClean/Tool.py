#coding=utf-8

class Tool:
    @staticmethod
    def __object(obj):
        if isinstance(obj,(str)):
            return  str(obj) ;
        elif isinstance(obj,(unicode)):
            return  str(obj) ;
        elif isinstance(obj,(set)) or isinstance(obj,(list)):
            result = "[";
            for a in obj:
                if result != "[":
                    result += ",";
                result += Tool.__object(a);
            return  result + ']' ;
        elif isinstance(obj,(dict)):
            result = "{";
            for (key,value) in obj.items():
                if(result != '{'):
                    result += ",";
                result += key + ":" + Tool.__object(value);
            return  result + '}'
        else:
            return str(obj);
    @staticmethod
    def toString(obj):
        return Tool.__object(obj);
    @staticmethod
    def Escape(str):
        str = str.replace("'","%27");
        str = str.replace("\"","%22");
        str = str.replace(" ","%20");
        str = str.replace("=","%3D");
        return str;
    @staticmethod
    def urlEncode(param):
        pass
        result = "";
        for property in param:
            if result != "":
                result += "&";
            if hasattr(param,property):
                value = Tool.toString(getattr(param,property));
            else:
                value =  Tool.toString(param[property]);
            value = Tool.Escape(value);
            result += property + "=" + value;
        return result;