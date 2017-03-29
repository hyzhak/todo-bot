from botstory.middlewares import option, text
import emoji
import logging

from todo import orm
from todo.tasks import task_story_helper

logger = logging.getLogger(__name__)


def setup(story):
    @story.on(option.Match('REOPEN_TASK_(.+)'))
    def open_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                task = await task_story_helper.current_task(ctx)
                if task.state == 'open':
                    await story.say(
                        'Task `{}` is already opened'.format(task.description),
                        user=ctx['user'])
                    return
                task.state = 'open'
                await task.save()
                await story.say(
                    emoji.emojize(':ok: Task `{}` was opened', use_aliases=True).format(task.description),
                    user=ctx['user'])
            except orm.errors.DoesNotExist:
                pass

    @story.on(option.Match('STOP_TASK_(.+)'))
    def stop_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                task = await task_story_helper.current_task(ctx)
                if task.state == 'open':
                    await story.say(
                        'Task `{}` is already opened'.format(task.description),
                        user=ctx['user'])
                    return
                task.state = 'open'
                await task.save()
                await story.say(
                    emoji.emojize(':ok: Task `{}` was stopped', use_aliases=True).format(task.description),
                    user=ctx['user'])
            except orm.errors.DoesNotExist:
                pass

    @story.on(option.Match('DONE_TASK_(.+)'))
    def done_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                task = await task_story_helper.current_task(ctx)
                if task.state == 'done':
                    await story.say(
                        'Task `{}` is already done'.format(task.description),
                        user=ctx['user'])
                    return
                task.state = 'done'
                await task.save()
                await story.say(
                    emoji.emojize(':ok: Task `{}` was done', use_aliases=True).format(task.description),
                    user=ctx['user'])
            except orm.errors.DoesNotExist:
                pass

    @story.on(option.Match('START_TASK_(.+)'))
    def start_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                task = await task_story_helper.current_task(ctx)
                if task.state == 'in progress':
                    await story.say(
                        'Task `{}` is already in progress'.format(task.description),
                        user=ctx['user'])
                    return
                task.state = 'in progress'
                await task.save()
                await story.say(
                    emoji.emojize(':ok: Task `{}` was started', use_aliases=True).format(task.description),
                    user=ctx['user'])
            except orm.errors.DoesNotExist:
                pass

    @story.on(text.Match('open last(?: task)?'))
    def open_last_task_story():
        @story.part()
        async def try_to_open_last_task(ctx):
            try:
                task = await task_story_helper.last_task(ctx)
                if task.state == 'open':
                    await story.say(
                        'Task `{}` is already opened'.format(task.description),
                        user=ctx['user'])
                    return
                task.state = 'open'
                await task.save()
                await story.say(
                    emoji.emojize(':ok: Task `{}` was opened', use_aliases=True).format(task.description),
                    user=ctx['user'])
            except orm.errors.DoesNotExist:
                pass
