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
        ctx.dialog([
            # Alice:
            'Buy a bread',
            # Bob:
            'Task `Buy a bread` was added to the job list.',
        ])
