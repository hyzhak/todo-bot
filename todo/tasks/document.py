class Query:
    def find(self):
        pass


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
