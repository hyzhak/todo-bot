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
            # TODO:
            # 1) get db
            # tasks = mongo.db.get_collection('tasks')
            #
            # # 2) store to db
            # tasks.insert({
            #     'list': 'list_1',
            #     'description': task_description,
            #     'state': 'new',
            #     'created_at': datetime.datetime.now(),
            #     'updated_at': datetime.datetime.now(),
            # })

            await document.TaskDocument(**{
                'list': 'list_1',
                'description': task_description,
                'state': 'new',
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(),
            }).save()

            # 3) send message that task was added
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
