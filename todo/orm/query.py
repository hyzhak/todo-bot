import asyncio
from todo.orm import errors


class Query:
    def __init__(self, item_cls):
        self.collection = item_cls.collection
        self.item_cls = item_cls
        self.limit_value = 0
        self.skip_value = 0
        self.query = {}

    def __call__(self, *args, **kwargs):
        self.query = args[0]
        return self

    async def delete(self):
        res = await self.collection.delete_many(self.query)
        return res.deleted_count

    def find(self, query={}):
        self.query = query
        return self

    async def find_one(self, query={}):
        l = await self.find(query).to_list()
        if len(l) > 0:
            return l[0]
        else:
            raise errors.DoesNotExist()

    def limit(self, limit):
        self.limit_value = limit
        return self

    def skip(self, skip):
        self.skip_value = skip
        return self

    async def to_list(self):
        cursor = self.collection.find(self.query)
        if self.skip_value > 0:
            cursor = cursor.skip(self.skip_value)
        if self.limit_value > 0:
            cursor = cursor.limit(self.limit_value)
        l = await cursor.to_list(None)
        return [self.item_cls(**i) for i in l]
