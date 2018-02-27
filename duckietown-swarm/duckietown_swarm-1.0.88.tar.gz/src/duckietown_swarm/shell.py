import os
from system_cmd.meat import system_cmd_result


def shell_access(port):
    script = '''#!/bin/bash
echo TERM=$TERM
echo Starting the shell > /dev/stderr
echo
echo Welcome to `hostname`
echo
echo If backspace does not work, you should call on the client the following command:
echo
echo     $  stty erase '^h'
echo
echo Note that ctrl-c does not work.
echo
echo
/bin/bash -i 2>&1
'''
    filename = '/tmp/shell'
    with open(filename, 'w') as f:
        f.write(script)

    os.chmod(filename, 0744)
    print('starting ncat')
    cmd = ['ncat' , '--deny', '1.0.1.1', '-k', '-l', '-p', str(port), '-e', filename]
    system_cmd_result('.', cmd, raise_on_error=True)
#    p = subprocess.Popen(
#                cmd,
#                stdout=sys.stdout,
#                stderr=sys.stderr,
#                bufsize=0,
#
#                cwd='.')
#
#    p.wait()
