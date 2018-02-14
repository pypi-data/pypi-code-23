import pytest

from spooler.task import Task


@pytest.mark.parametrize("fct", [
    print,
    filter,
    Task.execute,
    map,
])
def test_name_constraint(fct):
    task = Task(fct)
    fct_name = task.get_callback_name()
    task2 = Task.from_name(fct_name)
    assert task.callback is task2.callback


def test_task_execute():
    def foo(word):
        return word.upper()

    assert Task(foo, "bar").execute() == "BAR"
