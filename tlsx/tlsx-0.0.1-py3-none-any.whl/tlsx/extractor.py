import pandas as pd
import click


versions = {
    'tls1': 'TLS 1.0',
    'tls1_1':  'TLS 1.1',
    'tls1_2': 'TLS 1.2',
    'ssl3': 'SSLv3'
}


def find_account_by_name(full_account, dataframe):
    account_id = None

    for part in full_account:
        if part.isdigit():
            account_id = part
            full_account.remove(account_id)

    if not account_id:
        print('Incomplete account name. No account ID found in parameter')
        exit(1)

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
            print('Version:',  versions.get(v.sslversion))
            print('Audit Sessions:',  v.audit_sessions)
            print('Used in sites:\n------------\n' + '\n'.join(parse_sites(v.sites)) + '\n')
    except IndexError:
        print('Could not find account.\nMake sure an accurate name was provided.')
        exit(2)


@click.command()
@click.argument('account-name', nargs=-1)
@click.option('-f', '--file', required=True, help='TLS file in csv format to extract breakdown from')
def main(file, account_name):
    """
    Always prefer using full account name (name + ID) over ID alone, if possible.
    If account name is copied from Zendesk - drop any parentheses '()' around the account's ID.
    Account names are case sensitive.

    Usage example:\n
    Example 1: tlsx -f mytls.csv ACCOUNT NAME 123456\n
    Example 2: tlsx --file mytls.csv 98765
    """

    try:
        df = pd.read_csv(file, encoding='latin1')
    except FileNotFoundError:
        print('Invalid file path {}'.format(file))
        exit(1)

    if account_name:
        tls_account = find_account_by_name(list(account_name), df)
    else:
        print('Error. No account provided')
        exit(1)

    try:
        extract_tls_breakdown(tls_account)
    except UnboundLocalError:
        print('Unknown Error')
        exit(1)
