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
