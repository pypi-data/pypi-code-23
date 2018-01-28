
class XboxError(Exception):
    def __init__(self, code):
        self.code = code

    def error_str(self):
        if self.code == 500:
            return 'No Xbox Controller Driver found -- Please install it with sudo apt-get install xboxdrv'
