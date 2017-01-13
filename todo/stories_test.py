import aiohttp
import asyncio
import botstory
from botstory.integrations import fb, mongodb, mockhttp
from botstory.integrations.tests import fake_server
import datetime
import os
import pytest
from todo import tasks
from unittest import mock
from . import stories


@pytest.fixture
def build_context():
    class AsyncContext:
        def __init__(self):
            pass

        async def __aenter__(self):
            self.story = botstory.Story()
            self.fb_interface = self.story.use(
                fb.FBInterface(page_access_token='qwerty'))
            self.db_interface = self.story.use(mongodb.MongodbInterface(
                uri=os.environ.get('MONGODB_URI', 'mongo'),
                db_name=os.environ.get('MONGODB_TEST_DB', 'test'),
            ))
            self.http_interface = self.story.use(mockhttp.MockHttpInterface())

            stories.setup(self.story)
            await self.story.start()
            self.user = await self.db_interface.new_user(
                facebook_user_id='facebook_user_id',
            )
            tasks.document.setup(self.db_interface.db)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.db_interface.clear_collections()
            await self.story.stop()
            if hasattr(self, 'tasks_collection'):
                await self.tasks_collection.drop()
            self.db_interface = None

        async def add_tasks(self, tasks):
            if hasattr(self, 'tasks_collection'):
                await self.tasks_collection.drop()

            self.tasks_collection = self.db_interface.db.get_collection('tasks')

            for t in tasks:
                await self.tasks_collection.insert(t)

        async def receive_answer(self, message):
            # assert len(server.history) > 0
            # req = server.history[-1]['request']
            assert self.http_interface.post.call_count == 1
            _, obj = self.http_interface.post.call_args

            assert obj['json'] == {
                'recipient': {
                    'id': self.user['facebook_user_id'],
                },
                'message': {
                    'text': message
                }
            }

    return AsyncContext


def build_message(msg):
    return {
        'object': 'page',
        'entry': [{
            'id': 'PAGE_ID',
            'time': 1473204787206,
            'messaging': [{
                'sender': {
                    'id': 'facebook_user_id',
                },
                'recipient': {
                    'id': 'PAGE_ID'
                },
                'timestamp': 1458692752478,
                'message': {
                    'mid': 'mid.1457764197618:41d102a3e1ae206a38',
                    'seq': 73,
                    **msg,
                }
            }]
        }]
    }


@pytest.mark.asyncio
async def test_new_task_story(build_context, mocker):
    async with build_context() as context:
        facebook = context.fb_interface

        task = mock.Mock()
        task.save = aiohttp.test_utils.make_mocked_coro()
        mocker.patch.object(stories.document, 'TaskDocument', return_value=task)

        await facebook.handle(build_message({
            'text': 'hello, world!'
        }))

        assert stories.document.TaskDocument.called
        _, obj = stories.document.TaskDocument.call_args

        assert obj['list'] == 'list_1'
        assert obj['description'] == 'hello, world!'
        assert obj['state'] == 'new'
        assert 'created_at' in obj
        assert 'updated_at' in obj

        task.save.assert_called_with()


@pytest.mark.asyncio
async def test_list_of_active_tasks(build_context):
    async with build_context() as context:
        facebook = context.fb_interface

        await context.add_tasks([{
            'description': 'fry toasts',
            'user_id': context.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': context.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': context.user['_id'],
        }, ])

        await facebook.handle(build_message({
            'text': 'list'
        }))

        await context.receive_answer('List of actual tasks:\n'
                                     '* fry toasts\n'
                                     '* fry eggs\n'
                                     '* drop cheese')
