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
            self.tasks = self.db.get_collection('tasks')

            await self.tasks.insert({'description': 'monkey business'})
            await self.tasks.insert({'description': 'hokey-pokey'})

            return self.db

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.tasks.drop()
            self.tasks = None
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


@pytest.mark.asyncio
async def test_read(build_mock_db):
    async with build_mock_db() as db:
        document.setup(db)
        task = await document.TaskDocument.objects.find({
            'description': 'monkey business',
        })
        assert task is not None
        assert isinstance(task, list)
        assert len(task) == 1
        assert task[0]['description'] == 'monkey business'


def test_update():
    pass


def test_delete():
    pass
