from cloudshell.cli.command_template.command_template import CommandTemplate


ENABLE_SNMP_SERVER = CommandTemplate('configure system snmp no shutdown')

# SNMP V2
ENABLE_SNMPV2 = CommandTemplate('configure system security snmp community '
                                '{snmp_community} {access_mode} version v2c')
DISABLE_SNMPV2 = CommandTemplate('configure system security snmp no community {snmp_community}')


# SNMP V3
SHOW_USERS = CommandTemplate('show system security user')

ENABLE_VIEW = CommandTemplate('configure system security snmp view {view} subtree 1 mask ff')
DISABLE_VIEW = CommandTemplate('configure system security snmp no view {view}')

ENABLE_GROUP = CommandTemplate(
    'configure system security snmp access group {group} security-model usm '
    'security-level {security_level} '  # no-auth-no-privacy|auth-no-privacy|privacy  
    'read {view} write {view}'
)
DISABLE_GROUP = CommandTemplate('configure system security snmp no access group {group}')

ENABLE_USER_ACCESS = CommandTemplate('configure system security user {user} access snmp')
DISABLE_USER = CommandTemplate('configure system security no user {user}')

ENABLE_USER_SNMP_AUTH = CommandTemplate(
    'configure system security  user {user} snmp '
    'authentication {auth_type}[ {auth_key}]'  # none|md5|sha
    '[ privacy {priv_type}][ {priv_key}]'  # none|des-key|aes-128-cfb-key
)

ENABLE_USER_SNMP_GROUP = CommandTemplate(
    'configure system security user {user} snmp group {group}')
