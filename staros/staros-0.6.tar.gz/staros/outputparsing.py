import re
import additionalparse

def _parseshowsess(data):
    a1 = re.search(r'Active:\s{2,100}(\d{1,20})', data)
    a2 = re.search(r'sgw-gtp-ipv4:\s{2,100}(\d{1,20})', data)
    a3 = re.search(r'mme:\s{2,100}(\d{1,20})', data)
    a4 = re.search(r'ggsn-pdp-type-ipv4:\s{2,100}(\d{1,20})', data)
    a5 = re.search(r'sgsn:\s{2,100}(\d{1,20})', data)
    a6 = re.search(r'sgsn-pdp-type-ipv4:\s{2,100}(\d{1,20})', data)
    a7 = re.search(r'pgw-gtp-ipv4:\s{2,100}(\d{1,20})', data)
    a8 = re.search(r'Total\sSubscribers:\s{2,100}(\d{1,20})', data)
    res = {"total": {"Total Subscribers": a8.group(1),
                     "active":a1.group(1)},
           "utran": {"sgsn": a5.group(1),
                     "sgsn-pdp-type-ipv4": a6.group(1),
                     "ggsn-pdp-type-ipv4": a4.group(1)
                     },
           "eutran": {"mme": a3.group(1),
                      "sgw-gtp-ipv4": a2.group(1),
                      "pgw-gtp-ipv4": a7.group(1)
                      }
           }
    return res


def _parseEnodebAssoc(data):
    a1 = re.search(r'Total ENodeB Associations\s{2,100}:\s{1,10}(\d{1,20})', data)
    resp ={"Total ENodeB" : a1.group(1)}
    return resp


def _parseClearSubsc(data):
    a1 = re.search(r'No\ssubscribers\smatch\sthe\sspecified\scriteria', data)
    a2 = re.search(r'Number of subscribers cleared:\s{1,10}(\d{1,20})', data)
    if a1:
        return 'Not found'
    else:
        return 'Cleared: '+a2.group(1)


def _getsubscribermsisdn(data):
    a1 = re.findall(r'.{6}\s\w{8}\s\d{9,20}\s...\s{5,100}\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\s{1,5}\w{9}', data)
    a2 = re.findall(r'.{6}\s\w{8}\s\d{9,20}\s\d{5,15}\s{5,100}\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\s{1,50}\w{9}', data)
    i=1
    num =0
    resout={}
    for elem in a1:
        el = re.findall(r'\b\S{3,50}', elem)
        type = additionalparse._getsubsinfoparse(el[0])
        res = {i:{"sesstype":type,
                          "callid":el[1],
                          "imsi":el[2],
                          "msisdn":el[3],
                          "ip-address":el[4]}}
        i+=1
        resout.update(res)
    for elem1 in a2:
        el1 = re.findall(r'\b\S{3,50}', elem1)
        type1 = additionalparse._getsubsinfoparse(el1[0])
        res1 = {i: {"sesstype":type1,
                            "callid": el1[1],
                            "imsi": el1[2],
                            "msisdn": el1[3],
                            "ip-address": el1[4]}}
        num = i
        i += 1
        resout.update(res1)
    resout.update({"sessnum":num})
    return resout