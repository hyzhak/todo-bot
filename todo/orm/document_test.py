import asyncio
from motor import motor_asyncio
import os
import pytest
from todo.orm import errors

from . import document


class TaskDocument(document.BaseDocument):
    pass


@pytest.fixture
@pytest.mark.asyncio
def build_mock_db():
    class MockDBBuilder():
        async def __aenter__(self):
            self.cx = motor_asyncio.AsyncIOMotorClient(os.environ.get('MONGODB_URI'),
                                                       io_loop=asyncio.get_event_loop())
            self.db = self.cx.get_database(os.environ.get('MONGODB_TEST_DB', 'test'))
            self.tasks = self.db.get_collection('tasks')

            await self.tasks.insert({'description': 'chicane'})
            await self.tasks.insert({'description': 'fooling around'})
            await self.tasks.insert({'description': 'hokey-pokey'})
            await self.tasks.insert({'description': 'monkey business'})

            TaskDocument.set_collection(self.tasks)
            return self.db

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.tasks.drop()
            self.tasks = None
            self.db = None
            self.cx.close()
            self.cx = None

    return MockDBBuilder


def test_create():
    task = TaskDocument(description='one description')
    assert task.description == 'one description'


@pytest.mark.asyncio
async def test_create_and_save(build_mock_db):
    async with build_mock_db() as db:
        task = TaskDocument(description='one description')
        id = await task.save()
        assert id is not None


@pytest.mark.asyncio
async def test_read(build_mock_db):
    async with build_mock_db() as db:
        tasks = await TaskDocument.objects.find({
            'description': 'monkey business',
        })
        assert tasks is not None
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert tasks[0].description == 'monkey business'


@pytest.mark.asyncio
async def test_read_one(build_mock_db):
    async with build_mock_db() as db:
        task = await TaskDocument.objects.find_one({
            'description': 'monkey business',
        })
        assert task is not None
        assert isinstance(task, TaskDocument)
        assert task.description == 'monkey business'


@pytest.mark.asyncio
async def test_update(build_mock_db):
    async with build_mock_db() as db:
        old_task = await TaskDocument.objects.find_one({
            'description': 'monkey business',
        })
        with pytest.raises(AttributeError):
            assert old_task.status == 'done'
        old_task.status = 'done'

        await old_task.save()
        new_task = await TaskDocument.objects.find_one({
            'description': 'monkey business',
        })
        assert new_task.status == 'done'


@pytest.mark.asyncio
async def test_delete(build_mock_db):
    async with build_mock_db() as db:
        tasks = await TaskDocument.objects.find()
        assert len(tasks) == 4
        assert await TaskDocument.objects({
            'description': 'monkey business',
        }).delete() == 1

        with pytest.raises(errors.DoesNotExist):
            await TaskDocument.objects.find_one({
                'description': 'monkey business',
            })

        tasks = await TaskDocument.objects.find()
        assert len(tasks) == 3


@pytest.mark.asyncio
async def test_limit(build_mock_db):
    async with build_mock_db():
        tasks = await TaskDocument.objects.find().limit(2)
        assert len(tasks) == 2
        assert tasks[0].description == 'chicane'
        assert tasks[1].description == 'fooling around'


@pytest.mark.asyncio
async def test_skip(build_mock_db):
    async with build_mock_db():
        tasks = await TaskDocument.objects.find().skip(2)
        assert len(tasks) == 2
        assert tasks[0].description == 'hokey-pokey'
        assert tasks[1].description == 'monkey business'


@pytest.mark.asyncio
async def test_count(build_mock_db):
    async with build_mock_db():
        tasks_count = await TaskDocument.objects.find().count()
        assert tasks_count == 4


@pytest.mark.asyncio
async def test_isolate_commands(build_mock_db):
    async with build_mock_db():
        TaskDocument.objects.find({
            'description': 'monkey business',
        })
        assert await TaskDocument.objects.count() == 4
        TaskDocument.objects.limit(2)
        assert await TaskDocument.objects.count() == 4
        TaskDocument.objects.skip(2)
        assert await TaskDocument.objects.count() == 4
