from bson import json_util
from botstory.utils import advanced_json_encoder
import json
import logging
from todo import reflection
from todo.orm import query

logger = logging.getLogger(__name__)


class BaseDocument:
    __slots__ = ('fields',)
    collection = None
    objects = None

    @classmethod
    def set_collection(cls, collection):
        cls.collection = collection
        cls.objects = query.Query(cls)

    # TODO: should be able to process dictionary
    def __init__(self, **kwargs):
        self.fields = kwargs

    def __getattr__(self, item):
        if item in self.fields.keys():
            return self.fields[item]
        raise AttributeError(item)

    def __repr__(self):
        try:
            return json.dumps({
                'type': reflection.class_to_str(type(self)),
                'fields': self.fields,
            },
                default=json_util.default)
        except Exception as err:
            logging.error(err)
            return json.dumps({
                'type': reflection.class_to_str(type(self)),
                'error': err,
            },
                default=json_util.default)

    def __setattr__(self, key, value):
        if key in self.__slots__:
            return super().__setattr__(key, value)
        self.fields[key] = value

    async def save(self):
        try:
            return await self.collection.update({'_id': self._id}, self.fields)
        except AttributeError:
            return await self.collection.insert(self.fields)
