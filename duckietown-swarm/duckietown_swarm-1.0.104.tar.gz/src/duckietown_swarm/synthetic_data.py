import datetime
import os
import socket
import time


def synthetic_data_writer(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    delta = 60
    length = 1024

    i = 0
    while True:
        hname = socket.gethostname()[:8]
        while True:
            basename = 'dummy_%s_%05d.txt' % (hname, i)
            fn = os.path.join(dirname, basename)
            if os.path.exists(fn):
                i += 1
            else:
                break
        contents = str(datetime.datetime.now())
        contents += '\n' + '?' * length

        with open(fn, 'w') as f:
            f.write(contents)
        print('Created %s' % fn)
        time.sleep(delta)

