import sys

import pet_utils
import utils

G_STG_SSH_COMPLIANT = 'user-stg-compliant'
G_STG_SUDO_NON_COMPLIANT = 'user-stg-noncompliant'

G_BTCH_SSH = 'user-ci'
G_BTCH_SUDO = 'user-batch-noncompliant'

ALTUS_COMPLIANT = 'PaaS'
PAASREALM_PREP = 'Pre-Production'
PAASREALM_PROD = 'Production'
PAASREALM_STG = ['Staging','staging']
PAASREALM_LNP = 'LnP'
PAASREALM_QA = 'QA'

STACK_RAPTOR = 'raptor.marketplace'
STACK_RAPTOR_BTCH = 'raptorbatch.marketplace'

CorpPassWord = ''

def handle_result(results, user):
    print results
    compliant = results[0]['managedBy']
    stack = results[0]['stackId']
    paas_realm = results[0]['paasRealm']

    if compliant == ALTUS_COMPLIANT and stack != STACK_RAPTOR_BTCH:
        print 'User can not get SUDO access, because the pool is Altus-Compliance, and it is not raptorbatch!'
        if paas_realm in PAASREALM_STG or paas_realm == PAASREALM_LNP:
            print 'Join NetGroup via PET to get SSH access for Staging/LnP: ' + G_STG_SSH_COMPLIANT
            if pet_utils.is_user_in_group(user, G_STG_SSH_COMPLIANT):
                print user + ' Already in ' + G_STG_SSH_COMPLIANT + ', Should have SSH access.'
            else:
                print user + ' Not in ' + G_STG_SSH_COMPLIANT + ', help user send request to join.'
                # pet_utils.request_join_group(user,G_STG_SSH_COMPLIANT)

        elif paas_realm == PAASREALM_PREP or paas_realm == PAASREALM_PROD:
            print 'Join NetGroup via PET to get access for Pre-Prod & Prod'
        elif paas_realm == PAASREALM_QA:
            print 'Managed by Monterey, please use corp account login. like user@hostname -p 11022'

    elif compliant == ALTUS_COMPLIANT and stack == STACK_RAPTOR_BTCH:
        if paas_realm == PAASREALM_QA or paas_realm == PAASREALM_LNP or paas_realm in PAASREALM_STG:
            print 'Altus-Compliance && raptorbatch, Join NetGroup via PET to get SSH:' + G_BTCH_SSH
            if pet_utils.is_user_in_group(user, G_BTCH_SSH):
                print user + ' Already in ' + G_BTCH_SSH + ', Should have SSH access.'
            else:
                print user + ' Not in ' + G_BTCH_SSH + ', help user send request to join group.'
                # pet_utils.request_join_group(user, G_BTCH_SSH)

            print 'Altus-Compliance && raptorbatch, Join NetGroup via PET to get Sudo:' + G_BTCH_SUDO
            if pet_utils.is_user_in_group(user, G_BTCH_SUDO):
                print user + ' Already in ' + G_BTCH_SUDO + ', Should have Sudo access.'
            else:
                print user + ' Not in ' + G_BTCH_SUDO + ', help user send request to join group.'
                # pet_utils.request_join_group(user, G_BTCH_SUDO)

    elif compliant != ALTUS_COMPLIANT:
        if paas_realm in PAASREALM_STG or paas_realm == PAASREALM_LNP:
            print 'Join NetGroup via PET to get Sudo:' + G_STG_SUDO_NON_COMPLIANT
            if pet_utils.is_user_in_group(user, G_STG_SUDO_NON_COMPLIANT):
                print user + ' Already in ' + G_STG_SUDO_NON_COMPLIANT + ', Should have Sudo access.'
            else:
                print user + ' Not in ' + G_STG_SUDO_NON_COMPLIANT + ', help user send request to join group.'
                # pet_utils.request_join_group(user, G_STG_SUDO_NON_COMPLIANT)


def altus_compliant_group_by_host(hostname,user):
    q = 'Compute[@label="%s"].computes!VCluster.resourceClusters!ApplicationService{@resourceId,@managedBy,@paasRealm,@stackId}' % hostname
    result = utils.queryCMS(q, CorpPassWord)
    if len(result) > 0:
        handle_result(result, user)
    else:
        print 'No result for input: ' + hostname




if __name__ == "__main__":
    # is_compliant = altus_compliant_group_by_host('clsprv-1981880.phx02.dev.ebayc3.com','guoxu')
    args = sys.argv

    if len(args) == 4:
        is_compliant = altus_compliant_group_by_host(args[1], args[2])
        CorpPassWord = args[3]
    elif len(args) == 3:
        is_compliant = altus_compliant_group_by_host(args[1], args[2])
        # TODO Here need changed to your copr password, to query CMS
        CorpPassWord = '!QAZ2wsx#EDC'
    else:
        print "Please execute like: python access_rule.py hostname user CorpPassWord"
