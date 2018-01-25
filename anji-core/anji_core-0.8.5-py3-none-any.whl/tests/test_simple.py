from datetime import datetime

import rethinkdb as R

from .base_config import *  # pylint: disable=unused-wildcard-import


def test_command(anjibot):
    anjibot.push_message('!test echo')
    assert 'Echo worked!' in anjibot.pop_message()


def test_test_normal(anjibot):
    from anji_core.test import TestTask

    test_object = TestTask(anjibot.anji, task_delay=6)
    anjibot.push_message('!test normal')
    assert 'Task Test task was queued.' in anjibot.pop_message(timeout=30)
    target_task = test_object.find_similar()
    assert target_task
    assert len(target_task) == 1
    target_task[0].delete()

def test_test_chain(anjibot):

    from anji_core.test import TestTask
    from anji_core.signals import TaskDoneSignal, FlowNextSignal
    from anji_core.types import TaskStatus

    TEST_RESULT_BODY = 'Test result'

    test_object = TestTask(anjibot.anji, task_delay=6)
    anjibot.push_message('!test chain')
    assert 'Task Test task was queued.' in anjibot.pop_message(timeout=30)
    tasks_list = test_object.find_similar()
    assert tasks_list
    assert len(tasks_list) == 1
    target_task = tasks_list[0]
    task_result = dict(body=TEST_RESULT_BODY)
    assert target_task.start_timestamp is None, "start timestamp must be None for not started task!"
    target_task.start_timestamp = datetime.now(R.make_timezone("00:00"))
    target_task.done(task_result=task_result)
    anjibot.anji.signals.fire(TaskDoneSignal(target_task, task_result))
    assert TEST_RESULT_BODY in anjibot.pop_message(timeout=30)
    assert 'Soon command test normal will be executed' in anjibot.pop_message(timeout=30)
    anjibot.anji.signals.fire(FlowNextSignal(target_task))
    assert 'Task Test task was queued, estimed execution time ' in anjibot.pop_message(timeout=60)
    tasks_list = test_object.find_similar()
    assert tasks_list
    assert len(tasks_list) == 2
    next_task = next(filter(lambda x: x.status == TaskStatus.pending, tasks_list))
    assert next_task
    assert next_task.before_task_uuid_list == [target_task.id]
    assert next_task.after_task_command_list == ['test normal']
    with anjibot.anji.pool.connect() as conn:
        R.table(TestTask._table).delete().run(conn)
