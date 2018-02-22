from bitcoinrpc.authproxy import AuthServiceProxy
import sys
import csv
#rpc_user, rpc_password, account_name should match the configuration in bitcoind

account_name = 'c2'

def readInput():
    try:
        # Path to addresses missed csv file
        addr_csv = sys.argv[1]
        rpc_user = sys.argv[2]
        rpc_password = sys.argv[3]

    except IndexError:
        raise IndexError('First parameter should be path to addresses missed csv file'\
        '\n Second parameter should be rpc-user, Third parameter should be rpc-password'\
        '\n for example: python3 restore.py /home/david/Desktop/node_1/lost_addr.csv bitcoin-rpc PaSS')
    return (addr_csv,rpc_user,rpc_password)

def getConnection(rpc_user,rpc_password):
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:3457"%(rpc_user,rpc_password))
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

def main():
     (addr_csv,rpc_user,rpc_password) = readInput()
     rpc_connection = getConnection(rpc_user,rpc_password)
     reconcile(rpc_connection,addr_csv,account_name)

main()