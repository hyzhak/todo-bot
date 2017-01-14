from todo.orm import document, query


class TaskDocument(document.BaseDocument):
    pass


def setup(db):
    TaskDocument.collection = db.get_collection('tasks')
    TaskDocument.objects = query.Query(TaskDocument.collection, TaskDocument)
