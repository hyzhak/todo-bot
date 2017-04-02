import logging
import pytest
from todo.tasks import task_story_helper

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_quick_actions_for_new_task(build_context):
    async with build_context() as app_ctx:
        await app_ctx.dialog([
            # Alice:
            'buy a bread',
        ])

        task_id = (await task_story_helper.last_task(user=app_ctx.user))._id
        await app_ctx.dialog([
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
                    'title': 'list of tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
            },
        ])
