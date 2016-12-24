from ..db import base_document


class TaskDocument(base_document.BaseDocument):
    pass


def setup(connection):
    connection.document(name='tasks', cls=TaskDocument)
