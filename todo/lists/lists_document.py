from todo.orm import document, query


class ListDocument(document.BaseDocument):
    pass


def setup(db):
    ListDocument.set_collection(db.get_collection('lists'))
