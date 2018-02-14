import pymongo
from pymongo.errors import DuplicateKeyError

from spooler.connectors.base import Connector
from spooler.task import Task


class MongoConnector(Connector):

    def __init__(self, collection):
        collection.lock.create_index(
            [('expire', pymongo.ASCENDING)],
            expireAfterSeconds=0,
            background=True
        )
        self.collection = collection

    def get_available_tasks(self):
        for doc in self.collection.find():
            task = Task.from_name(doc.get("callback"), *doc.get("args"),
                                  **doc.get("kwargs"))
            task.uid = doc.get("_id")
            yield task

    def add_task(self, task):
        payload = {"callback": task.get_callback_name(), "args": task.args,
                   "kwargs": task.kwargs}
        result = self.collection.insert(payload)
        task.uid = result.inserted_id
        return task

    def mark_tasks_done(self, *ids):
        self.collection.remove({"_id": {"$in": ids}})

    def lock(self, id, expiry):
        try:
            self.collection.lock.insert_one({
                "_id": id,
                "expire": expiry
            })
            return True
        except DuplicateKeyError:
            return False
