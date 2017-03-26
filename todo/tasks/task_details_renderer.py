import humanize


def done_task_payload(task):
    return 'CLOSE_TASK_{}'.format(task._id)


def open_task_payload(task):
    return 'OPEN_TASK_{}'.format(task._id)


def reopen_task_payload(task):
    return 'REOPEN_TASK_{}'.format(task._id)


def remove_task_payload(task):
    return 'REMOVE_TASK_{}'.format(task._id)


def start_task_payload(task):
    return 'START_TASK_{}'.format(task._id)


def stop_task_payload(task):
    return 'STOP_TASK_{}'.format(task._id)


async def render(story, user, task):
    status = getattr(task, 'status', 'Unknown')
    if status == 'in progress':
        buttons = [{
            'type': 'postback',
            'title': 'Stop',
            'payload': stop_task_payload(task),
        }, {
            'type': 'postback',
            'title': 'Done',
            'payload': done_task_payload(task),
        }, ]
    elif status == 'close':
        buttons = [{
            'type': 'postback',
            'title': 'Reopen',
            'payload': reopen_task_payload(task),
        }]
    else:
        buttons = [{
            'type': 'postback',
            'title': 'Start',
            'payload': start_task_payload(task),
        }]
        # open by default
        status = 'open'

    buttons.append({
        'type': 'postback',
        'title': 'Remove',
        'payload': remove_task_payload(task),
    })

    await story.send_template(
        payload={
            'template_type': 'generic',
            'elements': [{
                'title': 'Task: {}'.format(task.description),
                # TODO: maybe we could generate individual images for each task
                # 'image_url': 'https://petersfancybrownhats.com/company_image.png',
                'subtitle': 'Status: {}\n'
                            'Created: {}\n'.format(status,
                                                   humanize.naturaltime(task.created_at)),
                'buttons': buttons,
            }]
        },
        user=user
    )
