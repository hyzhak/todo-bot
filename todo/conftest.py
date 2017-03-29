import botstory
from botstory import di
from botstory.integrations import fb, mongodb, mockhttp
import datetime
import emoji
import logging
import os
import pytest
from todo import lists, stories, tasks
from todo.test_helpers import env

logger = logging.getLogger(__name__)


def all_emoji(text):
    return emoji.emojize(emoji.emojize(text), use_aliases=True)


@pytest.fixture
def build_context():
    class AsyncContext:
        def __init__(self, use_app_stories=True):
            self.use_app_stories = use_app_stories

        async def __aenter__(self):
            self.story = botstory.Story()
            logger.debug('di.injector.root')
            logger.debug(di.injector.root)
            logger.debug('after create story')
            self.fb_interface = self.story.use(
                fb.FBInterface(page_access_token='qwerty'))
            logger.debug('after use fb')
            self.db_interface = self.story.use(mongodb.MongodbInterface(
                uri=os.environ.get('MONGODB_URI', 'mongo'),
                db_name=os.environ.get('MONGODB_TEST_DB', 'test'),
            ))
            logger.debug('after use db')
            self.http_interface = self.story.use(mockhttp.MockHttpInterface())
            logger.debug('after use http')

            if self.use_app_stories:
                stories.setup(self.story)

            logger.debug('after setup stories')
            await self.story.start()
            logger.debug('after stadsrt stories')
            self.user = await self.db_interface.new_user(
                facebook_user_id='facebook_user_id',
            )
            self.session = await self.db_interface.new_session(
                user=self.user,
            )
            logger.debug('after create new user')

            lists.lists_document.setup(self.db_interface.db)
            self.lists_document = self.db_interface.db.get_collection('lists')
            await self.lists_document.drop()

            tasks.tasks_document.setup(self.db_interface.db)
            self.tasks_collection = self.db_interface.db.get_collection('tasks')
            await self.tasks_collection.drop()

            return self

        async def add_test_tasks(self, last_state='open'):
            return await self.add_tasks([{
                'description': 'coffee with friends',
                'user_id': self.user['_id'],
                'state': 'done',
                'created_at': datetime.datetime(2017, 1, 1),
                'updated_at': datetime.datetime(2017, 1, 1),
            }, {
                'description': 'go to gym',
                'user_id': self.user['_id'],
                'state': 'in progress',
                'created_at': datetime.datetime(2017, 1, 2),
                'updated_at': datetime.datetime(2017, 1, 2),
            }, {
                'description': 'go to work',
                'user_id': self.user['_id'],
                'state': last_state,
                'created_at': datetime.datetime(2017, 1, 3),
                'updated_at': datetime.datetime(2017, 1, 3),
            },
            ])

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.db_interface.clear_collections()
            if hasattr(self, 'tasks_collection'):
                await self.lists_document.drop()
                await self.tasks_collection.drop()
                await self.db_interface.db.get_collection('lists').drop()
            await self.story.stop()
            self.story.clear()
            self.db_interface = None

        async def add_tasks(self, new_tasks):
            added_tasks = []
            for t in new_tasks:
                assert 'description' in t
                assert 'user_id' in t
                _id = await self.tasks_collection.insert(t)
                task = await tasks.TaskDocument.objects.find_one({'_id': _id})
                added_tasks.append(task)

            return added_tasks

        async def add_lists(self, new_lists):
            for l in new_lists:
                assert 'name' in l
                assert 'user_id' in l
                await self.lists_document.insert(l)

        async def ask(self, data):
            await self.fb_interface.handle(env.build_message(data))

        async def dialog(self, dialog_sequence):
            # even if it is only one phrase we add empty answer to get dialog
            if len(dialog_sequence) == 1:
                dialog_sequence.append(None)

            for q_a in zip(
                    dialog_sequence[:-1][::2],
                    dialog_sequence[1:][::2],
            ):
                question = q_a[0]
                if question:
                    if isinstance(question, str):
                        question = {'text': all_emoji(
                            question
                        )}

                    if 'entry' in question:
                        await self.fb_interface.handle(question)
                    else:
                        await self.ask(question)

                answer = q_a[1]
                if answer:
                    self.receive_answer(answer)

        def was_asked_with_quick_replies(self, options):
            assert self.http_interface.post.call_count > 0
            _, obj = self.http_interface.post.call_args
            assert obj['json']['message']['quick_replies'] == options

        def was_asked_with_without_quick_replies(self):
            assert self.http_interface.post.call_count > 0
            _, obj = self.http_interface.post.call_args
            assert 'quick_replies' not in obj['json']['message']

        def receive_answer(self, message, **kwargs):
            assert self.http_interface.post.call_count > 0
            _, obj = self.http_interface.post.call_args
            assert 'json' in obj
            assert obj['json']['recipient']['id'] == self.user['facebook_user_id']

            if isinstance(message, list):
                list_of_messages = message
                posted_list = obj['json']['message']['attachment']['payload']['elements']
                for idx, message in enumerate(list_of_messages):
                    if isinstance(message, str):
                        assert posted_list[idx]['title'] == all_emoji(message)
                    else:
                        if 'title' in message:
                            assert posted_list[idx]['title'] == all_emoji(message['title'])
                        if 'subtitle' in message:
                            assert posted_list[idx]['subtitle'] == all_emoji(message['subtitle'])
                if 'next_button' in kwargs:
                    next_button_title = kwargs['next_button']
                    if next_button_title is None:
                        assert 'buttons' not in obj['json']['message']['attachment']['payload'] or \
                               obj['json']['message']['attachment']['payload']['buttons'] == []
                    else:
                        assert obj['json']['message']['attachment']['payload']['buttons'][0][
                                   'title'] == next_button_title
            elif 'template_type' in message:
                assert 'attachment' in obj['json']['message']
                assert 'payload' in obj['json']['message']['attachment']
                assert 'type' in obj['json']['message']['attachment']
                assert obj['json']['message']['attachment']['type'] == 'template'
                template_payload = obj['json']['message']['attachment']['payload']
                assert template_payload['template_type'] == message['template_type']
                template_elements = template_payload['elements']
                assert template_elements[0]['title'] == message['title']
                assert template_elements[0]['subtitle'] == message['subtitle']
                assert template_elements[0]['buttons'] == message['buttons']
            else:
                assert 'message' in obj['json']
                assert 'text' in obj['json']['message']
                assert obj['json']['message']['text'] == all_emoji(message)

    return AsyncContext
