

class Color:
    @staticmethod
    def underline(string):
        return '\033[4m' + string + '\033[0m'

    @staticmethod
    def light(string):
        return '\033[2m' + string + '\033[0m'

    @staticmethod
    def red(string):
        return '\033[31m' + string + '\033[0m'

    @staticmethod
    def green(string):
        return '\033[32m' + string + '\033[0m'

    @staticmethod
    def orange(string):
        return '\033[33m' + string + '\033[0m'

    @staticmethod
    def blue(string):
        return '\033[34m' + string + '\033[0m'

    @staticmethod
    def pink(string):
        return '\033[35m' + string + '\033[0m'

    @staticmethod
    def light_blue(string):
        return '\033[36m' + string + '\033[0m'

    @staticmethod
    def white(string):
        return '\033[37m' + string + '\033[0m'

    @staticmethod
    def purple(string):
        return '\033[95m' + string + '\033[0m'
