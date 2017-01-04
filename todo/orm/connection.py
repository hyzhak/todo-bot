import inflection


class Connection:
    def __init__(self):
        self.collections = {}

    @classmethod
    def wrap(cls, db):
        conn = cls()
        conn.db = db
        return conn

    def document(self, document=None, cls=None):
        if document is None:
            document = inflection.tableize(cls.__name__)

        col = self.db.get_collection(document)
        cls.connection = self
        self.collections[cls] = col

    def get_collection_by_document_class(self, cls=None):
        return self.collections[cls]
