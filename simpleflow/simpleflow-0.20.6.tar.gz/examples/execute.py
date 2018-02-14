from simpleflow import activity, execute, futures, Workflow


def with_pypy(func):
    return execute.python("/usr/local/bin/pypy", kill_children=True)(func)


@activity.with_attributes(task_list='quickstart', version='example')
@with_pypy
def double(i):
    return i * 2


class BasicWorkflow(Workflow):
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self, x):
        y = self.submit(double, x)
        futures.wait(y)
        print 'FINISHED! {} * 2 = {}'.format(x, y.result)
