import botstory
from botstory.middlewares import any, text
import datetime
import logging

from todo.tasks import document

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

    @story.on(receive=text.Match('list'))
    @story.on(receive=text.Match('todo'))
    def list_of_stories():
        @story.part()
        async def show_list_of_stories(message):
            logger.info('list of tasks')
            # TODO: should filter the last one
            # TODO: should have pagination
            tasks = await document.TaskDocument.objects.find({
                'user_id': message['user']['_id'],
            })
            tasks_page = '\n'.join('* {}'.format(t.description) for t in tasks)
            await story.say('List of actual tasks:\n{}'.format(tasks_page), user=message['user'])

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

            await document.TaskDocument(**{
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
