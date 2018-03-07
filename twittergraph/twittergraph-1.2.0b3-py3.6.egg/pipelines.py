import os
import csv
import logging
from .utils import mkdirs
from .entities import Follower,Following
from .settings import settings
logger = logging.getLogger(__name__)
class SaveToFilePipeline(object):
    ''' pipeline que guarda info a disco '''
    def __init__(self):
        mkdirs(settings.SAVE_FOLLOWER_PATH)
        mkdirs(settings.SAVE_FOLLOWING_PATH)

    def process_item(self, item):
        ''' Proceso de guardado '''
        if isinstance(item, Follower):
            savePath = os.path.join(settings.SAVE_FOLLOWER_PATH , item['idMe'])
            with open(savePath,'a') as f:
                fieldnames = ['idFollower','nameFollower','idMe','nameMe']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(item.dicti())
                f.flush()
            logger.debug("Add follower:{}".format(item['nameFollower']))
            
        elif isinstance(item, Following):
            savePath = os.path.join(settings.SAVE_FOLLOWING_PATH, item['idMe'])
            with open(savePath,'a') as f:
                fieldnames = ['idMe','nameMe','idFollowing','nameFollowing']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(item.dicti())
                f.flush()
            logger.debug("Add following:{}".format(item['nameFollowing']))
        else:
            logger.info("Item type is not recognized! type = {}".format(item))


class SaveToMongoPipeline(object):

    ''' pipeline que guarda info a mongodb '''
    def __init__(self):
        connection = pymongo.MongoClient(settings.MONGODB['MONGODB_SERVER'], settings.MONGODB['MONGODB_PORT'])
        db = connection[settings.MONGODB['MONGODB_DB']]
        self.followerCollection = db[settings.MONGODB['MONGODB_FOLLOWER_COLLECTION']]
        self.followingCollection = db[settings.MONGODB['MONGODB_FOLLOWING_COLLECTION']]
        self.followerCollection.ensure_index([('ID', pymongo.ASCENDING)], unique=True, dropDups=True)
        self.followingCollection.ensure_index([('ID', pymongo.ASCENDING)], unique=True, dropDups=True)


    def process_item(self, item):
        ''' Proceso de guardado '''
        if isinstance(item, Follower):
            dbItem = self.followerCollection.find_one({'ID': item['idFollower']})
            if dbItem:
                pass
            else:
                self.followerCollection.insert_one(dict(item))
                logger.debug("Add Follower:%s" %item['nameFollower'])

        elif isinstance(item, Following):
            dbItem = self.followingCollection.find_one({'ID': item['idFollowing']})
            if dbItem:
                pass 
            else:
                self.followingCollection.insert_one(dict(item))
                logger.debug("Add Following:%s" %item['nameFollowing'])

        else:
            logger.info("Item type is not recognized! type = %s" %type(item))

