'''
Created on Sep 11, 2017

'''
from smc import session
from smc_monitoring.monitors.logs import LogQuery
from smc_monitoring.monitors.connections import ConnectionQuery
from smc_monitoring.monitors.blacklist import BlacklistQuery
from smc_monitoring.monitors.users import UserQuery
from smc_monitoring.monitors.routes import RoutingQuery
from smc_monitoring.monitors.sslvpn import SSLVPNQuery
from smc_monitoring.monitors.vpns import VPNSAQuery
from smc_monitoring.models.constants import LogField
from smc_monitoring.models.filters import AndFilter, InFilter
from smc_monitoring.models.values import FieldValue, IPValue
from smc_monitoring.models.formatters import CSVFormat

if __name__ == '__main__':
    session.login(url='http://172.18.1.150:8082', api_key='EiGpKD4QxlLJ25dbBEp20001', timeout=30,
                  domain='foo')
    
    #query = ConnectionQuery('sg_vm')              # Make a Connection Query
    #query = BlacklistQuery('sg_vm')                    # Make a Blacklist Query
    #query = UserQuery('sg_vm')                    # Make a User Query
    #query = VPNSAQuery('sg_vm')                   # Show all current VPNs
    #query = SSLVPNQuery('sg_vm')                  # Find connected SSL VPN users
    query = RoutingQuery('sg_vm')                 # Query the routing table
    
    # Filter by SRC field, with values of 192.168.4.82 or 172.18.1.152
    #myfilter = InFilter(FieldValue(LogField.SRC), [IPValue('192.168.4.82'), IPValue('172.18.1.152')])
    
    # Filter to look for source IP 192.168.4.82 AND destination of 8.8.8.8
    #myfilter = AndFilter([
    #    InFilter(FieldValue(LogField.SRC), [IPValue('192.168.4.82')]),
    #    InFilter(FieldValue(LogField.DST), [IPValue('8.8.8.8')])])


    #query = LogQuery()                              # Make a Log Query
    #query = LogQuery(fetch_size=50)                 # Make a Log Query, limit fetch size to 50
    #query.update_filter(myfilter)                  # Add the filter created above to the query
    #query.time_range.last_five_minutes()            # Get the last five minutes of log data
    #query.format.timezone('CST')			           # Set the timezone for the client display
    #query.format.field_ids([LogField.TIMESTAMP, LogField.SRC, LogField.DST])    # Customize the return data columns we care about
    for record in query.fetch_batch():		       # Fetch a batch of results
    #for record in query.fetch_batch(CSVFormat):	   # Fetch a batch but return in CSV Format:
    #for record in query.fetch_live():			   # Get the live results from query, equivalent to hitting Play in SMC
        print(record),
        
    session.logout()
