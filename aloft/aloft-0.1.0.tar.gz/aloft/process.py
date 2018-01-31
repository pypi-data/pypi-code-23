from subprocess import Popen, PIPE, CalledProcessError


def execute(cmd, ignore_error_messages=None, quiet=False):
    process = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True, encoding="utf-8")
    stderr, stdout = communicate(process, cmd, quiet)
    return_code = validate_return_code(process.returncode, ignore_error_messages, stderr, quiet)
    print_stderr(return_code, stderr, quiet)
    raise_if_error(return_code, cmd, stdout, stderr)

    return stdout


def communicate(process, cmd, quiet):
    stdout = ""

    if not quiet:
        print(f'\n**** {cmd}\n')

    for line in process.stdout:
        print_output(line.rstrip(), quiet)
        stdout += line

    stdout_empty, stderr = process.communicate()

    return stderr, stdout


def print_stderr(return_code, stderr, quiet):
    if return_code != 0:
        quiet = False

    if stderr:
        if not quiet:
            print("\nERROR:")
        for line in iter(stderr.splitlines()):
            print_output(line, quiet)
        print_output('', quiet)


def print_output(line, quiet):
    if not quiet:
        print(f'     {line}')


def validate_return_code(return_code, ignore_error_messages, stderr, quiet):
    if return_code != 0 and ignore_error_messages:
        for ignore_error_message in ignore_error_messages:
            if ignore_error_message in stderr:
                if not quiet:
                    print(f'\n** Ignoring return code: {return_code} - {ignore_error_messages[0]}')
                return_code = 0
                break

    return return_code


def raise_if_error(return_code, cmd, stdout, stderr):
    if return_code != 0:
        raise CalledProcessError(return_code, cmd, stdout, stderr)
