import asyncio

lock = asyncio.Lock()
initialized = False

async def initialize(msg):
    global initialized
    global lock
    print("coro {} sees initialized={} and locked={}".format(msg, initialized, lock.locked()))
    with (await lock):
        if initialized:
            print("coro {} returns".format(msg))
            return
        print("coro {} has got the lock".format(msg))
        await asyncio.sleep(0.4)
        initialized = True


loop = asyncio.get_event_loop()
n = 3

def run(labels):
    tasks = [ initialize(label) for label in labels ]
    loop.run_until_complete(asyncio.gather(*tasks))

run( [ "run0{}".format(i) for i in range(1, n+1) ] )
print("==========")
run( [ "run1{}".format(i) for i in range(1, n+1) ] )
