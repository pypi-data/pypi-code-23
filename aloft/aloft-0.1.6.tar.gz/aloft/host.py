import time
from aloft.output import print_action
from aloft.process import execute
from subprocess import CalledProcessError


def wait_for_domain_to_resolve(domain):
    print_action(f'Waiting for domain to resolve: {domain}')
    success_count_in_a_row = 0

    while success_count_in_a_row < 10:
        if does_domain_resolve(domain):
            success_count_in_a_row += 1
            print('+', end='', flush=True)
        else:
            success_count_in_a_row = 0
            print('.', end='', flush=True)
        time.sleep(2)

    print(' resolved\n')


def does_domain_resolve(domain):
    resolves = True

    try:
        execute(f'host -t SOA {domain}', quiet=True)
    except CalledProcessError:
        resolves = False

    return resolves


