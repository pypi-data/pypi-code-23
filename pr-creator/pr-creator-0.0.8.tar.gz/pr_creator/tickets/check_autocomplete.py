import subprocess
import readline
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


branches = subprocess.check_output("git  branch --remote --sort=-committerdate", shell=True).decode('utf-8').split('\n')
branches = filter(lambda x: x, [x.replace(',', '').replace('origin/', '').strip() for x in branches])


def completer(text, state):
    options = [x for x in branches if x.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None


readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

inp = raw_input("Pick a branch: ")
print "You entered", inp
