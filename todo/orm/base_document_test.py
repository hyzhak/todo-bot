import asyncio
from motor import motor_asyncio
import os
import pytest

from . import base_document, connection


class Character(base_document.BaseDocument):
    pass


@pytest.fixture
@pytest.mark.asyncio
def build_mock_db():
    class MockDBBuilder():
        async def __aenter__(self):
            self.cx = motor_asyncio.AsyncIOMotorClient(os.environ.get('TEST_MONGODB_URL', 'mongo'),
                                                  io_loop=asyncio.get_event_loop())
            self.db = self.cx.get_database(os.environ.get('TEST_MONGODB_DB', 'test'))
            self.characters = self.db.get_collection('characters')

            await self.characters.insert({'name': 'hamlet'})
            await self.characters.insert({'name': 'claudius'})
            await self.characters.insert({'name': 'gertrude'})

            c = connection.Connection.wrap(self.db)
            c.document(cls=Character)

            return self.db

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.characters.drop()
            self.characters = None
            self.db = None
            self.cx.close()
            self.cx = None

    return MockDBBuilder


async def test_create():
    document = base_document.BaseDocument(one_field='one field')
    assert document.one_field == 'one field'


# async def test_save():
#     document = Character(one_field='one field')
#     await document.save()


@pytest.mark.asyncio
async def test_read_async_list_by_field_match(build_mock_db):
    async with build_mock_db():
        hamlets = await Character.objects(name='hamlet')
        assert len(hamlets) == 1
        assert hamlets[0]['name'] == 'hamlet'


@pytest.mark.asyncio
async def test_read_async_count_and_item_by_field_match(build_mock_db):
    async with build_mock_db():
        hamlets = Character.objects(name='hamlet')
        assert await hamlets.count() == 1
        assert (await hamlets.getitem(0))['name'] == 'hamlet'


# TODO: MongoEngine ODMs
# skip first 10 and limit by 5
# base_document.BaseDocument.objects(field='equal value')[10:15]
# base_document.BaseDocument.objects(id=user_id)
# base_document.BaseDocument.objects(__raw__={'tags': 'coding'})
# base_document.BaseDocument.objects.get(id=user_id)
# len(base_document.BaseDocument.objects)


def test_update():
    pass


def test_delete():
    pass
