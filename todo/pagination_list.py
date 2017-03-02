from botstory import utils
from botstory.middlewares import any, option, text
import logging

logger = logging.getLogger(__name__)


loop = None


def setup(story):
    # Loop version
    async def _show_list_next_page(ctx):
        page_index = utils.safe_get(ctx, 'data', 'page_index', default=0)
        TargetDocument = ctx['data']['target_document']
        tasks = await TargetDocument.objects.find({
            'user_id': ctx['user']['_id'],
            # TODO: show last page by page_index
        })
        tasks_page = '\n'.join(':white_small_square: {}'.format(t.description) for t in tasks)

        await story.say(
            'List of actual tasks:\n{}'.format(tasks_page),
            user=ctx['user'],
            # TODO: don't show options if it is the end of list
            # TODO: `next 10`, `next 100`, `stop`
            options=[{
                'title': 'More',
                'payload': 'NEXT_PAGE_OF_TASKS_LIST'
            }],
        )

        # TODO: reach the end of list

        ctx['data']['page_index'] = page_index + 1

    global loop

    @story.callable()
    def loop():
        # TODO: get target collection (for example: tasks_document.TaskDocument)
        # as an argument. So we be able to reuse pager for different endless lists

        @story.part()
        async def show_zero_page(ctx):
            await _show_list_next_page(ctx)

        @story.loop()
        def list_loop():
            @story.on([
                option.Match('NEXT_PAGE_OF_TASKS_LIST'),
                text.text.EqualCaseIgnore('more'),
                text.text.EqualCaseIgnore('next'),
            ])
            def next_page():
                @story.part()
                async def show_part_of_list(ctx):
                    await _show_list_next_page(ctx)
