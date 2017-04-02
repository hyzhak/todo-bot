import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_quick_actions_for_new_task(build_context):
    async with build_context() as ctx:
        await ctx.dialog([
            # Alice:
            'buy a bread',

            # Bob:
            {
                'quick_actions': [
                    'start task',
                    'task details',
                    'list of tasks',
                ],
            },

            # we don't check payload of actions,
            # because it will require extra afford to check
            #
            # 'START_TASK_{}'.format(task_id)
            #
            # with just created task
        ])
