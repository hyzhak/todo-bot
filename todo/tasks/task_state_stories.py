from botstory.middlewares import option, text
import emoji
import logging
import re

from todo import orm
from todo.tasks import task_story_helper

logger = logging.getLogger(__name__)


def singular_vs_plural(singular):
    return ' was' if singular else 's were'


def setup(story):
    async def open_one_task(ctx, task):
        if task.state == 'open':
            await story.ask(
                'Task `{}` is already opened'.format(task.description),
                quick_replies=[{
                    'title': 'start',
                    'payload': 'START_TASK_{}'.format(task._id),
                }, {
                    'title': 'details',
                    'payload': 'TASK_DETAILS_{}'.format(task._id),
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                }, ],
                user=ctx['user'])
            return
        task.state = 'open'
        await task.save()
        await story.ask(
            emoji.emojize(':ok: Task `{}` was opened', use_aliases=True).format(task.description),
            quick_replies=[{
                'title': 'start',
                'payload': 'START_TASK_{}'.format(task._id),
            }, {
                'title': 'details',
                'payload': 'TASK_DETAILS_{}'.format(task._id),
            }, {
                'title': 'list tasks',
                'payload': 'LIST_TASKS_NEW_FIRST',
            }, ],
            user=ctx['user'])

    async def open_many_task(ctx, tasks):
        modified_descriptions = []
        for task in tasks:
            if task.state == 'done':
                task.state = 'open'
                await task.save()
                modified_descriptions.append(task.description)

        if len(modified_descriptions) == 0:
            await story.ask('There is no task to open',
                            quick_replies=[{
                                'title': 'add new task',
                                'payload': 'ADD_NEW_TASK',
                            }, {
                                'title': 'list tasks',
                                'payload': 'LIST_TASKS_NEW_FIRST',
                            },
                            ],
                            user=ctx['user'])
            return

        modified_descriptions_list = '\n'.join(
            [emoji.emojize(':white_check_mark: {}', use_aliases=True).format(t) for t in modified_descriptions])

        await story.ask(
            emoji.emojize(':ok: Task{} opened:\n{}', use_aliases=True).format(
                singular_vs_plural(len(modified_descriptions) == 1),
                modified_descriptions_list),
            quick_replies=[{
                'title': 'start all',
                'payload': 'START_ALL_TASKS',
            }, {
                'title': 'list tasks',
                'payload': 'LIST_TASKS_NEW_FIRST',
            },
            ],
            user=ctx['user'])

    async def start_one_task(ctx, task):
        if task.state == 'in progress':
            await story.ask(
                'Task `{}` is already in progress'.format(task.description),
                quick_replies=[{
                    'title': 'stop',
                    'payload': 'DONE_TASK_{}'.format(task._id),
                }, {
                    'title': 'done',
                    'payload': 'DONE_TASK_{}'.format(task._id),
                }, {
                    'title': 'details',
                    'payload': 'TASK_DETAILS_{}'.format(task._id),
                }, {
                    'title': 'stop',
                    'payload': 'STOP_TASK_{}'.format(task._id),
                }, ],
                user=ctx['user'])
            return
        task.state = 'in progress'
        await task.save()
        await story.ask(
            emoji.emojize(':ok: Task `{}` was started', use_aliases=True).format(task.description),
            quick_replies=[{
                'title': 'done',
                'payload': 'DONE_TASK_{}'.format(task._id),
            }, {
                'title': 'task details',
                'payload': 'TASK_DETAILS_{}'.format(task._id),
            }, {
                'title': 'stop',
                'payload': 'STOP_TASK_{}'.format(task._id),
            }, ],
            user=ctx['user'])

    async def start_many_task(ctx, tasks):
        modified_descriptions = []
        for task in tasks:
            if task.state == 'open':
                task.state = 'in progress'
                await task.save()
                modified_descriptions.append(task.description)

        if len(modified_descriptions) == 0:
            quick_replies = [{
                'title': 'add new task',
                'payload': 'ADD_NEW_TASK',
            }]
            if len(await task_story_helper.all_my_tasks(ctx)) > 0:
                quick_replies.append({
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                })
            await story.ask('There is no task to start',
                            quick_replies=quick_replies,
                            user=ctx['user'])
            return

        modified_descriptions_list = '\n'.join(
            [emoji.emojize(':white_check_mark: {}', use_aliases=True).format(t) for t in modified_descriptions])

        await story.ask(
            emoji.emojize(':ok: Task{} started:\n{}', use_aliases=True).format(
                singular_vs_plural(len(modified_descriptions) == 1),
                modified_descriptions_list),
            quick_replies=[{
                'title': 'stop all',
                'payload': 'STOP_ALL_TASKS',
            }, {
                'title': 'done all ',
                'payload': 'DONE_ALL_TASKS',
            }, {
                'title': 'list tasks',
                'payload': 'LIST_TASKS_NEW_FIRST',
            },
            ],
            user=ctx['user'])

    async def stop_one_task(ctx, task):
        if task.state == 'open':
            await story.ask(
                'Task `{}` is already stopped'.format(task.description),
                quick_replies=[{
                    'title': 'start',
                    'payload': 'START_TASK_{}'.format(task._id),
                }, {
                    'title': 'remove',
                    'payload': 'REMOVE_TASK_{}'.format(task._id),
                }, {
                    'title': 'details',
                    'payload': 'TASK_DETAILS_{}'.format(task._id),
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                },
                ],
                user=ctx['user'])
            return
        task.state = 'open'
        await task.save()
        await story.ask(
            emoji.emojize(':ok: Task `{}` was stopped', use_aliases=True).format(task.description),
            quick_replies=[{
                'title': 'start again',
                'payload': 'START_TASK_{}'.format(task._id),
            }, {
                'title': 'remove task',
                'payload': 'REMOVE_TASK_{}'.format(task._id),
            }, {
                'title': 'details',
                'payload': 'TASK_DETAILS_{}'.format(task._id),
            }, {
                'title': 'list tasks',
                'payload': 'LIST_TASKS_NEW_FIRST',
            },
            ],
            user=ctx['user'])

    async def stop_many_task(ctx, tasks):
        modified_descriptions = []
        for task in tasks:
            if task.state == 'in progress':
                task.state = 'open'
                await task.save()
                modified_descriptions.append(task.description)

        logger.debug('modified_descriptions')
        logger.debug(modified_descriptions)
        if len(modified_descriptions) == 0:
            await story.ask('There is no task to stop',
                            quick_replies=[{
                                'title': 'add new task',
                                'payload': 'ADD_NEW_TASK',
                            }, {
                                'title': 'list tasks',
                                'payload': 'LIST_TASKS_NEW_FIRST',
                            },
                            ],
                            user=ctx['user'])
            return

        modified_descriptions_list = '\n'.join(
            [emoji.emojize(':white_check_mark: {}', use_aliases=True).format(t) for t in modified_descriptions])

        await story.ask(
            emoji.emojize(':ok: Task{} stopped:\n{}', use_aliases=True).format(
                singular_vs_plural(len(modified_descriptions) == 1),
                modified_descriptions_list),
            quick_replies=[{
                'title': 'start all again',
                'payload': 'START_ALL_TASKS',
            }, {
                'title': 'remove all',
                'payload': 'REMOVE_ALL_TASKS',
            }, {
                'title': 'list tasks',
                'payload': 'LIST_TASKS_NEW_FIRST',
            },
            ],
            user=ctx['user'])

    async def done_one_task(ctx, task):
        if task.state == 'done':
            await story.ask(
                'Task `{}` is already done'.format(task.description),
                quick_replies=[{
                    'title': 'start',
                    'payload': 'START_TASK_{}'.format(task._id),
                }, {
                    'title': 'remove',
                    'payload': 'REMOVE_TASK_{}'.format(task._id),
                }, {
                    'title': 'details',
                    'payload': 'TASK_DETAILS_{}'.format(task._id),
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                }],
                user=ctx['user'])
            return
        task.state = 'done'
        await task.save()
        await story.ask(
            emoji.emojize(':ok: Task `{}` was done', use_aliases=True).format(task.description),
            quick_replies=[{
                'title': 'add new task',
                'payload': 'ADD_NEW_TASK',
            }, {
                'title': 'details about the next task',
                'payload': 'LAST_TASK_DETAILS',
            }, {
                'title': 'list tasks',
                'payload': 'LIST_TASKS_NEW_FIRST',

            }, ],
            user=ctx['user'])

    async def done_many_task(ctx, tasks):
        modified_descriptions = []
        for task in tasks:
            if task.state != 'done':
                task.state = 'done'
                await task.save()
                modified_descriptions.append(task.description)

        if len(modified_descriptions) == 0:
            await story.ask('There is no task to done',
                            quick_replies=[{
                                'title': 'add new task',
                                'payload': 'ADD_NEW_TASK',
                            }, {
                                'title': 'list tasks',
                                'payload': 'LIST_TASKS_NEW_FIRST',
                            },
                            ],
                            user=ctx['user'])
            return

        modified_descriptions_list = '\n'.join(
            [emoji.emojize(':white_check_mark: {}', use_aliases=True).format(t) for t in modified_descriptions])

        await story.ask(
            emoji.emojize(':ok: Task{} done:\n{}', use_aliases=True).format(
                singular_vs_plural(len(modified_descriptions) == 1),
                modified_descriptions_list),
            quick_replies=[{
                'title': 'reopen all',
                'payload': 'REOPEN_ALL_TASKS',
            }, {
                'title': 'add new task',
                'payload': 'ADD_NEW_TASK',
            }, {
                'title': 'list tasks',
                'payload': 'LIST_TASKS_NEW_FIRST',
            },
            ],
            user=ctx['user'])

    # postback commands

    @story.on(option.Match('REOPEN_TASK_(.+)'))
    def open_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                await open_one_task(ctx,
                                    task=await task_story_helper.current_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask(
                    emoji.emojize(':confused: I can\'t find that task. Do you mean something else?',
                                  use_aliases=True),
                    quick_replies=[{
                        'title': 'add new task',
                        'payload': 'ADD_NEW_TASK',
                    }, {
                        'title': 'list tasks',
                        'payload': 'LIST_TASKS_NEW_FIRST',
                    },
                    ],
                    user=ctx['user'],
                )

    @story.on(option.Match('STOP_TASK_(.+)'))
    def stop_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                await stop_one_task(ctx,
                                    task=await task_story_helper.current_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask(
                    emoji.emojize(':confused: I can\'t find that task. Do you mean something else?',
                                  use_aliases=True),
                    quick_replies=[{
                        'title': 'add new task',
                        'payload': 'ADD_NEW_TASK',
                    }, {
                        'title': 'list tasks',
                        'payload': 'LIST_TASKS_NEW_FIRST',
                    },
                    ],
                    user=ctx['user'],
                )

    @story.on(option.Match('DONE_TASK_(.+)'))
    def done_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                await done_one_task(ctx,
                                    task=await task_story_helper.current_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask(
                    emoji.emojize(':confused: I can\'t find that task. Do you mean something else?',
                                  use_aliases=True),
                    quick_replies=[{
                        'title': 'add new task',
                        'payload': 'ADD_NEW_TASK',
                    }, {
                        'title': 'list tasks',
                        'payload': 'LIST_TASKS_NEW_FIRST',
                    },
                    ],
                    user=ctx['user'],
                )

    @story.on(option.Match('START_TASK_(.+)'))
    def start_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                await start_one_task(ctx,
                                     task=await task_story_helper.current_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask(
                    emoji.emojize(':confused: I can\'t find that task. Do you mean something else?',
                                  use_aliases=True),
                    quick_replies=[{
                        'title': 'add new task',
                        'payload': 'ADD_NEW_TASK',
                    }, {
                        'title': 'list tasks',
                        'payload': 'LIST_TASKS_NEW_FIRST',
                    },
                    ],
                    user=ctx['user'],
                )

    @story.on(option.Match('START_TASKS_(.+)'))
    def start_few_of_my_tasks_story():
        @story.part()
        async def try_to_start_few_tasks(ctx):
            await start_many_task(ctx,
                                  tasks=await task_story_helper.current_tasks(ctx))

    # match "<do> last (task)"

    @story.on(text.Match('open last(?: task)?', flags=re.IGNORECASE))
    def open_last_task_story():
        @story.part()
        async def try_to_open_last_task(ctx):
            try:
                await open_one_task(ctx,
                                    task=await task_story_helper.last_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask('You do not have any task to open',
                                quick_replies=[{
                                    'title': 'add new task',
                                    'payload': 'ADD_NEW_TASK',
                                },
                                ],
                                user=ctx['user'])

    @story.on(text.Match('start last(?: task)?', flags=re.IGNORECASE))
    def start_last_task_story():
        @story.part()
        async def try_to_start_last_task(ctx):
            try:
                await start_one_task(ctx,
                                     task=await task_story_helper.last_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask('You do not have any task to start',
                                quick_replies=[{
                                    'title': 'add new task',
                                    'payload': 'ADD_NEW_TASK',
                                },
                                ],
                                user=ctx['user'])

    @story.on(text.Match('stop last(?: task)?', flags=re.IGNORECASE))
    def stop_last_task_story():
        @story.part()
        async def try_to_stop_last_task(ctx):
            try:
                await stop_one_task(ctx,
                                    task=await task_story_helper.last_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask('You do not have any task to stop',
                                quick_replies=[{
                                    'title': 'add new task',
                                    'payload': 'ADD_NEW_TASK',
                                },
                                ],
                                user=ctx['user'])

    @story.on(text.Match('done last(?: task)?', flags=re.IGNORECASE))
    def done_last_task_story():
        @story.part()
        async def try_to_done_last_task(ctx):
            try:
                await done_one_task(ctx,
                                    task=await task_story_helper.last_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask('You do not have any task to done',
                                quick_replies=[{
                                    'title': 'add new task',
                                    'payload': 'ADD_NEW_TASK',
                                },
                                ],
                                user=ctx['user'])

    # match "<do> all (task)"
    @story.on([
        option.Equal('REOPEN_ALL_TASK'),
        text.Match('open all(?: task)?', flags=re.IGNORECASE),
    ])
    def open_all_my_tasks_story():
        @story.part()
        async def try_to_open_all_tasks(ctx):
            await open_many_task(ctx,
                                 tasks=await task_story_helper.all_my_tasks(ctx))

    @story.on([
        option.Equal('START_ALL_TASK'),
        text.Match('start all(?: task)?', flags=re.IGNORECASE),
    ])
    def start_all_my_task_story():
        @story.part()
        async def try_to_start_all_tasks(ctx):
            await start_many_task(ctx,
                                  tasks=await task_story_helper.all_my_tasks(ctx))

    @story.on([
        option.Equal('STOP_ALL_TASK'),
        text.Match('stop all(?: task)?', flags=re.IGNORECASE),
    ])
    def stop_all_my_task_story():
        @story.part()
        async def try_to_stop_all_tasks(ctx):
            await stop_many_task(ctx,
                                 tasks=await task_story_helper.all_my_tasks(ctx))

    @story.on([
        option.Equal('DONE_ALL_TASK'),
        text.Match('done all(?: task)?', flags=re.IGNORECASE),
    ])
    def done_all_my_task_story():
        @story.part()
        async def try_to_done_all_tasks(ctx):
            await done_many_task(ctx,
                                 tasks=await task_story_helper.all_my_tasks(ctx))
