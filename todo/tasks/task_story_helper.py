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


async def current_tasks(ctx):
    """
    get current tasks from ctx
    :param ctx:
    :return:
    """
    task_ids = story_context.get_message_data(ctx, 'option', 'matches')[0].split(',')

    tasks = []
    for task_id in task_ids:
        tasks.append(await tasks_document.TaskDocument.objects.find_by_id(task_id))
    return tasks


async def last_task(ctx=None, user=None, count_of_tasks=1):
    if ctx:
        user = ctx['user']

    cursor = tasks_document.TaskDocument.objects({
        'user_id': user['_id'],
    }).sort(
        updated_at='desc',
    )

    if count_of_tasks == 1:
        return await cursor.first()

    return reversed(await cursor.limit(count_of_tasks))


async def all_my_tasks(ctx):
    return await tasks_document.TaskDocument.objects.find({
        'user_id': ctx['user']['_id'],
    })
