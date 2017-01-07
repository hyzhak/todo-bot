class Query:
    def __init__(self, collection):
        self.collection = collection

    async def find(self, query):
        l = await self.collection.find(query).to_list(None)
        return [TaskDocument(**i) for i in l]


class TaskDocument:
    collection = None

    def __init__(self, **kwargs):
        self.fields = kwargs

    def __getattr__(self, item):
        if item in self.fields.keys():
            return self.fields[item]
        return super(TaskDocument, self).__getattr__(item)

    async def save(self):
        return await TaskDocument.collection.insert(self.fields)


def setup(db):
    TaskDocument.collection = db.get_collection('tasks')
    TaskDocument.objects = Query(TaskDocument.collection)
