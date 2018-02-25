import pandas as pd
import click
import json as _json


# Consts

VERSIONS = {
    'tls1': 'TLS 1.0',
    'tls1_1':  'TLS 1.1',
    'tls1_2': 'TLS 1.2',
    'ssl3': 'SSLv3'
}

NO_SUCH_ACCOUNT = 'Could not find account.\nMake sure an accurate name was provided.'
NO_ACCOUNT_ID = 'Incomplete account name. No account ID found in arguments'
NO_ACCOUNT_ARG = 'Error. No account provided'
INVALID_PATH = 'Invalid path or file does not exist: {}'
UNKNOWN_ERR = 'Unknown error'
NO_OUTPUT = 'Can\'t pass --silent without --json. Exiting.'

# /Consts


def print_exception_and_exit(msg):
    print(msg)
    exit(1)


def find_account_by_name(full_account, dataframe):
    account_id = None

    for part in full_account:
        if part.isdigit():
            account_id = part
            full_account.remove(account_id)

    if not account_id:
        print_exception_and_exit(NO_ACCOUNT_ID)

    full_account = '{} - {}'.format(account_id, ' '.join(full_account))
    account_df = dataframe.loc[dataframe['account_id_name'].str.contains(full_account)]
    return account_df


def parse_sites(sites):
    arr = []
    for site in sites.split():
        if not site.isdigit() and not site == '-':
            arr.append(site)
    return arr


def extract_tls_breakdown(acc_df):
    try:
        print("#### TLS Breakdown ####\n")
        print('Account: {}'.format(acc_df['account_id_name'].iloc[0]))
        print('Plan: {} \n'.format(acc_df['plan'].iloc[0]))
        for v in acc_df.itertuples():
            print('Version:',  VERSIONS.get(v.sslversion))
            print('Audit Sessions:',  v.audit_sessions)
            print('Used in sites:\n------------\n' + '\n'.join(parse_sites(v.sites)) + '\n')
    except IndexError:
        print_exception_and_exit(NO_SUCH_ACCOUNT)


def write_json(acc_df):
    try:
        account = acc_df['account_id_name'].iloc[0]
        data = {
            account: {
                'Versions': {}
            }
        }
        for v in acc_df.itertuples():
            version = VERSIONS.get(v.sslversion)
            sessions = v.audit_sessions
            sites = parse_sites(v.sites)
            data[account]['Versions'][version] = {
                'Audit Sessions': sessions,
                'Sites': sites
            }
        with open(account + '.json', 'w') as file:
            file.write(_json.dumps(data, indent=4))
    except IndexError:
        print_exception_and_exit(NO_SUCH_ACCOUNT)


@click.command()
@click.argument('account-name', nargs=-1)
@click.option('-f', '--file', required=True, help='TLS file in csv format to extract breakdown from')
@click.option('--json', is_flag=True, help='Output to JSON file')
@click.option('-s', '--silent', is_flag=True, help='Do not print anything to sdout')
def main(file, account_name, json, silent):

    """
    Always prefer using full account name (name + ID) over ID alone, if possible.
    If account name is copied from Zendesk - drop any parentheses '()' around the account's ID.
    Account names are case sensitive.

    Usage example:\n
    Example 1: tlsx -f mytls.csv ACCOUNT NAME 123456\n
    Example 2: tlsx --file mytls.csv 98765
    """

    if silent and not json:
        print_exception_and_exit(NO_OUTPUT)

    try:
        df = pd.read_csv(file, encoding='latin1')
    except FileNotFoundError:
        print_exception_and_exit(INVALID_PATH.format(file))

    if account_name:
        tls_account = find_account_by_name(list(account_name), df)
    else:
        print_exception_and_exit(NO_ACCOUNT_ARG)

    if not silent:
        try:
            extract_tls_breakdown(tls_account)
        except UnboundLocalError:
            print_exception_and_exit(UNKNOWN_ERR)

    if json:
        write_json(tls_account)
