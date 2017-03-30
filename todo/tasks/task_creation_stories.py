from botstory.middlewares import option, text
import datetime
import emoji
import logging

from todo import orm
from todo.tasks import task_story_helper, tasks_document

logger = logging.getLogger(__name__)


def singular_vs_plural(singular):
    return ' was' if singular else 's were'


def setup(story):
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
                'state': 'open',
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(),
            }).save()

            await story.say('Task `{}` was added to the job list.'.format(task_description), ctx['user'])
