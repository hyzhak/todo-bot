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
    (2, 'STOP_TASK_{}', 'Task `{}` is already opened', 'open'),
])
async def test_start_task_by_postback(
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
