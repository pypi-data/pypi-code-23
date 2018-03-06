import celery

app = celery.Celery('app', broker='redis://', result_backend='redis://')
app.conf.result_backend = 'redis://'
app.conf.RESULT_BACKEND = 'redis://'


@app.task
def identity(i):
    return i


@app.task
def tsum(args):
    return sum(args)


if __name__ == '__main__':
    task = celery.chord([identity.s(i) for i in range(10)], tsum.s())().get()
    print(task)
    print(task().get())
