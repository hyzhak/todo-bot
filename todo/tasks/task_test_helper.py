import humanize
from todo.tasks import task_details_renderer


def assert_task_message(task,
                        ctx,
                        next_states):
    buttons = [{
                   'type': 'postback',
                   'title': state['title'],
                   'payload': state['payload'].format(task._id)}
               for state in next_states]
    buttons.append({
        'type': 'postback',
        'title': 'Remove',
        'payload': task_details_renderer.remove_task_payload(task),
    })

    ctx.receive_answer({
        'template_type': 'generic',
        'title': 'Task: {}'.format(task.description),
        'subtitle': 'State: {}\n'
                    'Created: {}'.format(getattr(task, 'state', ''),
                                         humanize.naturaltime(task.created_at)),
        'buttons': buttons,
    })

__all__ = [assert_task_message]
