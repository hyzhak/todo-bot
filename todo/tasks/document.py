class Query:
    def __init__(self, collection):
        self.collection = collection

    async def find(self, query):
        l = await self.collection.find(query).to_list(None)
        return [TaskDocument(**i) for i in l]

    async def find_one(self, query):
        l = await self.find(query)
        return len(l) > 0 and l[0]


class TaskDocument:
    __slots__ = ('fields',)
    collection = None

    def __init__(self, **kwargs):
        self.fields = kwargs

    def __getattr__(self, item):
        if item in self.fields.keys():
            return self.fields[item]
        raise AttributeError(item)

    def __setattr__(self, key, value):
        if key in self.__slots__:
            return super().__setattr__(key, value)
        self.fields[key] = value

    async def save(self):
        try:
            return await TaskDocument.collection.update({'_id': self._id}, self.fields)
        except AttributeError:
            return await TaskDocument.collection.insert(self.fields)


def setup(db):
    TaskDocument.collection = db.get_collection('tasks')
    TaskDocument.objects = Query(TaskDocument.collection)
