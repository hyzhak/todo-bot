import asyncio
import argparse
import botstory
from botstory.integrations import aiohttp, fb, mongodb
from botstory.integrations.ga import tracker
import logging
import os
import sys

from boilerplate import stories

BOT_NAME = 'boiledplate'

logger = logging.getLogger('boilerplate-bot')
logger.setLevel(logging.DEBUG)


class Bot:
    def __init__(self):
        self.story = botstory.Story()
        stories.setup(self.story)

    def init(self, auto_start, fake_http_session):
        self.story.use(fb.FBInterface(
            # will show on initial screen
            greeting_text='Hello dear {{user_first_name}}! '
                          'I'' m demo bot of BotStory framework.',
            # you should get on admin panel for the Messenger Product in Token Generation section
            page_access_token=os.environ.get('FB_ACCESS_TOKEN', 'TEST_TOKEN'),
            # menu of the bot that user has access all the time
            persistent_menu=[{
                'type': 'postback',
                'title': 'Monkey Business',
                'payload': 'MONKEY_BUSINESS'
            }, {
                'type': 'web_url',
                'title': 'Source Code',
                'url': 'https://github.com/botstory/bot-story/'
            }],
            # should be the same as in admin panel for the Webhook Product
            webhook_url='/webhook{}'.format(os.environ.get('FB_WEBHOOK_URL_SECRET_PART', '')),
            webhook_token=os.environ.get('FB_WEBHOOK_TOKEN', None),
        ))

        # Interface for HTTP
        http = self.story.use(aiohttp.AioHttpInterface(
            port=int(os.environ.get('API_PORT', 8080)),
            auto_start=auto_start,
        ))

        # User and Session storage
        self.story.use(mongodb.MongodbInterface(
            uri=os.environ.get('MONGODB_URI', 'mongo'),
            db_name=os.environ.get('MONGODB_DB_NAME', 'echobot'),
        ))

        self.story.use(tracker.GAStatistics(
            tracking_id=os.environ.get('GA_ID'),
        ))

        # for test purpose
        http.session = fake_http_session
        return http

    async def setup(self, fake_http_session=None):
        logger.info('setup')
        self.init(auto_start=False, fake_http_session=fake_http_session)
        await self.story.setup()

    async def start(self, auto_start=True, fake_http_session=None):
        logger.info('start')
        http = self.init(auto_start, fake_http_session)
        await self.story.start()
        return http.app

    async def stop(self):
        logger.info('stop')
        await self.story.stop()
        self.story.clear()


def setup():
    bot = Bot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.setup())


def start(forever=False):
    bot = Bot()
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(bot.start(auto_start=forever))
    if forever:
        bot.story.forever(loop)
    return app


def parse_args(args):
    parser = argparse.ArgumentParser(prog=BOT_NAME)
    parser.add_argument('--setup', action='store_true', default=False, help='setup bot')
    parser.add_argument('--start', action='store_true', default=False, help='start bot')
    return parser.parse_args(args), parser


def main():
    parsed, parser = parse_args(sys.argv[1:])
    if parsed.setup:
        return setup()

    if parsed.start:
        return start(forever=True)

    parser.print_help()


if __name__ == '__main__':
    main()
