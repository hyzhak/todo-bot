from botstory.ast import story_context
from botstory.middlewares import any, option, sticker, text
from bson.objectid import ObjectId
import datetime
import emoji
import logging
import os
import re

from todo import orm, pagination_list, reflection
from todo.lists import lists_document
from todo.tasks import task_story_helper, tasks_document, task_details_renderer

logger = logging.getLogger(__name__)


def setup(story):
    @story.on(option.Match('OPEN_TASK_(.+)'))
    def open_task_story():
        @story.part()
        async def try_to_open_task(ctx):
            try:
                task = await task_story_helper.current_task(ctx)
                task.state = 'open'
                await task.save()
                await story.say(
                    emoji.emojize(':ok: Task `{}` was opened', use_aliases=True).format(task.description),
                    user=ctx['user'])
            except orm.errors.DoesNotExist:
                pass
