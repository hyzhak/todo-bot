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
from todo.tasks import tasks_document, task_details_renderer


async def current_task(ctx):
    """
    get current task from ctx
    :param ctx:
    :return:
    """
    task_id = story_context.get_message_data(ctx, 'option', 'matches')[0]
    return await tasks_document.TaskDocument.objects.find_by_id(task_id)
