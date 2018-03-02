# noqa
import argparse
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('script')
        parser.add_argument(
            'script_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, script, script_args, **kwargs):  # noqa
        self.runcmd(
            [
                self.get_config('/PYTHON/python'),
                script,
            ] + remove_trailing_dashes(script_args),
            cwd=self.get_config('/PYTHON/src_dir')
        )
