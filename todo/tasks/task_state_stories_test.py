import emoji
import logging
import pytest
from todo.tasks import tasks_document
from todo.test_helpers import env

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.parametrize(('task_idx', 'command_tmpl', 'should_get_answer', 'should_get_state'), [
    (0, 'REOPEN_TASK_{}', ':ok: Task `{}` was opened', 'open'),
    (0, 'DONE_TASK_{}', 'Task `{}` is already done', 'done'),
    (1, 'STOP_TASK_{}', ':ok: Task `{}` was stopped', 'open'),
    (1, 'DONE_TASK_{}', ':ok: Task `{}` was done', 'done'),
    (1, 'START_TASK_{}', 'Task `{}` is already in progress', 'in progress'),
    (2, 'START_TASK_{}', ':ok: Task `{}` was started', 'in progress'),
    (2, 'REOPEN_TASK_{}', 'Task `{}` is already opened', 'open'),
    (2, 'STOP_TASK_{}', 'Task `{}` is already stopped', 'open'),
])
async def test_change_state_of_task_by_postback(
        build_context, task_idx, command_tmpl, should_get_answer, should_get_state):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks()

        target_task_id = created_tasks[task_idx]._id

        # Alice:
        await ctx.dialog([
            env.build_postback(command_tmpl.format(target_task_id)),
        ])

        task_after_command = await tasks_document.TaskDocument.objects.find_by_id(target_task_id)
        # Bob:
        await ctx.dialog([
            None,
            should_get_answer.format(task_after_command.description),
        ])
        assert task_after_command.state == should_get_state


@pytest.mark.asyncio
@pytest.mark.parametrize(('init_state', 'command', 'should_get_answer', 'should_get_state'), [
    ('done', 'open last', ':ok: Task `{}` was opened', 'open'),
    ('open', 'open last', 'Task `{}` is already opened', 'open'),
    ('open', 'start last', ':ok: Task `{}` was started', 'in progress'),
    ('in progress', 'start last', 'Task `{}` is already in progress', 'in progress'),
    ('in progress', 'stop last', ':ok: Task `{}` was stopped', 'open'),
    ('open', 'stop last', 'Task `{}` is already stopped', 'open'),
    ('in progress', 'done last', ':ok: Task `{}` was done', 'done'),
    ('done', 'done last', 'Task `{}` is already done', 'done'),
])
async def test_change_state_of_last_task(
        build_context, init_state, command, should_get_answer, should_get_state):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks(init_state)

        last_task_id = created_tasks[-1]._id

        # Alice:
        await ctx.dialog([
            command,
        ])

        task_after_command = await tasks_document.TaskDocument.objects.find_by_id(last_task_id)
        # Bob:
        await ctx.dialog([
            None,
            should_get_answer.format(task_after_command.description),
        ])
        assert task_after_command.state == should_get_state


@pytest.mark.asyncio
@pytest.mark.parametrize(('command', 'should_get_answer', 'should_get_states'), [
    ('open all', ':ok: Task was opened:\n{}', ['open', 'in progress']),
    ('start all', ':ok: Task was started:\n{}', ['in progress', 'done']),
    ('stop all', ':ok: Task was stopped:\n{}', ['open', 'done']),
    ('done all', ':ok: Tasks were done:\n{}', ['done']),
])
async def test_change_state_of_all_tasks(
        build_context, command, should_get_answer, should_get_states):
    async with build_context() as ctx:
        created_tasks = await ctx.add_test_tasks()

        description_of_tasks_that_will_be_modified = [
            t.description for t in created_tasks if t.state not in should_get_states
            ]

        # Alice:
        await ctx.dialog([
            command,
        ])

        for t in created_tasks:
            task_after_command = await tasks_document.TaskDocument.objects.find_by_id(t._id)
            assert task_after_command.state in should_get_states

        list_of_modified_tasks = '\n'.join(
            [emoji.emojize(':white_medium_square: {}').format(t) for t in description_of_tasks_that_will_be_modified])

        # Bob:
        await ctx.dialog([
            None,
            should_get_answer.format(list_of_modified_tasks),
        ])
