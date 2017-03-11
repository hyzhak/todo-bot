import botstory
from botstory.ast import story_context
from botstory.middlewares import any, option, text
import datetime
import emoji
import logging
import os

from todo import pagination_list, reflection
from todo.lists import lists_document
from todo.tasks import tasks_document

logger = logging.getLogger(__name__)

logger.debug('parse stories')


def setup(story):
    pagination_list.setup(story)

    @story.on_start()
    def on_start_story():
        """
        User just pressed `get started` button so we can greet him
        """

        @story.part()
        async def greetings(message):
            logger.info('greetings')
            await story.say('<Motivate user to act>', message['user'])

    @story.on(text.text.EqualCaseIgnore('all'))
    def list_of_lists_story():
        @story.part()
        async def show_list_of_stories(ctx):
            logger.info('list of tasks')
            # TODO: remove return solve one test, but why?
            return await pagination_list.pagination_loop(
                list_title='All lists:',
                target_document=reflection.class_to_str(lists_document.ListDocument),
                title_field='name',
                page_length=os.environ.get('LIST_PAGE_LENGTH', 5),
                **ctx,
            )

    @story.on([text.text.EqualCaseIgnore('list'),
               text.text.EqualCaseIgnore('todo')])
    def list_of_tasks_story():
        @story.part()
        async def list_of_tasks(ctx):
            logger.info('list of tasks')
            # TODO: should filter the last one

            return await pagination_list.pagination_loop(
                ctx,
                list_title='List of actual tasks:',
                target_document=reflection.class_to_str(tasks_document.TaskDocument),
                title_field='description',
                page_length=os.environ.get('LIST_PAGE_LENGTH', 5),
            )

    @story.on(text.text.EqualCaseIgnore('new list'))
    def new_list_tasks_story():
        @story.part()
        async def ask_name(message):
            logger.info('new list')
            return await story.ask(
                'You are about to create new list of tasks.\nWhat is the name of it?',
                user=message['user'],
            )

        @story.part()
        async def create_list(ctx):
            logger.info('create list')
            list_name = text.get_raw_text(ctx)
            new_list = await lists_document.ListDocument(**{
                'user_id': ctx['user']['_id'],
                'name': list_name,
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(),
            }).save()
            await story.say('You\'ve just created list of tasks: '
                            '`{}`.\n'
                            'Now you can add tasks to it.'.format(list_name), user=ctx['user'])

    @story.on([
        text.Match('delete last'),
        text.Match('drop last'),
        text.Match('forget about last'),
        text.Match('kill last'),
        text.Match('remove last'),
    ])
    def remove_last_job_story():
        @story.part()
        async def remove_last_job(ctx):
            logger.info('remove last job')
            jobs = await tasks_document.TaskDocument.objects({
                'user_id': ctx['user']['_id'],
            }).sort(
                updated_at='desc',
            )

            logger.debug('jobs')
            logger.debug(jobs)

            last_job = (await tasks_document.TaskDocument.objects({
                'user_id': ctx['user']['_id'],
            }).sort(
                updated_at='desc',
            ).limit(1))[0]
            logger.debug(last_job.fields)
            desc = last_job.description
            logger.debug('going to remove job `{}`'.format(desc))
            # await tasks_document.TaskDocument.objects.delete_one({
            #     '_id': last_job._id,
            # })
            msg = emoji.emojize(':skull: job `{}` was removed'.format(desc))
            logger.info(msg)
            await story.say(msg, user=ctx['user'])

    @story.on([
        text.Match('delete (.*)'),
        text.Match('drop (.*)'),
        text.Match('forget about (.*)'),
        text.Match('kill (.*)'),
        text.Match('remove (.*)'),
    ])
    def remove_something_story():
        """
        got request to remove something (list or task)
        """

        @story.part()
        async def remove_list_or_task(ctx):
            logger.info('remove list or task')
            target = story_context.get_message_data(ctx)['text']['matches'][0]
            logger.info('target {}'.format(target))

            count = await lists_document.ListDocument.objects({
                'name': target,
                'user_id': ctx['user']['_id'],
            }).delete()
            logger.info('remove {} lists'.format(count))
            if count > 0:
                await story.say(emoji.emojize(':skull: List {} was removed'.format(target)),
                                user=ctx['user'])
                return

            await story.say('We can\'t find `{}` what do you want to remove?'.format(target),
                            user=ctx['user'])
            # TODO: try to remove task
            # if count == 0:

    @story.on(receive=text.Any())
    def new_task_story():
        """
        Any text that doesn't match specific cases
        consider as new task
        """

        @story.part()
        async def add_new_task(ctx):
            logger.info('new task')
            task_description = text.get_raw_text(ctx)

            await tasks_document.TaskDocument(**{
                'user_id': ctx['user']['_id'],
                'list': 'list_1',
                'description': task_description,
                'state': 'new',
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(),
            }).save()

            await story.say('Task `{}` was added to the job list.'.format(task_description), ctx['user'])

    @story.on(receive=any.Any())
    def any_story():
        """
        And all the rest messages as well
        """

        @story.part()
        async def something_else(message):
            logger.info('something_else')
            await story.say('<React on unknown message>', message['user'])
