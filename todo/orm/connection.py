class Connection:
    def __init__(self):
        pass

    @classmethod
    def wrap(cls, db):
        conn = cls()
        conn.db = db
        return conn

    def document(self, document=None, cls=None):
        if document is None:
            document = cls.__name__
        pass
