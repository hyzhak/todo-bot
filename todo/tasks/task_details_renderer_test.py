import humanize
import pytest
import datetime
from todo.stories_test import build_context, build_like, build_message
from todo.tasks import task_details_renderer

__all__ = [build_context]


def assert_task_message(task, ctx):
    ctx.receive_answer({
        'template_type': 'generic',
        'title': 'Task: {}'.format(task.description),
        'subtitle': 'Status: {}\n'
                    'Created: {}\n'.format(task.status,
                                           humanize.naturaltime(task.created_at)),
        'buttons': [{
            'type': 'postback',
            'title': 'Re-Open',
            'payload': task_details_renderer.reopen_task_payload(task),
        }, {
            'type': 'postback',
            'title': 'Remove',
            'payload': task_details_renderer.remove_task_payload(task),
        }, {
            'type': 'next task',
            'title': 'Remove',
            'payload': task_details_renderer.open_task_payload(task),
        }, ],
    })


@pytest.mark.asyncio
async def test_render_task_details(build_context):
    async with build_context(use_app_stories=False) as ctx:
        facebook = ctx.fb_interface
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
        assert_task_message(target_task, ctx)
