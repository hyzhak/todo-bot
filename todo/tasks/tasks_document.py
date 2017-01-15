from todo.orm import document, query


class TaskDocument(document.BaseDocument):
    pass


def setup(db):
    TaskDocument.set_collection(db.get_collection('tasks'))
