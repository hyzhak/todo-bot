import pytest
import datetime
from todo.tasks import task_details_renderer, task_test_helper
from todo.test_helpers import env

build_context = env.build_context


@pytest.mark.asyncio
async def test_render_task_details(build_context):
    async with build_context(use_app_stories=False) as ctx:
        story = ctx.story

        tasks = await ctx.add_tasks([{
            'description': 'coffee with friends',
            'user_id': ctx.user['_id'],
            'created_at': datetime.datetime(2017, 1, 1),
            'updated_at': datetime.datetime(2017, 1, 1),
            'status': 'close',
        }, {
            'description': 'go to gym',
            'user_id': ctx.user['_id'],
            'created_at': datetime.datetime(2017, 1, 2),
            'updated_at': datetime.datetime(2017, 1, 2),
            'status': 'in progress',
        }, {
            'description': 'go to work',
            'user_id': ctx.user['_id'],
            'created_at': datetime.datetime(2017, 1, 3),
            'updated_at': datetime.datetime(2017, 1, 3),
            'status': 'open',
        },
        ])

        target_task = tasks[0]

        await task_details_renderer.render(story, ctx.user, target_task)
        task_test_helper.assert_task_message(target_task, ctx)
