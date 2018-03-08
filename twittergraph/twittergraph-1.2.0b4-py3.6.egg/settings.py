from collections import deque


class settings(object):

    # -*- coding: utf-8 -*-


    USER_AUTH = "hufeallu@hotmail.com"
    PASS_AUTH = "123456Abc"

    SAVE_MODE = "Disk"
    #SAVE_MODE = "MongoDB"

    # Total of users that the program will be extract
    TOTAL_USERS_EXTRACT = 5000


    # Total time to extract in ms
    TOTAL_EXTRACT_TIME = 1


    USERS_LIST = deque("")

    TIMEOUT =  -1



    # settings for where to save data on disk
    SAVE_FOLLOWER_PATH = './Data/follower/'
    SAVE_FOLLOWING_PATH = './Data/following/'

    # settings for mongodb
    MONGODB = dict(
      MONGODB_SERVER = "127.0.0.1",
      MONGODB_PORT = 27017,
      MONGODB_DB = "TwitterGraph"  ,      # database name to save the crawled data
      MONGODB_FOLLOWER_COLLECTION = "follower",
      MONGODB_FOLLOWING_COLLECTION = "following"
    ) 

  


