from fastgets import Task


def test_task_detail_url():
    task = Task()
    task.url = 'http://www.baidu.com'
    assert task.detail_url == 'http://www.baidu.com'

    task = Task()
    task.url = 'http://www.baidu.com'
    task.get_payload['b'] = 2
    assert task.detail_url == 'http://www.baidu.com?b=2'

    task = Task()
    task.url = 'http://www.baidu.com?a=1'
    task.get_payload['b'] = 2
    assert task.detail_url == 'http://www.baidu.com?a=1&b=2'
