# encoding: utf-8

'''
Created on 2018年1月30日 下午2:32:51

@author: jiangyuanshu
'''
from thrift4p import generate_client_from_zk

def generate_client(api):
    """tests
    """
    
    from logutils.connection import getZkAddr
    
    zkAddr = getZkAddr()
    client = generate_client_from_zk(api,zkAddr)
    
    return client
    
if __name__ == "__main__":
#     api2ip_port_set,api2path_set = get_api_server()
#     print api2ip_port_set
     
    client = generate_client("com.didapinche.thrift.dm.hub.holder.DmOperationHubService")
     
#     result = client.holdTaxiOrder(42,998,u'半径太小'.encode("utf-8"),True)
#     print result
    #generate_client("com.didapinche.thrift.dm_ratio_predict.RatioPredictService")
    #generate_client("com.didapinche.thrift.dm_ride_relationship.RideRelationshipService")