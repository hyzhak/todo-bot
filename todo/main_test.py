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
