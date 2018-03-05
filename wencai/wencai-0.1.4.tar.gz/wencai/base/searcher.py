# -*- coding:utf-8 -*-
import logging
import datetime as dt
from time import sleep
import pandas as pd
from wencai.base.cons import WENCAI_URL,WENCAI_ENGLISH_CHINESE
from wencai.base.session import Session
pd.set_option('display.width',2000)

class Searcher(object):


    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
        )
        self.session = Session()()



    def get_search_report(self):
        '?query={}&firstDraw=1'
        payload = {
            # 'query':"",
            'source':'Ths_iwencai_Xuangu',
            'question':'今日热门股推荐',
            'log_info':{"other_info":"{\"eventId\":\"iwencai_app_hpxg_recommend\",\"ct\":1512572005742}","other_utype":"random","other_uid":"Ths_iwencai_Xuangu_jd5locvrl7oj4cwmyxf20rwb5pj15w52"},
            'user_name': 'kumldvqxvo',
            'kefu_user_id':"",
            "kefu_record_id":"",
            "user_id":"",

            'version':1.2,
            '_':1512572005745
        }
        response = self.session.get("http://www.iwencai.com/data-robot/chat/?source=Ths_iwencai_Xuangu&question=%E4%BB%8A%E6%97%A5%E7%83%AD%E9%97%A8%E8%82%A1%E6%8E%A8%E8%8D%90&kefu_user_id=&kefu_record_id=&user_id=&log_info=%7B%22other_info%22%3A%22%7B%5C%22eventId%5C%22%3A%5C%22iwencai_app_hpxg_recommend%5C%22%2C%5C%22ct%5C%22%3A1512572005742%7D%22%2C%22other_utype%22%3A%22random%22%2C%22other_uid%22%3A%22Ths_iwencai_Xuangu_jd5locvrl7oj4cwmyxf20rwb5pj15w52%22%7D&user_name=kumldvqxvo&version=1.2&_=1512572005745")
        # response = self.session.get(WENCAI_URL['search'],params=payload)
        json_data = response.json()['data']['answer'][0]['table'][0]['tr']

        json_list = []
        for j in json_data:
            temp = {}
            temp['stock_code'] =  j[0]['val']
            temp['stock_name'] = j[1]['val']
            temp['price'] = j[2]['val']
            temp['percent'] = j[3]['val']
            temp['hotIndex'] = j[4]['val']
            temp['marketAttention'] = j[5]['val']
            json_list.append(temp)

        df = pd.DataFrame().from_dict(json_list)
        print(df)

    def bb(self):
        response = self.session.get("http://www.iwencai.com/traceback/strategy/report?id=88384&qs=backtest_open_tab1###")
        print(response.text)

if __name__ == '__main__':
    searcher = Searcher()
    searcher.get_search_report()



