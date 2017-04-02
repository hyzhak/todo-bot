import logging
import pytest
from todo.tasks import task_story_helper

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_quick_actions_for_new_task(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'buy a bread',
        ])

        task_id = (await task_story_helper.last_task(user=ctx.user))._id
        await ctx.dialog([
            None,
            # Bob:
            {
                'quick_actions': [{
                    'title': 'start task',
                    'payload': 'START_TASK_{}'.format(task_id),
                }, {
                    'title': 'task details',
                    'payload': 'TASK_DETAILS_{}'.format(task_id),
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_start_task(build_context):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks()
        last_task_id = created_tasks[-1]._id

        await ctx.dialog([
            # Alice:
            'start last',
        ])

        await ctx.dialog([
            None,
            # Bob:
            {
                'quick_actions': [{
                    'title': 'done',
                    'payload': 'DONE_TASK_{}'.format(last_task_id),
                }, {
                    'title': 'task details',
                    'payload': 'TASK_DETAILS_{}'.format(last_task_id),
                }, {
                    'title': 'stop',
                    'payload': 'STOP_TASK_{}'.format(last_task_id),
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_stop_task(build_context):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks(
            last_task_state='in progress')
        last_task_id = created_tasks[-1]._id

        await ctx.dialog([
            # Alice:
            'stop last',
        ])

        await ctx.dialog([
            None,
            # Bob:
            {
                'quick_actions': [{
                    'title': 'start again',
                    'payload': 'START_TASK_{}'.format(last_task_id),
                }, {
                    'title': 'remove task',
                    'payload': 'REMOVE_TASK_{}'.format(last_task_id),
                }, {
                    'title': 'details',
                    'payload': 'TASK_DETAILS_{}'.format(last_task_id),
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])