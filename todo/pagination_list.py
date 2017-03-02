from botstory import utils
from botstory.middlewares import any, option, text
import logging
from todo import reflection

logger = logging.getLogger(__name__)


loop = None


def setup(story):
    # Loop version
    async def _show_list_next_page(ctx):
        page_index = utils.safe_get(ctx, 'data', 'page_index', default=0)
        list_title = ctx['data']['list_title']
        TargetDocument = reflection.str_to_class(ctx['data']['target_document'])

        items = await TargetDocument.objects.find({
            'user_id': ctx['user']['_id'],
            # TODO: show last page by page_index
        })
        items_page = '\n'.join(':white_small_square: {}'.format(t.description) for t in items)

        await story.say(
            '{}\n{}'.format(list_title, items_page),
            user=ctx['user'],
            # TODO: don't show options if it is the end of list
            # TODO: `next 10`, `next 100`, `stop`
            options=[{
                'title': 'More',
                'payload': 'NEXT_PAGE_OF_A_LIST'
            }],
        )

        # TODO: reach the end of list

        ctx['data']['page_index'] = page_index + 1

    global loop

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
