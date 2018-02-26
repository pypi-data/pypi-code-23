from rx import Observable, Observer
from rx.concurrency import ThreadPoolScheduler
import time 
import random
from threading import current_thread

poolsch = ThreadPoolScheduler(8)

# xs = Observable.range(0,100000) \
#   .subscribe(on_next=lambda res: print(res), on_completed=lambda: print("wow"))

def intense_calculation(value,x):
    # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
    # x = 0
    # for _ in range(100):
    #     x += 1

    return value

Observable.interval(100) \
    .map(lambda i: i * 100) \
    .observe_on(poolsch) \
    .map(lambda s,x: intense_calculation(s,x)) \
    .subscribe(on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
               on_error=lambda e: print(e))

input("Press any key to exit\n")

# ys = Observable.range(200000,300000) \
#   .subscribe_on(poolsch) \
#   .subscribe(on_next=lambda res: print(res), on_completed=lambda: print("wowz"))



# https://gist.github.com/staltz/868e7e9bc2a7b8c1f754

# To create such stream with a single value is very simple in Rx*. The official terminology for 
# a stream is "Observable", for the fact that it can be observed, but I find it to be a silly name, so I call it stream.

# var requestStream = Rx.Observable.just('https://api.github.com/users');
# But now, that is just a stream of strings, doing no other operation, so we need to somehow make 
# something happen when that value is emitted. That's done by subscribing to the stream.

# requestStream.subscribe(function(requestUrl) {
#   // execute the request
#   jQuery.getJSON(requestUrl, function(responseData) {
#     // ...
#   });
# }