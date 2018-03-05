import subprocess
import readline
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


def branch_autocomplete(app):
    branches = subprocess.check_output("git -C $PROJECTS/{0} branch --remote --sort=-committerdate".format(app),
                                       shell=True).split('\n')
    branches = filter(lambda x: x, [x.replace(',', '').replace('origin/', '').strip() for x in branches])

    def completer(text, state):
        options = [x for x in branches if x.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    # Unfortunately, we can't sort the completer output correctly without a big lift.
    # See https://pewpewthespells.com/blog/osx_readline.html.

    inp = ""
    while inp not in branches:
        inp = raw_input("Pick a branch for {0} (tab to complete): ".format(app))

    return inp
