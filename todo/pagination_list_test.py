import pytest

@pytest.mark.asyncio
@pytest.mark.skip('should call pagination_list.pagination_loop direct')
async def test_pagination_of_list_of_active_tasks(build_context, monkeypatch):
    async with build_context() as ctx:
        command = 'todo'
        facebook = ctx.fb_interface

        monkeypatch.setattr(os, 'environ', {
            'LIST_PAGE_LENGTH': 2,
        })

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

        await facebook.handle(build_message({
            'text': command,
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
