class Connection:
    def __init__(self):
        pass

    def document(self, document=None, cls=None):
        if document is None:
            document = cls.__name__
        pass
