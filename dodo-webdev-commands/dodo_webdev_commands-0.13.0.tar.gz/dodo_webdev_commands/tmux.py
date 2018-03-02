# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework import CommandError
import os


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        pass

    def handle_imp(self, **kwargs):  # noqa
        check_exists = self.get_config('/TMUX/check_exists', '/')
        if not os.path.exists(check_exists):
            raise CommandError("Path %s does not exist" % check_exists)

        default_script = os.path.join(
            self.get_config("/ROOT/res_dir"),
            "tmux.sh"
        )
        tmux_script = self.get_config("/TMUX/script_file", default_script)
        self.runcmd(["chmod", "+x", tmux_script])
        self.runcmd([tmux_script])
