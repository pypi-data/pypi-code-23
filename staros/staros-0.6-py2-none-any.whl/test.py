from staros import StarClient


cli = StarClient("login", "password", "10.21.219.18", 22)

# 1) get number of enode-b associations
print cli.getEnodebAssociatNum()
#response
#{'Total ENodeB': '332'}

# 2) get full number of total subscribers and subscribers on mme/pgw/sgw/ggsn/sgsn
print cli.getsubssessionmain()
#response
#{
# 'utran': {'sgsn': '0', 'ggsn-pdp-type-ipv4': '19351', 'sgsn-pdp-type-ipv4': '0'},
# 'total': {'active': '61289', 'Total Subscribers': '75281'},
# 'eutran': {'mme': '18742', 'pgw-gtp-ipv4': '18447', 'sgw-gtp-ipv4': '18786'}
# }


# 3) get some info about msisdn sessions
print cli.getsubscrmsisdn("375298766719")
#response
#{
#   4: {
#               'msisdn': '375298766719', 'callid': '24c9bd29', 'ip-address': '100.125.194.236', 'imsi': '257027519540042',
#               'sesstype': {
#                               'Call state': 'Connected',
#                               'Access CSCF status': 'Not Applicable',
#                               'Access tech': 'eUTRAN',
#                               'Access type': 'sgw-gtp-ipv4',
#                               'Network type': 'IP',
#                               'Link status': 'Online/Active'
#                           }
#       },
#   5: {
#               'msisdn': '375298766719', 'callid': '24c9bd2a', 'ip-address': '100.125.194.236', 'imsi': '257027519540042',
#               'sesstype': {
#                               'Call state': 'Connected',
#                               'Access CSCF status': 'Not Attached',
#                               'Access tech': 'eUTRAN',
#                               'Access type': 'pgw-gtp-ipv4',
#                               'Network type': 'IP',
#                               'Link status': 'Online/Active'
#                           }
#       },
#   1: {
#               'msisdn': 'n/a', 'callid': '0c5aed12', 'ip-address': '100.73.22.252', 'imsi': '257027518529391',
#               'sesstype': {
#                               'Call state': 'Connected',
#                               'Access CSCF status': 'Not Applicable',
#                               'Access tech': 'eUTRAN',
#                               'Access type': 's1-mme',
#                               'Network type': 'IP',
#                               'Link status': 'Online/Active'
#                           }
#       },
#   2: {
#               'msisdn': 'n/a', 'callid': '2dba6ef5', 'ip-address': '100.125.194.236', 'imsi': '257027519540042',
#               'sesstype': {
#                               'Call state': 'Connected',
#                               'Access CSCF status': 'Not Applicable',
#                               'Access tech': 'eUTRAN',
#                               'Access type': 's1-mme',
#                               'Network type': 'IP',
#                               'Link status': 'Online/Active'
#                           }
#       },
#   3: {
#               'msisdn': '375298766719', 'callid': '0cf2bf6e', 'ip-address': '100.73.22.252', 'imsi': '257027518529391',
#               'sesstype': {
#                               'Call state': 'Connected',
#                               'Access CSCF status': 'Not Applicable',
#                               'Access tech': 'eUTRAN',
#                               'Access type': 'sgw-gtp-ipv4',
#                               'Network type': 'IP',
#                               'Link status': 'Online/Active'
#                           }
#       },
# 'sessnum': 5
# }
#
# if not found response
# {'sessnum': 0}

