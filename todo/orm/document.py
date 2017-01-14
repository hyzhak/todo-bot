class BaseDocument:
    __slots__ = ('fields',)
    collection = None

    # TODO: should be able to process dictionary
    def __init__(self, **kwargs):
        self.fields = kwargs

    def __getattr__(self, item):
        if item in self.fields.keys():
            return self.fields[item]
        raise AttributeError(item)

    def __setattr__(self, key, value):
        if key in self.__slots__:
            return super().__setattr__(key, value)
        self.fields[key] = value

    async def save(self):
        try:
            return await self.collection.update({'_id': self._id}, self.fields)
        except AttributeError:
            return await self.collection.insert(self.fields)

