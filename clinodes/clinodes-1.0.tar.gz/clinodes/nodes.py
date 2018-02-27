import sys

class Node(object):
    def __init__(self):
        self.expects_more = True

    def run(self, *args_remained): pass
    def setup(self): pass


class ArgNode(Node):
    count = 1
    storage = {}

    def __init__(self):
        super().__init__()
        self.commands = {}
        self.switches = {}
        self.enable_any = False
        self.expects_more = True
        self.__work()

    def __work(self):
        self.setup()
        cur_args = sys.argv[ArgNode.count::]
        ArgNode.count += 1
        if self.expects_more:
            arg = cur_args[0]
            if not self.enable_any:
                if arg not in self.commands.keys() and arg not in self.switches.keys():
                    raise KeyError("Invalid arg: {}".format(arg))
                else:
                    if arg in self.commands:
                        self.commands[arg]()
                    if arg in self.switches:
                        self.switches[arg](self)
                        ArgNode.count += 1
        self.run(*cur_args)

    def setup(self):
        pass

    def run(self, *args_remained):
        pass



class Switch(Node):
    def __init__(self, next=None):
        super().__init__()
        self.expects_more = False
        self.__work(next)

    def __call__(self, next=None):
        self.__work(next)

    def __work(self, next_node):
        self.setup()
        cur_args = sys.argv[ArgNode.count::]
        self.run(*cur_args)
        next_node.__init__()

    def setup(self): pass
    def run(self, *args): pass