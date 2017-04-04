from botstory.middlewares.option.option import OnStart
import logging
import pytest
from todo.tasks import task_story_helper
from todo.test_helpers import env

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
async def test_quick_actions_on_start_task_already_in_progress(build_context):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks('in progress')
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
                    'title': 'stop',
                    'payload': 'STOP_TASK_{}'.format(last_task_id),
                }, {
                    'title': 'done',
                    'payload': 'DONE_TASK_{}'.format(last_task_id),
                }, {
                    'title': 'details',
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


@pytest.mark.asyncio
async def test_quick_actions_on_stop_task_already_stopped(build_context):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks(
            last_task_state='open')
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
                    'title': 'start',
                    'payload': 'START_TASK_{}'.format(last_task_id),
                }, {
                    'title': 'remove',
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


@pytest.mark.asyncio
async def test_quick_actions_on_done_task(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks(
            last_task_state='in progress')

        await ctx.dialog([
            # Alice:
            'done last',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'details about the next task',
                    'payload': 'LAST_TASK_DETAILS',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_done_task_that_already_is_done(build_context):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks(props=[
            None,
            None,
            {
                'state': 'done',
            }
        ])
        logger.debug('created_tasks')
        logger.debug(created_tasks)
        last_task_id = created_tasks[-1]._id

        await ctx.dialog([
            # Alice:
            'done last',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'start',
                    'payload': 'START_TASK_{}'.format(last_task_id),
                }, {
                    'title': 'remove',
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


@pytest.mark.asyncio
async def test_quick_actions_on_remove_task(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks(
            last_task_state='in progress')

        await ctx.dialog([
            # Alice:
            'remove last',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'details about the next task',
                    'payload': 'LAST_TASK_DETAILS',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_remove_task_but_got_none(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'remove last',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_start_all(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            'start all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'stop all',
                    'payload': 'STOP_ALL_TASKS',
                }, {
                    'title': 'done all ',
                    'payload': 'DONE_ALL_TASKS',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_start_all_but_got_none_to_start(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks([{
            'state': 'in progress',
        }, {
            'state': 'in progress',
        }, {
            'state': 'in progress',
        }])

        await ctx.dialog([
            # Alice:
            'start all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_start_all_but_got_none(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'start all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_stop_all(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            'stop all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'start all again',
                    'payload': 'START_ALL_TASKS',
                }, {
                    'title': 'remove all',
                    'payload': 'REMOVE_ALL_TASKS',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_stop_all_but_got_none_to_stop(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks(props=[{
            'state': 'open',
        }, {
            'state': 'open',
        }, {
            'state': 'open',
        }, ])

        await ctx.dialog([
            # Alice:
            'stop all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_done_all(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            'done all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'reopen all',
                    'payload': 'REOPEN_ALL_TASKS',
                }, {
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_done_all_but_got_none(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks(props=[{
            'state': 'done',
        }, {
            'state': 'done',
        }, {
            'state': 'done',
        }, ])

        await ctx.dialog([
            # Alice:
            'done all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_remove_all(build_context):
    async with build_context() as ctx:
        await ctx.add_test_tasks()

        await ctx.dialog([
            # Alice:
            'remove all',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'Sure, remove all!',
                    'payload': 'CONFIRM_REMOVE_ALL'
                }, {
                    'title': 'Nope.',
                    'payload': 'REFUSE_REMOVE_ALL'
                }],
            },
            # Alice:
            'yes',
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_start(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            env.build_postback(OnStart.DEFAULT_OPTION_PAYLOAD),
            # Bob:
            {
                'quick_actions': [{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                },
                ],
            },
        ])


@pytest.mark.asyncio
async def test_quick_actions_on_add_few_tasks(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'eggs and bacon',
        ])

        added_tasks = await task_story_helper.last_task(user=ctx.user,
                                                        count_of_tasks=2)

        await ctx.dialog([
            None,
            # Bob:
            {
                'quick_actions': [{
                    'title': 'start all of them',
                    'payload': 'START_TASKS_{}'.format(','.join([str(t._id) for t in added_tasks])),
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])
