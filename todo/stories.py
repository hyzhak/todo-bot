import botstory
from botstory.middlewares import any, text
import datetime
import logging

from todo.lists import lists_document
from todo.tasks import tasks_document

logger = logging.getLogger(__name__)

logger.debug('parse stories')


def setup(story):
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
        async def show_list_of_stories(message):
            logger.info('list of tasks')
            # TODO: should have pagination
            lists = await lists_document.ListDocument.objects.find({
                'user_id': message['user']['_id'],
            })
            logger.info('lists:')
            logger.info(lists)
            lists_page = '\n'.join(':white_small_square: {}'.format(l.name) for l in lists)
            await story.say('All lists:\n{}'.format(lists_page), user=message['user'])

    @story.on(text.text.EqualCaseIgnore('list'))
    @story.on(text.text.EqualCaseIgnore('todo'))
    def list_of_tasks_story():
        @story.part()
        async def show_list_of_tasks(message):
            logger.info('list of tasks')
            # TODO: should filter the last one
            # TODO: should have pagination
            tasks = await tasks_document.TaskDocument.objects.find({
                'user_id': message['user']['_id'],
            })
            tasks_page = '\n'.join('* {}'.format(t.description) for t in tasks)
            await story.say('List of actual tasks:\n{}'.format(tasks_page), user=message['user'])

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
        async def create_list(message):
            logger.info('create list')
            list_name = message['data']['text']['raw']
            new_list = await lists_document.ListDocument(**{
                'user_id': message['user']['_id'],
                'name': list_name,
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(),
            }).save()
            await story.say('You\'ve just created list of tasks: '
                            '`{}`.\n'
                            'Now you can add tasks to it.'.format(list_name), user=message['user'])

    @story.on(text.Match('remove (.*)'))
    def remove_something_story():
        """
        got request to remove something (list or task)
        """

        @story.part()
        async def remove_list_or_task(ctx):
            logger.info('remove list or task')
            target = ctx['data']['text']['matches'][0]
            logger.info('target {}'.format(target))

            count = await lists_document.ListDocument.objects({
                'name': target,
                'user_id': ctx['user']['_id'],
            }).delete()
            logger.info('remove {} lists'.format(count))
            if count > 0:
                await story.say(':skull: List {} was removed'.format(target),
                                user=ctx['user'])
                return

            # TODO: try to remove task
            # if count == 0:

    @story.on(receive=text.Any())
    def new_task_story():
        """
        Any text that doesn't match specific cases
        consider as new task
        """

        @story.part()
        async def add_new_task(message):
            logger.info('new task')
            task_description = message['data']['text']['raw']

            await tasks_document.TaskDocument(**{
                'user_id': message['user']['_id'],
                'list': 'list_1',
                'description': task_description,
                'state': 'new',
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(),
            }).save()

            await story.say('Task `{}` was added to the job list.'.format(task_description), message['user'])

    @story.on(receive=any.Any())
    def any_story():
        """
        And all the rest messages as well
        """

        @story.part()
        async def something_else(message):
            logger.info('something_else')
            await story.say('<React on unknown message>', message['user'])
