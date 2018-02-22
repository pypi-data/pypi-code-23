from pymongo import MongoClient
from time import time
import  traceback

class Mongo(object):

    ##### GENERAL #####
    def __init__(self, host, port, db):
        self.host       = host
        self.port       = port
        self.db         = db

        self.client     = None
        self.connection = None
        self.connect()

    def connect(self):
        self.client     = MongoClient(self.host, self.port)
        self.connection = self.client[self.db]


    ##### JUSTPITH SERVER #####
    def insert_news(self, news):
        try:
            selected_collection = self.connection['News']
            find_result = selected_collection.find_one({"_id":news["_id"]})
            if find_result is not None:
                selected_collection.replace_one({"_id": news["_id"]}, news)
            else:
                print("-------------------------------->news already present {}".format(news["_id"]))
                result = selected_collection.insert(news)
        except Exception as e:
            traceback.print_exc()

    def update_news_report(self, id_news, queue_name, queue_op):
        selected_collection = self.connection['News']
        result = selected_collection.update_one({'_id': id_news}, {'$push': {'report': {'queue_name': queue_name, 'queue_op': queue_op, 'timestamp': str(time())}}}, upsert=True)

    def update_news_after_parsing(self, id_news, ttl, article, article_cleaned, queue_name,timestamp):
        selected_collection = self.connection['News']
        result = selected_collection.update_one({'_id': id_news}, {'$set': {'TTL': ttl, 'article': article, 'article_cleaned': article_cleaned,"timestamp":timestamp}, '$push': {'report': {'queue_name': queue_name, 'queue_op': 'IN', 'timestamp': str(time())}}}, upsert=True)

    def update_news_after_similarity(self, id_news, doc_sim, topic_sim):
        selected_connection = self.connection['News']
        result = selected_connection.update_one({'_id': id_news}, {'$set': {'doc_sims': doc_sim, 'topic_sims': topic_sim}})

    def get_list_news(self, list_id_news):
        selected_collection = self.connection['News']
        result = selected_collection.find( { "_id" : { "$in": list_id_news } }, {"_id":1, "img_path":1, "category_title":1, "news_source":1, "url":1, "date":1, "article":1, "tags":1, "category_id":1, "place":1, "title":1, "news_source_id":1} )
        return result

    def copy_lifo(self, id_user, category_id):

        try:
            collection_name = "LifoNews_{}".format(category_id)
            selected_collection = self.connection[collection_name]

            result = selected_collection.find_one({"_id":0})
            if result:
                result["_id"] = int(id_user)

                selected_collection.insert(result)
        except Exception as e:
            traceback.print_exc()


    def add_in_lifo(self, id_user, id_news, category_id, news, action, timestamp):
        selected_collection = self.connection['LifoNews_{}'.format(category_id)]
        result = None
        if action == 1:
            #result = selected_collection.update_one({"_id": int(id_user)}, {"$set":{id_news:{"add":1, "timestamp": timestamp}}}, upsert=True )
            # result = selected_collection.update_one({"_id": int(id_user)},
            #                                         {"$set": {"{}.add".format(id_news): 1, "{}.timestamp".format(id_news):timestamp}},
            #                                         upsert=True)
            #selected_collection.update({"_id":int(id_user)},{"$addToSet":{"list_news":{"id":int(id_news),"add":-1,"del":-1,"timestamp":timestamp}}},upsert=True)
            result = selected_collection.find({"_id":int(id_user),"list_news":{"$elemMatch":{"id":int(id_news)}}}).count()
            if result>0:
                selected_collection.update({"_id":int(id_user), "list_news.id":int(id_news)},{"$set":{"list_news.$.add":1,"list_news.$.id":int(id_news),"list_news.$.timestamp":timestamp,"list_news.$.news":news}},upsert=True)
            else:
                #selected_collection.update({"_id":int(id_user)},{"$push":{"list_news":{"id":int(id_news),"add":1,"del":-1,"timestamp":timestamp, "news":news}}},upsert=True)
                selected_collection.update({"_id": int(id_user)}, {"$push": {
                    "list_news": {"$each":[{"id": int(id_news), "add": 1, "del": -1, "timestamp": timestamp, "news": news}],"$position":0,"$slice":100}}},
                                           upsert=True)
        else:
            #result = selected_collection.update_one({"_id": int(id_user)}, {"$set":{id_news:{"del":1, "timestamp": timestamp}}}, upsert=True )
            # result = selected_collection.update_one({"_id": int(id_user)},
            #                                         {"$set": {"{}.del".format(id_news): 1,
            #                                                   "{}.timestamp".format(id_news): timestamp}},
            #                                         upsert=True)

            #selected_collection.update({"_id": int(id_user)},{"$addToSet": {"list_news": {"id":int(id_news),"add":-1,"del":-1,"timestamp":timestamp}}},upsert=True)
            #selected_collection.update({"_id": int(id_user), "list_news.id": int(id_news)}, {"$set": {"list_news.$.del": 1, "list_news.$.id": int(id_news), "list_news.$.timestamp": timestamp}},upsert=True)
            result = selected_collection.find(
                {"_id": int(id_user), "list_news": {"$elemMatch": {"id": int(id_news)}}}).count()
            if result > 0:
                selected_collection.update({"_id": int(id_user), "list_news.id": int(id_news)}, {
                    "$set": {"list_news.$.del": 1, "list_news.$.id": int(id_news), "list_news.$.timestamp": timestamp}},
                                           upsert=True)
            else:
                selected_collection.update({"_id": int(id_user)}, {
                    "$push": {"list_news": {"id": int(id_news), "add": -1, "del": 1, "timestamp": timestamp, "news":news}}},
                                           upsert=True)

    def remove_in_lifo(self,user_id, category):
        selected_collection = self.connection['LifoNews_{}'.format(category)]
        selected_collection.update({"_id":int(user_id)}, {"$pull":{"list_news": {"del":1}}}, multi=True)


    def get_in_lifo(self, user_id, category_id, num_page, page_size, bias=None):
        selected_collection = self.connection['LifoNews_{}'.format(category_id)]
        result = selected_collection.find({"_id": int(user_id), "list_news": {"$elemMatch":{"del":{"$ne":1}}}})
        # import json
        # for elem in result:
        #     print(json.dumps(elem))
        data = []

        # if result.count():
        #     no_to_del=[elem for elem in result[0]["list_news"] if elem["del"] != 1]
        #     data = list(reversed(no_to_del))[num_page*page_size:(num_page+1)*page_size]

        if result.count():
            #no_to_del=[elem for elem in result[0]["list_news"]]
            #[elem for elem in result[0]["list_news"] if elem["id"] < int(bias)]
            if bias != None:
                biased = [elem for elem in result[0]["list_news"] if elem["id"] < int(bias)]
                #data = list(reversed(biased))[num_page*page_size:(num_page+1)*page_size]
                data = biased[num_page*page_size:(num_page+1)*page_size]
            else:
                #data = list(reversed(result[0]["list_news"]))[num_page*page_size:(num_page+1)*page_size]
                data = result[0]["list_news"][num_page*page_size:(num_page+1)*page_size]

        return data


    def update_into_container(self, container_id, content_obj):
        #db.prova.update({"_id":2, "content_list.id":2},{"$set":{"content_list.$":{} }})
        id = content_obj["_id"]
        selected_collection = self.connection['Containers']
        result = selected_collection.update({"_id": container_id, "content_list._id": id}, {"$set": {"content_list.$":content_obj}})

    def add_into_container(self, container_id, content_obj):
        selected_collection = self.connection['Containers']
        result = selected_collection.update({"_id": container_id}, {"$push":{"content_list": content_obj}}, upsert=True)

    def del_from_container(self, container_id, content_id):
        selected_collection = self.connection['Containers']
        result = selected_collection.update({"_id": container_id}, {"$pull":{"content_list": {"_id": content_id}}}, multi=True)

    def delete_container(self, container_id):
        selected_collection = self.connection['Containers']
        result = selected_collection.delete_one({"_id": container_id})

    def get_container_content(self, container_id):
        selected_collection = self.connection['Containers']
        result = selected_collection.find_one({"_id": container_id})
        if result:
            return result["content_list"]
        else:
            return []


    def get_expiring_news_from_container(self, container_id, start_time, stop_time):
        selected_collection = self.connection['Containers']
        result = selected_collection.find_one({"_id": container_id})
        expiring_news_cont = 0
        if result:
            content_list = result["content_list"]
            for content in content_list:
                if ((content["birthday"] < start_time) and (content["birthday"] > stop_time)):
                    expiring_news_cont = expiring_news_cont +1

        return expiring_news_cont

    def get_changed_objects_from_container(self, container_id):
        selected_collection = self.connection['Containers']
        result = selected_collection.find_one({"_id": container_id})
        changed_objects_cont = 0
        if result:
            content_list = result["content_list"]
            for content in content_list:
                if (content["watched"] == 0):
                    changed_objects_cont = changed_objects_cont + 1

        return changed_objects_cont

    def get_images_url_and_size_from_container(self, container_id, main_category):
        selected_collection = self.connection['Containers']
        result = selected_collection.find_one({"_id": container_id})
        urls = []
        size = 0
        if result:
            content_list = result["content_list"]
            if content_list:
                size = len(content_list)
                i = 0
                for content in content_list:
                    if i == 4:
                        break
                    if main_category == 1:
                        urls.append(content["img_path"])
                    if main_category == 3:
                        urls.append(content["item_image"])
                    i = i + 1
            else:
                return (urls, size)
        return (urls, size)


    def reset_watched_field_into_container(self, container_id):
        selected_collection = self.connection['Containers']
        container_content = selected_collection.find_one({"_id": container_id})
        if container_content:
            new_content_list = []
            if container_content["content_list"]:
                content_list = container_content["content_list"]
                for content in content_list:
                    content["watched"] = 1
                    new_content_list.append(content)
                result = selected_collection.update({"_id": container_id}, {"$set": {"content_list": new_content_list}})

        # result = selected_collection.update({"_id": container_id, "content_list.watched": 0}, {"$set": {"content_list.$.watched": 1}})



    def get_container_content_paged(self, container_id, num_page, page_size, main_category, is_temp):
        selected_collection = self.connection['Containers']

        if main_category == 3: #shopping
            if num_page == 0:
                # import pdb
                # pdb.set_trace()
                result_watched_zero = selected_collection.aggregate([{"$match":{"content_list.watched": 0, "_id": int(container_id)}},{"$unwind": "$content_list"},{"$match":{"content_list.watched": 0}}])
                watched_zero = [elem["content_list"] for elem in result_watched_zero if elem["_id"] == int(container_id)]

                result_watched_uno = selected_collection.aggregate([{"$match":{"content_list.watched": 1, "_id": int(container_id)}},{"$unwind": "$content_list"},{"$match":{"content_list.watched": 1}}])
                watched_uno = [elem["content_list"] for elem in result_watched_uno if elem["_id"] == int(container_id)]

                # new_page_size = page_size - len(watched_zero)
                # if new_page_size == 0:
                #     return watched_zero

                watched_uno_reversed = watched_uno[::-1]

                return watched_zero + watched_uno_reversed[num_page*page_size:(num_page+1)*page_size]
            else:
                result_watched_uno = selected_collection.aggregate([{"$match": {"content_list.watched": 1, "_id": int(container_id)}}, {"$unwind": "$content_list"},{"$match": {"content_list.watched": 1}}])
                watched_uno = [elem["content_list"] for elem in result_watched_uno if elem["_id"] == int(container_id)]

                watched_uno_reversed = watched_uno[::-1]
                return watched_uno_reversed[num_page*page_size:(num_page+1)*page_size]
        elif main_category == 1: #news
            if is_temp == 1:
                # per i contenitori temporanei le news devono essere mostrate dalla meno recente alla piu' recente
                result = selected_collection.find_one({"_id": int(container_id)})["content_list"]
                result_news = list(result)
                return result_news[num_page*page_size:(num_page+1)*page_size]
            else:
                # per i contenitori personalizzati le news devono essere mostrate dalla piu' recente alla meno recente
                result = selected_collection.find_one({"_id": int(container_id)},{"content_list":1})["content_list"]
                result_news = list(result)
                result_news_reversed = result_news[::-1]
                return result_news_reversed[num_page*page_size:(num_page+1)*page_size]

    # def get_container_content_paged(self, container_id, num_page, page_size):
    #         selected_collection = self.connection['Containers']
    #         import pdb
    #         pdb.set_trace()
    #
    #
    #         if num_page == 0:
    #             result = selected_collection.find({"content_list.watched":0},{"_id": container_id, "content_list":{"$elemMatch": {"watched":0}}})
    #             for elem in result:
    #                 print(elem)
    #                 if elem["_id"] == int(container_id):
    #                     watched_zero = elem["content_list"]
    #                     break
    #             #watched_zero = [elem["content_list"] for elem in result if elem["_id"] == int(container_id)]
    #             pdb.set_trace()
    #             result_uno = selected_collection.find({"content_list.watched": 1},{"_id": container_id, "content_list": {"$elemMatch": {"watched": 1}}})
    #             for elem_uno in result_uno:
    #                 if elem_uno["_id"] == int(container_id):
    #                     new_page_size = page_size -len(watched_zero)
    #                     last_elements = elem_uno["content_list"][::-1][num_page*new_page_size:(num_page+1)*new_page_size]
    #                     break
    #             return watched_zero + last_elements
    #         else:
    #             pass
    #
    #         for elem in result_uno:
    #             print(elem)
    #         #result = selected_collection.find_one({"_id": container_id, "content_list.watched": 0})
    #
    #         if result:
    #             return result["content_list"][::-1][num_page*page_size:(num_page+1)*page_size]
    #         else:
    #             return []


    ##### JUSTPITH WEB SERVICE TEXT ANALYSIS #####
    def get_docs_to_build_model(self, category):
        selected_collection = self.connection['News']
        result = selected_collection.find({'category_title': category, 'in_model': 1})
        # docs = []
        # for doc in result:
        #     docs.append(doc['article'])
        # return docs
        return result

    def update_news_id_for_model(self, id_news, id_news_corpus):
        selected_connection = self.connection['News']
        result = selected_connection.update_one({'_id': id_news}, {'$set': {'id_corpus': id_news_corpus}})


    def update_reccomended_users(self, id_news, users_list):
        selected_connection = self.connection['News']
        result = selected_connection.update_one({'_id': id_news}, {'$set': {'users_list': users_list}})

    def get_reccomended_users(self, id_news):
        selected_connection = self.connection['News']
        result = selected_connection.find_one({'_id': id_news})
        return result['users_list']

    def insert_list_id_corpus(self,id_index, list_id_corpus):
        selected_connection = self.connection['Indexes']
        result = selected_connection.update_one({'_id': id_index}, {'$set': {'list_id_corpus': list_id_corpus}})


    def insert_index(self, data):
        selected_collection = self.connection['Indexes']
        _id = data['_id']
        model_exist = selected_collection.find({'_id': _id}).count()
        if model_exist == 0:
            result = selected_collection.insert(data)

    def update_active_index(self, id_index, active, category, type):
        if active == 1:
            #result1 = self.connection['Indexes'].update_many({"active": 1, "category":category, "type": type}, {"$set": {"active": 0}})
            result2 = self.connection['Indexes'].find_one_and_update({'_id': id_index}, {'$set': {'active': active}})
        elif active == 0:
            result3 = self.connection['Indexes'].find_one_and_update({'_id': id_index}, {'$set': {'active': active}})

    def set_in_model(self, category):
        selected_connection = self.connection["News"]
        result = selected_connection.update_many({ "article_cleaned": { "$gt": [] }, "category_title": category }, {"$set": {"in_model": 1}})
        result = selected_connection.find({"category_title": category, "in_model": 1}).count()
        return int(result)

    def get_news_parsed(self, category):
        selected_connection = self.connection["News"]
        result = selected_connection.find({"article_cleaned": {"$gt": []}, "category_title": category})
        return result


    def get_info_active_model(self, category, type):
        selected_collection = self.connection['Indexes']
        result = selected_collection.find_one({'category': category, 'type': type, 'active': 1})
        return result

    def get_info_active_model_by_id(self, id):
        selected_collection = self.connection['Indexes']
        result = selected_collection.find_one({'_id': id, 'active': 1})
        return result


    def update_news_similarities(self, doc_id, doc_sims, topic_sims=[]):
        selected_connection = self.connection["News"]
        result = selected_connection.update({"_id": doc_id}, {"$set": {"doc_sims": doc_sims, "topic_sims": topic_sims}})

    def get_news_from_idcorpus(self,list_id):
        docs = []
        selected_connection = self.connection["News"]
        result = selected_connection.find({"id_corpus": {"$in": list_id}}, {"_id":1, "id_corpus":1,"category_title":1,"title":1,"tags":1,"url":1,"article":1})
        for doc in result:
            docs.append(doc)
        return docs

    def get_one_news_from_idcorpus(self,id,category):
        docs = []
        selected_connection = self.connection["News"]
        result = selected_connection.find_one({"id_corpus": id, "category_title":category},
                                          {"_id": 1, "id_corpus": 1, "category_title": 1, "title": 1, "tags": 1,
                                           "url": 1, "article": 1})
        return result

    def get_news_from_id(self,id):
        selected_connection = self.connection["News"]
        result = selected_connection.find_one({"_id":id})
        return result


    def get_id_corpus(self, id):
        selected_connection = self.connection["Indexes"]
        result = selected_connection.find_one({"_id":id}, {"id_to_idcorpus":1})['id_to_idcorpus']

        return result

    def get_all_models(self):
        models = []
        selected_collection = self.connection['Indexes']
        result = selected_collection.find()
        for elem in result:
            models.append(elem)
        return models

    def remove_model(self, id):
        selected_connection = self.connection["Indexes"]
        result = selected_connection.delete_one({'_id': id})
        return result

    def get_categories(self):
        selected_collection = self.connection['Indexes']
        selected_collection.find({'category_title'})

    ###########  NEWS CONSUMER  #####################

    def get_mf_users_raccomandations(self, job_id):
        selected_collection = self.connection['Users']
        #result = selected_collection.find({},{'mf_raccomandations.{}'.format(str(job_id)):1})
        result = selected_collection.find({"mf_raccomandations.{}".format(str(job_id)):{"$exists": True}}, {'mf_raccomandations.{}'.format(str(job_id)):1})
        #result = selected_collection.find({})
        return result

    def update_users_raccomandations(self, news_id, users_to_raccomand):
        selected_collection = self.connection['Users']
        for elem in users_to_raccomand:
            id_user = elem[0]
            weight_racc = elem[1]
            selected_collection.update({'_id': str(id_user)}, {'$set': {'raccomandations.{}'.format(str(news_id)): weight_racc}}, upsert=True)

    def get_index(self, id_index):
        selected_collection = self.connection['Indexes']
        return selected_collection.find_one({'_id': id_index})


    def get_all_categories(self):
        selected_collection = self.connection['Categories']
        return selected_collection.find()

