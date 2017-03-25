import humanize


def open_task_payload(task):
    return 'OPEN_TASK_{}'.format(task._id)


def reopen_task_payload(task):
    return 'REOPEN_TASK_{}'.format(task._id)


def remove_task_payload(task):
    return 'REMOVE_TASK_{}'.format(task._id)


async def render(story, user, task):
    await story.send_template(
        payload={
            'template_type': 'generic',
            'elements': [{
                'title': 'Task: {}'.format(task.description),
                # TODO: maybe we could generate individual images for each task
                # 'image_url': 'https://petersfancybrownhats.com/company_image.png',
                'subtitle': 'Status: {}\n'
                            'Created: {}\n'.format(getattr(task, 'status', 'Unknown'),
                                                   humanize.naturaltime(task.created_at)),
                'buttons': [{
                    'type': 'postback',
                    'title': 'Re-Open',
                    'payload': reopen_task_payload(task),
                }, {
                    'type': 'postback',
                    'title': 'Remove',
                    'payload': remove_task_payload(task),
                }, {
                    'type': 'postback',
                    'title': 'Next Task',
                    'payload': open_task_payload(task),
                }, ],
            }]
        },
        user=user
    )
