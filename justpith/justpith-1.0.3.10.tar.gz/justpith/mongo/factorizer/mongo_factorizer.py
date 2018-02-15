from ..mongo import Mongo

class MongoFactorizer(Mongo):
    def __init__(self,host, port, db):
        super(MongoFactorizer,self).__init__(host, port, db)


    # def get_staged_news(self):
    #     selected_collection = self.connection["NewsStage"]
    #     result = selected_collection.find_one({})
    #     return result

    def get_voted_news(self, news_list):
        selected_collection = self.connection["NewsVotes"]
        result = selected_collection.find({"_id": {"$in": news_list}})
        return result

    def write_mf_raccomandation(self, id_job, id_user, raccomandation_list):
        selected_collection = self.connection["Users"]
        result = selected_collection.update({"_id": id_user}, {"$set": {"mf_raccomandations."+str(id_job): raccomandation_list}}, upsert=True)

    def insert_matrix(self, data):
        selected_collection = self.connection["Matrix"]
        result = selected_collection.insert(data)

    def delete_old_mf_raccomadations(self, old_job_id):
        selected_collection = self.connection["Users"]
        selected_collection.update_many({}, {"$unset": {"mf_raccomandations.{}".format(old_job_id): 1}})


    def clean_mf_raccomandations(self):
        selected_collection = self.connection["ControllerJobs"]
        results = selected_collection.find({"active":1})
        job_ids = []
        for result in results:
            id_job = result["_id"]
            print(id_job)
            job_ids.append(id_job)

        selected_collection = self.connection["Users"]
        user = selected_collection.find_one({"_id": "61"})
        user_mf = user["mf_raccomandations"]
        new_user_mf = {}
        for job, mf_racc in user_mf.iteritems():
            if job in job_ids:
                new_user_mf[job] = mf_racc
        print(new_user_mf.keys())
        selected_collection.update({"_id": "61"}, {"$set": {"mf_raccomandations": new_user_mf}})


