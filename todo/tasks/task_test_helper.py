import humanize
from todo.tasks import task_details_renderer


def assert_task_message(task,
                        ctx,
                        next_statuses):
    buttons = [{
                   'type': 'postback',
                   'title': status['title'],
                   'payload': status['payload'].format(task._id)}
               for status in next_statuses]
    buttons.append({
        'type': 'postback',
        'title': 'Remove',
        'payload': task_details_renderer.remove_task_payload(task),
    })

    ctx.receive_answer({
        'template_type': 'generic',
        'title': 'Task: {}'.format(task.description),
        'subtitle': 'Status: {}\n'
                    'Created: {}'.format(getattr(task, 'status', ''),
                                         humanize.naturaltime(task.created_at)),
        'buttons': buttons,
    })


__all__ = [assert_task_message]
