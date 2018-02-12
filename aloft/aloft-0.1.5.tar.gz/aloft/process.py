import time
from aloft.output import print_action, print_details, print_details_line
from subprocess import Popen, PIPE, CalledProcessError


def execute(cmd, ignore_error_messages=None, quiet=False, retry_error_messages=['x509']):
    process = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True, encoding='utf-8')
    stderr, stdout = communicate(process, cmd, quiet)
    return_code = process.returncode
    should_ignore_error = should_ignore_return_code(return_code, ignore_error_messages, stderr, quiet)
    print_stderr(stderr, return_code, should_ignore_error)

    if should_retry(return_code, retry_error_messages, stderr, quiet):
        time.sleep(2)
        return execute(cmd, ignore_error_messages, quiet, retry_error_messages)
    else:
        if not should_ignore_error:
            raise_if_error(return_code, cmd, stdout, stderr)

    return stdout


def communicate(process, cmd, quiet):
    stdout = ""

    if not quiet:
        print_action(cmd)

    for line in process.stdout:
        if not quiet:
            print_details_line(line.rstrip())
        stdout += line

    if not quiet and stdout:
        print('')

    stdout_empty, stderr = process.communicate()

    return stderr, stdout


def print_stderr(stderr, return_code, ignoring):
    if stderr and return_code != 0 and not ignoring:
        print("\nERROR:")
        print_details(stderr)


def should_ignore_return_code(return_code, ignore_error_messages, stderr, quiet):
    ignore = False
    if return_code != 0 and ignore_error_messages:
        for ignore_error_message in ignore_error_messages:
            if ignore_error_message in stderr:
                if not quiet:
                    print_details(f'Ignoring return code: {return_code} - {ignore_error_message}')
                ignore = True
                break

    return ignore


def should_retry(return_code, retry_error_messages, stderr, quiet):
    retry = False

    if return_code != 0 and retry_error_messages:
        for retry_error_message in retry_error_messages:
            if retry_error_message in stderr:
                if not quiet:
                    print_details(f'Retrying: {return_code} - {retry_error_message}')
                    retry = True
                break

    return retry

def raise_if_error(return_code, cmd, stdout, stderr):
    if return_code != 0:
        raise CalledProcessError(return_code, cmd, stdout, stderr)
