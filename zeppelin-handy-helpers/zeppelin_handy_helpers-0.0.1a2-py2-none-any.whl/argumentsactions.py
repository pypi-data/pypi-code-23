import argparse

from handlers import ActionHandler, Action


class Read(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        ActionHandler.action(Action.read, namespace, namespace.end_point, namespace.slack_end_point)


class Check(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        ActionHandler.action(Action.check, namespace, namespace.end_point, namespace.slack_end_point)


class Stop(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        ActionHandler.action(Action.stop, namespace, namespace.end_point, namespace.slack_end_point)


class Monitor(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        ActionHandler.action(Action.monitor, namespace, namespace.end_point, namespace.slack_end_point)
