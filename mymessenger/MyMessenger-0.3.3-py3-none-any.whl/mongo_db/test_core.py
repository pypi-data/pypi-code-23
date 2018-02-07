from .core import MongoRepo


class TestMongoRepo:
    def setup(self):
        self.mongo_repo = MongoRepo()

    def test_push_and_pop(self):
        if not self.mongo_repo.connected:
            return
        self.mongo_repo.push('test_from', 'test_to', 'test_message')
        self.mongo_repo.push('test_from', 'test_to', 'test_message_2')
        result1 = None
        result2 = None
        result3 = None
        for item in self.mongo_repo.db.messages.find({'from': 'test_from', 'to': 'test_to'}):
            result1 = item
        for item in self.mongo_repo.pop('test_from', 'test_to'):
            result2 = item
        for item in self.mongo_repo.db.messages.find({'from': 'test_from', 'to': 'test_to'}):
            result3 = item
        assert result1 == result2
        assert result3 != result2
