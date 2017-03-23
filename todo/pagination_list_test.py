from botstory.integrations import fb, mongodb, mockhttp
from botstory.utils import answer
import os
import pytest
from todo import pagination_list, reflection
from todo.stories_test import build_context, build_message
from todo.tasks import tasks_document

__all__ = [build_context]


# TODO:
#
# make pagination list part of framework
#
# 1) create class iterator for:
# 1.1) iterate DB (like we have right now)
# 1.2) iterate third party endpoints
# so we will get class-strategy and its state passed and stored in ctx


@pytest.mark.asyncio
async def test_pure_list_of_active_tasks_on_list(build_context):
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
async def test_template_list_of_active_tasks_on_list(build_context):
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
async def test_pagination_of_list(build_context):
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

        await facebook.handle(build_message({
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

        await facebook.handle(build_message({
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

        await facebook.handle(build_message({
            'text': 'next',
        }))

        ctx.receive_answer('\n'.join([':white_medium_square: eat',
                                      '',
                                      pagination_list.BORDER]))

        ctx.was_asked_with_without_quick_replies()
