class BaseDocument:
    __slots__ = ['_data']

    def __init__(self, **values):
        self.__dict__['_data'] = {}
        for key, value in values.items():
            setattr(self, key, value)

    # def __getattr__(self, name):
    #     return self.__dict__[name]
    #
    # def __setattr__(self, name, value):
    #     self._data[name] = value
    #     self.__dict__[name] = value

    async def save(self):
        pass
