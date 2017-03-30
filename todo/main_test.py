import aiohttp
import contextlib
from io import StringIO
import os
import pytest
from unittest.mock import Mock

from . import main, test_utils


@pytest.mark.asyncio
async def test_start_bot(event_loop):
    async with test_utils.SandboxBot(event_loop, main.Bot()) as sandbox:
        assert len(sandbox.fb.history) == 0


@pytest.mark.asyncio
async def test_text_echo(event_loop):
    async with test_utils.SandboxBot(event_loop, main.Bot()) as sandbox:
        await test_utils.post('http://0.0.0.0:{}/webhook'.format(os.environ.get('API_PORT', 8080)),
                              json={
                                  "object": "page",
                                  "entry": [{
                                      "id": "PAGE_ID",
                                      "time": 1458692752478,
                                      "messaging": [{
                                          "sender": {
                                              "id": "USER_ID"
                                          },
                                          "recipient": {
                                              "id": "PAGE_ID"
                                          },
                                          "timestamp": 1458692752478,
                                          "message": {
                                              "mid": "mid.1457764197618:41d102a3e1ae206a38",
                                              "seq": 73,
                                              "text": "hello world!",
                                          }
                                      }]
                                  }]
                              })

        assert len(sandbox.fb.history) == 1
        assert await sandbox.fb.history[0]['request'].json() == {
            'message': {
                'text': 'Task `hello world!` was added to the job list.'
            },
            'recipient': {'id': 'USER_ID'},
        }


def test_parser_empry_arguments():
    parsed, _ = main.parse_args([])
    assert parsed.setup is not True
    assert parsed.start is not True


def test_parser_setup_arguments():
    parsed, _ = main.parse_args(['--setup'])
    assert parsed.setup is True
    assert parsed.start is not True


def test_parser_start_arguments():
    parsed, _ = main.parse_args(['--start'])
    assert parsed.setup is False
    assert parsed.start is True


def test_show_help_if_no_any_arguments():
    main.sys.argv = []
    temp_stdout = StringIO()
    with contextlib.redirect_stdout(temp_stdout):
        main.main()
    output = temp_stdout.getvalue().strip()
    assert 'help' in output
    assert 'setup' in output
    assert 'start' in output


def test_setup_bot_on_setup_argument(mocker):
    main.sys.argv = ['', '--setup']
    handler = mocker.patch('todo.main.setup')
    main.main()
    assert handler.called is True


def test_start_bot_on_setup_argument(mocker):
    main.sys.argv = ['', '--start']
    handler = mocker.patch('todo.main.start')
    main.main()
    assert handler.called is True
