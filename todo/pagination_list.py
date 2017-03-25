# TODO:
#
# make pagination list part of framework
#
# 1) create class iterator for:
# 1.1) iterate DB (like we have right now)
# 1.2) iterate third party endpoints
# so we will get class-strategy and its state passed and stored in ctx


from botstory.ast import callable, loop, story_context
from botstory.middlewares import option, sticker, text
import emoji
import logging
from todo import reflection

logger = logging.getLogger(__name__)

pagination_loop = None

BORDER = '✁ ---------------------------'


def setup(story):
    global pagination_loop

    # Loop version
    async def _show_list_next_page(ctx):
        user_data = story_context.get_user_data(ctx)
        page_index = user_data.get('page_index', 0)
        list_title = user_data['list_title']
        title_field = user_data['title_field']
        page_length = user_data['page_length']
        list_type = user_data.get('list_type', 'pure')

        TargetDocument = reflection.str_to_class(user_data['target_document'])

        cursor = TargetDocument.objects.find({
            'user_id': ctx['user']['_id'],
        })

        start_index = page_index * page_length
        count = await cursor.count()
        items = await cursor.limit(page_length).skip(page_index * page_length).sort(updated_at='desc')

        msg = '\n'.join(emoji.emojize(':white_medium_square: {}').format(getattr(t, title_field)) for t in items)

        if page_index == 0:
            msg = '\n'.join([list_title, msg])

        the_end_of_list = False

        has_move_item = True

        logger.debug('page_index {}'.format(page_index))
        logger.debug('page_length {}'.format(page_length))
        logger.debug('count {}'.format(count))
        if count == 0:
            await story.ask('You don\'t have any tickets yet.',
                            user=ctx['user'],
                            quick_replies=[{
                                'title': emoji.emojize('Add New Task', use_aliases=True),
                                'payload': 'ADD_NEW_TASK'
                            }])
            return
        if (page_index + 1) * page_length >= count:
            the_end_of_list = True
            msg = '\n'.join([msg,
                             '',
                             BORDER,
                             ])
            has_move_item = False

        logger.debug('has_move_item {}'.format(has_move_item))

        # based on list template
        if list_type == 'template':
            buttons = []
            if has_move_item:
                buttons = [
                    {
                        'title': 'More',
                        'payload': 'NEXT_PAGE_OF_A_LIST'
                    }
                ]
            await story.list_elements(
                elements=[{
                              # 'title': '#{}'.format(start_index + index + 1),
                              # 'subtitle': getattr(i, title_field),
                              'title': getattr(item, title_field),
                              'buttons': [{
                                  'title': 'Task #{}'.format(start_index + index + 1),
                                  'type': 'postback',
                                  'payload': 'OPEN_TASK_{}'.format(item._id),
                              }]
                          }
                          for index, item in enumerate(items)],
                buttons=buttons,
                options={
                    'top_element_style': 'compact',
                },
                user=ctx['user'],
            )
        else:
            # based on pure text message (default)
            await story.ask(
                msg,
                user=ctx['user'],
                # TODO: don't show options if it is the end of list
                # TODO: `next 10`, `next 100`, `stop`
                quick_replies=None if the_end_of_list else [{
                    'title': 'More',
                    'payload': 'NEXT_PAGE_OF_A_LIST',
                }],
            )

        user_data['page_index'] = page_index + 1
        return has_move_item

    @story.callable()
    def pagination_loop():
        @story.part()
        async def show_zero_page(ctx):
            if not await _show_list_next_page(ctx):
                return callable.EndOfStory()

        @story.loop()
        def list_loop():
            @story.on([
                option.Match('NEXT_PAGE_OF_A_LIST'),
                sticker.Like(),
                text.text.EqualCaseIgnore('more'),
                text.text.EqualCaseIgnore('next'),
            ])
            def next_page():
                @story.part()
                async def show_part_of_list(ctx):
                    if not await _show_list_next_page(ctx):
                        return loop.BreakLoop()
                    return None


__all__ = [pagination_loop]
