import time


class Util:

    @staticmethod
    def current_time_millis():
        return int(round(time.time() * 1000))

    @staticmethod
    def lock_time_millis():
        return int(round(time.time() * 1000)) + 5*60*1000
