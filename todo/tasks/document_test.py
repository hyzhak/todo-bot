import asyncio
from motor import motor_asyncio
import os
import pytest

from . import document


@pytest.fixture
@pytest.mark.asyncio
def build_mock_db():
    class MockDBBuilder():
        async def __aenter__(self):
            self.cx = motor_asyncio.AsyncIOMotorClient(os.environ.get('TEST_MONGODB_URL', 'mongo'),
                                                       io_loop=asyncio.get_event_loop())
            self.db = self.cx.get_database(os.environ.get('TEST_MONGODB_DB', 'test'))
            self.characters = self.db.get_collection('characters')

            await self.characters.insert({'name': 'hamlet', 'gender': 'male'})
            await self.characters.insert({'name': 'claudius', 'gender': 'male'})
            await self.characters.insert({'name': 'gertrude', 'gender': 'female'})
            await self.characters.insert({'name': 'polonius', 'gender': 'male'})

            return self.db

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.characters.drop()
            self.characters = None
            self.db = None
            self.cx.close()
            self.cx = None

    return MockDBBuilder


def test_create():
    task = document.TaskDocument(description='one description')
    assert task.description == 'one description'


@pytest.mark.asyncio
async def test_create_and_save(build_mock_db):
    async with build_mock_db() as db:
        document.setup(db)
        task = document.TaskDocument(description='one description')
        id = await task.save()
        assert id is not None


def test_read():
    pass


def test_update():
    pass


def test_delete():
    pass
