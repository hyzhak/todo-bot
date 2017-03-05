from botstory import utils
from botstory.ast import story_context
from botstory.middlewares import any, option, text
import emoji
import logging
from todo import reflection

logger = logging.getLogger(__name__)

loop = None


def setup(story):
    global loop

    # Loop version
    async def _show_list_next_page(ctx):
        user_data = story_context.get_user_data(ctx)
        page_index = user_data.get('page_index', 0)
        list_title = user_data['list_title']
        title_field = user_data['title_field']
        page_length = user_data['page_length']

        TargetDocument = reflection.str_to_class(user_data['target_document'])

        cursor = TargetDocument.objects.find({
            'user_id': ctx['user']['_id'],
        })

        count = await cursor.count()
        items = await cursor.limit(page_length).skip(page_index * page_length).to_list()

        msg = '\n'.join(emoji.emojize(':white_small_square: {}').format(getattr(t, title_field)) for t in items)

        if page_index == 0:
            msg = '\n'.join([list_title, msg])

        the_end_of_list = False

        if (page_index + 1) * page_length >= count:
            the_end_of_list = True

        await story.say(
            msg,
            user=ctx['user'],
            # TODO: don't show options if it is the end of list
            # TODO: `next 10`, `next 100`, `stop`
            options=None if the_end_of_list else [{
                'title': 'More',
                'payload': 'NEXT_PAGE_OF_A_LIST'
            }],
        )

        user_data['page_index'] = page_index + 1

    @story.callable()
    def loop():
        @story.part()
        async def show_zero_page(ctx):
            await _show_list_next_page(ctx)

        @story.loop()
        def list_loop():
            @story.on([
                option.Match('NEXT_PAGE_OF_A_LIST'),
                text.text.EqualCaseIgnore('more'),
                text.text.EqualCaseIgnore('next'),
            ])
            def next_page():
                @story.part()
                async def show_part_of_list(ctx):
                    await _show_list_next_page(ctx)


__all__ = [loop]
