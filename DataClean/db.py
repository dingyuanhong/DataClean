#coding=utf-8

class Config:
    @staticmethod
    def mongo():
        return  {
                "member":[
                    "192.168.127.128:27017"
                    ,"192.168.127.128:27018"
                    ,"192.168.127.128:27019"
                ],
                "options":{
                    "replicaSet":"testset"
                }
            };