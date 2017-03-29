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
from todo import task_state_stories

logger = logging.getLogger(__name__)

logger.debug('parse stories')


def setup(story):
    pagination_list.setup(story)
    task_state_stories.setup(story)

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
                page_length=os.environ.get('LIST_PAGE_LENGTH', 4),
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
                subtitle_renderer=reflection.class_to_str(tasks_document.task_details_renderer),
                list_title='List of actual tasks:',
                list_type='template',
                page_length=os.environ.get('LIST_PAGE_LENGTH', 4),
                target_document=reflection.class_to_str(tasks_document.TaskDocument),
                title_field='description',
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

            last_job = await tasks_document.TaskDocument.objects({
                'user_id': ctx['user']['_id'],
            }).sort(
                updated_at='desc',
            ).first()
            if not last_job:
                logger.warn('user doesnt have tickets to remove')
                await story.say(emoji.emojize(
                    'You don\'t have any tickets yet.\n'
                    ':information_source: Please send my few words about it and I will add it to your TODO list.'),
                    user=ctx['user'],
                )
                return
            desc = last_job.description
            logger.debug('going to remove job `{}`'.format(desc))
            await tasks_document.TaskDocument.objects({
                '_id': last_job._id,
            }).delete_one()
            msg = emoji.emojize(':ok: job `{}` was removed'.format(desc), use_aliases=True)
            logger.info(msg)
            await story.say(msg, user=ctx['user'])

    @story.on(option.Match('REMOVE_TASK_(.+)'))
    def remove_task_story():
        @story.part()
        async def try_to_remove_task(ctx):
            task_id = story_context.get_message_data(ctx, 'option', 'matches')[0]
            try:
                task = await tasks_document.TaskDocument.objects.find_one({
                    '_id': ObjectId(task_id),
                })
                await tasks_document.TaskDocument.objects({
                    '_id': task._id,
                }).delete_one()
                await story.say(emoji.emojize(
                    ':ok: Task `{}` was deleted', use_aliases=True).format(task.description), user=ctx['user'])
            except orm.errors.DoesNotExist:
                await story.say(emoji.emojize(':confused: Can\'t find task with id 58d99754e61713000143a2e1.\n'
                                              'It seems that it was already removed.', use_aliases=True).format(
                    task_id), user=ctx['user'])

    @story.on([
        text.Match('delete all(?: tasks)?(?: jobs)?'),
        text.Match('drop all(?: tasks)?'),
        text.Match('forget all(?: tasks)?'),
        text.Match('kill all(?: tasks)?'),
        text.Match('remove all(?: tasks)?'),
    ])
    def remove_all_jobs_story():
        @story.part()
        async def ask_whether_user_really_want_to_remove_all_tasks(ctx):
            logger.info('ask whether remove all tasks or not')
            return await story.ask(emoji.emojize(
                ':question: Do you really want to remove all your tasks '
                'of current list?',
                use_aliases=True,
            ), quick_replies=[{
                'title': 'Sure, remove all!',
                'payload': 'CONFIRM_REMOVE_ALL'
            }, {
                'title': 'Nope.',
                'payload': 'REFUSE_REMOVE_ALL'
            }], user=ctx['user'])

        @story.case([
            option.Match('CONFIRM_REMOVE_ALL'),
            sticker.Like(),
            text.Match('(.*) remove all (.*)', flags=re.IGNORECASE),
            text.Match('ok', flags=re.IGNORECASE),
            text.Match('sure (.*)', flags=re.IGNORECASE),
            text.Match('yes', flags=re.IGNORECASE),
        ])
        def confirm_to_remove_all():
            @story.part()
            async def remove_all_jobs(ctx):
                logger.info('remove all tasks')
                tasks_count = await tasks_document.TaskDocument.objects({
                    'user_id': ctx['user']['_id'],
                }).delete()

                msg = emoji.emojize(':ok: {} tasks were removed'.format(tasks_count), use_aliases=True)
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

            logger.debug('try to remove task {}'.format(target))
            count = await tasks_document.TaskDocument.objects({
                'description': target,
                'user_id': ctx['user']['_id'],
            }).delete()
            logger.info('remove {} lists'.format(count))
            if count > 0:
                await story.say(emoji.emojize(':ok: Task `{}` was removed'.format(target), use_aliases=True),
                                user=ctx['user'])
                return

            logger.debug('try to remove list {}'.format(target))
            count = await lists_document.ListDocument.objects({
                'name': target,
                'user_id': ctx['user']['_id'],
            }).delete()
            logger.info('remove {} lists'.format(count))
            if count > 0:
                await story.say(emoji.emojize(':ok: List `{}` was removed'.format(target), use_aliases=True),
                                user=ctx['user'])
                return

            await story.say('We can\'t find `{}` what do you want to remove?'.format(target),
                            user=ctx['user'])

    @story.on([
        text.Match('more about(.+)'),
        text.Match('see(.+)'),
    ])
    def task_details_story_by_text_match():
        @story.part()
        async def send_task_details(ctx):
            query = story_context.get_message_data(ctx, 'text', 'matches')[0].strip()
            try:
                task = await tasks_document.TaskDocument.objects.find({
                    'description': query,
                })
                if len(task) == 1:
                    await task_details_renderer.render(story, ctx['user'], task[0])
                else:
                    pass
                    # TODO:
            except orm.errors.DoesNotExist:
                # TODO:
                pass

    @story.on(option.Match('TASK_DETAILS_(.+)'))
    def task_details_story_by_option_match():
        @story.part()
        async def send_task_details_back(ctx):
            task_id = story_context.get_message_data(ctx, 'option', 'matches')[0]
            try:
                task = await tasks_document.TaskDocument.objects.find_one({
                    '_id': ObjectId(task_id),
                })
                await task_details_renderer.render(story, ctx['user'], task)
            except orm.errors.DoesNotExist:
                await story.say('Can\'t find task details. With id {}'.format(task_id), user=ctx['user'])

    @story.on(text.Match('last(?: task)?'))
    def last_task_story():
        @story.part()
        async def send_last_task_details(ctx):
            last_task = await tasks_document.TaskDocument.objects({
                'user_id': ctx['user']['_id'],
            }).sort(
                updated_at='desc',
            ).first()
            if not last_task:
                await story.ask('There is no last task yet. Please add few.',
                                user=ctx['user'],
                                quick_replies=[{
                                    'title': emoji.emojize('Add New Task', use_aliases=True),
                                    'payload': 'ADD_NEW_TASK'
                                }])
            else:
                await task_details_renderer.render(story, ctx['user'], last_task)

    @story.on(receive=sticker.Like())
    def like_story():
        @story.part()
        async def test_message(ctx):
            await story.list_elements(
                elements=[{
                    'title': '#100',  # (*) required
                    # 'image_url': 'https://peterssendreceiveapp.ngrok.io/img/collection.png',
                    'subtitle': 'See all our colors',
                    # 'default_action': {
                    #     'type': 'web_url',
                    #     'url': 'https://peterssendreceiveapp.ngrok.io/shop_collection',
                    #     'messenger_extensions': True,
                    #     'webview_height_ratio': 'tall',
                    #     'fallback_url': 'https://peterssendreceiveapp.ngrok.io/'
                    # },
                    'buttons': [{
                        'title': 'Open Task #100',
                        'type': 'postback',
                        'payload': 'payload'
                    }]
                }, {
                    'title': '#101',
                    # 'image_url': 'https://peterssendreceiveapp.ngrok.io/img/white-t-shirt.png',
                    'subtitle': '100% Cotton, 200% Comfortable',
                    # 'default_action': {
                    #     'type': 'web_url',
                    #     'url': 'https://peterssendreceiveapp.ngrok.io/view?item=100',
                    #     'messenger_extensions': True,
                    #     'webview_height_ratio': 'tall',
                    #     'fallback_url': 'https://peterssendreceiveapp.ngrok.io/'
                    # },
                    'buttons': [{
                        'title': 'Open Task #101',
                        'type': 'postback',
                        'payload': 'payload'
                    }]
                }, {
                    'title': '#102',
                    # 'image_url': 'https://peterssendreceiveapp.ngrok.io/img/blue-t-shirt.png',
                    'subtitle': '100% Cotton, 200% Comfortable',
                    # 'default_action': {
                    #     'type': 'web_url',
                    #     'url': 'https://peterssendreceiveapp.ngrok.io/view?item=101',
                    #     'messenger_extensions': True,
                    #     'webview_height_ratio': 'tall',
                    #     'fallback_url': 'https://peterssendreceiveapp.ngrok.io/'
                    # },
                    'buttons': [{
                        'title': 'Open Task #102',
                        'type': 'postback',
                        'payload': 'payload'
                    }]
                }, {
                    'title': '#103',
                    # 'image_url': 'https://peterssendreceiveapp.ngrok.io/img/black-t-shirt.png',
                    'subtitle': '100% Cotton, 200% Comfortable',
                    # 'default_action': {
                    #     'type': 'web_url',
                    #     'url': 'https://peterssendreceiveapp.ngrok.io/view?item=102',
                    #     'messenger_extensions': True,
                    #     'webview_height_ratio': 'tall',
                    #     'fallback_url': 'https://peterssendreceiveapp.ngrok.io/'
                    # },
                    'buttons': [{
                        'title': 'Open Task #103',
                        'type': 'postback',
                        'payload': 'payload'
                    }]
                }],
                buttons=[
                    {
                        'title': 'View More',
                        'type': 'postback',
                        'payload': 'payload'
                    }
                ],
                options={
                    'top_element_style': 'compact',
                },
                user=ctx['user'],
            )

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

    @story.on(receive=any.Any())
    def any_story():
        """
        And all the rest messages as well
        """

        @story.part()
        async def something_else(message):
            logger.info('something_else')
            await story.say('<React on unknown message>', message['user'])
