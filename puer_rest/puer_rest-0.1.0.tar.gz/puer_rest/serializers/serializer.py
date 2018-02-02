from marshmallow import Schema

__all__ = ["Serializer"]


class Serializer(Schema):
    async def create(self, data):
        pass

    async def update(self, obj, data):
        pass

    async def get(self, id):
        pass

    async def list(self, filters, page=0, page_size=20, sort=(None, -1)):
        pass

    async def count(self, filters):
        pass

    async def delete(self, id):
        pass

    async def to_representation(self, obj):
        pass
