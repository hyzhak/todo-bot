class BaseDocument:
    def __init__(self, **values):
        for key, value in values.items():
            setattr(self, key, value)

    async def save(self):
        pass
