import aiohttp
from botstory.middlewares import sticker
import datetime
import logging
import os
import pytest
from todo import lists, tasks, pagination_list, stories
from todo.tasks import task_test_helper, tasks_document
from todo.test_helpers import env
from unittest import mock

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_new_task_story(build_context, mocker):
    async with build_context() as ctx:
        facebook = ctx.fb_interface

        task = mock.Mock()
        task.save = aiohttp.test_utils.make_mocked_coro()
        mocker.patch.object(stories.tasks_document, 'TaskDocument', return_value=task)

        await facebook.handle(env.build_message({
            'text': 'hello world!'
        }))

        assert stories.tasks_document.TaskDocument.called
        _, obj = stories.tasks_document.TaskDocument.call_args

        assert obj['list'] == 'list_1'
        assert obj['description'] == 'hello world!'
        assert obj['state'] == 'open'
        assert 'created_at' in obj
        assert 'updated_at' in obj

        task.save.assert_called_with()


@pytest.mark.parametrize('command',
                         [
                             'list',
                             'list tasks',
                             'todo',
                             env.build_postback('LIST_TASKS_NEW_FIRST'),
                         ])
@pytest.mark.asyncio
async def test_list_of_active_tasks_on_list(build_context, command):
    async with build_context() as ctx:
        facebook = ctx.fb_interface

        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
            'state': 'open',
            # 'created_at': datetime.datetime.now(),
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
            'state': 'open',
            # 'created_at': datetime.datetime.now(),
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
            # 'state': 'open',
            # 'created_at': datetime.datetime.now(),
        }, ])

        await ctx.dialog([
            # Alice
            command,
        ])

        ctx.receive_answer([
            # Bob
            'fry toasts',
            'fry eggs',
            'drop cheese',
        ], next_button=None)


@pytest.mark.asyncio
async def test_pagination_of_list_of_active_tasks(build_context, monkeypatch):
    async with build_context() as ctx:
        command = 'todo'
        facebook = ctx.fb_interface

        monkeypatch.setattr(os, 'environ', {
            'LIST_PAGE_LENGTH': 2,
        })

        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
            'state': 'open',
            'created_at': datetime.datetime.now(),
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
            'state': 'open',
            'created_at': datetime.datetime.now(),
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
            'state': 'open',
            'created_at': datetime.datetime.now(),
        }, {
            'description': 'serve',
            'user_id': ctx.user['_id'],
            'state': 'open',
            'created_at': datetime.datetime.now(),
        }, {
            'description': 'eat',
            'user_id': ctx.user['_id'],
            'state': 'open',
            'created_at': datetime.datetime.now(),
        }, ])

        await facebook.handle(env.build_message({
            'text': command,
        }))

        ctx.receive_answer([
            'fry toasts',
            'fry eggs',
        ], next_button='More')

        await facebook.handle(env.build_message({
            'text': 'next',
        }))

        ctx.receive_answer([
            'drop cheese',
            'serve',
        ], next_button='More')

        await facebook.handle(env.build_message({
            'text': 'next',
        }))

        ctx.receive_answer([
            'eat',
        ], next_button=None)


@pytest.mark.asyncio
async def test_after_the_end_of_infinity_list_of_active_tasks(build_context, monkeypatch):
    async with build_context() as ctx:
        command = 'todo'

        monkeypatch.setattr(os, 'environ', {
            'LIST_PAGE_LENGTH': 2,
        })

        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
        }, ])

        # here we have just reach the end of list.
        # so any other message should propagate to global matches
        # and word `next` will be considered as new task

        ctx.dialog([
            # Alice:
            command, None,
            # Alice:
            'next', None,
            # Alice:
            'next',
            # Bob:
            ':ok: Task `next` was added',
        ])


@pytest.mark.asyncio
async def test_immediatly_reach_the_end_of_pagination_list_and_all_upcoming_commands_are_leaking_to_global_scope(
        build_context, monkeypatch):
    async with build_context() as ctx:
        command = 'todo'

        monkeypatch.setattr(os, 'environ', {
            'LIST_PAGE_LENGTH': 5,
        })

        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
        }, ])

        # here we have just immediately reach the end of list.
        # so any other message should propagate to global matches
        # and word `next` will be considered as new task
        await ctx.dialog([
            # Alice:
            'todo',
            None,
            # Alice:
            'next',
            # Bob:
            ':ok: Task `next` was added',
        ])


@pytest.mark.asyncio
async def test_list_of_active_tasks_on_new_list(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'new list',
            # Bob:
            'You are about to create new list of tasks.\n'
            'What is the name of it?',
            # Alice:
            'My Favorite List',
            # Bob:
            'You\'ve just created list of tasks: `My Favorite List`.\n'
            'Now you can add tasks to it.'
        ])


@pytest.mark.asyncio
async def test_list_all_lists(build_context):
    async with build_context() as ctx:
        await ctx.add_lists([{
            'name': 'google calendar events',
            'user_id': ctx.user['_id'],
        }, {
            'name': 'grocery store',
            'user_id': ctx.user['_id'],
        }, {
            'name': 'travel to Sri Lanka',
            'user_id': ctx.user['_id'],
        },
        ])

        await ctx.dialog([
            # Alice:
            'all',
            # Bob:
            '\n'.join([
                'All lists:',
                ':white_medium_square: google calendar events',
                ':white_medium_square: grocery store',
                ':white_medium_square: travel to Sri Lanka',
                '',
                pagination_list.BORDER,
            ])
        ])


@pytest.mark.parametrize('command',
                         ['delete', 'drop', 'forget about', 'kill', 'remove'])
@pytest.mark.asyncio
async def test_remove_list(build_context, command):
    async with build_context() as ctx:
        await ctx.add_lists([{
            'name': 'morning business',
            'user_id': ctx.user['_id'],
        }, {
            'name': 'noon business',
            'user_id': ctx.user['_id'],
        }, {
            'name': 'night shift',
            'user_id': ctx.user['_id'],
        },
        ])

        await ctx.dialog([
            # Alice:
            '{} night shift'.format(command),
            # Bob:
            ':ok: List `night shift` was removed',
        ])

        res_lists = await lists.ListDocument.objects.find({
            'user_id': ctx.user['_id'],
        })

        assert len(res_lists) == 2
        assert all(
            l.name != 'night shift' for l in res_lists
        )


@pytest.mark.asyncio
async def test_ask_again_if_we_can_find_what_to_remove(build_context):
    async with build_context() as ctx:
        await ctx.add_lists([{
            'name': 'morning business',
            'user_id': ctx.user['_id'],
        }, {
            'name': 'noon business',
            'user_id': ctx.user['_id'],
        }, {
            'name': 'night shift',
            'user_id': ctx.user['_id'],
        },
        ])

        await ctx.dialog([
            # Alice:
            'remove uncertainty',
            # Bob:
            ':confused: We can\'t find `uncertainty` what do you want to remove?',
        ])

        res_lists = await lists.ListDocument.objects.find({
            'user_id': ctx.user['_id'],
        })

        assert len(res_lists) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize('command',
                         ['delete last', 'drop last', 'forget about last', 'kill last', 'remove last', 'remove next',
                          env.build_postback('REMOVE_LAST_TASK')])
async def test_remove_last_added_task(build_context, command):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            command,
            # Bob:
            ':ok: task `go to work` was removed'
        ])

        res_lists = await tasks.TaskDocument.objects.find({
            'user_id': ctx.user['_id'],
        })

        assert len(res_lists) == 2
        assert all(
            l.description != 'go to work' for l in res_lists
        )


@pytest.mark.asyncio
async def test_remove_certain_task_by_complete_name(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            'remove go to gym',
            # Bob:
            ':ok: Task `go to gym` was removed'
        ])

        res_lists = await tasks.TaskDocument.objects.find({
            'user_id': ctx.user['_id'],
        })

        assert len(res_lists) == 2
        assert all(
            l.description != 'go to gym' for l in res_lists
        )


@pytest.mark.asyncio
async def test_remove_last_warn_if_we_do_not_have_any_tickets_now(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'delete last',
            # Bob:
            'You don\'t have any tickets yet.\n'
            ':information_source: Please send my few words about it and I will add it to your TODO list.',
        ])


@pytest.mark.asyncio
@pytest.mark.parametrize('command',
                         ['delete all', 'delete all tasks', 'delete all jobs',
                          env.build_postback('REMOVE_ALL_TASKS')])
async def test_remove_all_task(build_context, command):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            command,
            # Bob:
            ':question: Do you really want to remove all your tasks '
            'of current list?',
            # Alice:
            'ok',
            # Bob:
            ':ok: 3 tasks were removed',
        ])

        res_lists = await tasks.TaskDocument.objects.find({
            'user_id': ctx.user['_id'],
        })

        assert len(res_lists) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(('answer', 'removed'),
                         [({'text': 'ok'}, True),
                          ({'text': 'Yes'}, True),
                          # TODO:
                          ({'sticker_id': sticker.SMALL_LIKE}, True),
                          ({'text': '', 'quick_reply': {'payload': 'CONFIRM_REMOVE_ALL'}}, True),
                          ({'text': 'no'}, False),
                          ({'text': 'qwerty'}, False),
                          ({'text': '', 'quick_reply': {'payload': 'REFUSE_REMOVE_ALL'}}, False),
                          ])
async def test_remove_all_tasks_answer_in_different_way(build_context, answer, removed):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice::
            'delete all',
            # Bob:
            ':question: Do you really want to remove all your tasks '
            'of current list?',
            # Alice::
            answer,
            # Bob:
            ':ok: 3 tasks were removed' if removed
            else None,
        ])

        res_lists = await tasks.TaskDocument.objects.find({
            'user_id': ctx.user['_id'],
        })

        if removed:
            assert len(res_lists) == 0
        else:
            assert len(res_lists) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize('command', [
    'details',
    'last task',
    'last',
    'next details',
    'next task',
    'task details',
    env.build_postback('LAST_TASK_DETAILS'),
])
async def test_show_task_details_on_last_task(build_context, command):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks()

        # Alice:
        await ctx.dialog([
            command,
        ])

        # Bob:
        task_test_helper.assert_task_message(created_tasks[-1],
                                             ctx,
                                             next_states=[{
                                                 'title': 'Start',
                                                 'payload': 'START_TASK_{}',
                                             }])


@pytest.mark.asyncio
async def test_react_on_last_task_when_there_is_no_any_task_yet(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'last task',
            # Bob:
            'There is no last task yet. Please add few.',
        ])


@pytest.mark.asyncio
@pytest.mark.parametrize(('current_states', 'next_states'),
                         [
                             ('open', [
                                 {'payload': 'START_TASK_{}', 'title': 'Start'}
                             ]),
                             ('in progress', [
                                 {'payload': 'STOP_TASK_{}', 'title': 'Stop'},
                                 {'payload': 'DONE_TASK_{}', 'title': 'Done'}
                             ]),
                             ('done', [
                                 {'payload': 'REOPEN_TASK_{}', 'title': 'Reopen'}
                             ]),
                         ])
async def test_send_task_details(build_context, current_states, next_states):
    async with build_context() as ctx:
        facebook = ctx.fb_interface
        created_tasks = await ctx.add_tasks([{
            'description': 'coffee with friends',
            'user_id': ctx.user['_id'],
            'state': 'done',
            'created_at': datetime.datetime(2017, 1, 1),
            'updated_at': datetime.datetime(2017, 1, 1),
        }, {
            'description': 'go to gym',
            'user_id': ctx.user['_id'],
            'state': current_states,
            'created_at': datetime.datetime(2017, 1, 2),
            'updated_at': datetime.datetime(2017, 1, 2),
        }, {
            'description': 'go to work',
            'user_id': ctx.user['_id'],
            'state': 'open',
            'created_at': datetime.datetime(2017, 1, 3),
            'updated_at': datetime.datetime(2017, 1, 3),
        },
        ])

        target_task = created_tasks[1]

        # Alice:
        await facebook.handle(env.build_postback(
            'TASK_DETAILS_{}'.format(target_task._id)))

        # Bob:
        task_test_helper.assert_task_message(target_task,
                                             ctx,
                                             next_states=next_states)


@pytest.mark.asyncio
async def test_show_details_of_task_by_exact_description(build_context):
    async with build_context() as ctx:
        facebook = ctx.fb_interface
        created_tasks = await ctx.add_test_tasks()

        # Alice:
        await facebook.handle(env.build_text(
            'see go to work',
        ))

        # Bob:
        task_test_helper.assert_task_message(created_tasks[2],
                                             ctx,
                                             next_states=[{
                                                 'title': 'Start',
                                                 'payload': 'START_TASK_{}',
                                             }])


@pytest.mark.asyncio
async def test_remove_task_by_postback(build_context):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            env.build_postback('REMOVE_TASK_{}'.format(created_tasks[0]._id)),
            # Bob:
            {
                'text': ':ok: Task `{}` was deleted'.format(created_tasks[0].description),
                'quick_replies': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ]
            },
        ])
        tasks_left = await tasks_document.TaskDocument.objects.find()
        assert len(tasks_left) == 2


@pytest.mark.asyncio
async def test_remove_task_by_postback_fail_if_wrong_id(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            env.build_postback('REMOVE_TASK_58d99754e61713000143a2e1'),
            # Bob:
            {
                'text': ':confused: Can\'t find task.\n'
                        'It seems that it was already removed.',
                'quick_replies': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                }],
            }
        ])
        tasks_left = await tasks_document.TaskDocument.objects.find()
        assert len(tasks_left) == 3


@pytest.mark.asyncio
async def test_react_on_unknown_command(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            env.build_postback('WRONG_POSTBACK_MESSGE'),

            # Bob:
            {
                'text': ':confused: Sorry I don\'t know, how to react on such message yet.\n'
                        'Here are few things that you can do quickly',
                'quick_replies': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                }],
            },
        ])
