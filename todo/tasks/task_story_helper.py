from botstory.ast import story_context
from todo.tasks import tasks_document


async def current_task(ctx):
    """
    get current task from ctx
    :param ctx:
    :return:
    """
    task_id = story_context.get_message_data(ctx, 'option', 'matches')[0]
    return await tasks_document.TaskDocument.objects.find_by_id(task_id)


async def last_task(ctx):
    return await tasks_document.TaskDocument.objects({
        'user_id': ctx['user']['_id'],
    }).sort(
        updated_at='desc',
    ).first()
