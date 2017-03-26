import os
import pytest
from todo import pagination_list, reflection
from todo.tasks import tasks_document
from todo.test_helpers import env


@pytest.mark.asyncio
async def test_pure_one_page_list(build_context):
    async with build_context() as ctx:
        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
        }, ])

        await pagination_list.pagination_loop(
            list_title='List of actual tasks:',
            list_type='pure',
            target_document=reflection.class_to_str(tasks_document.TaskDocument),
            title_field='description',
            page_length=os.environ.get('LIST_PAGE_LENGTH', 4),
            session=ctx.session,
            user=ctx.user,
        )

        ctx.receive_answer('\n'.join(['List of actual tasks:',
                                      ':white_medium_square: fry toasts',
                                      ':white_medium_square: fry eggs',
                                      ':white_medium_square: drop cheese',
                                      '',
                                      pagination_list.BORDER]))


@pytest.mark.asyncio
async def test_template_one_page_list(build_context):
    async with build_context() as ctx:
        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
        }, ])

        await pagination_list.pagination_loop(
            list_title='List of actual tasks:',
            list_type='template',
            target_document=reflection.class_to_str(tasks_document.TaskDocument),
            title_field='description',
            page_length=os.environ.get('LIST_PAGE_LENGTH', 4),
            session=ctx.session,
            user=ctx.user,
        )

        ctx.receive_answer([
            'fry toasts',
            'fry eggs',
            'drop cheese',
        ], next_button=None)


@pytest.mark.asyncio
async def test_pure_pagination_of_list(build_context):
    async with build_context(use_app_stories=False) as ctx:
        facebook = ctx.fb_interface
        story = ctx.story
        pagination_list.setup(story)

        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'serve',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'eat',
            'user_id': ctx.user['_id'],
        }, ])

        @story.on('hi')
        def one_story():
            @story.part()
            async def run_pagination(ctx):
                return await pagination_list.pagination_loop(
                    ctx,
                    list_title='List of actual tasks:',
                    list_type='pure',
                    target_document=reflection.class_to_str(tasks_document.TaskDocument),
                    title_field='description',
                    page_length=2,
                )

        await facebook.handle(env.build_message({
            'text': 'hi',
        }))

        ctx.receive_answer('\n'.join(['List of actual tasks:',
                                      ':white_medium_square: fry toasts',
                                      ':white_medium_square: fry eggs',
                                      ]))

        ctx.was_asked_with_quick_replies([{
            'content_type': 'text',
            'payload': 'NEXT_PAGE_OF_A_LIST',
            'title': 'More',
        }])

        await facebook.handle(env.build_message({
            'text': 'next',
        }))

        ctx.receive_answer('\n'.join([':white_medium_square: drop cheese',
                                      ':white_medium_square: serve',
                                      ]))

        ctx.was_asked_with_quick_replies([{
            'content_type': 'text',
            'payload': 'NEXT_PAGE_OF_A_LIST',
            'title': 'More',
        }])

        await facebook.handle(env.build_message({
            'text': 'next',
        }))

        ctx.receive_answer('\n'.join([':white_medium_square: eat',
                                      '',
                                      pagination_list.BORDER]))

        ctx.was_asked_with_without_quick_replies()


@pytest.mark.asyncio
async def test_template_pagination_of_list(build_context):
    async with build_context(use_app_stories=False) as ctx:
        facebook = ctx.fb_interface
        story = ctx.story
        pagination_list.setup(story)

        await ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'serve',
            'user_id': ctx.user['_id'],
        }, {
            'description': 'eat',
            'user_id': ctx.user['_id'],
        }, ])

        @story.on('hi')
        def one_story():
            @story.part()
            async def run_pagination(ctx):
                return await pagination_list.pagination_loop(
                    ctx,
                    list_title='List of actual tasks:',
                    list_type='template',
                    target_document=reflection.class_to_str(tasks_document.TaskDocument),
                    title_field='description',
                    page_length=2,
                )

        await facebook.handle(env.build_message({
            'text': 'hi',
        }))

        ctx.receive_answer(['fry toasts',
                            'fry eggs'],
                           next_button='More')

        await facebook.handle(env.build_message({
            'text': 'next',
        }))

        ctx.receive_answer(['drop cheese',
                            'serve',
                            ],
                           next_button='More')

        await facebook.handle(env.build_message({
            'text': 'next',
        }))

        ctx.receive_answer(['eat'])


@pytest.mark.asyncio
async def test_could_use_like_to_request_next_page(build_context):
    async with build_context(use_app_stories=False) as app_ctx:
        facebook = app_ctx.fb_interface
        story = app_ctx.story
        pagination_list.setup(story)

        await app_ctx.add_tasks([{
            'description': 'fry toasts',
            'user_id': app_ctx.user['_id'],
        }, {
            'description': 'fry eggs',
            'user_id': app_ctx.user['_id'],
        }, {
            'description': 'drop cheese',
            'user_id': app_ctx.user['_id'],
        }, {
            'description': 'serve',
            'user_id': app_ctx.user['_id'],
        }, {
            'description': 'eat',
            'user_id': app_ctx.user['_id'],
        }, ])

        @story.on('hi')
        def one_story():
            @story.part()
            async def run_pagination(ctx):
                return await pagination_list.pagination_loop(
                    ctx,
                    list_title='List of actual tasks:',
                    list_type='template',
                    target_document=reflection.class_to_str(tasks_document.TaskDocument),
                    title_field='description',
                    page_length=2,
                )

        await facebook.handle(env.build_message({
            'text': 'hi',
        }))

        app_ctx.receive_answer(['fry toasts',
                                'fry eggs'],
                               next_button='More')

        await facebook.handle(env.build_like())

        app_ctx.receive_answer(['drop cheese',
                                'serve',
                                ],
                               next_button='More')

        await facebook.handle(env.build_like())

        app_ctx.receive_answer(['eat'])


@pytest.mark.asyncio
async def test_pure_empty_listt(build_context):
    async with build_context() as ctx:
        await pagination_list.pagination_loop(
            list_title='List of actual tasks:',
            list_type='pure',
            target_document=reflection.class_to_str(tasks_document.TaskDocument),
            title_field='description',
            page_length=os.environ.get('LIST_PAGE_LENGTH', 4),
            session=ctx.session,
            user=ctx.user,
        )

        ctx.receive_answer('You don\'t have any tickets yet.')


@pytest.mark.asyncio
async def test_template_list_for_one_task(build_context):
    async with build_context() as ctx:
        await ctx.add_tasks([{
            'description': 'be the best',
            'user_id': ctx.user['_id'],
        }, ])

        await pagination_list.pagination_loop(
            list_title='List of actual tasks:',
            list_type='template',
            target_document=reflection.class_to_str(tasks_document.TaskDocument),
            title_field='description',
            page_length=os.environ.get('LIST_PAGE_LENGTH', 4),
            session=ctx.session,
            user=ctx.user,
        )

        ctx.receive_answer([
            'be the best',
            '...',
        ], next_button=None)
