from bitcoinrpc.authproxy import AuthServiceProxy
import click
import sys
import csv

# account_name is the account that need to be restored

account_name = 'payment'

def getConnection(rpc_user,rpc_password,rpc_port):
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:%s"%(rpc_user,rpc_password,rpc_port))
    return rpc_connection

def reconcile(rpc_connection,addr_csv,account_name):
    current_addresses = rpc_connection.getaddressesbyaccount("%s"%(account_name))
    print ('Number of address in current wallet backup: %s'%len(current_addresses))

    with open(addr_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print ("this address %s is set on %s account"%(row['address'],account_name))
            rpc_connection.setaccount("%s"%(row['address']),"%s"%account_name)
    return

@click.command()
@click.argument('addr_csv',required = True)
@click.argument('rpc_user',required = True)
@click.argument('rpc_password',required = True)
@click.argument('rpc_port',required = True)

def main(addr_csv,rpc_user,rpc_password,rpc_port):
    """ 'path_to_csv', 'rpc_user' and 'rpc_password' are all required for this script """
    #  (addr_csv,rpc_user,rpc_password) = readInput()
    rpc_connection = getConnection(rpc_user,rpc_password,rpc_port)
    reconcile(rpc_connection,addr_csv,account_name)