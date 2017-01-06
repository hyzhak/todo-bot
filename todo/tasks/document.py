class TaskDocument:
    collection = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def setup(db):
    TaskDocument.collection = db.get_collection('tasks')
