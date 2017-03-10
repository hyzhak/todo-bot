import asyncio
import pymongo
from todo.orm import errors


class Query:
    def __init__(self, item_cls, limit_value=0, skip_value=0, sort_list=None, query=None):
        self.collection = item_cls.collection
        self.item_cls = item_cls
        self.limit_value = limit_value
        self.skip_value = skip_value
        self.sort_list = sort_list or []
        self.query = query or {}

    def __await__(self):
        cursor = self.collection.find(self.query)
        if self.skip_value > 0:
            cursor = cursor.skip(self.skip_value)
        if self.limit_value > 0:
            cursor = cursor.limit(self.limit_value)
        l = yield from cursor.to_list(None)
        return [self.item_cls(**i) for i in l]

    def __call__(self, *args, **kwargs):
        self.query = args[0]
        return self

    async def count(self):
        return len(await self)

    def clone(self):
        return Query(item_cls=self.item_cls,
                     limit_value=self.limit_value,
                     skip_value=self.skip_value,
                     query=self.query,
                     )

    async def delete(self):
        res = await self.collection.delete_many(self.query)
        return res.deleted_count

    def find(self, query=None):
        q = self.clone()
        q.query = query or {}
        return q

    async def find_one(self, query={}):
        l = await self.find(query)
        if len(l) > 0:
            return l[0]
        else:
            raise errors.DoesNotExist()

    def limit(self, limit):
        q = self.clone()
        q.limit_value = limit
        return q

    def skip(self, skip):
        q = self.clone()
        q.skip_value = skip
        return q

    def sort(self, **kwargs):
        q = self.clone()
        q.sort_list = [{k: pymongo.ASCENDING if direction == 'asc' else pymongo.DESCENDING} for k, direction in
                       kwargs.items()]
        return q
