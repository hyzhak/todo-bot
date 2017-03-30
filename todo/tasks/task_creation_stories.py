from botstory.middlewares import option, text
import datetime
import emoji
import logging

from todo import orm, sense
from todo.tasks import task_story_helper, tasks_document

logger = logging.getLogger(__name__)


def singular_vs_plural(singular):
    return ' was' if singular else 's were'


def extract_tasks(sense_list):
    for s in sense_list:
        if s['intent'] == 'ADD_NEW_TASK':
            for e in s['entities']:
                yield e['title']
        else:
            raise NotImplemented()


async def build_task(ctx, title):
    await tasks_document.TaskDocument(**{
        'user_id': ctx['user']['_id'],
        'list': 'list_1',
        'description': title,
        'state': 'open',
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
    }).save()


def setup(story):
    @story.on(receive=text.Any())
    def new_task_story():
        """
        Any text that doesn't match specific cases
        consider as new task
        """

        @story.part()
        async def add_new_task(ctx):
            # ctx = task_entities.extract_entities(text.get_raw_text(ctx))
            #
            logger.info('new task')
            task_titles = list(extract_tasks(
                sense.extract_sense(text.get_raw_text(ctx))
            ))

            if len(task_titles) == 1:
                task_description = task_titles[0]
                await build_task(ctx, task_description)

                await story.say('Task `{}` was added to the job list.'.format(task_description), ctx['user'])
            elif len(task_titles) > 1:
                for t in task_titles:
                    await build_task(ctx, t)

                await story.say(
                    'Tasks were added:\n{}'.format(
                        '\n'.join([':white_medium_square: {}'.format(t) for t in task_titles])
                    ),
                    user=ctx['user'],
                )
            else:
                raise NotImplemented()
