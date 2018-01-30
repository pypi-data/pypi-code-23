import sys
import getpass
import os.path
import ldap3
from .manager import ActiveDirectorySimpleManager, DN, OBJ_ATTR_SIMPLE_PARAMS, UAC_ACCOUNTDISABLE, \
    UAC_DONT_EXPIRE_PASSWORD, UAC_NA, UAC_SMARTCARD_REQUIRED, GRPTYPE_FLG_GLOBAL, GRPTYPE_FLG_LOCAL, \
    GRPTYPE_FLG_UNIVERSAL, GRP_SEC_GLOBAL, GRPTYPE_FLG_SYSTEM, GRPTYPE_FLG_SECURITY, GRP_SYS, MS_DOMAIN_VERSION, \
    PWDPROP_DOMAIN_PASSWORD_COMPLEX, PWDPROP_DOMAIN_PASSWORD_NO_ANON_CHANGE, PWDPROP_DOMAIN_PASSWORD_NO_CLEAR_CHANGE, \
    PWDPROP_DOMAIN_PASSWORD_STORE_CLEARTEXT
from .simcli import SimpleCli, ERR_OK, ERR_UNKONWN, ERR_FAILED, ERR_INVALID_SYNTAX, ERR_MSG

if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding("utf-8")


ADSMT_VERSION = '1.0.10'
ADSMT_TITLE = "Active Directory Simple Management Toolkit (AD-SMT)"
ADSMT_CONF = '/etc/adsmt.conf'

ERR_NOT_FOUND = 4
ERR_REALM_UNKNOWN = 5
ERR_REALM_NOT_SELECTED = 6
ERR_LDAPGET_DOMAIN_ENTRY = 7
ERR_LDAPGET_DC_LIST = 8
ERR_LDAPGET_COMPUTERS_LIST = 9
ERR_LDAPGET_USERS_LIST = 10
ERR_LDAPGET_GROUPS_LIST = 11
ERR_LDAPGET_DOMAIN_TREE = 12
ERR_NONUNIQUE_CN = 13
ERR_NONUNIQUE_LOGIN = 14
ERR_USER_PASSWORD_TOO_SHORT = 15
ERR_USER_PASSWORD_CONFIRM = 16
ERR_PATH_NOT_EXISTS = 17
ERR_INVALID_PARAMETERS = 18
ERR_INVALID_LDAP_USER = 19
ERR_NOT_DELETING_BECAUSE_SYSCRITICAL = 20
ERR_NOT_SUPPORTED = 21
ERR_USER_GROUPS_MEMBERSHIP = 22
ERR_USER_NOT_IN_GROUP = 23
ERR_USER_ATTR_NOT_SUPPORTED = 24
ERR_GROUP_IS_PRIMARY = 25
ERR_GROUP_MEMBERS = 26
ERR_GROUP_BUILTIN_TYPE_CHANGE = 27
ERR_GROUP_BUILTIN_DELETE = 28
ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL = 29
ERR_OU_NOT_EMPTY = 30
ERR_NOT_DELETING_BECAUSE_SYSCRITICAL_CHILDS = 31
ERR_REALM_MISMATCH = 32
ERR_COMPUTER_GROUPS_MEMBERSHIP = 33
ERR_COMPUTER_NOT_IN_GROUP = 34
ERR_COMPUTER_ATTR_NOT_SUPPORTED = 35
ERR_COMPUTER_NAME_SYNTAX = 36
ERR_NONUNIQUE_COMPUTER_NAME = 37
ERR_MSG.update({
    ERR_UNKONWN: "unknown error",
    ERR_FAILED: "operation failed",
    ERR_INVALID_SYNTAX: "invalid syntax",
    ERR_NOT_FOUND: "not found",
    ERR_REALM_UNKNOWN: "given realm is not defined in the configuration",
    ERR_REALM_NOT_SELECTED: "no realm is selected to manage, use 'select' command",
    ERR_LDAPGET_DOMAIN_ENTRY: "cannot get domain entry from LDAP",
    ERR_LDAPGET_DC_LIST: "cannot get list of domain controllers",
    ERR_LDAPGET_COMPUTERS_LIST: "cannot get list of domain computers",
    ERR_LDAPGET_USERS_LIST: "cannot get list of domain users",
    ERR_LDAPGET_GROUPS_LIST: "cannot get list of domain groups",
    ERR_LDAPGET_DOMAIN_TREE: "cannot get domain tree structure",
    ERR_NONUNIQUE_CN: "there is another domain object with given name",
    ERR_NONUNIQUE_LOGIN: "there is another user with given login name",
    ERR_USER_PASSWORD_TOO_SHORT: "password must be at least 6 characters length",
    ERR_USER_PASSWORD_CONFIRM: "password and its confirmation does not matches",
    ERR_PATH_NOT_EXISTS: "path does not exists in the domain structure",
    ERR_INVALID_PARAMETERS: "invalid parameter(s)",
    ERR_INVALID_LDAP_USER: "invalid Active Directory user entry",
    ERR_NOT_DELETING_BECAUSE_SYSCRITICAL: "cannot delete because it is system critical",
    ERR_NOT_SUPPORTED: "not supported",
    ERR_USER_GROUPS_MEMBERSHIP: "cannot get list of groups for the domain user",
    ERR_USER_NOT_IN_GROUP: "user is not a member of given group",
    ERR_USER_ATTR_NOT_SUPPORTED: "given user attribute is not supported by this toolkit",
    ERR_GROUP_IS_PRIMARY: "given group is a primary group of the object",
    ERR_GROUP_MEMBERS: "cannot get members of the given group",
    ERR_GROUP_BUILTIN_TYPE_CHANGE: "cannot change type of built-in system group",
    ERR_GROUP_BUILTIN_DELETE: "cannot delete built-in system group",
    ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL: "won't modify because it is system critical",
    ERR_OU_NOT_EMPTY: "given OU is not empty",
    ERR_NOT_DELETING_BECAUSE_SYSCRITICAL_CHILDS: "won't delete because consists of child system critical object(s)",
    ERR_REALM_MISMATCH: "cannot deal with objects from other than currently selected realm",
    ERR_COMPUTER_GROUPS_MEMBERSHIP: "cannot get list of groups for the domain computer",
    ERR_COMPUTER_NOT_IN_GROUP: "computer is not a member of given group",
    ERR_COMPUTER_ATTR_NOT_SUPPORTED: "given computer attribute is not supported by this toolkit",
    ERR_COMPUTER_NAME_SYNTAX: "computer name must consist of 'A-Z', '0-9' and '_' characters only",
    ERR_NONUNIQUE_COMPUTER_NAME: "given computer name is not unique (already exists)"
})

_HELP_ROOT = """
\033[2mMain options:\033[0m
\033[93mselect\033[0m                  Use given domain to manage
\033[93mdomain\033[0m                  Manage domain structure
\033[93musers\033[0m                   Manage domain users
\033[93mgroups\033[0m                  Manage domain groups
\033[93mcomputers\033[0m               Manage domain computers
\033[93mcontacts\033[0m*               Manage domain contacts
\033[93mdns\033[0m*                    Manage DNS records
\033[93mtree\033[0m                    Show domain directory tree
\033[93mls\033[0m                      Show domain directory tree with objects
\033[93mhelp\033[0m                    Display this help
\033[93mversion\033[0m                 Display this toolkit version
\033[93mexit|quit\033[0m               Exit from this CLI
* not implemented yet
"""
HELP_SELECT = """
select  -- for list of available realms to use
select <realm>
* realm - the one of configured via configuration file realms
"""
HELP_DOMAIN = """
\033[2mDomain management options:\033[0m
\033[93mshow\033[0m                    Show this domain details
\033[93mattrs\033[0m                   Show this domain raw LDAP attributes
\033[93mtree\033[0m                    Show domain directory tree
\033[93mls\033[0m                      Show domain directory tree with objects
\033[93mmkou\033[0m                    Make new OU (organizational unit) in the tree
\033[93mrmou\033[0m                    Remove OU (organizational unit) from the tree
\033[93mmvou\033[0m                    Move OU (organizational unit) to the new location
\033[93mrenameou\033[0m                Rename OU (organizational unit)
\033[93msearchou\033[0m                Search for the OU (organizational unit) over domain tree

\033[2m* This toolkit is not designed to manage domain system options such changes
  in FSMO owners or domain level modifications! Please use correct Samba toolkit
  or Management console to accomplish those operations.\033[0m
"""
HELP_USERS = """
\033[2mUser management:\033[0m
\033[93madd\033[0m                     Add new user
\033[93medit\033[0m                    Edit existing user
\033[93mrm\033[0m                      Delete existing user
\033[93mrename\033[0m                  Rename existing user
\033[93mmv\033[0m                      Move existing user to the new path
\033[93mpwd\033[0m                     Show where this user is located at
\033[93mlist\033[0m                    List existing users
\033[93mls\033[0m                      List existing users using directory tree
\033[93mshow\033[0m                    Show existing user's details
\033[93mpasswd\033[0m                  Change user's password
\033[93mlock\033[0m                    Lock user (disable)
\033[93munlock\033[0m                  Unlock user (enable)
\033[93msearch\033[0m                  Search for user by given [username] or [display name]
\033[93mgmemberof\033[0m               List groups which this user belongs to
\033[93mgadd\033[0m                    Add user to the group
\033[93mgremove\033[0m                 Remove user from the group
\033[93mattrs\033[0m                   Display raw LDAP attributes for the user
"""
HELP_GROUPS = """
\033[2mGroup management:\033[0m
\033[93madd\033[0m                     Add new group
\033[93mtype\033[0m                    Show or set existing group type
\033[93mrm\033[0m                      Delete existing group
\033[93mrename\033[0m                  Rename existing group
\033[93mmv\033[0m                      Move existing group to the new path
\033[93mpwd\033[0m                     Show where this group is located at
\033[93mlist\033[0m                    List existing groups
\033[93mls\033[0m                      List existing groups using directory tree
\033[93mshow\033[0m                    Show existing group's details
\033[93msearch\033[0m                  Search for group by given name
\033[93mmembers\033[0m                 List members of the group
\033[93mattrs\033[0m                   Display raw LDAP attributes for the group
"""
HELP_COMPUTERS = """
\033[2mComputers management:\033[0m
\033[93madd\033[0m                     Add new computer to domain
\033[93medit\033[0m                    Edit existing computer
\033[93mrm\033[0m                      Delete existing computer from domain
\033[93mrename\033[0m                  Rename existing computer in domain
\033[93mmv\033[0m                      Move existing computer to the new path
\033[93mpwd\033[0m                     Show where this computer is located at
\033[93mlist\033[0m                    List existing computers
\033[93mls\033[0m                      List existing computers using directory tree
\033[93mshow\033[0m                    Show existing computer's details
\033[93msearch\033[0m                  Search for computer by given name
\033[93mgmemberof\033[0m               List groups which this computer belongs to
\033[93mgadd\033[0m                    Add computer to the group
\033[93mgremove\033[0m                 Remove computer from the group
\033[93mattrs\033[0m                   Display raw LDAP attributes for the computer
"""
HELP_SYNTAX_USERS_EDIT = (
    "users edit <login> name <value>\n"
    "users edit <login> first-name <value>\n"
    "users edit <login> last-name <value>\n"
    "users edit <login> initials <value>\n"
    "users edit <login> disabled yes|no\n"
    "users edit <login> pwd-infinite yes|no\n"
    "users edit <login> smartcard-req yes|no\n"
    "users edit <login> req-pwd-change yes|no\n"
    "users edit <login> primary-group <value>\n"
    "users edit <login> description <value>\n"
    "users edit <login> comments <value>\n"
    "users edit <login> mail <value>\n"
    "users edit <login> phone <value>\n"
    "users edit <login> homepage <value>\n"
    "users edit <login> delivery-address <value>\n"
    "users edit <login> city <value>\n"
    "users edit <login> state <value>\n"
    "users edit <login> post-box <value>\n"
    "users edit <login> postal-code <value>\n"
    "users edit <login> address <value>\n"
    "users edit <login> company <value>\n"
    "users edit <login> department <value>\n"
    "users edit <login> job-title <value>\n"
    "users edit <login> home-dir <value>\n"
    "users edit <login> profile-dir <value>\n"
    "users edit <login> script <value>\n"
)
HELP_SYNTAX_GROUPS_ADD = (
    "groups add <name> [-security|-distribution] [-global|-local|-universal]\n"
    "* by default global security group will be created"
)
HELP_SYNTAX_GROUPS_TYPE = (
    "groups type <name> [-security|-distribution] [-global|-local|-universal]\n"
    "* with no modificators the current group's type will be shown"
)
HELP_SYNTAX_GROUPS_RENAME = (
    "groups rename <name> => <new name>\n"
    "  example:\n"
    "  groups rename My orinal group => My other group name"
)
HELP_SYNTAX_GROUPS_MV = (
    "groups move <name> => <new domain tree location>\n"
    "  example:\n"
    "  groups move My group => /Groups/New groups/My"
)
HELP_SYNTAX_GROUPS_MEMBERS = (
    "groups members <name> [-by-login|-by-name]\n"
    "  \033[2mshows current members of the group\033[0m\n"
    "groups members <name> => +<login> [,+<login>, +<login>]\033[0m\n"
    "groups members <name> => -<login> [,-<login>, -<login>]\033[0m\n"
    "  \033[2madd or remove user(s) to (from) the membership of the group\033[0m\n"
    "  \033[2mexample:\033[0m\n"
    "  \033[2mgroups members My group => +myuser1, +myuser2, -myuser3\033[0m\n"
    "groups members <name> => +<@name> [,+<@name>, +<@name>]\033[0m\n"
    "groups members <name> => -<@name> [,-<@name>, -<@name>]\033[0m\n"
    "  \033[2madd or remove group(s) to (from) the membership of the group\033[0m\n"
    "  \033[2mexample:\033[0m\n"
    "  \033[2mgroups members My group => +@Group1, +@Group2, -@Group3\033[0m\n"
    "  \033[2m* you may combine users and groups membership management\033[0m"
)
HELP_SYNTAX_COMPUTERS_EDIT = (
    "computers edit <name> dns-name <value>\n"
    "computers edit <name> description <value>\n"
    "computers edit <name> primary-group <value>\n"
    "computers edit <name> os-system <value>\n"
    "computers edit <name> os-version <value>\n"
    "computers edit <name> os-servicepack <value>\n"
    "computers edit <name> os-hotfix <value>\n"
)
HELP_SYNTAX = {
    'version': "version",
    'domain show': "domain show",
    'domain attrs': "domain attrs",
    'domain tree': "domain tree",
    'domain ls': "domain ls [/starting/from] [-by-login|-by-name]",
    'domain mkou': "domain mkou /full/path/to/new/ou",
    'domain rmou': "domain rmou /full/path/to/removing/ou [-recursive]",
    'domain mvou': "domain mvou /from/path/ou-name => /path/where/to",
    'domain renameou': "domain renameou /path/to/ou-name => <new ou name>",
    'domain searchou': "domain searchou <what>",
    'users add': "users add <login> <name>",
    'users edit': HELP_SYNTAX_USERS_EDIT,
    'users rm': "users rm <login>",
    'users rename': "users rename <login> <new_login>",
    'users mv': "users mv <login> </new/domain/tree/location>",
    'users pwd': "users pwd <login>",
    'users show': "users show <login> [-detail]",
    'users list': "users list [-by-login|-by-name]",
    'users ls': "users ls [/path/starting/from] [-by-login|-by-name] [-recursive]",
    'users passwd': "users passwd <login>",
    'users search': "users search <part of login or name> [-by-login|-by-name]",
    'users lock': "users lock <login>",
    'users unlock': "users unlock <login>",
    'users gmemberof': "users gmemberof <login>",
    'users gadd': "users gadd <username> <group>",
    'users gremove': "users gremove <username> <group>",
    'users attrs': "users attrs <login>",
    'groups add': HELP_SYNTAX_GROUPS_ADD,
    'groups type': HELP_SYNTAX_GROUPS_TYPE,
    'groups rm': "groups rm <name>",
    'groups rename': HELP_SYNTAX_GROUPS_RENAME,
    'groups mv': HELP_SYNTAX_GROUPS_MV,
    'groups pwd': "groups pwd <name>",
    'groups list': "groups list",
    'groups ls': "groups ls </path/starting/from> [-recursive]",
    'groups show': "groups show <name> [-detail]",
    'groups attrs': "groups attrs <name>",
    'groups members': HELP_SYNTAX_GROUPS_MEMBERS,
    'groups search': "groups search <part of name>",
    'computers add': "computers add <name> [dns-name]",
    'computers edit': HELP_SYNTAX_COMPUTERS_EDIT,
    'computers rm': "computers rm <name>",
    'computers rename': "computers rename <name> <new-name>",
    'computers mv': "computers mv <name> </new/computer/location>",
    'computers pwd': "computers pwd <name>",
    'computers show': "computers show <name>",
    'computers list': "computers list",
    'computers ls': "computers ls [/path/starting/from] [-recursive]",
    'computers search': "computers search <part of name>",
    'computers gmemberof': "computers gmemberof <name>",
    'computers gadd': "computers gadd <name> <group>",
    'computers gremove': "computers gremove <name> <group>",
    'computers attrs': "computers attrs <name>",
    'ls': "ls [/starting/from] [-by-login|-by-name]",
    'tree': "tree",
}
_CLI = {
    'help': {
        '_default': ('cli_help', _HELP_ROOT),
    },
    'version': {
        '_default': ('cli_version', HELP_SYNTAX['version']),
        'help': ('cli_help', HELP_SYNTAX['version']),
    },
    'select': {
        '_noop': True,
        '_default': ('cli_select', HELP_SELECT),
        'help': ('cli_help', HELP_SELECT),
    },
    'domain': {
        'help': ('cli_help', HELP_DOMAIN),
        'show': ('cli_domain_show', HELP_SYNTAX['domain show']),
        'attrs': ('cli_domain_attrs', HELP_SYNTAX['domain attrs']),
        'tree': ('cli_domain_tree', HELP_SYNTAX['domain tree']),
        'ls': ('cli_domain_ls', HELP_SYNTAX['domain ls']),
        'mkou': ('cli_domain_mkou', HELP_SYNTAX['domain mkou']),
        'rmou': ('cli_domain_rmou', HELP_SYNTAX['domain rmou']),
        'mvou': ('cli_domain_mvou', HELP_SYNTAX['domain mvou']),
        'renameou': ('cli_domain_renameou', HELP_SYNTAX['domain renameou']),
        'searchou': ('cli_domain_searchou', HELP_SYNTAX['domain searchou']),
    },
    'users': {
        'help': ('cli_help', HELP_USERS),
        'add': ('cli_users_add', HELP_SYNTAX['users add']),
        'edit': ('cli_users_edit', HELP_SYNTAX['users edit']),
        'rm': ('cli_users_rm', HELP_SYNTAX['users rm']),
        'rename': ('cli_users_rename', HELP_SYNTAX['users rename']),
        'mv': ('cli_users_mv', HELP_SYNTAX['users mv']),
        'pwd': ('cli_users_pwd', HELP_SYNTAX['users pwd']),
        'show': ('cli_users_show', HELP_SYNTAX['users show']),
        'list': ('cli_users_list', HELP_SYNTAX['users list']),
        'ls': ('cli_users_ls', HELP_SYNTAX['users ls']),
        'passwd': ('cli_users_passwd', HELP_SYNTAX['users passwd']),
        'search': ('cli_users_search', HELP_SYNTAX['users search']),
        'lock': ('cli_users_lock', HELP_SYNTAX['users lock']),
        'unlock': ('cli_users_unlock', HELP_SYNTAX['users unlock']),
        'gmemberof': ('cli_users_gmemberof', HELP_SYNTAX['users gmemberof']),
        'gadd': ('cli_users_gadd', HELP_SYNTAX['users gadd']),
        'gremove': ('cli_users_gremove', HELP_SYNTAX['users gremove']),
        'attrs': ('cli_users_attrs', HELP_SYNTAX['users attrs']),
    },
    'groups': {
        'help': ('cli_help', HELP_GROUPS),
        'add': ('cli_groups_add', HELP_SYNTAX['groups add']),
        'type': ('cli_groups_type', HELP_SYNTAX['groups type']),
        'rm': ('cli_groups_rm', HELP_SYNTAX['groups rm']),
        'rename': ('cli_groups_rename', HELP_SYNTAX['groups rename']),
        'mv': ('cli_groups_mv', HELP_SYNTAX['groups mv']),
        'pwd': ('cli_groups_pwd', HELP_SYNTAX['groups pwd']),
        'list': ('cli_groups_list', HELP_SYNTAX['groups list']),
        'ls': ('cli_groups_ls', HELP_SYNTAX['groups ls']),
        'show': ('cli_groups_show', HELP_SYNTAX['groups show']),
        'attrs': ('cli_groups_attrs', HELP_SYNTAX['groups attrs']),
        'members': ('cli_groups_members', HELP_SYNTAX['groups members']),
        'search': ('cli_groups_search', HELP_SYNTAX['groups search']),
    },
    'computers': {
        'help': ('cli_help', HELP_COMPUTERS),
        'add': ('cli_computers_add', HELP_SYNTAX['computers add']),
        'edit': ('cli_computers_edit', HELP_SYNTAX['computers edit']),
        'rm': ('cli_computers_rm', HELP_SYNTAX['computers rm']),
        'rename': ('cli_computers_rename', HELP_SYNTAX['computers rename']),
        'mv': ('cli_computers_mv', HELP_SYNTAX['computers mv']),
        'pwd': ('cli_computers_pwd', HELP_SYNTAX['computers pwd']),
        'show': ('cli_computers_show', HELP_SYNTAX['computers show']),
        'list': ('cli_computers_list', HELP_SYNTAX['computers list']),
        'ls': ('cli_computers_ls', HELP_SYNTAX['computers ls']),
        'search': ('cli_computers_search', HELP_SYNTAX['computers search']),
        'gmemberof': ('cli_computers_gmemberof', HELP_SYNTAX['computers gmemberof']),
        'gadd': ('cli_computers_gadd', HELP_SYNTAX['computers gadd']),
        'gremove': ('cli_computers_gremove', HELP_SYNTAX['computers gremove']),
        'attrs': ('cli_computers_attrs', HELP_SYNTAX['computers attrs']),
    },
    'contacts': {

    },
    'dns': {

    },
    'ls': {
        '_noop': True,
        '_default': ('cli_domain_ls', HELP_SYNTAX['ls']),
    },
    'tree': {
        '_noop': True,
        '_default': ('cli_domain_tree', HELP_SYNTAX['tree']),
    },
}
NOREALM_CMD = ('version', 'help', 'select')


class ActiveDirectorySimpleCli(SimpleCli, ActiveDirectorySimpleManager):
    HELP_ROOT = _HELP_ROOT
    CLI = _CLI

    def __init__(self, **kwargs):
        self._selected = ""
        self._config = {}
        self.config = {}
        self._clidef = {}
        SimpleCli.__init__(self)
        ActiveDirectorySimpleManager.__init__(self, **kwargs)
        self._prompt_template = kwargs.pop('prompt', '\033[1m(\033[92mad-cli\033[97m)\033[0m\033[94m~{{realm}}#\033[0m')
        self.prompt = self._prompt_template.replace('{{realm}}', "")
        self.history = os.path.join(os.path.expanduser('~'), '.adsmt_history')

    def _init_config(self):
        config = {}
        for realm in self.config:
            realm_ = realm.lower()
            config[realm_] = {}
            for k in self.config[realm]:
                k_ = k.lower()
                config[realm_][k_] = self.config[realm][k]
            if 'server' not in config[realm_]:
                del(config[realm_])
            if 'default_user_path' not in config[realm_]:
                config[realm_]['default_user_path'] = 'Users'
            if 'default_group_path' not in config[realm_]:
                config[realm_]['default_group_path'] = 'Users'
            if 'default_computer_path' not in config[realm_]:
                config[realm_]['default_computer_path'] = 'Computers'
        self.config = config

    def _load_config(self, cfgfile=ADSMT_CONF):
        if not os.path.isfile(cfgfile):
            print("\033[1m\033[91mERROR\033[0m: cannot find configuration at '%s'!\n" % cfgfile)
            return False
        print("Loading configuration from %s" % cfgfile)
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        except:
            print("Cannot import Python module 'ConfigParser'!")
            return False
        cfg = ConfigParser()
        cfg.read(cfgfile)
        self.config = {}
        for realm in cfg.sections():
            realm_ = realm.lower()
            c = {}
            for k in cfg.options(realm):
                k_ = k.lower()
                c[k_] = cfg.get(realm, k)
            if 'server' not in c:
                continue
            self.config[realm_] = c
            print("Found realm '%s'" % realm_)
        self._init_config()
        return True

    def _get_credentials(self):
        username = self._input_val("Enter Active Directory username to use: ")
        password = getpass.getpass("Enter corresponding password: ")
        return username, password

    def _select(self, realm, credentials=None):
        realm = realm.lower()
        if realm not in self.config:
            print("\033[1m\033[91mERROR\033[0m: realm '%s' is not defined in the configuration!\n" % realm)
            return False
        _config = self.config[realm]
        self._config = {}
        self._selected = ""
        self.prompt = self._prompt_template.replace('{{realm}}', "")
        if credentials is not None and isinstance(credentials, (list, tuple)) and len(credentials) == 2:
            self.ldap_username, self.ldap_password = credentials
        elif 'username' in _config and 'password' in _config:
            self.ldap_username = _config['username']
            self.ldap_password = _config['password']
        else:
            self.ldap_username, self.ldap_password = self._get_credentials()
        if not self.ldap_username or not self.ldap_password:
            print("\033[1m\033[91mERROR\033[0m: username and password must be given to select the realm!\n")
            return False
        self.ldap_server = _config['server']
        self.ldap_server_port = _config.get('server_port', None)
        self.ldap_realm = realm
        self.ldap_use_ssl = False \
            if str(_config.get('use_ssl', True)).lower() in ('false', 'n', 'no', '0') \
            else True
        msgssl = "secure connection" if self.ldap_use_ssl else "\033[91mnon-secure connection\033[0m"
        sys.stdout.write("Connecting the Active Directory domain controller (%s)... " % msgssl)
        if not self.connect():
            sys.stdout.write("\033[1m\033[91mFAILED\033[0m\n")
            return False
        sys.stdout.write("\033[1m\033[92mOK\033[0m\n")
        sys.stdout.write("Using realm: %s for [%s]\n" % (self._realm, self.ldap_realm))
        sys.stdout.write("Using administrative server: %s\n" % _config['server'])
        sys.stdout.write("\n")
        self._config = _config
        self._selected = realm
        self.prompt = self._prompt_template.replace('{{realm}}', realm)
        return True

    def _print_err(self, errcode=ERR_UNKONWN, errmsg=None, extra_cr=True):
        if errcode in (ERR_FAILED, ERR_UNKONWN) and self.cn.result['description']:
            errmsg = ERR_MSG[errcode]
            errmsg += ": %s" % str(self.cn.result['description'])
        super(ActiveDirectorySimpleCli, self)._print_err(errcode, errmsg, extra_cr)

    @staticmethod
    def _print_total_qty(qty):
        print("\033[95m--- total quantity: %i ---\033[0m" % qty)

    def _validaterq(self, method_name, helpmsg, cmd, op, *args):
        if not self._selected and cmd not in NOREALM_CMD:
            self._print_err(ERR_REALM_NOT_SELECTED)
            return False
        return True

    def start(self, select=None, credentials=None, verbose=True):
        """ The entry point for the AD-SMT CLI """
        if verbose:
            print("%s." % ADSMT_TITLE)
        if select is None:
            if not self._load_config():
                return False
        elif isinstance(select, str):
            if not self._load_config():
                return False
            select = select.lower()
            if select not in self.config:
                print("\033[1m\033[91mERROR\033[0m: realm '%s' is not defined in the configuration file!" % select)
                return False
        elif isinstance(select, dict):
            if 'realm' not in select:
                print("\033[1m\033[91mERROR\033[0m: 'realm' is not defined in the given configuration!")
                return False
            realm = select['realm'].lower()
            self.config = {realm: select}
            self._init_config()
            select = select['realm'].lower()
        if select:
            self._select(select, credentials=credentials)
        elif len(self.config.keys()) == 1:
            self._select(list(self.config.keys())[0], credentials=credentials)
        else:
            print("Use '\033[1mselect <realm>\033[0m' command to select realm to manage.\n")
        super(ActiveDirectorySimpleCli, self).start()
        if verbose:
            print("bye...")

    @staticmethod
    def cli_version(*args):
        """ Prints this toolkit version """
        print("%s.\nVersion: %s\nAuthor: Denis Khodus aka 'Reagent'\nLicense: MIT" % (ADSMT_TITLE, ADSMT_VERSION))

    def cli_help(self, *args):
        """ Prints help for the command """
        if not args or args[0] == 'help':
            print(self.HELP_ROOT)
            return
        cmd = args[0]
        if cmd not in self.CLI:
            print("There is no help page for this command defined\n")
            return
        helpmsg = self.CLI[cmd].get('help', False)
        if not helpmsg:
            print("There is no help page for this command defined\n")
            return
        helpmsg = helpmsg[1]
        if not helpmsg.startswith('\n'):
            helpmsg = "\n" + helpmsg
        print(helpmsg)
        return

    def cli_select(self, *args):
        """ Selects realm to manage """
        params = args[2:]
        # List available to select realms
        if not params:
            print("Realms available for select:")
            for realm in self.config:
                print("  %s" % realm)
            return
        realm = params[0]
        if realm not in self.config:
            return ERR_REALM_UNKNOWN
        if not self._select(realm):
            return ERR_FAILED
        return ERR_OK, 'realm selected'

    def cli_domain_attrs(self, *args):
        """ Prints raw attributes for domain LDAP object """
        if not self.cn.search(
                self._realm,
                '(&(objectclass = domain)(distinguishedName=%s))' % self._realm,
                attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        ) or self.cn.result['result'] != 0 or not self.cn.entries:
            return ERR_LDAPGET_DOMAIN_ENTRY
        print(self.cn.entries[0])

    def cli_domain_show(self, *args):
        """ Prints details for domain """
        # Getting the entry for domain itself
        if not self.cn.search(
                self._realm,
                '(&(objectclass = domain)(distinguishedName=%s))' % self._realm,
                attributes=[DN, 'whenCreated', 'whenChanged', 'minPwdAge', 'maxPwdAge', 'minPwdLength',
                            'pwdHistoryLength', 'pwdProperties', 'name', 'msDS-Behavior-Version']
        ) or self.cn.result['result'] != 0 or not self.cn.entries:
            return ERR_LDAPGET_DOMAIN_ENTRY
        d = self.cn.entries[0]
        _dn = self._dn(d)
        if not _dn:
            return ERR_LDAPGET_DOMAIN_ENTRY
        _when_created = self._e_val(d, 'whenCreated', False)
        _when_changed = self._e_val(d, 'whenChanged', False)
        _min_pwd_age = self._e_val(d, 'minPwdAge', False)
        _max_pwd_age = self._e_val(d, 'maxPwdAge', False)
        _min_pwd_len = self._e_val(d, 'minPwdLength', 0)
        _pwd_history_length = self._e_val(d, 'pwdHistoryLength', 0)
        _pwd_properties = self._e_val(d, 'pwdProperties', 0)
        _name = self._e_val(d, 'name', '?')
        _version = self._e_val(d, 'msDS-Behavior-Version', None)
        if _max_pwd_age == -0x8000000000000000:
            _max_pwd_age = False
        elif _max_pwd_age != 0:
            # converting to the seconds (div by 1000000000)
            _max_pwd_age /= 1000000000
            # converting to the minutes (div by 60)
            _max_pwd_age /= 60
            _max_pwd_age = int(round(_max_pwd_age))
        if _min_pwd_age == -0x8000000000000000:
            _min_pwd_age = False
        elif _min_pwd_age != 0:
            # converting to the seconds (div by 1000000000)
            _min_pwd_age /= 1000000000
            # converting to the minutes (div by 60)
            _min_pwd_age /= 60
            _min_pwd_age = int(round(_min_pwd_age))

        # Getting the list of domain controllers
        dcs = self.get_domain_dcs()
        if dcs is False:
            self._print_err(ERR_LDAPGET_DC_LIST, extra_cr=False)
            dcs = list()
        else:
            dcs = sorted([self._e_val(x, 'name', '') for x in dcs])

        # Getting the list of domain computers
        _comps = self.get_computers_entries(attrs=[DN])
        if _comps is False:
            self._print_err(ERR_LDAPGET_COMPUTERS_LIST, extra_cr=False)
            _qty_comps = False
        else:
            _qty_comps = len(_comps)

        # Getting the list of domain users
        _users = self.get_users_entries(attrs=[DN])
        if _users is False:
            self._print_err(ERR_LDAPGET_USERS_LIST, extra_cr=False)
            _qty_users = False
        else:
            _qty_users = len(_users)

        # Getting the list of domain groups
        _groups = self.get_groups_entries(attrs=[DN])
        if _groups is False:
            self._print_err(ERR_LDAPGET_GROUPS_LIST, extra_cr=False)
            _qty_groups = False
        else:
            _qty_groups = len(_groups)

        # Determining the domain level/version
        domain_version = MS_DOMAIN_VERSION[_version] if _version in MS_DOMAIN_VERSION else 'unknown'

        # Printing results
        print("\n\033[1m%s \033[94m[%s]\033[0m" % (self.ldap_realm, _dn))
        print("{0:<30}\t{1}".format("Domain short name:", _name.upper()))
        print("{0:<30}\t{1}".format("Domain realm (FQDN):", self.ldap_realm))
        print("{0:<30}\t{1}".format("Domain level:", domain_version))
        print("{0:<30}\t{1}".format("Domain controllers:", ", ".join([x for x in dcs if x])))
        if _when_created:
            print("{0:<30}\t{1}".format("Created:", _when_created))
        if _when_changed:
            print("{0:<30}\t{1}".format("Changed:", _when_changed))
        print("")
        print("Password policy:")
        print("{0:<40}\t{1}".format("  Minimum length:", _min_pwd_len if _min_pwd_len else "Off"))
        print("{0:<40}\t{1}".format("  Minimum age (minutes):", _min_pwd_age if _min_pwd_age else "Off"))
        print("{0:<40}\t{1}".format("  Maximum age (minutes):", _max_pwd_age if _max_pwd_age else "Off"))
        print("{0:<40}\t{1}".format("  Remember previous passwords:", _pwd_history_length))
        print("{0:<40}\t{1}".format(
            "  Require complex passwords:",
            "Yes" if _pwd_properties & PWDPROP_DOMAIN_PASSWORD_COMPLEX else "No"))
        print("{0:<40}\t{1}".format(
            "  Require user to be logged in to change:",
            "Yes" if _pwd_properties & PWDPROP_DOMAIN_PASSWORD_NO_ANON_CHANGE else "No"))
        print("{0:<40}\t{1}".format(
            "  Require secure connection to change:",
            "Yes" if _pwd_properties & PWDPROP_DOMAIN_PASSWORD_NO_CLEAR_CHANGE else "No"))
        print("{0:<40}\t{1}".format(
            "  Store all in clear-text (non-hashed):",
            "Yes" if _pwd_properties & PWDPROP_DOMAIN_PASSWORD_STORE_CLEARTEXT else "No"))
        print("")
        print("Domain statistics:")
        print("{0:<40}\t{1}".format("  Computers:", "n/a" if _qty_comps is False else _qty_comps))
        print("{0:<40}\t{1}".format("  Groups:", "n/a" if _qty_groups is False else _qty_groups))
        print("{0:<40}\t{1}".format("  Users:", "n/a" if _qty_users is False else _qty_users))
        print("{0:<40}\t{1}".format("  Contacts:", "not supported yet"))
        print("")
        print("FSMO roles owners:")
        _fsmo_owners = self.get_domain_fsmo_owners()
        for role in _fsmo_owners:
            owner = _fsmo_owners[role]
            if not owner or not isinstance(owner, str):
                ownerdc = "None"
            else:
                owner_ = owner.split(',')
                if owner_[0].lower() == 'cn=ntds settings':
                    owner_ = owner_[1:]
                ownerdc = owner_[0]
                if ownerdc.lower().startswith('cn='):
                    ownerdc = ownerdc[3:]
            print("{0:<40}\t{1}".format("  %s" % role, ownerdc))

    def cli_domain_tree(self, *args):
        """ Prints domain tree structure (OUs, CNs) like file system tree """
        tree = self.get_domain_tree()
        if tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        sys.stdout.write("[\033[1m\033[93m%s\033[0m]\n" % self.ldap_realm)
        for p in sorted(tree.keys()):
            z = p.count('/') + 1
            d = p.split('/')[-1]
            sys.stdout.write(" |" * z)
            sys.stdout.write("-" if z else "")
            sys.stdout.write("\033[1m\033[93m%s\033[0m\n" % d)

    def cli_domain_ls(self, *args):
        """ Prints domain tree structure (OUs, CNs) like file system tree, including
        objects, located in them """
        params = args[2:]
        sort_ = 'by-login'
        recursive_ = False
        if params:
            if self._ifcli(params[-1], '-recursive', 2):
                recursive_ = True
                params = params[:-1]
        if params:
            if self._ifcli(params[-1], '-by-name', 5):
                sort_ = 'by-name'
                params = params[:-1]
            elif self._ifcli(params[-1], '-by-login', 5):
                params = params[:-1]
        start_path = " ".join(params) if params else '/'
        if not start_path.startswith('/'):
            start_path = "/%s" % start_path
        if start_path.endswith('/'):
            start_path = start_path[:-1]
        start_path = start_path[1:]

        tree = self.get_domain_tree()
        if tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        if start_path and start_path not in [x.lower() for x in tree.keys()]:
            return ERR_PATH_NOT_EXISTS

        path = [x.lower() for x in start_path.split('/')][::-1] if start_path else []
        if not path:
            recursive_ = True

        users = self.get_users_entries(attrs=[DN, 'name', 'sAMAccountName'])
        groups = self.get_groups_entries(attrs=[DN, 'name'])
        comps = self.get_computers_entries(attrs=[DN, 'name'])

        users = sorted(
            [x for x in users if self._enumerate_branch_of(self._e_val(x, DN).lower()) == path],
            key=lambda y: self._e_val(y, 'name', '?')
            if sort_ == 'by-name'
            else self._e_val(y, 'sAMAccountName', '?')
        ) if not recursive_ else sorted(
            (([x for x in users if self._enumerate_branch_of(self._e_val(x, DN).lower())[len(path) * -1:] == path])
             if path
             else users),
            key=lambda y: self._e_val(y, 'name', '?')
            if sort_ == 'by-name'
            else self._e_val(y, 'sAMAccountName', '?')
        )
        groups = sorted(
            [x for x in groups
             if self._enumerate_branch_of(self._e_val(x, DN).lower()) == path],
            key=lambda y: self._e_val(y, 'name', '?')
        ) if not recursive_ else sorted(
            (([x for x in groups if self._enumerate_branch_of(self._e_val(x, DN).lower())[len(path) * -1:] == path])
             if path
             else groups),
            key=lambda y: self._e_val(y, 'name', '?')
        )
        comps = sorted(
            [x for x in comps if self._enumerate_branch_of(self._e_val(x, DN).lower()) == path],
            key=lambda y: self._e_val(y, 'name', '?')
        ) if not recursive_ else sorted(
            (([x for x in comps if self._enumerate_branch_of(self._e_val(x, DN).lower())[len(path) * -1:] == path])
             if path
             else comps),
            key=lambda y: self._e_val(y, 'name', '?')
        )
        path_ = "/".join(path[::-1]).lower()
        if path_:
            tree = [x for x in tree.keys()
                    if x.lower() == path_ or (("%s/" % x.lower()).startswith("%s/" % path_) and recursive_)]
        else:
            tree = list(tree.keys())
        dirs = {}
        for u in users:
            dn = self._e_val(u, DN)
            cnou = self._enumerate_branch_of(dn)
            cnou_ = "/".join(cnou[::-1]).lower()
            if cnou_ not in dirs:
                dirs[cnou_] = [[], [], []]
            dirs[cnou_][0].append(u)
        for g in groups:
            dn = self._e_val(g, DN)
            cnou = self._enumerate_branch_of(dn)
            cnou_ = "/".join(cnou[::-1]).lower()
            if cnou_ not in dirs:
                dirs[cnou_] = [[], [], []]
            dirs[cnou_][1].append(g)
        for c in comps:
            dn = self._e_val(c, DN)
            cnou = self._enumerate_branch_of(dn)
            cnou_ = "/".join(cnou[::-1]).lower()
            if cnou_ not in dirs:
                dirs[cnou_] = [[], [], []]
            dirs[cnou_][2].append(c)
        if not path:
            sys.stdout.write("[\033[1m\033[93m%s\033[0m]\n" % self.ldap_realm)
        for p in sorted(tree):
            z = p.count('/') - max(len(path) - 1, 0)
            if not path:
                z += 1
            d = p.split('/')[-1]
            sys.stdout.write("  |" * z)
            sys.stdout.write("-" if z else "")
            sys.stdout.write("\033[1m/\033[93m%s\033[0m\n" % d)
            p_ = p.lower()
            if p_ not in dirs:
                continue
            objs = dirs[p_]
            users_ = objs[0]
            groups_ = objs[1]
            comps_ = objs[2]
            for c in comps_:
                sys.stdout.write("  |" * (z + 1))
                sys.stdout.write("-\033[96m[C]\033[0m ")
                sys.stdout.write("\033[96m%s\033[0m\n" % self._e_val(c, 'name', '?'))
            for g in groups_:
                sys.stdout.write("  |" * (z + 1))
                sys.stdout.write("-\033[1m[G]\033[0m ")
                sys.stdout.write("\033[1m%s\033[0m\n" % self._e_val(g, 'name', '?'))
            for u in users_:
                r_ = (
                    self._e_val(u, 'sAMAccountName', '?'),
                    self._e_val(u, 'name', '?'),
                    int(self._e_val(u, 'userAccountControl', 0)) & UAC_ACCOUNTDISABLE
                )
                sys.stdout.write("  |" * (z + 1))
                sys.stdout.write("-")
                cc = "\033[9m" if r_[2] else ""
                cb = '[U]' if not r_[2] else '\033[91m[X]\033[0m'
                name = r_[1]
                login = r_[0]
                if sort_ == 'by-login':
                    sys.stdout.write("{2} {0}\033[2m  {3}({1})\033[0m\n".format(login, name, cb, cc))
                else:
                    sys.stdout.write("{2} {1}\033[2m  {3}({0})\033[0m\n".format(login, name, cb, cc))

    def cli_domain_renameou(self, *args):
        """ Renames OU in the domain tree structure """
        params = args[2:]
        if not params or (" ".join(params)).count('=>') != 1:
            return ERR_INVALID_SYNTAX
        src, dst = " ".join(params).split('=>')
        if not src.strip() or not dst.strip():
            return ERR_INVALID_SYNTAX
        if '/' in dst.strip():
            return ERR_INVALID_SYNTAX
        ou = self.get_ou_entry(src.strip())
        if ou is False:
            return ERR_NOT_FOUND, "source OU not found"
        is_crifital = self._e_val(ou, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        if not self.rename_ou(ou, dst.strip()):
            return ERR_FAILED
        return ERR_OK, 'renamed'

    def cli_domain_mvou(self, *args):
        """ Moves OU to the new domain tree location """
        params = args[2:]
        if not params or (" ".join(params)).count('=>') != 1:
            return ERR_INVALID_SYNTAX
        src, dst = " ".join(params).split('=>')
        if not src.strip() or not dst.strip():
            return ERR_INVALID_SYNTAX
        if dst.endswith('/'):
            dst = dst[:-1]
        src_ou = self.get_ou_entry(src.strip())
        if src_ou is False:
            return ERR_NOT_FOUND, "source OU not found"
        is_crifital = self._e_val(src, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        dst_ou = self.get_ou_entry(dst.strip())
        if dst_ou is False:
            return ERR_NOT_FOUND, "destination OU not found, it must already exist"
        if not self.move_object(src_ou, self._e_val(dst_ou, DN)):
            return ERR_FAILED
        return ERR_OK, 'moved'

    def cli_domain_mkou(self, *args):
        """ Creates new OU in domain tree structure with given name at given location """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        fqpath = " ".join(params).strip()
        if fqpath.startswith('/'):
            fqpath = fqpath[1:]
        if fqpath.endswith('/'):
            return ERR_INVALID_PARAMETERS, 'no new OU name given in the path'
        path = fqpath.split('/')
        ouname = path[-1]
        oupath = "/".join(path[:-1])
        if oupath:
            tree = self.get_domain_tree(lowercase=True)
            if not tree:
                return ERR_LDAPGET_DOMAIN_TREE
            if oupath.lower() not in tree.keys():
                return ERR_PATH_NOT_EXISTS, 'parent location for new OU does not exists'
        cnou = self._get_branch_from_path(oupath)
        if not self.create_ou(ouname, cnou):
            return ERR_FAILED
        return ERR_OK, 'created'

    def cli_domain_rmou(self, *args):
        """ Removes OU from the domain, deleting objects belongs to it if 'recursive' flag is set """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        recursive = False
        if self._ifcli(params[-1], '-recursive', 2):
            recursive = True
            params = params[:-1]
        fqpath = " ".join(params).strip()
        if fqpath.startswith('/'):
            fqpath = fqpath[1:]
        if fqpath.endswith('/'):
            return ERR_INVALID_PARAMETERS, 'no OU name given in the path'
        dn = self._get_branch_from_path(fqpath)
        ou = self.get_ou_entry(fqpath)
        if ou is False:
            return ERR_NOT_FOUND, 'OU not found'
        is_crifital = self._e_val(ou, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_DELETING_BECAUSE_SYSCRITICAL
        childs = self.get_objects_in_branch(dn, attrs=['isCriticalSystemObject', 'groupType'])
        if childs and not recursive:
            return ERR_OU_NOT_EMPTY
        if childs:
            if not self.test_for_syscritical(*childs):
                return ERR_NOT_DELETING_BECAUSE_SYSCRITICAL_CHILDS
        rq = self._input("\033[1m\033[91mWARNING!\033[0m\033[93m please confirm OU deletion\033[0m [yes/no]:")
        if rq.lower() not in ('y', 'yes'):
            print("cancelled")
            return
        if not self.delete_ou(ou, recursive=recursive):
            return ERR_FAILED
        return ERR_OK, 'removed'

    def cli_domain_searchou(self, *args):
        """ Looks for OUs in domain tree structure """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        what = (" ".join(params)).lower()
        tree = self.get_domain_tree()
        if tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        found = []
        for d in tree:
            d_ = d.split('/')
            if what not in d_[-1].lower():
                continue
            found.append(d)
        if not found:
            print("None found")
            return
        for d in found:
            print("/%s" % d)

    def cli_users_add(self, *args):
        """ Adds new user in interactive mode to the domain """
        params = args[2:]
        if not params or len(params) < 2:
            return ERR_INVALID_SYNTAX
        _login = params[0]
        _name = " ".join(params[1:])
        if bool(self.get_user_entry(_login, attrs=[DN])):
            return ERR_NONUNIQUE_LOGIN
        self._print_err(ERR_OK, 'new user passed test for uniqueness', extra_cr=False)
        password1 = getpass.getpass("Enter new user's password: ")
        if len(password1) < 6:
            return ERR_USER_PASSWORD_TOO_SHORT
        password2 = getpass.getpass("Confirm new user's password: ")
        if password1 != password2:
            return ERR_USER_PASSWORD_CONFIRM
        domain_tree = self.get_domain_tree(lowercase=True)
        if domain_tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        _path = self._input_val("Create at [%s]: " % self._config['default_user_path'])
        if not _path:
            _path = self._config['default_user_path']
        if _path.startswith('/'):
            _path = _path[1:]
        if _path.endswith('/'):
            _path = _path[:-1]
        _path = _path.lower()
        if _path not in domain_tree.keys():
            return ERR_PATH_NOT_EXISTS
        _cnou = domain_tree[_path]

        _first_name = self._input_val("First name []: ").strip()
        _last_name = self._input_val("Last name []: ").strip()
        _initials = self._input_val("Initials []: ").strip()
        _description = self._input_val("Description []: ").strip()
        _mail = self._input_val("E-Mail []: ").strip()
        _phone = self._input_val("Phone []: ").strip()
        _company = self._input_val("Company []: ").strip()
        _department = self._input_val("Department []: ").strip()
        _jobtitle = self._input_val("Job title []: ").strip()
        _delivery_address = self._input_val("Delivery address []: ").strip()
        _comments = self._input_val("Comments []: ").strip()
        _req_pwd_change = self._input_val("Demand user to change his/her password at next log on? [y/N]: ")
        _req_pwd_change = bool(_req_pwd_change.lower() in ('y', 'ye', 'yes'))
        if not _req_pwd_change:
            _is_pwd_infinite = self._input_val("Is password age is infinite? [Y/n]: ")
            _is_pwd_infinite = bool(_is_pwd_infinite.lower() not in ('n', 'no'))
        else:
            _is_pwd_infinite = False
        _do_add = None
        print("")
        while _do_add is None:
            _rq_add = self._input_val("Do add new user? [y/n]: ")
            if _rq_add.lower() in ('y', 'ye', 'yes'):
                _do_add = True
            elif _rq_add.lower() in ('n', 'no'):
                _do_add = False
        if not _do_add:
            print("cancelled")
            return
        print("Creating new Active Directory user...")
        kw = {}
        if _first_name:
            kw['firstname'] = _first_name
        if _last_name:
            kw['lastname'] = _last_name
        if _initials:
            kw['initials'] = _initials
        if _description:
            kw['description'] = _description
        if _mail:
            kw['mail'] = _mail
        if _phone:
            kw['phone'] = _phone
        if _company:
            kw['company'] = _company
        if _department:
            kw['department'] = _department
        if _jobtitle:
            kw['jobtitle'] = _jobtitle
        if _delivery_address:
            kw['delivery_address'] = _delivery_address
        if _comments:
            kw['comments'] = _comments
        kw['req_pwd_change'] = _req_pwd_change
        if not _req_pwd_change and _is_pwd_infinite:
            kw['pwd_infinite'] = True
        if not self.add_user(_login, _name, password1, _cnou, **kw):
            return ERR_FAILED
        return ERR_OK, 'added'

    def cli_users_mv(self, *args):
        """ Moves user to the other domain tree location """
        params = args[2:]
        if len(params) < 2:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        domain_tree = self.get_domain_tree(lowercase=True)
        if domain_tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        p = (" ".join(params[1:])).lower()
        if p.startswith('/'):
            p = p[1:]
        if p not in domain_tree:
            return ERR_PATH_NOT_EXISTS
        cnou = domain_tree[p]
        if not self.move_object(u, cnou):
            return ERR_FAILED
        return ERR_OK, 'moved'

    def cli_users_pwd(self, *args):
        """ Print user's domain tree location """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        _dn = self._e_val(u, DN)
        _dn_cnou = ((_dn[:(len(_dn) - len(self._realm) - 1)].split(','))[1:])[::-1]
        _path = "/".join([x[3:] for x in _dn_cnou])
        print("/%s" % _path)

    def cli_users_list(self, *args):
        """ Print list of users (without any tree structure) """
        params = args[2:]
        if params \
                and not self._ifcli(params[0], '-by-login', 5) \
                and not self._ifcli(params[0], '-by-name', 5):
            return ERR_INVALID_PARAMETERS, "user list sort may be only '-by-login' or '-by-name'"
        sort_ = 'by-login' if not params or self._ifcli(params[0], '-by-login', 5) else 'by-name'
        ul = self.get_users_list(sort_)
        if ul is False or not isinstance(ul, list):
            print("None users found")
            return
        for u in ul:
            cc = "\033[2m" if not u[2] else ""
            cc2 = "\033[2m\033[9m" if not u[2] else ""
            cb = "\033[91m[X]\033[0m" if not u[2] else "[ ]"
            name = u[1]
            login = u[0]
            if sort_ == 'by-login':
                print("{2} {3}{0:<35}\033[0m\t{4}{1}\033[0m".format(login, name, cb, cc, cc2))
            else:
                print("{2} {3}{0:<55}\033[0m\t{4}{1}\033[0m".format(name, login, cb, cc, cc2))
        self._print_total_qty(len(ul))

    def cli_users_ls(self, *args):
        """ Print list of users as domain tree """
        params = args[2:]
        sort_ = 'by-login'
        recursive_ = False
        if params:
            if self._ifcli(params[-1], '-recursive', 2):
                recursive_ = True
                params = params[:-1]
        if params:
            if self._ifcli(params[-1], '-by-name', 5):
                sort_ = 'by-name'
                params = params[:-1]
            elif self._ifcli(params[-1], '-by-login', 5):
                params = params[:-1]
        start_path = " ".join(params) if params else '/'
        if not start_path.startswith('/'):
            start_path = "/%s" % start_path
        if start_path.endswith('/'):
            start_path = start_path[:-1]
        start_path = start_path[1:]
        path = [x.lower() for x in start_path.split('/')][::-1] if start_path else []
        if not path:
            recursive_ = True
        users = self.get_users_entries(attrs=[DN, 'name', 'sAMAccountName', 'userAccountControl'])
        if users is False or not isinstance(users, (list, tuple)) or not users:
            print("None users found")
            return
        users = sorted(
            [x for x in users
             if self._enumerate_branch_of(self._e_val(x, DN).lower()) == path],
            key=lambda y: self._e_val(y, 'name', '?')
            if sort_ == 'by-name'
            else self._e_val(y, 'sAMAccountName', '?')
        ) if not recursive_ else sorted(
            (([x for x in users
               if self._enumerate_branch_of(self._e_val(x, DN).lower())[
                  len(path) * -1:] == path])
             if path
             else users),
            key=lambda y: self._e_val(y, 'name', '?')
            if sort_ == 'by-name'
            else self._e_val(y, 'sAMAccountName', '?')
        )
        if not users:
            print("None users found")
            return
        dirs = {}
        for u in users:
            dn = self._e_val(u, DN)
            cnou = self._enumerate_branch_of(dn)
            cnou_ = "/".join(cnou[::-1])
            if cnou_ not in dirs:
                dirs[cnou_] = []
            dirs[cnou_].append(u)
        for p in sorted(dirs.keys()):
            z = p.count('/') - max(len(path) - 1, 0)
            d = p.split('/')[-1]
            sys.stdout.write("  |" * z)
            sys.stdout.write("-" if z else "")
            sys.stdout.write("\033[1m/\033[93m%s\033[0m\n" % d)
            for u in dirs[p]:
                r_ = (
                    self._e_val(u, 'sAMAccountName', '?'),
                    self._e_val(u, 'name', '?'),
                    int(self._e_val(u, 'userAccountControl', 0)) & UAC_ACCOUNTDISABLE
                )
                sys.stdout.write("  |" * (z + 1))
                sys.stdout.write("--")
                cc = "\033[9m" if r_[2] else ""
                cb = '[ ]' if not r_[2] else '\033[91m[X]\033[0m'
                name = r_[1]
                login = r_[0]
                if sort_ == 'by-login':
                    sys.stdout.write("{2} {0}\033[2m  {3}({1})\033[0m\n".format(login, name, cb, cc))
                else:
                    sys.stdout.write("{2} {1}\033[2m  {3}({0})\033[0m\n".format(login, name, cb, cc))
        self._print_total_qty(len(users))

    def cli_users_search(self, *args):
        """ Search over domain for users with name or login consisting of given pattern """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        sort_ = 'by-login'
        if len(params) > 1:
            if self._ifcli(params[-1], '-by-name', 5):
                sort_ = 'by-name'
                params = params[:-1]
            elif self._ifcli(params[-1], '-by-login', 5):
                params = params[:-1]
        what = str(" ".join(params)).lower()
        all_users = self.get_users_list(sort_)
        if all_users is False or not isinstance(all_users, list):
            print("None users found")
            return
        found_users = list()
        for r_ in all_users:
            login = r_[0].lower()
            name = r_[1].lower()
            if what not in login and what not in name:
                continue
            found_users.append(r_)
        if not found_users:
            print("None users found")
            return
        for r_ in found_users:
            cc = "\033[2m" if not r_[2] else ""
            cc2 = "\033[2m\033[9m" if not r_[2] else ""
            cb = "\033[91m[X]\033[0m" if not r_[2] else "[ ]"
            name = r_[1]
            login = r_[0]
            if sort_ == 'by-login':
                print("{2} {3}{0:<35}\033[0m\t{4}{1}\033[0m".format(login, name, cb, cc, cc2))
            else:
                print("{2} {3}{0:<55}\033[0m\t{4}{1}\033[0m".format(name, login, cb, cc, cc2))
        self._print_total_qty(len(found_users))

    def cli_users_attrs(self, *args):
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        print(u)

    def cli_users_show(self, *args):
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        detailed = False if len(params) < 2 else self._ifcli(params[1], '-detail', 4)
        _dn = self._e_val(u, 'distinguishedName')
        _dn_cnou = ((_dn[:(len(_dn) - len(self._realm) - 1)].split(','))[1:])[::-1]
        _path = "/".join([x[3:] for x in _dn_cnou])
        _displayname = self._e_val(u, 'displayName', '') or self._e_val(u, 'name', '')
        _login = self._e_val(u, 'sAMAccountName', '')
        _first_name = self._e_val(u, 'givenName', '')
        _last_name = self._e_val(u, 'sn', '')
        _initials = self._e_val(u, 'initials', '')
        _pwd_last_set = self._e_val(u, 'pwdLastSet', None)
        _principal_name = self._e_val(u, 'userPrincipalName', '')
        _last_logon = self._e_val(u, 'lastLogon', None)
        _when_created = self._e_val(u, 'whenCreated', None)
        _when_changed = self._e_val(u, 'whenChanged', None)
        _bad_pw_attempts = self._e_val(u, 'badPwdCount', None)
        _sid = self._e_val(u, 'objectSid', '?')
        _guid = self._e_val(u, 'objectGUID', '?')
        _uac = self._e_val(u, 'userAccountControl', UAC_NA)
        _is_disabled = _uac & UAC_ACCOUNTDISABLE
        _is_pwd_infinite = _uac & UAC_DONT_EXPIRE_PASSWORD
        _is_smartcard_req = _uac & UAC_SMARTCARD_REQUIRED
        _description = self._e_val(u, 'description', "")
        _mail = self._e_val(u, 'mail', "")
        _phone = self._e_val(u, 'telephoneNumber', "")
        _phones = self._e_val(u, 'otherTelephone', None)
        _delivery_address = self._e_val(u, 'physicalDeliveryOfficeName', "")
        _homepage = self._e_val(u, 'wWWHomePage', "")
        _homepages = self._e_val(u, 'url', "")
        _city = self._e_val(u, 'l', "")
        _state = self._e_val(u, 'state', "")
        _post = self._e_val(u, 'postOfficeBox', "")
        _postalcode = self._e_val(u, 'postalCode', "")
        _address = self._e_val(u, 'streetAddress', "")
        _company = self._e_val(u, 'company', "")
        _department = self._e_val(u, 'department', "")
        _jobtitle = self._e_val(u, 'title', "")
        _comments = self._e_val(u, 'info', "")
        _homedir = self._e_val(u, 'homeDirectory', "")
        _profiledir = self._e_val(u, 'profilePath', "")
        _scriptpath = self._e_val(u, 'scriptPath', "")

        _pwd_ch_req = _pwd_last_set is False
        if _uac == UAC_NA:
            return ERR_INVALID_LDAP_USER
        print("\n\033[1m%s [%s]\033[0m" % (_displayname, _login))
        if detailed:
            print("\033[2m%s\033[0m" % _dn)
        print("")
        print("{0:<30}\t\033[93m{1}\033[0m".format("Location (path):", "/%s" % _path))
        if detailed:
            print("{0:<30}\t\033[93m{1}\033[0m".format("Parent:", ",".join(_dn_cnou), self._realm))
        print("{0:<30}\t\033[93m{1}\033[0m".format("Login:", _login))
        if detailed:
            print("{0:<30}\t\033[93m{1}\033[0m".format("Principal name:", _principal_name))
        print("{0:<30}\t\033[94m{1}\033[0m".format("Name:", _displayname))
        if detailed or _first_name:
            print("{0:<30}\t\033[94m{1}\033[0m".format("First name:", _first_name))
        if detailed or _last_name:
            print("{0:<30}\t\033[94m{1}\033[0m".format("Last name:", _last_name))
        if detailed or _initials:
            print("{0:<30}\t\033[94m{1}\033[0m".format("Name initials:", _initials))
        if _description:
            print("{0:<30}\t{1}".format("Description:", _description))
        if _mail:
            print("{0:<30}\t{1}".format("E-Mail:", _mail))
        if _phone:
            print("{0:<30}\t{1}".format("Phone:", _phone))
        if detailed and _last_logon:
            print("{0:<30}\t{1}".format("Last logon:", str(_last_logon)))
        if detailed and _when_created:
            print("{0:<30}\t{1}".format("Created:", str(_when_created)))
        if detailed and _when_changed:
            print("{0:<30}\t{1}".format("Changed:", str(_when_changed)))
        if detailed and not _pwd_ch_req and _pwd_last_set:
            print("{0:<30}\t{1}".format("Password changed:", str(_pwd_last_set)))
        elif _pwd_ch_req:
            print("{0:<30}\t\033[91m{1}\033[0m".format("Password:", "Change is required"))
        if detailed and _bad_pw_attempts:
            print("{0:<30}\t{1}".format("Bad password attmpts:", _bad_pw_attempts))
        if detailed or _is_pwd_infinite:
            print("{0:<30}\t{1}".format("Password is infinite:", "Yes" if _is_pwd_infinite else "No"))
        if detailed or _is_smartcard_req:
            print("{0:<30}\t{1}".format("Smart-card is req:", "Yes" if _is_smartcard_req else "No"))
        if detailed:
            print("{0:<30}\t{1}".format("SID:", _sid))
            print("{0:<30}\t{1}".format("GUID:", _guid))
        if detailed or _homedir:
            print("{0:<30}\t{1}".format("Home directory:", _homedir))
        if detailed or _profiledir:
            print("{0:<30}\t{1}".format("Profile directory:", _profiledir))
        if detailed or _scriptpath:
            print("{0:<30}\t{1}".format("Script:", _scriptpath))
        print("{0:<30}\t{1}".format("State:",
                                    "\033[91mDISABLED\033[0m"
                                    if _is_disabled
                                    else "\033[92mENABLED\033[0m"))
        if detailed or _comments:
            print("{0:<30}\t{1}".format("Comments:", _comments))

        if detailed:
            print("")
            print("Other phones:")
            if _phones and isinstance(_phones, (list, tuple)):
                for v in _phones:
                    print("  %s" % str(v))
            else:
                print("  None")
            print("{0:<30}\t{1}".format("Home page:", _homepage))
            print("Other URLs:")
            if _homepages and isinstance(_homepages, (list, tuple)):
                for v in _homepages:
                    print("  %s" % str(v))
            else:
                print("  None")
            print("{0:<30}\t{1}".format("Delivery address:", _delivery_address))
            print("{0:<30}\t{1}".format("City:", _city))
            print("{0:<30}\t{1}".format("State:", _state))
            print("{0:<30}\t{1}".format("Office post box:", _post))
            print("{0:<30}\t{1}".format("Postal code:", _postalcode))
            print("{0:<30}\t{1}".format("Address:", _address))
            print("{0:<30}\t{1}".format("Company:", _company))
            print("{0:<30}\t{1}".format("Department:", _department))
            print("{0:<30}\t{1}".format("Job title:", _jobtitle))

            memberof = self.get_user_memberof(u)
            if isinstance(memberof, (list, tuple)) and len(memberof) > 0:
                print("")
                print("Member of groups:")
                for g in memberof:
                    if g[1]:
                        print("  \033[1m\033[93m[P]\033[97m %s\033[0m" % g[0])
                    else:
                        print("  [ ] %s" % g[0])
                print(" * P = Primary user's group")

    def cli_users_passwd(self, *args):
        """ Change Active Directory user's password (using MSAD extension) """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        password1 = getpass.getpass("Enter new password: ")
        if not password1 or len(password1) < 6:
            return ERR_USER_PASSWORD_TOO_SHORT
        password2 = getpass.getpass("Confirm new password: ")
        if password1 != password2:
            return ERR_USER_PASSWORD_CONFIRM
        if not self.update_user_password(u, password1):
            return ERR_FAILED
        return ERR_OK, 'password changed'

    def cli_users_rm(self, *args):
        """ Deletes the domain user """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN, 'isCriticalSystemObject'])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        is_crifital = self._e_val(u, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_DELETING_BECAUSE_SYSCRITICAL
        rq = self._input_val("\033[1m\033[91mWARNING!\033[0m\033[93m please confirm user deletion\033[0m [yes/no]:")
        if rq.lower() not in ('y', 'yes'):
            print("cancelled")
            return
        if not self.delete_user(u):
            return ERR_FAILED
        return ERR_OK, 'deleted'

    def cli_users_lock(self, *args):
        """ Locks the domain user (disables him/her) """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN, 'userAccountControl'])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        r = self.lock_user(u)
        if r is False:
            return ERR_FAILED
        elif r is None:
            return ERR_OK, 'already locked (disabled)'
        return ERR_OK, 'locked (disabled)'

    def cli_users_unlock(self, *args):
        """ Unlocks the domain user (enables him/her) """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN, 'userAccountControl'])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        r = self.unlock_user(u)
        if r is False:
            return ERR_FAILED
        elif r is None:
            return ERR_OK, 'already unlocked (enabled)'
        return ERR_OK, 'unlocked (enabled)'

    def cli_users_rename(self, *args):
        """ Renames the domain user's login to the another login """
        params = args[2:]
        if not params or len(params) != 2:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        is_crifital = self._e_val(u, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        if bool(self.get_user_entry(params[1], attrs=[DN])):
            return ERR_NONUNIQUE_LOGIN
        if not self.rename_user(u, params[1]):
            return ERR_FAILED
        return ERR_OK, 'renamed'

    def cli_users_edit(self, *args):
        """ Sets the user's attribute """
        params = args[2:]
        if not params or len(params) < 2:
            return ERR_INVALID_SYNTAX
        p = params[1]
        u = self.get_user_entry(params[0])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        r = None
        params = list(params)
        if len(params) < 3:
            params.append("")
        for k in OBJ_ATTR_SIMPLE_PARAMS:
            fk, ifc = OBJ_ATTR_SIMPLE_PARAMS[k]
            if self._ifcli(p, k, ifc):
                v = " ".join(params[2:])
                kw_ = {fk: v}
                r = self.update_user(u, **kw_)
                break
        if r is None:
            if self._ifcli(p, 'name', 2):
                v = " ".join(params[2:])
                r = self.update_user(u, name=v)
            elif self._ifcli(p, 'first-name', 2):
                v = " ".join(params[2:])
                r = self.update_user(u, firstname=v)
            elif self._ifcli(p, 'last-name', 2):
                v = " ".join(params[2:])
                r = self.update_user(u, lastname=v)
            elif self._ifcli(p, 'initials', 2):
                v = " ".join(params[2:])
                r = self.update_user(u, initials=v)
            elif self._ifcli(p, 'disabled', 2):
                v = True if params[2].lower() in ('y', 'yes', 'on', '1', 'true') else False
                if v:
                    r = self.lock_user(u)
                else:
                    r = self.unlock_user(u)
                if r is None:
                    r = True
            elif self._ifcli(p, 'pwd-infinite', 5):
                v = True if params[2].lower() in ('y', 'yes', 'on', '1', 'true') else False
                r = self.update_user(u, pwd_infinite=v)
            elif self._ifcli(p, 'smartcard-req', 3):
                v = True if params[2].lower() in ('y', 'yes', 'on', '1', 'true') else False
                r = self.update_user(u, smartcard_req=v)
            elif self._ifcli(p, 'req-pwd-change', 5):
                v = True if params[2].lower() in ('y', 'yes', 'on', '1', 'true') else False
                r = self.update_user(u, req_pwd_change=v)
            elif self._ifcli(p, 'primary-group', 3):
                v = " ".join(params[2:])
                user_groups = self.get_user_memberof(u, simple=True)
                if not isinstance(user_groups, (list, tuple)):
                    return ERR_USER_GROUPS_MEMBERSHIP
                if v.lower() not in [x.lower() for x in user_groups]:
                    return ERR_USER_NOT_IN_GROUP
                r = self.update_user(u, primary_group=v)
        if r is None:
            return ERR_USER_ATTR_NOT_SUPPORTED
        if r is False:
            return ERR_FAILED
        return ERR_OK, 'set'

    def cli_users_gmemberof(self, *args):
        """ Prints all groups which given user is member of """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN, 'memberOf', 'primaryGroupID', 'objectSid'])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        groups = self.get_user_memberof(u)
        if groups is False or not isinstance(groups, list):
            return ERR_USER_GROUPS_MEMBERSHIP
        for g in groups:
            if g[1]:
                print("\033[1m\033[93m[P]\033[97m %s\033[0m" % g[0])
            else:
                print("[ ] %s" % g[0])
        print("*P = Primary user's group")

    def cli_users_gadd(self, *args):
        """ Adds given domain user to the given domain group """
        params = args[2:]
        if not params or len(params) < 2:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN, 'memberOf', 'primaryGroupID'])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        groups = self.get_user_memberof(u, simple=True)
        if groups is False or not isinstance(groups, list):
            return ERR_USER_GROUPS_MEMBERSHIP
        groupname = " ".join(params[1:])
        if groupname.lower() in [x.lower() for x in groups]:
            return ERR_OK, "is already a member of the given group"
        group = self.get_group_entry(groupname, attrs=[DN, 'member', 'objectSid'])
        if group is False:
            return ERR_NOT_FOUND, 'group not found'
        members = self._e_val(group, 'member', [])
        user_dn = self._e_val(u, DN)
        if user_dn in members:
            return ERR_OK, "is already a member of the given group"
        if not self.group_add_member(group, u):
            return ERR_FAILED
        return ERR_OK, 'member added'

    def cli_users_gremove(self, *args):
        """ Removes given domain user from the given domain group """
        params = args[2:]
        if not params or len(params) < 2:
            return ERR_INVALID_SYNTAX
        u = self.get_user_entry(params[0], attrs=[DN, 'memberOf', 'primaryGroupID'])
        if not u:
            return ERR_NOT_FOUND, 'user not found'
        groups = self.get_user_memberof(u)
        if groups is False or not isinstance(groups, list):
            return ERR_USER_GROUPS_MEMBERSHIP
        groupname = " ".join(params[1:])
        if groupname.lower() not in [str(x[0]).lower() for x in groups]:
            return ERR_USER_NOT_IN_GROUP
        for x in groups:
            if x[0].lower() == groupname.lower() and x[1]:
                return ERR_GROUP_IS_PRIMARY
        group = self.get_group_entry(groupname, attrs=[DN, 'member', 'objectSid'])
        if group is False:
            return ERR_NOT_FOUND, 'group not found'
        members = self._e_val(group, 'member', [])
        user_dn = self._e_val(u, DN)
        if user_dn not in members:
            return ERR_USER_NOT_IN_GROUP
        if not self.group_remove_member(group, u):
            return ERR_FAILED
        return ERR_OK, 'member removed'

    def cli_groups_list(self, *args):
        """ Prints a list of domain groups """
        gl = self.get_groups_list()
        if gl is False or not isinstance(gl, list):
            print("None groups found")
            return
        for g in gl:
            print(g)
        self._print_total_qty(len(gl))

    def cli_groups_show(self, *args):
        """ Prints details about given group """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        detailed = False
        if self._ifcli(params[-1], '-detail', 4):
            detailed = True
            params = params[:-1]
        if not params:
            return ERR_INVALID_SYNTAX
        group = " ".join(params)
        if not group:
            return ERR_INVALID_SYNTAX
        g = self.get_group_entry(group)
        if g is False:
            return ERR_NOT_FOUND, 'group not found'
        _when_created = self._e_val(g, 'whenCreated', False)
        _when_changed = self._e_val(g, 'whenChanged', False)
        _name = self._e_val(g, 'name', '?')
        _description = self._e_val(g, 'description', "")
        _mail = self._e_val(g, 'mail', "")
        _type = self._e_val(g, 'groupType', GRP_SYS)
        _dn = self._e_val(g, DN)
        _dn_cnou = ((_dn[:(len(_dn) - len(self._realm) - 1)].split(','))[1:])[::-1]
        _path = "/".join([x[3:] for x in _dn_cnou])
        _sid = self._e_val(g, 'objectSid', '?')
        _guid = self._e_val(g, 'objectGUID', '?')
        _members = self.get_group_members(g, members_attrs=[DN, 'name', 'sAMAccountName'])
        if _type & GRPTYPE_FLG_SYSTEM:
            _type_txt = "Built-it system"
        else:
            _type_txt = []
            if _type & GRPTYPE_FLG_SECURITY:
                _type_txt.append('Security')
            else:
                _type_txt.append('Distribution')
            if _type & GRPTYPE_FLG_GLOBAL:
                _type_txt.append("(Global)")
            elif _type & GRPTYPE_FLG_LOCAL:
                _type_txt.append("(Local)")
            elif _type & GRPTYPE_FLG_UNIVERSAL:
                _type_txt.append("(Universal)")
            _type_txt = " ".join(_type_txt) if _type_txt else "Unknown (Unsupported)"

        print("\n\033[1m%s\033[0m" % _name)
        if detailed:
            print("\033[2m%s\033[0m" % _dn)
            print("")
        print("{0:<30}\t\033[93m{1}\033[0m".format("Location (path):", "/%s" % _path))
        if detailed:
            print("{0:<30}\t\033[93m{1}\033[0m".format("Parent:", ",".join(_dn_cnou), self._realm))
        print("{0:<30}\t\033[94m{1}\033[0m".format("Name:", _name))
        print("{0:<30}\t\033[95m{1}\033[0m".format("Type:", _type_txt))
        if _description or detailed:
            print("{0:<30}\t{1}".format("Description:", _description))
        if _mail or detailed:
            print("{0:<30}\t{1}".format("E-Mail:", _mail))
        if detailed and _when_created:
            print("{0:<30}\t{1}".format("Created:", str(_when_created)))
        if detailed and _when_changed:
            print("{0:<30}\t{1}".format("Changed:", str(_when_changed)))
        if detailed:
            print("{0:<30}\t{1}".format("SID:", _sid))
            print("{0:<30}\t{1}".format("GUID:", _guid))
        if not detailed:
            if _members is not False:
                _members_qty = len(_members['users']) + len(_members['groups']) + len(_members['computers'])
                print("{0:<30}\t{1}".format("Quantity of members:", _members_qty))
            else:
                print("{0:<30}\t{1}".format("Quantity of members:", 0))
        if detailed:
            print("")
            print("Members of the group:")
            if _members is False:
                print("  None")
            else:
                _mu, _mg, _mc = _members['users'], _members['groups'], _members['computers']
                if not _mu and not _mg and not _mc:
                    print("  None")
                else:
                    _mg = sorted(_mg, key=lambda x: self._e_val(x, 'name').lower())
                    _mu = sorted(_mu, key=lambda x: self._e_val(x, 'sAMAccountName').lower())
                    _mc = sorted(_mc, key=lambda x: self._e_val(x, 'name').lower())
                    for g in _mg:
                        print("  \033[1m[G] %s\033[0m" % self._e_val(g, 'name'))
                    for c in _mc:
                        print("  \033[96m[C] %s\033[0m" % self._e_val(c, 'name'))
                    for u in _mu:
                        print("  [U] %s \033[2m(%s)\033[0m" %
                              (self._e_val(u, 'sAMAccountName'), self._e_val(u, 'name')))
                    print("  \033[2m* G = Group,  U = User,  C = Computer\033[0m")

    def cli_groups_members(self, *args):
        """ Prints a list of members of the group, or modifies members list (add, remove) """
        params = args[2:]
        if not params or (" ".join(params)).count('=>') > 1:
            return ERR_INVALID_SYNTAX
        if '=>' not in " ".join(params):
            # Display members of the group
            sort_ = 'by-login'
            if len(params) > 1:
                if self._ifcli(params[-1], '-by-name', 5):
                    sort_ = 'by-name'
                    params = params[:-1]
                elif self._ifcli(params[-1], '-by-login', 5):
                    params = params[:-1]
            g = self.get_group_entry(" ".join(params), attrs=[DN, 'name', 'member', 'objectSid'])
            if not g:
                return ERR_NOT_FOUND, 'group not found'
            members = self.get_group_members(g)
            if members is False:
                return ERR_GROUP_MEMBERS
            users, groups, comps = members['users'], members['groups'], members['computers']
            if len(users) + len(groups) + len(comps) == 0:
                print("Group has none members")
                return
            for r in sorted(groups, key=lambda x: self._e_val(x, 'name', '')):
                print("\033[1m[G] %s\033[0m" % self._e_val(r, 'name', '?'))
            for r in sorted(comps, key=lambda x: self._e_val(x, 'name', '')):
                print("\033[96m[C] %s\033[0m" % self._e_val(r, 'name', '?'))
            sort_attr = 'name' if sort_ == 'by-name' else 'sAMAccountName'
            for r in sorted(users, key=lambda x: self._e_val(x, sort_attr, '')):
                if sort_ == 'by-login':
                    print("[U] {0:<30}\t{1}".format(
                        self._e_val(r, 'sAMAccountName', '?'), self._e_val(r, 'name', '?')))
                else:
                    print("[U] {1:<50}\t{0}".format(
                        self._e_val(r, 'sAMAccountName', '?'), self._e_val(r, 'name', '?')))
            print("\033[2m* G = Group,  U = User,  C = Computer\033[0m")
        else:
            # Manage members of the group
            groupname, objsline = (" ".join(params)).split('=>')
            g = self.get_group_entry(groupname.strip(), attrs=[DN, 'name', 'member', 'objectSid'])
            if not g:
                return ERR_NOT_FOUND, 'group not found'
            members_to_add = list()
            members_to_remove = list()
            objs = [x.strip() for x in objsline.split(',') if x.strip() != ""]
            for obj in objs:
                mlist = members_to_remove if obj.startswith("-") else members_to_add
                member = obj[1:] if obj[0] in ("-", "+") else obj
                if member.startswith('@'):
                    m = self.get_group_entry(member[1:], attrs=[DN])
                    if m is False:
                        return ERR_NOT_FOUND, 'member group not found: %s' % member[1:]
                    mlist.append(m)
                else:
                    m = self.get_user_entry(member, attrs=[DN])
                    if m is False:
                        return ERR_NOT_FOUND, 'member user not found: %s' % member
                    mlist.append(m)
            if not members_to_add and not members_to_remove:
                print("Noting to do with the group, breaking...")
                return
            if not members_to_add:
                members_to_add = None
            if not members_to_remove:
                members_to_remove = None
            if not self.group_modify_members(g, members_to_add, members_to_remove):
                return ERR_FAILED
            return ERR_OK, 'members modified'

    def cli_groups_ls(self, *args):
        """ Print list of groups formatted as domain tree structure """
        params = args[2:]
        recursive_ = False
        if params:
            if self._ifcli(params[-1], '-recursive', 2):
                recursive_ = True
                params = params[:-1]
        start_path = " ".join(params) if params else '/'
        if not start_path.startswith('/'):
            start_path = "/%s" % start_path
        if start_path.endswith('/'):
            start_path = start_path[:-1]
        start_path = start_path[1:]
        path = [x.lower() for x in start_path.split('/')][::-1] if start_path else []
        if not path:
            recursive_ = True
        groups = self.get_groups_entries(attrs=[DN, 'name'])
        if groups is False or not isinstance(groups, (list, tuple)) or not groups:
            print("None groups found")
            return
        groups = sorted(
            [x for x in groups if self._enumerate_branch_of(self._e_val(x, DN).lower()) == path],
            key=lambda y: self._e_val(y, 'name', '?')
        ) if not recursive_ else sorted(
            (([x for x in groups
               if self._enumerate_branch_of(self._e_val(x, DN).lower())[len(path) * -1:] == path])
             if path
             else groups),
            key=lambda y: self._e_val(y, 'name', '?')
        )
        if not groups:
            print("None groups found")
            return
        dirs = {}
        for g in groups:
            dn = self._e_val(g, DN)
            cnou = self._enumerate_branch_of(dn)
            cnou_ = "/".join(cnou[::-1])
            if cnou_ not in dirs:
                dirs[cnou_] = []
            dirs[cnou_].append(g)
        for p in sorted(dirs.keys()):
            z = p.count('/') - max(len(path) - 1, 0)
            d = p.split('/')[-1]
            sys.stdout.write("  |" * z)
            sys.stdout.write("-" if z else "")
            sys.stdout.write("\033[1m/\033[93m%s\033[0m\n" % d)
            for g in dirs[p]:
                sys.stdout.write("  |" * (z + 1))
                sys.stdout.write("--")
                sys.stdout.write("%s\n" % self._e_val(g, 'name', '?'))
        self._print_total_qty(len(groups))

    def cli_groups_search(self, *args):
        """ Searches for group over entire domain """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        what = str(" ".join(params)).lower()
        all_groups = self.get_groups_list()
        if all_groups is False or not isinstance(all_groups, list):
            print("None groups found")
            return
        found_groups = list()
        for g in all_groups:
            if what not in g.lower():
                continue
            found_groups.append(g)
        if not found_groups:
            print("None groups found")
            return
        for g in found_groups:
            print(g)
        self._print_total_qty(len(found_groups))

    def cli_groups_attrs(self, *args):
        """ Prints raw LDAP entry attributes of the group object """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        g = self.get_group_entry(" ".join(params))
        if not g:
            return ERR_NOT_FOUND, 'group not found'
        print(g)

    def cli_groups_type(self, *args):
        """ Prints the type of the domain group or modifies group's type """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        dt = None
        gt = None
        if self._ifcli(params[-1], '-global', 2):
            dt = GRPTYPE_FLG_GLOBAL
            params = params[:-1]
        elif self._ifcli(params[-1], '-local', 2):
            dt = GRPTYPE_FLG_LOCAL
            params = params[:-1]
        elif self._ifcli(params[-1], '-universal', 2):
            dt = GRPTYPE_FLG_UNIVERSAL
            params = params[:-1]
        if self._ifcli(params[-1], '-security', 2):
            gt = True
            params = params[:-1]
        elif self._ifcli(params[-1], '-distribution', 2):
            gt = False
            params = params[:-1]
        g = self.get_group_entry(" ".join(params), attrs=[DN, 'groupType', 'isCriticalSystemObject'])
        if g is False:
            return ERR_NOT_FOUND, 'group not found'
        is_crifital = self._e_val(g, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        g_cur_type = self._e_val(g, 'groupType', GRP_SEC_GLOBAL)
        if dt is None and gt is None:
            if g_cur_type & GRPTYPE_FLG_SYSTEM:
                grp_txt_type = "built-it system"
            else:
                grp_txt_type = []
                if g_cur_type & GRPTYPE_FLG_SECURITY:
                    grp_txt_type.append('security')
                else:
                    grp_txt_type.append('distribution')
                if g_cur_type & GRPTYPE_FLG_GLOBAL:
                    grp_txt_type.append("(global)")
                elif g_cur_type & GRPTYPE_FLG_LOCAL:
                    grp_txt_type.append("(local)")
                elif g_cur_type & GRPTYPE_FLG_UNIVERSAL:
                    grp_txt_type.append("(universal)")
                grp_txt_type = " ".join(grp_txt_type) if grp_txt_type else "unknown (unsupported)"
            print("Group type is \033[95m%s\033[0m" % grp_txt_type)
            return
        if g_cur_type & GRPTYPE_FLG_SYSTEM:
            return ERR_GROUP_BUILTIN_TYPE_CHANGE
        g_set_type = g_cur_type
        if gt is not None:
            if g_cur_type & GRPTYPE_FLG_SECURITY and gt is False:
                g_set_type &= ~GRPTYPE_FLG_SECURITY
            elif not g_cur_type & GRPTYPE_FLG_SECURITY and gt is True:
                g_set_type |= GRPTYPE_FLG_SECURITY
        if dt is not None:
            g_set_type &= ~GRPTYPE_FLG_GLOBAL
            g_set_type &= ~GRPTYPE_FLG_LOCAL
            g_set_type &= ~GRPTYPE_FLG_UNIVERSAL
            g_set_type |= dt
        if g_set_type == g_cur_type:
            return ERR_OK, "is already a given type"
        if not self.set_group_type(g, g_set_type):
            return ERR_FAILED
        return ERR_OK, 'type set'

    def cli_groups_rm(self, *args):
        """ Deletes domain group """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        g = self.get_group_entry(" ".join(params), attrs=[DN, 'isCriticalSystemObject', 'groupType'])
        if not g:
            return ERR_NOT_FOUND, 'group not found'
        is_crifital = self._e_val(g, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_DELETING_BECAUSE_SYSCRITICAL
        grouptype = self._e_val(g, 'groupType', GRP_SYS)
        if grouptype & GRPTYPE_FLG_SYSTEM:
            return ERR_GROUP_BUILTIN_DELETE
        rq = self._input_val("\033[1m\033[91mWARNING!\033[0m\033[93m please confirm group deletion\033[0m [yes/no]:")
        if rq.lower() not in ('y', 'yes'):
            print("cancelled")
            return
        if not self.delete_group(g):
            return ERR_FAILED
        return ERR_OK, 'deleted'

    def cli_groups_rename(self, *args):
        """ Renames domain group """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        p = " ".join(params)
        if p.count('=>') != 1:
            return ERR_INVALID_SYNTAX
        name1, name2 = p.split('=>')
        if not name1 or not name2:
            return ERR_INVALID_SYNTAX
        g = self.get_group_entry(name1.strip(), attrs=[DN, 'isCriticalSystemObject', 'groupType'])
        if not g:
            return ERR_NOT_FOUND, 'group not found'
        is_crifital = self._e_val(g, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        grouptype = self._e_val(g, 'groupType', GRP_SYS)
        if grouptype & GRPTYPE_FLG_SYSTEM:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        if not self.rename_group(g, name2.strip()):
            return ERR_FAILED
        return ERR_OK, 'renamed'

    def cli_groups_mv(self, *args):
        """ Move domain group to the other domain tree location """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        p = " ".join(params)
        if p.count('=>') != 1:
            return ERR_INVALID_SYNTAX
        name, path = p.split('=>')
        if not name or not path:
            return ERR_INVALID_SYNTAX
        g = self.get_group_entry(name.strip(), attrs=[DN, 'isCriticalSystemObject', 'groupType'])
        if not g:
            return ERR_NOT_FOUND, 'group not found'
        is_crifital = self._e_val(g, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        grouptype = self._e_val(g, 'groupType', GRP_SYS)
        if grouptype & GRPTYPE_FLG_SYSTEM:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        domain_tree = self.get_domain_tree(lowercase=True)
        if domain_tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        path = path.strip().lower()
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        if path not in domain_tree:
            return ERR_PATH_NOT_EXISTS
        cnou = domain_tree[path]
        if not self.move_object(g, cnou):
            return ERR_FAILED
        return ERR_OK, 'moved'

    def cli_groups_pwd(self, *args):
        """ Prints location of the group """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        g = self.get_group_entry(" ".join(params), attrs=[DN])
        if not g:
            return ERR_NOT_FOUND, 'group not found'
        _dn = self._e_val(g, DN)
        _dn_cnou = ((_dn[:(len(_dn) - len(self._realm) - 1)].split(','))[1:])[::-1]
        _path = "/".join([x[3:] for x in _dn_cnou])
        print("/%s" % _path)

    def cli_groups_add(self, *args):
        """ Adds a new group to the domain """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        dt = None
        gt = None
        if self._ifcli(params[-1], '-global', 2):
            dt = GRPTYPE_FLG_GLOBAL
            params = params[:-1]
        elif self._ifcli(params[-1], '-local', 2):
            dt = GRPTYPE_FLG_LOCAL
            params = params[:-1]
        elif self._ifcli(params[-1], '-universal', 2):
            dt = GRPTYPE_FLG_UNIVERSAL
            params = params[:-1]
        if self._ifcli(params[-1], '-security', 2):
            gt = True
            params = params[:-1]
        elif self._ifcli(params[-1], '-distribution', 2):
            gt = False
            params = params[:-1]
        name = " ".join(params)
        g = self.get_group_entry(name, attrs=[DN])
        if g is not False:
            return ERR_NONUNIQUE_CN
        g_set_type = GRP_SEC_GLOBAL
        if gt is not None:
            if g_set_type & GRPTYPE_FLG_SECURITY and gt is False:
                g_set_type &= ~GRPTYPE_FLG_SECURITY
            elif not g_set_type & GRPTYPE_FLG_SECURITY and gt is True:
                g_set_type |= GRPTYPE_FLG_SECURITY
        if dt is not None:
            g_set_type &= ~GRPTYPE_FLG_GLOBAL
            g_set_type &= ~GRPTYPE_FLG_LOCAL
            g_set_type &= ~GRPTYPE_FLG_UNIVERSAL
            g_set_type |= dt
        domain_tree = self.get_domain_tree(lowercase=True)
        if domain_tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        _path = self._input_val("Create at [%s]: " % self._config['default_group_path'])
        if not _path:
            _path = self._config['default_group_path']
        if _path.startswith('/'):
            _path = _path[1:]
        if _path.endswith('/'):
            _path = _path[:-1]
        _path = _path.lower()
        if _path not in domain_tree.keys():
            return ERR_PATH_NOT_EXISTS
        _cnou = domain_tree[_path]
        if not self.add_group(name, g_set_type, _cnou):
            return ERR_FAILED
        return ERR_OK, 'added'

    def cli_computers_add(self, *args):
        """ Adds a new computer to the domain """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        name = params[0].upper()
        fqdn = params[1] if len(params) >= 2 else "%s.%s" % (name.lower(), self.ldap_realm)
        c = self.get_computer_entry(name, attrs=[DN])
        if c is not False:
            return ERR_NONUNIQUE_COMPUTER_NAME
        domain_tree = self.get_domain_tree(lowercase=True)
        if domain_tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        _path = self._input_val("Create at [%s]: " % self._config['default_computer_path'])
        if not _path:
            _path = self._config['default_computer_path']
        if _path.startswith('/'):
            _path = _path[1:]
        if _path.endswith('/'):
            _path = _path[:-1]
        _path = _path.lower()
        if _path not in domain_tree.keys():
            return ERR_PATH_NOT_EXISTS
        _cnou = domain_tree[_path]
        _description = self._input_val("Description []: ").strip()
        _os_system = self._input_val("Operating system type []: ").strip()
        _os_version = self._input_val("Operating system version []: ").strip()
        _os_servicepack = self._input_val("Operating system service pack []: ").strip()
        _os_hotfix = self._input_val("Operating system hotfix []: ").strip()
        kw = {}
        if _description:
            kw['description'] = _description
        if _os_system:
            kw['os_system'] = _os_system
        if _os_version:
            kw['os_version'] = _os_version
        if _os_servicepack:
            kw['os_servicepack'] = _os_servicepack
        if _os_hotfix:
            kw['os_hotfix'] = _os_hotfix
        print("Adding computer \033[1m\033[96m%s\033[0m with dns name \033[96m%s\033[0m" % (name, fqdn))
        if not self.add_computer(name, fqdn, _cnou, **kw):
            return ERR_FAILED
        return ERR_OK, 'added'

    def cli_computers_rm(self, *args):
        """ Deletes the domain computer """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name, attrs=[DN, 'isCriticalSystemObject'])
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        is_crifital = self._e_val(c, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_DELETING_BECAUSE_SYSCRITICAL
        rq = self._input_val("\033[1m\033[91mWARNING!\033[0m\033[93m please confirm computer deletion\033[0m [yes/no]:")
        if rq.lower() not in ('y', 'yes'):
            print("cancelled")
            return
        if not self.delete_computer(c):
            return ERR_FAILED
        return ERR_OK, 'deleted'

    def cli_computers_edit(self, *args):
        """ Sets the computer's attribute """
        params = args[2:]
        if not params or len(params) < 2:
            return ERR_INVALID_SYNTAX
        p = params[1]
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name)
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        r = None
        params = list(params)
        if len(params) < 3:
            params.append("")
        for k in OBJ_ATTR_SIMPLE_PARAMS:
            fk, ifc = OBJ_ATTR_SIMPLE_PARAMS[k]
            if self._ifcli(p, k, ifc):
                v = " ".join(params[2:])
                kw_ = {fk: v}
                r = self.update_computer(c, **kw_)
                break
        if r is None:
            if self._ifcli(p, 'name', 2):
                v = " ".join(params[2:])
                if " " in name:
                    return ERR_COMPUTER_NAME_SYNTAX
                r = self.update_computer(c, name=v)
            elif self._ifcli(p, 'primary-group', 3):
                v = " ".join(params[2:])
                comp_groups = self.get_computer_memberof(c, simple=True)
                if not isinstance(comp_groups, (list, tuple)):
                    return ERR_COMPUTER_GROUPS_MEMBERSHIP
                if v.lower() not in [x.lower() for x in comp_groups]:
                    return ERR_COMPUTER_NOT_IN_GROUP
                r = self.update_computer(c, primary_group=v)
        if r is None:
            return ERR_COMPUTER_ATTR_NOT_SUPPORTED
        if r is False:
            return ERR_FAILED
        return ERR_OK, 'set'

    def cli_computers_rename(self, *args):
        """ Renames the domain computer, changing its net name (and DNS if acceptable) """
        params = args[2:]
        if not params or len(params) != 2:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name)
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        is_crifital = self._e_val(c, 'isCriticalSystemObject', False)
        if is_crifital:
            return ERR_NOT_MODIFYING_BECAUSE_SYSCRITICAL
        if bool(self.get_computer_entry(params[1], attrs=[DN])):
            return ERR_NONUNIQUE_COMPUTER_NAME
        if not self.rename_computer(c, params[1]):
            return ERR_FAILED
        return ERR_OK, 'renamed'

    def cli_computers_mv(self, *args):
        """ Moves computer to the other domain tree location """
        params = args[2:]
        if len(params) < 2:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name)
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        domain_tree = self.get_domain_tree(lowercase=True)
        if domain_tree is False:
            return ERR_LDAPGET_DOMAIN_TREE
        p = (" ".join(params[1:])).lower()
        if p.startswith('/'):
            p = p[1:]
        if p not in domain_tree:
            return ERR_PATH_NOT_EXISTS
        cnou = domain_tree[p]
        if not self.move_object(c, cnou):
            return ERR_FAILED
        return ERR_OK, 'moved'

    def cli_computers_pwd(self, *args):
        """ Print computer's domain tree location """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name, attrs=[DN])
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        _dn = self._e_val(c, DN)
        _dn_cnou = ((_dn[:(len(_dn) - len(self._realm) - 1)].split(','))[1:])[::-1]
        _path = "/".join([x[3:] for x in _dn_cnou])
        print("/%s" % _path)

    def cli_computers_list(self, *args):
        """ Prints a list of domain computers """
        cl = self.get_computers_list()
        if cl is False or not isinstance(cl, list):
            print("None computers found")
            return
        for c in cl:
            print(c)
        self._print_total_qty(len(cl))

    def cli_computers_ls(self, *args):
        """ Print list of computers formatted as domain tree structure """
        params = args[2:]
        recursive_ = False
        if params:
            if self._ifcli(params[-1], '-recursive', 2):
                recursive_ = True
                params = params[:-1]
        start_path = " ".join(params) if params else '/'
        if not start_path.startswith('/'):
            start_path = "/%s" % start_path
        if start_path.endswith('/'):
            start_path = start_path[:-1]
        start_path = start_path[1:]
        path = [x.lower() for x in start_path.split('/')][::-1] if start_path else []
        if not path:
            recursive_ = True
        comps = self.get_computers_entries(attrs=[DN, 'name'])
        if comps is False or not isinstance(comps, (list, tuple)) or not comps:
            print("None computers found")
            return
        comps = sorted(
            [x for x in comps if self._enumerate_branch_of(self._e_val(x, DN).lower()) == path],
            key=lambda y: self._e_val(y, 'name', '?')
        ) if not recursive_ else sorted(
            (([x for x in comps
               if self._enumerate_branch_of(self._e_val(x, DN).lower())[len(path) * -1:] == path])
             if path
             else comps),
            key=lambda y: self._e_val(y, 'name', '?')
        )
        if not comps:
            print("None computers found")
            return
        dirs = {}
        for g in comps:
            dn = self._e_val(g, DN)
            cnou = self._enumerate_branch_of(dn)
            cnou_ = "/".join(cnou[::-1])
            if cnou_ not in dirs:
                dirs[cnou_] = []
            dirs[cnou_].append(g)
        for p in sorted(dirs.keys()):
            z = p.count('/') - max(len(path) - 1, 0)
            d = p.split('/')[-1]
            sys.stdout.write("  |" * z)
            sys.stdout.write("-" if z else "")
            sys.stdout.write("\033[1m/\033[93m%s\033[0m\n" % d)
            for g in dirs[p]:
                sys.stdout.write("  |" * (z + 1))
                sys.stdout.write("--")
                sys.stdout.write("%s\n" % self._e_val(g, 'name', '?'))
        self._print_total_qty(len(comps))

    def cli_computers_show(self, *args):
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name)
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        detailed = False if len(params) < 2 else self._ifcli(params[1], '-detail', 4)
        _dn = self._e_val(c, 'distinguishedName')
        _dn_cnou = ((_dn[:(len(_dn) - len(self._realm) - 1)].split(','))[1:])[::-1]
        _path = "/".join([x[3:] for x in _dn_cnou])
        _name = self._e_val(c, 'name', '')
        _fqdn = self._e_val(c, 'dNSHostName', '')
        _last_logon = self._e_val(c, 'lastLogon', None)
        _when_created = self._e_val(c, 'whenCreated', None)
        _when_changed = self._e_val(c, 'whenChanged', None)
        _sid = self._e_val(c, 'objectSid', '?')
        _guid = self._e_val(c, 'objectGUID', '?')
        _description = self._e_val(c, 'description', "")
        _accountname = self._e_val(c, 'sAMAccountName', "")
        _os_system = self._e_val(c, 'operatingSystem', "")
        _os_version = self._e_val(c, 'operatingSystemVersion', "")
        _os_servicepack = self._e_val(c, 'operatingSystemServicePack', "")
        _os_hotfix = self._e_val(c, 'operatingSystemHotfix', "")
        _os = []
        if _os_system:
            _os.append(_os_system)
            if _os_version:
                _os.append(_os_version)
        _os = "" if not _os else " ".join(_os)
        print("\n\033[1m%s\033[0m" % _name)
        if detailed:
            print("\033[2m%s\033[0m" % _dn)
            print("")
        print("{0:<30}\t\033[93m{1}\033[0m".format("Location (path):", "/%s" % _path))
        if detailed:
            print("{0:<30}\t\033[93m{1}\033[0m".format("Parent:", ",".join(_dn_cnou), self._realm))
        print("{0:<30}\t\033[93m{1}\033[0m".format("Name:", _name))
        print("{0:<30}\t\033[93m{1}\033[0m".format("DNS name:", _fqdn))
        if detailed:
            print("{0:<30}\t{1}".format("Account:", _accountname))
        if _description or detailed:
            print("{0:<30}\t{1}".format("Description:", _description))
        if _os and not detailed:
            print("{0:<30}\t{1}".format("Operating system:", _os))
        if detailed:
            print("{0:<30}\t{1}".format("Operating system type:", _os_system))
            print("{0:<30}\t{1}".format("Operating system version:", _os_version))
        if detailed or _os_servicepack:
            print("{0:<30}\t{1}".format("Operating system service pack:", _os_servicepack))
        if detailed or _os_hotfix:
            print("{0:<30}\t{1}".format("Operating system hotfix:", _os_hotfix))
        if detailed and _last_logon:
            print("{0:<30}\t{1}".format("Last logon:", str(_last_logon)))
        if detailed and _when_created:
            print("{0:<30}\t{1}".format("Created:", str(_when_created)))
        if detailed and _when_changed:
            print("{0:<30}\t{1}".format("Changed:", str(_when_changed)))
        if detailed:
            print("{0:<30}\t{1}".format("SID:", _sid))
            print("{0:<30}\t{1}".format("GUID:", _guid))
            memberof = self.get_computer_memberof(c)
            if isinstance(memberof, (list, tuple)) and len(memberof) > 0:
                print("")
                print("Member of groups:")
                for g in memberof:
                    if g[1]:
                        print("  \033[1m\033[93m[PRI]\033[97m %s\033[0m" % g[0])
                    else:
                        print("  [   ] %s" % g[0])
                print(" * PRI = Primary user's group")

    def cli_computers_search(self, *args):
        """ Searches for computer over entire domain """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        what = str(" ".join(params)).lower()
        all_comps = self.get_computers_list()
        if all_comps is False or not isinstance(all_comps, list):
            print("None computers found")
            return
        found_comps = list()
        for c in all_comps:
            if what not in c.lower():
                continue
            found_comps.append(c)
        if not found_comps:
            print("None computers found")
            return
        for c in found_comps:
            print(c)
        self._print_total_qty(len(found_comps))

    def cli_computers_gmemberof(self, *args):
        """ Prints all groups which given computer is member of """
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name, attrs=[DN, 'memberOf', 'primaryGroupID', 'objectSid'])
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        groups = self.get_computer_memberof(c)
        if groups is False or not isinstance(groups, list):
            return ERR_USER_GROUPS_MEMBERSHIP
        for g in groups:
            if g[1]:
                print("\033[1m\033[93m[P]\033[97m %s\033[0m" % g[0])
            else:
                print("[ ] %s" % g[0])
        print("*P = Primary user's group")

    def cli_computers_gadd(self, *args):
        """ Adds given domain computer to the given domain group """
        params = args[2:]
        if not params or len(params) < 2:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name, attrs=[DN, 'memberOf', 'primaryGroupID'])
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        groups = self.get_computer_memberof(c, simple=True)
        if groups is False or not isinstance(groups, list):
            return ERR_COMPUTER_GROUPS_MEMBERSHIP
        groupname = " ".join(params[1:])
        if groupname.lower() in [x.lower() for x in groups]:
            return ERR_OK, "is already a member of the given group"
        group = self.get_group_entry(groupname, attrs=[DN, 'member', 'objectSid'])
        if group is False:
            return ERR_NOT_FOUND, 'group not found'
        members = self._e_vals(group, 'member', [])
        comp_dn = self._e_val(c, DN)
        if comp_dn in members:
            return ERR_OK, "is already a member of the given group"
        if not self.group_add_member(group, c):
            return ERR_FAILED
        return ERR_OK, 'member added'

    def cli_computers_gremove(self, *args):
        """ Removes given domain computer from the given domain group """
        params = args[2:]
        if not params or len(params) < 2:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name, attrs=[DN, 'memberOf', 'primaryGroupID'])
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        groups = self.get_computer_memberof(c)
        if groups is False or not isinstance(groups, list):
            return ERR_COMPUTER_GROUPS_MEMBERSHIP
        groupname = " ".join(params[1:])
        if groupname.lower() not in [str(x[0]).lower() for x in groups]:
            return ERR_COMPUTER_NOT_IN_GROUP
        for x in groups:
            if x[0].lower() == groupname.lower() and x[1]:
                return ERR_GROUP_IS_PRIMARY
        group = self.get_group_entry(groupname, attrs=[DN, 'member', 'objectSid'])
        if group is False:
            return ERR_NOT_FOUND, 'group not found'
        members = self._e_vals(group, 'member', [])
        comp_dn = self._e_val(c, DN)
        if comp_dn not in members:
            return ERR_COMPUTER_NOT_IN_GROUP
        if not self.group_remove_member(group, c):
            return ERR_FAILED
        return ERR_OK, 'member removed'

    def cli_computers_attrs(self, *args):
        params = args[2:]
        if not params:
            return ERR_INVALID_SYNTAX
        name = params[0]
        if '.' in name:
            name = name.split('.')[0]
            realm = name.split('.')[1:]
            if realm.lower() != self.ldap_realm.lower():
                return ERR_REALM_MISMATCH
        c = self.get_computer_entry(name)
        if not c:
            return ERR_NOT_FOUND, 'computer not found'
        print(c)


def main():
    manager = ActiveDirectorySimpleCli()
    manager.start()


if __name__ == '__main__':
    main()

