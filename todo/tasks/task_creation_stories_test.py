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
async def test_add_simple_task(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'Buy a bread',
            # Bob:
            ':ok: Task `Buy a bread` was added',
        ])


@pytest.mark.asyncio
@pytest.mark.skip('advanced feature')
async def test_add_simple_task_(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'gonna buy a bread',
            'I going to buy a bread',
            'I should to buy a bread',
            'I need to buy a bread',
            'I want to buy a bread',
            # Bob:
            ':ok: Task `Buy a bread` was added',
        ])


@pytest.mark.asyncio
async def test_add_few_tasks_from_sequence_of_actions(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'Tom, Dick and Harry',
            # Bob:
            'Tasks were added:\n'
            ':white_medium_square: Tom\n'
            ':white_medium_square: Dick\n'
            ':white_medium_square: Harry',
        ])

        res_lists = await tasks.TaskDocument.objects.find({
            'user_id': ctx.user['_id'],
        })

        assert len(res_lists) == 3
        assert res_lists[0].description == 'Tom'
        assert res_lists[1].description == 'Dick'
        assert res_lists[2].description == 'Harry'


@pytest.mark.asyncio
async def test_add_task_on_postback_message(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            env.build_postback('ADD_NEW_TASK'),

            # Bob:
            'Please enter the name of your task (max 140 symbols).\n'
            ':information_source: You can also enumerate tasks by comma (get laptop, charger, passport).',

            # Alice:
            'Buy a bread',

            # Bob:
            ':ok: Task `Buy a bread` was added',
        ])


@pytest.mark.asyncio
async def test_add_task_on_text_message(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'Add new task',

            # Bob:
            'Please enter the name of your task (max 140 symbols).\n'
            ':information_source: You can also enumerate tasks by comma (get laptop, charger, passport).',
        ])


@pytest.mark.asyncio
async def test_cancel_add_task_on_postback_message(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            env.build_postback('ADD_NEW_TASK'),

            # Bob:
            {
                'text': 'Please enter the name of your task (max 140 symbols).\n'
                        ':information_source: You can also enumerate tasks by comma (get laptop, charger, passport).',
                'quick_replies': [{
                    'title': 'cancel',
                    'payload': 'CANCEL',
                }],
            },

            # Alice:
            'Cancel',

            # Bob:
            {
                'text': 'OK, lets create task next time.',
                'quick_replies': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                }],
            },
        ])
