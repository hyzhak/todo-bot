from todo.orm import errors


class Query:
    def __init__(self, item_cls):
        self.collection = item_cls.collection
        self.item_cls = item_cls

    def __call__(self, *args, **kwargs):
        self.query = args[0]
        return self

    async def delete(self):
        res = await self.collection.delete_many(self.query)
        return res.deleted_count

    async def find(self, query={}):
        l = await self.collection.find(query).to_list(None)
        return [self.item_cls(**i) for i in l]

    async def find_one(self, query={}):
        l = await self.find(query)
        if len(l) > 0:
            return l[0]
        else:
            raise errors.DoesNotExist()
