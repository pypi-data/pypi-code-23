# encoding:utf-8
 
from thrift4p.utils import generate_client
 
client = generate_client("com.didapinche.thrift.dm.proxy.dm_proxy_service.DMProxyService")
 
# print dir(client)
 
# result = client.setLbsTag('hexagon',2,'5996179','AC_CI_LBS_NO_COUPON')
# 
# print result

result = client.unsetLbsTag('hexagon',2,'5996179','AC_CI_LBS_NO_COUPON')

print result

# result = client.getLbsTags('hexagon',2,'5996179')
# print result
# result = client.getUserCreditInfo(1655222)
# 
# print result.creditInfo
# print result.tags