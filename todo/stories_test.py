import aiohttp
import botstory
from botstory.integrations import fb, mongodb, mockdb, mockhttp
import datetime
import os
import pytest
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
            # self.db_interface = self.story.use(
            #     mongodb.MongodbInterface(uri=os.environ.get('MONGODB_URI', 'mongo'),
            #                              db_name=os.environ.get('MONGODB_TEST_DB', 'test')))
            self.db_interface = self.story.use(mockdb.MockDB())
            self.http_interface = self.story.use(mockhttp.MockHttpInterface())

            stories.setup(self.story)
            await self.story.start()
            # return fb_interface, story
            # await self.db_interface.start()
            # await self.db_interface.clear_collections()
            # return self.db_interface
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.story.stop()
            # await self.db_interface.clear_collections()
            self.db_interface = None

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

        # TODO: mock task document
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
