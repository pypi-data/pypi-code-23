# -*- coding: utf-8 -*-

import redis
import fire
import json
from datetime import datetime as dt
import dateutil.parser
from operator import itemgetter
import pprint

slice1 = '10.1.221.60'
slice2 = '10.1.221.61'
slice3 = '10.1.222.48'
redis_key_price = "hhub:RoomPrice:"
redis_key_roomcount = "hhub:RoomCount:"
redis_key_salecondition1 = "hhub:SalesConditon1:"
redis_key_salecondition2 = 'hhub:SalesConditon2:'


# def compareDesc(opentravelentity1, opentravelentity2):
#     """根据pushdate和locator比较两个opentravel实体的顺序"""
#     date1 = dateutil.parser.parse(opentravelentity1["pushdate"])
#     date2 = dateutil.parser.parse(opentravelentity2["pushdate"])

#     return cmp(date1,date2)
# if(date1 > date2):
#     return 1
# elif date1 < date2:
#     return -1
# else:
#     if opentravelentity1["locatorid"] >= opentravelentity2["locatorid"]:
#         return 1
#     else:
#         return -1

class GlobalRedis(object):
    """global redis cluster operation class"""

    def __init__(self, host=slice1):

        self.rclient = self.getClient(host)
        self.rhost = host

    def getClient(self, host, port=6379, db=0):
        """get redis client"""

        return redis.StrictRedis(host, port, db)

    def info(self):
        """redis info command"""
        print(self.rclient.info())

    def keys(self, wildcard):
        """search keys with prefix"""
        if "*" in wildcard and len(wildcard) == 1:
            raise Exception("不允许直接使用*进行查询")
        else:
            return self.rclient.keys(wildcard)

    def zrangebyscore(self, key, begin, end):
        """get set by score"""
        return self.rclient.zrangebyscore(key, min=begin, max=end)

    def fetchOpenTravelEntityFromRedis(self, rediskey, hotelid, bizday, roomtype=None, rateplancode=None):
        """通用获取redis中的Opentravel数据"""
        begin, end = self.calculatezsetscore(bizday)
        wrapFunc = self.WrapOpentravelWithRedisInfo_closure(roomtype, rateplancode)
        redis_value = self.zrangebyscore(rediskey + hotelid, begin, end)
        if len(redis_value) is not 0:
            return list(map(wrapFunc, redis_value))
        else:
            return None

    def WrapOpentravelWithRedisInfo_closure(self, roomtype, rateplancode):
        """
        返回一个包含房型筛选的redis信息填充闭包
        """

        def WrapOpentravelWithRedisInfo(jsonStr):
            """装填redis信息"""
            if json is None:
                return None
            else:
                dict = json.loads(jsonStr)
                if dict is not None and roomtype is not None:
                    if dict["InvTypeCode"] != roomtype or dict["InvTypeCode"] == "***":
                        dict = None

                if dict is not None and rateplancode is not None:
                    if dict["RatePlanCode"] is None or dict["RatePlanCode"] != rateplancode:
                        dict = None

                if dict is not None:
                    dict["redis"] = self.rhost
                    return dict

        return WrapOpentravelWithRedisInfo

    def calculatezsetscore(self, datetime):
        """convert datetime to format like yyXXX0000, yyXXX9999"""
        year = str(datetime.year)[-2:]
        dayofyear = str(datetime.timetuple().tm_yday)
        return year + dayofyear.zfill(3) + "0000", year + dayofyear.zfill(3) + "9999"


class RedisOperationGroup:

    def __init__(self, client_address_list=None):
        """通过地址列表生成Redis客户端,地址列表不传则使用默认列表，db不能修改，为0"""
        if client_address_list is None:
            self.rgroup = [GlobalRedis(slice1), GlobalRedis(slice2), GlobalRedis(slice3)]
        else:
            self.rgroup = [GlobalRedis(a) for a in client_address_list]

    def fetchOpenTravelEntityFromRedis(self, rediskey, hotelid, bizday, roomtype=None, rateplancode=None):
        """客户端列表轮训获取值"""
        for c in self.rgroup:
            result = c.fetchOpenTravelEntityFromRedis(rediskey, hotelid, bizday, roomtype, rateplancode)
            if result is None or len(result) == 0:
                pass
            else:
                if (rediskey == redis_key_salecondition2):
                    return sorted(list(filter(lambda x: x is not None, result)),
                                  key=itemgetter("PushDate"))  # Booper没有locatorid，不能用locatorid作为排序的条件
                else:
                    return sorted(list(filter(lambda x: x is not None, result)),
                                  key=itemgetter("PushDate", "LocatorID"))

        return None


if __name__ == '__main__':
    # gr = RedisOperationGroup()
    # result = gr.fetchOpenTravelEntityFromRedis(redis_key_salecondition2, "0372", dt.now(),"DBA","RA3HZU")
    pp = pprint.PrettyPrinter(indent=1)
    # [pp.pprint(r) for r in result]

    gr = RedisOperationGroup(client_address_list=["10.1.249.139"])
    result = gr.fetchOpenTravelEntityFromRedis(redis_key_price, "1434", dt.now())  # 取出酒店该日所有的房量数据
    pp.pprint(result)
