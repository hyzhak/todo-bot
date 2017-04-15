from botstory.ast import story_context
from botstory.middlewares import any, option, sticker, text
from bson.objectid import ObjectId
import datetime
import emoji
import logging
import os
import random
import re

from todo import orm, pagination_list, reflection
from todo.lists import lists_document
from todo.tasks import \
    task_creation_stories, \
    task_details_renderer, \
    task_state_stories, \
    task_story_helper, \
    tasks_document

logger = logging.getLogger(__name__)

logger.debug('parse stories')

SHORT_HELP = 'Short Help:\n' \
             '===========\n' \
             '\n' \
             ':white_check_mark: Please give me few names of tasks (command: add new task)\n' \
             ':white_check_mark: In any time when you work with your task you can change its status ' \
             'from open :arrow_right: in progress :arrow_right: done ' \
             '(commands: start, stop, done, reopen)\n' \
             ':white_check_mark: list all your tasks (command: list)\n' \
             ':white_check_mark: details about task (command: last details)\n' \
             ':white_check_mark: work with last task (command: start last, stop last, done last, ' \
             'reopen last, last task, remove last)\n' \
             ':white_check_mark: change all tasks at once (commands: start all, stop all, ' \
             'done all, reopen all, remove all)\n' \
             '\n' \
             'All my source could be found here:\n' \
             'https://github.com/botstory/todo-bot/, feedback and PRs are welcomed!'

SHORT_HELP_EMOJI = emoji.emojize(SHORT_HELP, use_aliases=True)


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
            await story.say('Nice to see you here!\n'
                            'My goal is to help you with your list of tasks.',
                            user=message['user'])
            await story.say(SHORT_HELP_EMOJI,
                            user=message['user'])
            await story.ask('let\'s begin!',
                            quick_replies=[{
                                'title': 'add new task',
                                'payload': 'ADD_NEW_TASK',
                            }],
                            user=message['user'])

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

    @story.on([
        option.Equal('LIST_TASKS_NEW_FIRST'),
        text.Match('^list(( all)? tasks)?', flags=re.IGNORECASE),
        text.EqualCaseIgnore('todo'),
    ])
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
        option.Equal('REMOVE_LAST_TASK'),
        text.Match('delete last', flags=re.IGNORECASE),
        text.Match('drop last', flags=re.IGNORECASE),
        text.Match('forget about last', flags=re.IGNORECASE),
        text.Match('kill last', flags=re.IGNORECASE),
        text.Match('remove (last|next)', flags=re.IGNORECASE),
    ])
    def remove_last_task_story():
        @story.part()
        async def remove_last_task(ctx):
            logger.info('remove last task')

            try:
                last_task = await task_story_helper.last_task(ctx)
                desc = last_task.description
                logger.debug('going to remove task `{}`'.format(desc))
                await tasks_document.TaskDocument.objects({
                    '_id': last_task._id,
                }).delete_one()
                msg = emoji.emojize(':ok: task `{}` was removed'.format(desc), use_aliases=True)
                logger.info(msg)
                await story.ask(msg,
                                quick_replies=[{
                                    'title': 'remove next',
                                    'payload': 'REMOVE_LAST_TASK',
                                }, {
                                    'title': 'next details',
                                    'payload': 'LAST_TASK_DETAILS',
                                }, {
                                    'title': 'add task',
                                    'payload': 'ADD_NEW_TASK',
                                }, {
                                    'title': 'list',
                                    'payload': 'LIST_TASKS_NEW_FIRST',
                                },
                                ],
                                user=ctx['user'])
            except orm.errors.DoesNotExist:
                logger.warning('user doesnt have tickets to remove')
                await story.ask(emoji.emojize(
                    'You don\'t have any tickets yet.\n'
                    ':information_source: Please send my few words about it and I will add it to your TODO list.',
                    use_aliases=True,
                ),
                    quick_replies=[{
                        'title': 'add new task',
                        'payload': 'ADD_NEW_TASK',
                    }],
                    user=ctx['user'],
                )

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
                await story.ask(emoji.emojize(':ok: Task `{}` was deleted', use_aliases=True).format(task.description),
                                quick_replies=[{
                                    'title': 'add new task',
                                    'payload': 'ADD_NEW_TASK',
                                }, {
                                    'title': 'list tasks',
                                    'payload': 'LIST_TASKS_NEW_FIRST',
                                },
                                ],
                                user=ctx['user'])
            except orm.errors.DoesNotExist:
                await story.ask(emoji.emojize(':confused: Can\'t find task.\n'
                                              'It seems that it was already removed.', use_aliases=True),
                                quick_replies=[{
                                    'title': 'add new task',
                                    'payload': 'ADD_NEW_TASK',
                                }, {
                                    'title': 'list tasks',
                                    'payload': 'LIST_TASKS_NEW_FIRST',
                                },
                                ],
                                user=ctx['user'])

    @story.on([
        option.Equal('REMOVE_ALL_TASKS'),
        text.Match('delete all(?: tasks)?(?: jobs)?', flags=re.IGNORECASE),
        text.Match('drop all(?: tasks)?', flags=re.IGNORECASE),
        text.Match('forget all(?: tasks)?', flags=re.IGNORECASE),
        text.Match('kill all(?: tasks)?', flags=re.IGNORECASE),
        text.Match('remove all(?: tasks)?', flags=re.IGNORECASE),
    ])
    def remove_all_tasks_story():
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
                'title': 'Nope',
                'payload': 'REFUSE_REMOVE_ALL'
            }], user=ctx['user'])

        @story.case([
            option.Equal('CONFIRM_REMOVE_ALL'),
            sticker.Like(),
            text.Match('confirm', flags=re.IGNORECASE),
            text.Match('ok', flags=re.IGNORECASE),
            text.Match('(.*)remove(.*)', flags=re.IGNORECASE),
            text.Match('sure(.*)', flags=re.IGNORECASE),
            text.Match('yeah', flags=re.IGNORECASE),
            text.Match('yes', flags=re.IGNORECASE),
        ])
        def confirm_to_remove_all():
            @story.part()
            async def remove_all_tasks(ctx):
                logger.info('remove all tasks')
                tasks_count = await tasks_document.TaskDocument.objects({
                    'user_id': ctx['user']['_id'],
                }).delete()

                msg = emoji.emojize(':ok: {} tasks were removed'.format(tasks_count), use_aliases=True)
                logger.info(msg)
                await story.ask(msg,
                                quick_replies=[{
                                    'title': 'remove next',
                                    'payload': 'REMOVE_LAST_TASK',
                                }, {
                                    'title': 'next details',
                                    'payload': 'LAST_TASK_DETAILS',
                                }, {
                                    'title': 'add task',
                                    'payload': 'ADD_NEW_TASK',
                                }, {
                                    'title': 'list',
                                    'payload': 'LIST_TASKS_NEW_FIRST',
                                },
                                ],
                                user=ctx['user'])

    @story.on([
        text.Match('delete (.*)', flags=re.IGNORECASE),
        text.Match('drop (.*)', flags=re.IGNORECASE),
        text.Match('forget about (.*)', flags=re.IGNORECASE),
        text.Match('kill (.*)', flags=re.IGNORECASE),
        text.Match('remove (.*)', flags=re.IGNORECASE),
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

            await story.say(emoji.emojize(':confused: We can\'t find `{}` what do you want to remove?'.format(target),
                                          use_aliases=True),
                            user=ctx['user'])

    @story.on([
        text.Match('more about(.+)', flags=re.IGNORECASE),
        text.Match('see(.+)', flags=re.IGNORECASE),
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
                await story.ask(emoji.emojize(
                    ':confused: Can\'t find task details.',
                    use_aliases=True),
                    quick_replies=[{
                        'title': 'add new task',
                        'payload': 'ADD_NEW_TASK',
                    }, {
                        'title': 'list tasks',
                        'payload': 'LIST_TASKS_NEW_FIRST',
                    }],
                    user=ctx['user'])

    @story.on([
        option.Equal('LAST_TASK_DETAILS'),
        text.Match('last(?: task)?', flags=re.IGNORECASE),
        text.Match('next (details|task)', flags=re.IGNORECASE),
        text.Match('^(task )?details', flags=re.IGNORECASE),
    ])
    def last_task_story():
        @story.part()
        async def send_last_task_details(ctx):
            try:
                await task_details_renderer.render(story, ctx['user'],
                                                   task=await task_story_helper.last_task(ctx))
            except orm.errors.DoesNotExist:
                await story.ask('There is no last task yet. Please add few.',
                                user=ctx['user'],
                                quick_replies=[{
                                    'title': 'Add New Task',
                                    'payload': 'ADD_NEW_TASK'
                                }])

    @story.on([
        option.Equal('ABOUT_ME'),
        text.Equal('?'),
        text.Equal('/?'),
        text.EqualCaseIgnore('-h'),
        text.EqualCaseIgnore('--help'),
        text.Match('help( me)?', flags=re.IGNORECASE),
        text.EqualCaseIgnore('what can I do here?'),
    ])
    def about_me_story():
        @story.part()
        async def say_about_me(ctx):
            await story.ask(SHORT_HELP_EMOJI,
                            user=ctx['user'],
                            quick_replies=[{
                                'title': 'add new task',
                                'payload': 'ADD_NEW_TASK',
                            }, {
                                'title': 'list tasks',
                                'payload': 'LIST_TASKS_NEW_FIRST',
                            }])

    @story.on(receive=sticker.Like())
    def like_story():
        @story.part()
        async def test_message(ctx):
            msgs = [':wink:', ':heart_eyes:', ':smirk:', ':wink:', ':metal:', 'Thanks!', 'I like you too!']
            await story.ask(emoji.emojize(random.choice(msgs), use_aliases=True),
                            quick_replies=[{
                                'title': 'add new task',
                                'payload': 'ADD_NEW_TASK',
                            }, {
                                'title': 'list tasks',
                                'payload': 'LIST_TASKS_NEW_FIRST',
                            }],
                            user=ctx['user'])

    task_creation_stories.setup(story)

    @story.on(receive=any.Any())
    def any_story():
        """
        And all the rest messages as well
        """

        @story.part()
        async def something_else(message):
            logger.info('something_else')
            await story.ask(
                emoji.emojize(':confused: Sorry I don\'t know, how to react on such message yet.\n'
                              'Here are few things that you can do quickly',
                              use_aliases=True),
                quick_replies=[{
                    'title': 'add new task',
                    'payload': 'ADD_NEW_TASK',
                }, {
                    'title': 'list tasks',
                    'payload': 'LIST_TASKS_NEW_FIRST',
                }],
                user=message['user'])
