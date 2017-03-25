import humanize
from todo.tasks import task_details_renderer


def assert_task_message(task, ctx):
    ctx.receive_answer({
        'template_type': 'generic',
        'title': 'Task: {}'.format(task.description),
        'subtitle': 'Status: {}\n'
                    'Created: {}\n'.format(getattr(task, 'status', ''),
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
            'type': 'postback',
            'title': 'Next Task',
            'payload': task_details_renderer.open_task_payload(task),
        }, ],
    })


__all__ = [assert_task_message]
