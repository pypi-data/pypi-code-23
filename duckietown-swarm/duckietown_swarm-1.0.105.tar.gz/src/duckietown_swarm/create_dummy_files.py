import os
import random
import sys
import time

if __name__ == '__main__':
    print('%s <where> <interval>' % sys.argv[0])
    where = sys.argv[1]
    interval = int(sys.argv[2])
    while True:
        basename = 'dummy%d' % random.randint(1, 100000)
        size = 100 * 1000
        fn = os.path.join(where, basename)
        with open(fn, 'wb') as f:
            for i in range(size):
                f.write(str(i))
        print('written %s' % fn)

        time.sleep(interval)
