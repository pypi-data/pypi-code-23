import ldap3
from ldap3.extend.microsoft.modifyPassword import ad_modify_password
# from ldap3.extend.microsoft.unlockAccount import ad_unlock_account
import ldap3.core.exceptions
import ldap3.abstract.entry
import datetime

# pwdProperties
PWDPROP_DOMAIN_PASSWORD_COMPLEX = 1
PWDPROP_DOMAIN_PASSWORD_NO_ANON_CHANGE = 2
PWDPROP_DOMAIN_PASSWORD_NO_CLEAR_CHANGE = 4
PWDPROP_DOMAIN_LOCKOUT_ADMINS = 8
PWDPROP_DOMAIN_PASSWORD_STORE_CLEARTEXT = 16
PWDPROP_DOMAIN_REFUSE_PASSWORD_CHANGE = 32

# msDS-Behavior-Version
MS_DOMAIN_VERSION = {
    0: 'Windows 2000',
    1: 'Windows 2003 mixed',
    2: 'Windows 2003',
    3: 'Windows 2008',
    4: 'Windows 2008R2',
    5: 'Windows 2012',
    6: 'Windows 2012R2',
    7: 'Windows 2016'
}

# sAMAccountType
SAM_DOMAIN_OBJECT = 0x0
SAM_GROUP_OBJECT = 0x10000000
SAM_NON_SECURITY_GROUP_OBJECT = 0x10000001
SAM_ALIAS_OBJECT = 0x20000000
SAM_NON_SECURITY_ALIAS_OBJECT = 0x20000001
SAM_USER_OBJECT = 0x30000000
SAM_NORMAL_USER_ACCOUNT = 0x30000000
SAM_MACHINE_ACCOUNT = 0x30000001
SAM_TRUST_ACCOUNT = 0x30000002
SAM_APP_BASIC_GROUP = 0x40000000
SAM_APP_QUERY_GROUP = 0x40000001
SAM_ACCOUNT_TYPE_MAX = 0x7fffffff

# userAccountControl flags (bits)
UAC_NA = 0
UAC_SCRIPT = 1
UAC_ACCOUNTDISABLE = 2
UAC_HOMEDIR_REQUIRED = 4
UAC_PASSWD_NOTREQD = 32
UAC_ENCRYPTED_TEXT_PWD_ALLOWED = 128
UAC_TEMP_DUPLICATE_ACCOUNT = 256
UAC_NORMAL_ACCOUNT = 512
UAC_INTERDOMAIN_TRUST_ACCOUNT = 2048
UAC_WORKSTATION_TRUST_ACCOUNT = 4096
UAC_SERVER_TRUST_ACCOUNT = 8192
UAC_DONT_EXPIRE_PASSWORD = 65536
UAC_SMARTCARD_REQUIRED = 262144
UAC_TRUSTED_FOR_DELEGATION = 524288
UAC_NOT_DELEGATED = 1048576
UAC_DONT_REQ_PREAUTH = 4194304

# Distribution groups
GRP_DIST_LOCAL = 4
GRP_DIST_GLOBAL = 2
GRP_DIST_UNIVERSAL = 8
# Security groups
GRP_SEC_LOCAL = -2147483644
GRP_SEC_GLOBAL = -2147483646
GRP_SEC_UNIVERSAL = -2147483640
# System
GRP_SYS = -2147483643
# Group type flags
GRPTYPE_FLG_SYSTEM = 1
GRPTYPE_FLG_GLOBAL = 2
GRPTYPE_FLG_LOCAL = 4
GRPTYPE_FLG_UNIVERSAL = 8
GRPTYPE_FLG_APP_BASIC = 16
GRPTYPE_FLG_APP_QUERY = 32
GRPTYPE_FLG_SECURITY = 2147483648

# Internal constants
LDAP_SIMPLE_ATTR = {
    'firstname': 'givenName',
    'lastname': 'sn',
    'initials': 'initials',
    'description': 'description',
    'mail': 'mail',
    'phone': 'telephoneNumber',
    'delivery_address': 'physicalDeliveryOfficeName',
    'homepage': 'wWWHomePage',
    'city': 'l',
    'state': 'state',
    'post': 'postOfficeBox',
    'postalcode': 'postalCode',
    'address': 'streetAddress',
    'company': 'company',
    'department': 'department',
    'jobtitle': 'title',
    'comments': 'info',
    'homedir': 'homeDirectory',
    'profiledir': 'profilePath',
    'scriptpath': 'scriptPath',
    'fqdn': 'dNSHostName',
    'os_system': 'operatingSystem',
    'os_version': 'operatingSystemVersion',
    'os_servicepack': 'operatingSystemServicePack',
    'os_hotfix': 'operatingSystemHotfix',
}
OBJ_ATTR_SIMPLE_PARAMS = {
    'first-name': ('firstname', 3),
    'last-name': ('lastname', 3),
    'description': ('description', 4),
    'comments': ('comments', 3),
    'mail': ('mail', 2),
    'phone': ('phone', 3),
    'homepage': ('homepage', 5),
    'delivery-address': ('delivery_address', 5),
    'city': ('city', 2),
    'state': ('state', 3),
    'post-box': ('post', 5),
    'postal-code': ('postalcode', 5),
    'address': ('address', 4),
    'company': ('company', 4),
    'department': ('department', 3),
    'job-title': ('jobtitle', 3),
    'home-dir': ('homedir', 5),
    'profile-dir': ('profiledir', 4),
    'script': ('scriptpath', 4),
    'dns-name': ('fqdn', 4),
    'os-system': ('os_system', 5),
    'os-version': ('os_version', 4),
    'os-servicepack': ('os_servicepack', 5),
    'os-hotfix': ('os_hotfix', 4),
}

# Shortcuts
DN = "distinguishedName"


class LdapConnectionWrapper(ldap3.Connection):
    """ This class used to give an opportunity to automatically re-connect to the
    Active Directory domain controller if connection timed out, but administrator
    want to do something. """

    def search(self, *args, **kwargs):
        try:
            r = super(LdapConnectionWrapper, self).search(*args, **kwargs)
        except ldap3.core.exceptions.LDAPSessionTerminatedByServerError:
            super(LdapConnectionWrapper, self).bind()
            r = super(LdapConnectionWrapper, self).search(*args, **kwargs)
        return r

    def modify(self,
               dn,
               changes,
               controls=None):
        try:
            r = super(LdapConnectionWrapper, self).modify(dn, changes, controls=controls)
        except ldap3.core.exceptions.LDAPSessionTerminatedByServerError:
            super(LdapConnectionWrapper, self).bind()
            r = super(LdapConnectionWrapper, self).modify(dn, changes, controls=controls)
        return r

    def modify_dn(self,
                  dn,
                  relative_dn,
                  delete_old_dn=True,
                  new_superior=None,
                  controls=None):
        try:
            r = super(LdapConnectionWrapper, self).modify_dn(dn,
                                                             relative_dn,
                                                             delete_old_dn=delete_old_dn,
                                                             new_superior=new_superior,
                                                             controls=controls)
        except ldap3.core.exceptions.LDAPSessionTerminatedByServerError:
            super(LdapConnectionWrapper, self).bind()
            r = super(LdapConnectionWrapper, self).modify_dn(dn,
                                                             relative_dn,
                                                             delete_old_dn=delete_old_dn,
                                                             new_superior=new_superior,
                                                             controls=controls)
        return r

    def add(self,
            dn,
            object_class=None,
            attributes=None,
            controls=None):
        try:
            r = super(LdapConnectionWrapper, self).add(dn,
                                                       object_class=object_class,
                                                       attributes=attributes,
                                                       controls=controls)
        except ldap3.core.exceptions.LDAPSessionTerminatedByServerError:
            super(LdapConnectionWrapper, self).bind()
            r = super(LdapConnectionWrapper, self).add(dn,
                                                       object_class=object_class,
                                                       attributes=attributes,
                                                       controls=controls)
        return r

    def delete(self,
               dn,
               controls=None):
        try:
            r = super(LdapConnectionWrapper, self).delete(dn, controls=controls)
        except ldap3.core.exceptions.LDAPSessionTerminatedByServerError:
            super(LdapConnectionWrapper, self).bind()
            r = super(LdapConnectionWrapper, self).delete(dn, controls=controls)
        return r


class ActiveDirectorySimpleManager(object):
    """ Base management class used as interface to the LDAP domain directory. Does not
    contains any interactivity code.
    """
    def __init__(self, **kwargs):
        """
        :server                     Host or IP address of the domain controller which will
                                    be used for administration;
        :server_port                TCP port number of the domain controller;
        :realm                      Name of the realm (example: "mydomain.lan");
        :username                   Username of the user which has administrative rights
                                    enought for the domain administration;
        :password                   Corresponding user's password;
        :use_ssl                    'True' (default) to establish secured connection to the
                                    domain controller, using SSL/TSL; 'False' to establish
                                    non-secure connnection (note that Active Directory
                                    controllers ofter does not offers some operations to be
                                    done via non-secure connections);
        """
        self._realm = ""
        self.ldap_server = kwargs.pop('server', None)
        self.ldap_server_port = kwargs.pop('server_port', None)
        self.ldap_realm = kwargs.pop('realm', None)
        self.ldap_username = kwargs.pop('username', None)
        self.ldap_password = kwargs.pop('password', None)
        self.ldap_use_ssl = bool(kwargs.pop('use_ssl', True))
        self.srv = None
        self.cn = None
        self.domain_sid = ""

    @staticmethod
    def _e_has(entry, name):
        try:
            return hasattr(entry, name)
        except ldap3.core.exceptions.LDAPCursorError:
            return False

    def _e_val(self, entry, name, default=None):
        """
        :entry                      The LDAP object entry;
        :name                       The name of the LDAP attribute to get to;
        :default                    Default value which will be returned if no attribute
                                    with given name will be found in the LDAP object;
        :returns                    A value of the ldap3.Entry's attribute if it is
                                    exists in the LDAP object, or given default value
                                    instead (defaults to None).
        """
        if not self._e_has(entry, name):
            return default
        attr = getattr(entry, name)
        if isinstance(attr.value, datetime.datetime):
            return attr.value if attr.raw_values[0] != b'0' else False
        elif isinstance(attr.value, (list, tuple)) or len(attr.values) > 1:
            return attr.values
        return attr.value

    def _e_vals(self, entry, name, default=None):
        """
        :entry                      The LDAP object entry;
        :name                       The name of the LDAP attribute to get to;
        :default                    Default value which will be returned if no attribute
                                    with given name will be found in the LDAP object;
        :returns                    A list of values of the ldap3.Entry's attribute if it is
                                    exists in the LDAP object, or given default value
                                    instead (defaults to None).
        """
        if not self._e_has(entry, name):
            return default
        attr = getattr(entry, name)
        return attr.values

    def _e_name(self, e, default="?"):
        """
        :e                          The LDAP object entry;
        :default                    Default value if cannot get the name of the object;
        :returns                    The name of the LDAP object, or default value if
                                    cannot get the name.
        """
        return self._e_val(e, "displayName") if self._e_has(e, "displayName") else self._e_val(e, "name", default)

    @staticmethod
    def _enumerate_branch_of(dn):
        """
        :dn                         DN of the object;
        :returns                    A list of branch elements, without elements' types.
                                    Example: dn="CN=MyUser,OU=Office1,OU=Personnel,DC=dom,DC=lan"
                                    returns: ['Office1', 'Personnel']
        """
        return [x[3:] for x in dn.split(',')[1:] if (x.lower().startswith('ou=') or x.lower().startswith('cn='))]

    def _get_branch_from_path(self, path):
        """
        :path                       A filesystem-like path for which base to return to;
        :returns                    A string containing LDAP base for the given path;
                                    Example: path="/Personnel/Office1"
                                    returns: "OU=Office1,OU=Personnel,DC=dom,DC=lan"
        """
        if not isinstance(path, str):
            return False
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        if not path:
            return self._realm
        path = path.lower()
        tree = self.get_domain_tree(lowercase=True)
        return False if path not in tree else tree[path]

    def _get_branch(self, s):
        """
        :s                          Source string containing LDAP base of the branch or
                                    its filesystem-like path;
        :returns                    A LDAP base for the given branch if succeed, False
                                    otherwise (for example, if corresponding branch does
                                    not exists in the domain tree).
        """
        if '/' in s:
            return self._get_branch_from_path(s)
        return s

    def _dn(self, e):
        """
        :e                          Source element to decode;
        :returns                    distinguishedName for the given element if succeed,
                                    False otherwise.
        """
        if isinstance(e, str):
            return e
        elif not isinstance(e, ldap3.abstract.entry.Entry):
            return False
        return self._e_val(e, DN, False)

    @staticmethod
    def _is_alike_dn(s):
        """
        :returns                    True if given string alike distinguished name of the,
                                    LDAP object, False otherwise. Not searches for the
                                    object itself so cannot guarantee that the object with
                                    given DN is really exists.
        """
        return ',' in s and '=' in s and 'dc=' in s.lower()

    # -----------------------------------------------------------------------------------------------------------------

    def connect(self):
        """ Connects and binds to the Active Directory domain controller.
        :returns                    True if succeed, False otherwise.
        """
        if not self.ldap_server:
            raise ValueError("ldap_server must be set to the host or IP address of domain controller!")
        if not self.ldap_realm:
            raise ValueError("ldap_realm must be set!")
        if not self.ldap_username or not self.ldap_password:
            raise ValueError("username and password must be set prior to connect the Active Directory!")
        self._realm = ",".join(list(("dc=%s" % x) for x in (self.ldap_realm.split('.'))))
        self.srv = ldap3.Server(
            host=self.ldap_server,
            port=(self.ldap_server_port
                  if self.ldap_server_port
                  else (389 if not self.ldap_use_ssl else 636)),
            use_ssl=bool(self.ldap_use_ssl),
            get_info=ldap3.ALL,
            mode=ldap3.IP_V4_ONLY
        )
        if '\\' in self.ldap_username:
            self.ldap_username = "%s@%s" % (self.ldap_username.split('\\')[1], self.ldap_username.split('\\')[0])
        elif '@' not in self.ldap_username:
            self.ldap_username = "%s@%s" % (self.ldap_username, self.ldap_realm)
        self.cn = LdapConnectionWrapper(
            self.srv,
            user=self.ldap_username,
            password=self.ldap_password,
            authentication=ldap3.SIMPLE,
            raise_exceptions=False,
            auto_bind=ldap3.AUTO_BIND_NONE,
            version=3,
            client_strategy=ldap3.SYNC,
            read_only=False,
            lazy=False
        )
        if not self.cn.bind():
            return False
        self.cn.search(self._realm, '(&(objectclass=domain)(distinguishedName=%s))' % self._realm,
                       attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES])
        if self.cn.result['result'] != 0 or len(self.cn.entries) == 0:
            return False
        self.domain_sid = self._e_val(self.cn.entries[0], 'objectSid', "")
        if not self.domain_sid:
            return False
        return True

    # -----------------------------------------------------------------------------------------------------------------

    def get_object_entry(self, dn, attrs=None):
        """
        :dn                         The DN of the object entry to get;
        :attrs                      A set of LDAP attributes of the object entry to be
                                    returned in the entry; all attributes returns if
                                    not set;
        :returns                    The domain object entry if succeed, False otherwise.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if not self.cn.search(dn, "(distinguishedName=%s)" % dn, attributes=attrs) \
                or self.cn.result['result'] != 0 \
                or len(self.cn.entries) == 0:
            return False
        return self.cn.entries[0]

    def get_objects_in_branch(self, branch, attrs=None):
        """
        :branch                     The existing domain branch (LDAP base path or filesystem-like
                                    path);
        :attrs                      A set of LDAP attributes of the objects entries to be
                                    returned for the each entry; all attributes returns if
                                    not set;
        :returns                    A list of LDAP entries which are located in the given branch.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        branch = self._get_branch(branch)
        if not self.cn.search(branch, '(&(objectClass=*)(!(distinguishedName=%s)))' % branch, attributes=attrs):
            return []
        return list(self.cn.entries)

    def move_object(self, e, branch):
        """ Moves the existing domain object to the new location.
        :e                          The existing domain object entry or it's DN;
        :branch                     The branch where the specified object to move to;
        :returns                    True if succeed, False otherwise.
        """
        dn = self._dn(e)
        if not dn:
            return False
        base = dn.split(',')[0]
        branch = self._get_branch(branch)
        return self.cn.modify_dn(dn, base, new_superior=branch, delete_old_dn=True) and self.cn.result['result'] == 0

    def delete_object(self, e):
        """ Deletes the existing domain object.
        :e                          The existing domain object entry of it's DN;
        :returns                    True if succeed, False otherwise.
        """
        dn = self._dn(e)
        if not dn:
            return False
        return self.cn.delete(dn) and self.cn.result['result'] == 0

    def get_object_memberof(self, e, simple=False):
        """
        :e                          The existing domain object entry or it's DN;
        :simple                     If set to True - only groups' names will be returned,
                                    otherwise (default) for each group a tuple of group
                                    name and flag 'isPrimary' will be returned (bool).
        :returns                    A list of groups names to which this computer belongs to
                                    if succeed, False otherwise.
        """
        if not isinstance(e, ldap3.abstract.entry.Entry):
            e = self.get_object_entry(e)
        if e is False:
            return False
        memberof = []
        if self._e_has(e, 'memberOf'):
            memberof_ = self._e_vals(e, 'memberOf')
            for m in memberof_:
                memberof.append((m.split(',')[0][3:], False))
        primary_group_id = self._e_val(e, 'primaryGroupID', None)
        if primary_group_id:
            pgsid = "%s-%s" % (self.domain_sid, str(primary_group_id))
            r = self.cn.search(self._realm, '(&(objectclass=group)(objectSid=%s))' % pgsid, attributes=[DN, 'name'])
            if not r or self.cn.result['result'] != 0 or len(self.cn.entries) == 0:
                return False
            memberof.append((self._e_val(self.cn.entries[0], 'name', ""), True))
        memberof = sorted(memberof, key=lambda x: x[0])
        return memberof if not simple else [x[0] for x in memberof]

    def test_for_syscritical(self, *args):
        """
        :returns                    False if at least one of given objects is system critical,
                                    True otherwise. Objects must be given as ldap3 resulting entries
                                    enumeration. Objects must be retrieved fully or at least has
                                    attributes 'isCriticalSystemObject' and 'groupType' (last for groups).
        """
        if not args:
            return True
        for child in args:
            if not isinstance(child, ldap3.abstract.entry.Entry):
                raise TypeError("test_for_syscritical() requires a set of ldap3 entries to be given!")
            is_crifital = self._e_val(child, 'isCriticalSystemObject', False)
            if is_crifital:
                return False
            grouptype = self._e_val(child, 'groupType', False)
            if isinstance(grouptype, int) and grouptype & GRPTYPE_FLG_SYSTEM:
                return False
        return True

    # -----------------------------------------------------------------------------------------------------------------

    def get_ou_entry(self, path, attrs=None):
        """
        :path                       String containing the filesystem-like path to the
                                    corresponding OU or it's DN;
        :attrs                      A set of LDAP attributes of the OU entry to be
                                    returned in the entry; all attributes returns if
                                    not set;
        :returns                    The domain OU entry if succeed, False otherwise.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if self._is_alike_dn(path):
            return self.get_object_entry(path, attrs=attrs)
        return self.get_object_entry(self._get_branch_from_path(path), attrs=attrs)

    def rename_ou(self, ou, new_name):
        """ Renames the existing domain OU to the new name. New name must be unique in the
        corresponding LDAP base path.
        :ou                         The existing OU entry, it's DN or FS-like path;
        :new_name                   The new name to rename to;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(ou, str) and not self._is_alike_dn(ou):
            ou = self.get_ou_entry(ou, attrs=[DN])
        if not ou:
            return False
        dn = self._dn(ou)
        if not dn:
            return False
        new_dn = "CN=%s" % new_name
        return self.cn.modify_dn(dn, new_dn)

    def delete_ou(self, ou, recursive=False):
        """ Deletes the existing domain OU.
        :ou                         The existing OU entry, it's DN or FS-like path;
        :recursive                  If set to True and there are objects in the deleting
                                    OU - they will be removed recursively prior to deleting
                                    specified OU; otherwise, if set to False (default) and
                                    tehre are objects in the OU - method will fail.
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(ou, str) and not self._is_alike_dn(ou):
            ou = self.get_ou_entry(ou, attrs=[DN])
        if not ou:
            return False
        if not isinstance(recursive, (bool, list, tuple)):
            raise TypeError("delete_ou() requires 'recursive' to be type of bool, list or tuple!")
        dn = self._dn(ou)
        if not dn:
            return False
        if recursive is not False:
            childs = recursive \
                if isinstance(recursive, (list, tuple)) \
                else self.get_objects_in_branch(dn, attrs=[DN, 'isCriticalSystemObject', 'groupType'])
            if not isinstance(childs, (list, tuple)):
                childs = []
            if childs and not self.test_for_syscritical(*childs):
                return False
            if childs:
                childs_dns = sorted(
                    [self._dn(x) for x in childs],
                    key=lambda y: (len(self._enumerate_branch_of(y)), "/".join(self._enumerate_branch_of(y)[::-1])))
                for child in childs_dns[::-1]:
                    if not self.delete_object(child):
                        return False
        return self.delete_object(ou)

    def create_ou(self, name, branch):
        """ Creates a new OU in the domain tree with given name and at given branch.
        :name                       The name of the new OU;
        :branch                     The branch where the new OU to place to;
        :returns                    True if succeed, False otherwise.
        """
        branch = self._get_branch(branch)
        object_class = ['top', 'organizationalUnit']
        attrs = {}
        dn = "OU=%s,%s" % (name, branch)
        return self.cn.add(dn, object_class, attrs) and self.cn.result['result'] == 0

    # -----------------------------------------------------------------------------------------------------------------

    def get_domain_fsmo_owners(self):
        """
        :returns                    A dict containing a set of FSMO roles and corresponding domain
                                    controllers which own corresponding roles (LDAP owner definition).
        """
        owners = {
            'SchemaMasterRole': None,
            'InfrastructureMasterRole': None,
            'RidAllocationMasterRole': None,
            'PdcEmulationMasterRole': None,
            'DomainNamingMasterRole': None,
            'DomainDnsZonesMasterRole': None,
            'ForestDnsZonesMasterRole': None
        }
        domain_dn = self._realm
        # TODO: temporary using (domain_dn) as (forest_dn): don't know how to get forest dns for now
        forest_dn = domain_dn
        configuration_dn = "CN=Configuration,%s" % domain_dn

        role_dns = {
            'SchemaMasterRole': "CN=Schema,%s" % configuration_dn,
            'InfrastructureMasterRole': "CN=Infrastructure,%s" % domain_dn,
            'RidAllocationMasterRole': "CN=RID Manager$,CN=System,%s" % domain_dn,
            'PdcEmulationMasterRole': domain_dn,
            'DomainNamingMasterRole': "CN=Partitions,%s" % configuration_dn,
            'DomainDnsZonesMasterRole': "CN=Infrastructure,DC=DomainDnsZones,%s" % domain_dn,
            'ForestDnsZonesMasterRole': "CN=Infrastructure,DC=ForestDnsZones,%s" % forest_dn
        }
        for role in role_dns:
            role_dn = role_dns[role]
            if not self.cn.search(role_dn, "(distinguishedName=%s)" % role_dn,  attributes=['fSMORoleOwner', ]) \
                    or self.cn.result['result'] != 0 \
                    or not self.cn.entries:
                continue
            e = self.cn.entries[0]
            owner = self._e_val(e, 'fSMORoleOwner', None)
            if not owner or not isinstance(owner, str):
                continue
            owners[role] = owner
        return owners

    def get_domain_dcs(self):
        """
        :returns                    Returns a list of domain controller entries for the managing
                                    domain; False if failed.
        """
        if not self.cn.search(
                self._realm,
                '(&(objectclass = computer)(userAccountControl:1.2.840.113556.1.4.803:=8192))',
                attributes=[DN, 'name']) \
                or self.cn.result['result'] != 0 \
                or not self.cn.entries:
            return False
        return list(self.cn.entries)

    def get_domain_tree(self, lowercase=False, inc_system=False):
        """
        :lowercase                  If set to True - resulting dict's keys, representing filesystem-
                                    like paths, will be lower-cased;
        :inc_system                 If set to True - system CNs (System, LostAndFound, Program Data...)
                                    will be included in the resulting tree; if not (default) - those
                                    CNs will be skipped;
        :returns                    A dict of domain tree structure items, where keys represents
                                    a filesystem-like path to the corresponding branch, and values
                                    represents corresponding LDAP base for the path;
                                    Example:
                                    {
                                        'Users': "CN=Users,DC=domain,DC=lan",
                                        'Personnel': "OU=Personnel,DC=domain,DC=lan",
                                        'Personnel/Staff': "OU=Staff,OU=Personnel,DC=domain,DC=lan"
                                        ...
                                    }
                                    Returns False if the request failed.
        """
        if not self.cn.search(
                self._realm,
                '(|(objectclass=organizationalUnit)(objectclass=container))',
                attributes=[DN]) or self.cn.result['result'] != 0 or len(self.cn.entries) == 0:
            return False
        tree = {}
        for e in self.cn.entries:
            dn = self._dn(e)
            if dn is False:
                continue
            dn_ = dn[:(len(dn) - len(self._realm) - 1)].split(',')[::-1]
            if not dn_:
                continue
            if dn_[0].lower() in \
                    ('cn=system', 'cn=lostandfound', 'cn=program data', 'cn=tpm devices', 'cn=ntds quotas') \
                    and not inc_system:
                continue
            p = "/".join([x[3:] for x in dn_])
            if lowercase:
                p = p.lower()
            tree[p] = dn
        return tree

    # -----------------------------------------------------------------------------------------------------------------

    def get_groups_entries(self, attrs=None):
        """
        :attrs                      A set of LDAP attributes of the groups' entries to be
                                    returned in the each entry; all attributes returns if
                                    not set;
        :returns                    A list of domain groups' entries.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if not self.cn.search(self._realm, '(objectclass=group)', attributes=attrs) or self.cn.result['result'] != 0:
            return False
        return list(self.cn.entries)

    def get_groups_list(self):
        """
        :returns                    A sorted list of domain groups' names if succeed,
                                    False otherwise.
        """
        groups = self.get_groups_entries()
        return sorted([self._e_name(e) for e in groups], key=lambda x: str(x).lower()) \
            if groups is not False and isinstance(groups, list) \
            else False

    def get_group_entry(self, name, attrs=None):
        """
        :name                       String containing the name of the existing domain
                                    group which to be returned or it's DN;
        :attrs                      A set of LDAP attributes of the group entry to be
                                    returned in the entry; all attributes returns if
                                    not set;
        :returns                    The domain group entry if succeed, False otherwise.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if self._is_alike_dn(name):
            return self.get_object_entry(name, attrs=attrs)
        if not self.cn.search(
                self._realm,
                '(&(objectclass=group)(name=%s))' % name,
                attributes=attrs) or self.cn.result['result'] != 0 or len(self.cn.entries) == 0:
            return False
        return self.cn.entries[0]

    def group_modify_members(self, group, to_add=None, to_remove=None):
        """ Adds and removes specified members to the (from the) group.
        :group                      The existing group entry, it's DN or name;
        :to_add                     A set of members' entries to add to the group; no new
                                    members will be added to the group if this
                                    parameter is ommited;
        :to_remove                  A set of members' entires to remove from the group;
                                    no members will be removed if this parameter
                                    is ommited;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(group, str) and not self._is_alike_dn(group):
            group = self.get_group_entry(group, attrs=[DN])
        if not group:
            return False
        dn = self._dn(group)
        if not dn:
            return False
        members = self.get_group_members(dn, only_dn=True)
        if members is False:
            return False
        if to_add is not None and isinstance(to_add, (list, tuple)):
            for member in to_add:
                member_dn = self._dn(member)
                if not member_dn or member_dn in members:
                    continue
                members.append(member_dn)
        if to_remove is not None and isinstance(to_remove, (list, tuple)):
            for member in to_remove:
                member_dn = self._dn(member)
                if not member_dn or member_dn not in members:
                    continue
                del(members[members.index(member_dn)])
        if not self.cn.modify(dn, {'member': [(ldap3.MODIFY_REPLACE, members)]}) or self.cn.result['result'] != 0:
            return False
        return True

    def group_add_member(self, group, *args):
        """ Adds specified members to the group.
        :group                      The existing group entry, it's DN or name;
        :*args                      A set of members' entries to add to the group;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(group, str) and not self._is_alike_dn(group):
            group = self.get_group_entry(group, attrs=[DN])
        if not group:
            return False
        dn = self._dn(group)
        if not dn:
            return False
        members = self.get_group_members(dn, only_dn=True)
        if members is False:
            return False
        for member in args:
            member_dn = self._dn(member)
            if not member_dn or member_dn in members:
                continue
            members.append(member_dn)
        if not self.cn.modify(dn, {'member': [(ldap3.MODIFY_REPLACE, members)]}) or self.cn.result['result'] != 0:
            return False
        return True

    def group_remove_member(self, group, *args):
        """ Removes specified members from the group.
        :group                      The existing group entry, it's DN or name;
        :*args                      A set of members' entries to remove from the group;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(group, str) and not self._is_alike_dn(group):
            group = self.get_group_entry(group, attrs=[DN])
        if not group:
            return False
        dn = self._dn(group)
        if not dn:
            return False
        members = self.get_group_members(dn, only_dn=True)
        if members is False:
            return False
        for member in args:
            member_dn = self._dn(member)
            if not member_dn or member_dn not in members:
                continue
            del(members[members.index(member_dn)])
        if not self.cn.modify(dn, {'member': [(ldap3.MODIFY_REPLACE, members)]}) or self.cn.result['result'] != 0:
            return False
        return True

    def get_group_members(self, group, only_dn=False, members_attrs=None):
        """ Collects and returns domain objects (user, groups, computers, etc) which belongs
        to the specified group.
        :group                      The existing domain group entry, it's DN or name;
        :only_dn                    If set to True -- only DN of group members will be returned
                                    as a list; otherwise (default) method returns a dict
                                    containing separate lists of entries for every object type;
        :members_attrs              A set of LDAP attributes to retrieve for each group member;
                                    if not set - all attributes will be got;
        :returns                    A list of group members if 'only_dn' is True; a dict of
                                    group members divided into corresponding object types
                                    otherwise.
        """
        if isinstance(group, str) and not self._is_alike_dn(group):
            group = self.get_group_entry(group, attrs=[DN])
        if not group:
            return False
        if not isinstance(group, ldap3.abstract.entry.Entry):
            group = self.get_group_entry(group)
        if members_attrs is None:
            members_attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        if isinstance(members_attrs, (list, tuple)) and DN not in members_attrs:
            members_attrs.append(DN)
        if isinstance(members_attrs, (list, tuple)) and 'objectClass' not in members_attrs:
            members_attrs.append('objectClass')
        sid = self._e_val(group, 'objectSid', None)
        if not sid:
            return False
        members_dn = self._e_val(group, 'member', None)
        if not isinstance(members_dn, list):
            members_dn = [members_dn, ] if members_dn else []
        r_members = []
        r_primembers = []
        if members_dn:
            f = []
            for dn in members_dn:
                f.append("(%s)" % str(dn).split(',')[0])
            f = "(&(|(objectClass=group)(objectClass=computer)" \
                "(&(objectClass=user)(objectCategory=person)))(|%s))" % ("".join(f))
            if not self.cn.search(self._realm, f, attributes=members_attrs):
                return False
            if self.cn.result['result'] != 0:
                return False
            r_members = list(self.cn.entries)
        if str(sid).startswith(self.domain_sid):
            pri_sid = str(sid)[len(self.domain_sid)+1:]
            f = "(&(|(objectClass=computer)(&(objectClass=user)(objectCategory=person)))(primaryGroupID=%s))" % pri_sid
            if not self.cn.search(self._realm, f, attributes=members_attrs):
                return False
            if self.cn.result['result'] != 0:
                return False
            r_primembers = list(self.cn.entries)
        members = r_members + r_primembers
        if only_dn:
            return [self._dn(x) for x in members]
        members_users = []
        members_groups = []
        members_comps = []
        for m in members:
            object_class = self._e_val(m, 'objectClass', [])
            if not isinstance(object_class, (list, tuple)):
                object_class = [object_class, ]
            if 'group' in [str(x).lower() for x in object_class]:
                members_groups.append(m)
            elif 'computer' in [str(x).lower() for x in object_class]:
                members_comps.append(m)
            else:
                members_users.append(m)
        return {
            'users': members_users,
            'groups': members_groups,
            'computers': members_comps
        }

    def set_group_type(self, group, grouptype):
        """ Updates the existing domain group, changing its type (secude|distribution)
        (local|global|universal).
        :group                      The existing domain group entry, it's DN or name;
        :grouptype                  An integer containing corresponding group type;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(group, str) and not self._is_alike_dn(group):
            group = self.get_group_entry(group, attrs=[DN])
        if not group:
            return False
        dn = self._dn(group)
        if not dn:
            return False
        return self.cn.modify(dn, {'groupType': [(ldap3.MODIFY_REPLACE, [grouptype])]})

    def delete_group(self, group):
        """ Deletes the existing domain group.
        :group                      The existing domain group entry, it's DN or name;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(group, str) and not self._is_alike_dn(group):
            group = self.get_group_entry(group, attrs=[DN])
        if not group:
            return False
        return self.delete_object(group)

    def rename_group(self, group, new_name):
        """ Renames the existing domain group.
        :group                      The existing domain group entry, it's DN or name;
        :new_name                   String containing the new name for the group;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(group, str) and not self._is_alike_dn(group):
            group = self.get_group_entry(group, attrs=[DN])
        if not group:
            return False
        dn = self._dn(group)
        if not dn:
            return False
        if not self.cn.modify(dn, {'sAMAccountName': [(ldap3.MODIFY_REPLACE, [new_name])]}):
            return False
        new_dn = "CN=%s" % new_name
        return self.cn.modify_dn(dn, new_dn)

    def add_group(self, name, grouptype, branch='Users'):
        """ Creates a new domain group.
        :name                       A name of the new domain group;
        :grouptype                  An integer containing corresponding group type;
        :branch                     A location where this new group to place to;
        :returns                    True if succeed, False otherwise.
        """
        branch = self._get_branch(branch)
        object_class = ['top', 'group']
        attrs = {
            'sAMAccountName': name,
            'groupType': grouptype
        }
        dn = "cn=%s,%s" % (name, branch)
        return self.cn.add(dn, object_class, attrs) and self.cn.result['result'] == 0

    # -----------------------------------------------------------------------------------------------------------------

    def get_users_entries(self, attrs=None):
        """
        :attrs                      A set of LDAP attributes of the users' entries to be
                                    returned in the each entry; all attributes returns if
                                    not set;
        :returns                    A list of all domain users' entries.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if not self.cn.search(self._realm, '(&(objectCategory=person)(objectClass=user))', attributes=attrs) \
                or self.cn.result['result'] != 0:
            return False
        return list(self.cn.entries)

    def get_users_list(self, sort_by='by-login'):
        """
        :sort_by                    Which attribute to use for sort a list of users:
                                    'by-login' will sort using users' logins (sAMAccountName);
                                    'by-name' will sort using users' human readable names;
        :returns                    A sorted list of all domain users; each record in the list is a
                                    tuple containing user's login, name and 'isEnabled' flag;
                                    for example:
                                    [('login1', 'User 1', True), ('login2', 'User 2', False), ...]
        """
        users = self.get_users_entries(attrs=[DN, 'sAMAccountName', 'displayName', 'name', 'userAccountControl'])
        return sorted(
            list([
                    str(self._e_val(e, 'sAMAccountName', '')),
                    str(self._e_val(e, 'displayName', '') or self._e_val(e, 'name', '')),
                    not(bool(self._e_val(e, 'userAccountControl', UAC_NA) & UAC_ACCOUNTDISABLE))
                 ] for e in users),
            key=lambda x: x[0].lower() if sort_by == 'by-login' else x[1].lower())\
            if users is not False and isinstance(users, list) \
            else False

    def get_user_entry(self, login, attrs=None):
        """
        :login                      String containing the existing domain user login
                                    or it's DN;
        :attrs                      A set of LDAP attributes of the user entry to be
                                    returned in the entry; all attributes returns if
                                    not set;
        :returns                    The user entry if succeed, False otherwise.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if self._is_alike_dn(login):
            return self.get_object_entry(login, attrs=attrs)
        if not self.cn.search(
                self._realm,
                '(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))' % login,
                attributes=attrs) or self.cn.result['result'] != 0 or len(self.cn.entries) == 0:
            return False
        return self.cn.entries[0]

    def get_user_memberof(self, user, simple=False):
        """ Collects and returns a set of groups which this user belongs to.
        :user                       The existing domain user entry, it's DN or login;
        :simple                     If set to True - only groups' names will be returned,
                                    otherwise (default) for each group a tuple of group
                                    name and flag 'isPrimary' will be returned (bool).
        :return:                    A list of groups which this user belogns to. Example
                                    for 'simple=False':
                                    [('Group 1', False), ('Domain users', True), ('Group 2', False)... ]
                                    Example for 'simple=True':
                                    ['Group 1', 'Domain users', 'Group 2', ...]
        """
        if isinstance(user, str) and not self._is_alike_dn(user):
            user = self.get_user_entry(user, attrs=[DN])
        if not user:
            return False
        return self.get_object_memberof(user, simple=simple)

    def delete_user(self, user):
        """ Deletes the existing domain user.
        :user                       The existing domain user entry, it's DN or login;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(user, str) and not self._is_alike_dn(user):
            user = self.get_user_entry(user, attrs=[DN])
        if not user:
            return False
        dn = self._dn(user)
        if not dn:
            return False
        return self.cn.delete(dn)

    def lock_user(self, user):
        """ Unlocks the existing domain user (enables it, allowing to log on using
        corresponding services or computers).
        :user                       The existing domain user entry, it's DN or login;
        :returns                    True if succeed, None if no changes are needed,
                                    False if not succeed.
        """
        if isinstance(user, str) and not self._is_alike_dn(user):
            user = self.get_user_entry(user, attrs=[DN])
        if not user:
            return False
        dn = self._dn(user)
        if not dn:
            return False
        uac = self._e_val(user, 'userAccountControl', UAC_NA)
        if uac == UAC_NA or not uac & UAC_NORMAL_ACCOUNT:
            return False
        if uac & UAC_ACCOUNTDISABLE:
            return None
        uac = uac | UAC_ACCOUNTDISABLE
        changes = {'userAccountControl': [(ldap3.MODIFY_REPLACE, [uac])]}
        return self.cn.modify(dn, changes)

    def unlock_user(self, user):
        """ Locks the existing domain user (disables it, disallowing to log on using
        any kind of service or computer).
        :user                       The existing domain user entry, it's DN or login;
        :returns                    True if succeed, None if no changes are needed,
                                    False if not succeed.
        """
        if isinstance(user, str) and not self._is_alike_dn(user):
            user = self.get_user_entry(user, attrs=[DN])
        if not user:
            return False
        dn = self._dn(user)
        if not dn:
            return False
        uac = self._e_val(user, 'userAccountControl', UAC_NA)
        if uac == UAC_NA or not uac & UAC_NORMAL_ACCOUNT:
            return False
        if not uac & UAC_ACCOUNTDISABLE:
            return None
        uac = uac - UAC_ACCOUNTDISABLE
        changes = {'userAccountControl': [(ldap3.MODIFY_REPLACE, [uac])]}
        return self.cn.modify(dn, changes)

    def add_user(self, login, name, password, branch='Users', **kwargs):
        """ Adds new domain user.
        :login                      String containing a new user's login (sAMAccountName);
        :name                       String containing a new user's human readable name;
        :password                   String containing a new user's password;
        :branch                     Location where new user place to;
        :kwargs                     A set of attributes to set for the new user (see
                                    'update_user' method);
        :returns                    True if succeed, False otherwise.
        """
        branch = self._get_branch(branch)
        object_class = ['top', 'person', 'organizationalPerson', 'user']
        attrs = {
            'displayName': name,
            'sAMAccountName': login,
            'userPrincipalName': "%s@%s" % (login, self.ldap_realm)
        }
        for k in kwargs:
            if k not in LDAP_SIMPLE_ATTR:
                continue
            ldap_k = LDAP_SIMPLE_ATTR[k]
            ldap_v = kwargs[k]
            if not ldap_v:
                continue
            attrs[ldap_k] = str(kwargs[k])
        dn = "cn=%s,%s" % (name, branch)
        if not self.cn.add(dn, object_class, attrs) or self.cn.result['result'] != 0:
            return False
        if not ad_modify_password(self.cn, dn, password, None):
            return False
        changes = {}
        uac = UAC_NORMAL_ACCOUNT
        if 'req_pwd_change' in kwargs and bool(kwargs['req_pwd_change']):
            changes['pwdLastSet'] = [(ldap3.MODIFY_REPLACE, [0])]
        elif 'pwd_infinite' in kwargs and bool(kwargs['pwd_infinite']):
            uac = uac | UAC_DONT_EXPIRE_PASSWORD
        changes['userAccountControl'] = [(ldap3.MODIFY_REPLACE, [uac])]
        if not self.cn.modify(dn, changes) or self.cn.result['result'] != 0:
            return False
        # if not ad_unlock_account(self.cn, dn):
        #     return False
        return True

    def update_user(self, user, **kwargs):
        """ Updates the existing domain user. A set of available **kwargs options (and
        corresponding LDAP attributes) are:
            name:                   ldap: name & displayName
            login:                  ldap: sAMAccountName & userPrincipalName
            firstname:              ldap: givenName
            lastname:               ldap: sn
            initials:               ldap: initial
            pwd_infinite:           ldap-flag: userAccountControl
            smartcard_req:          ldap-flag: userAccountControl
            req_pwd_change:         ldap: pwdLastSet -> b'0' / b'-1'
            primary_group:          ldap: primaryGroupID (resolving group name to short SID)
            description:            ldap: description
            mail:                   ldap: mail
            phone:                  ldap: telephoneNumber
            delivery_address:       ldap: physicalDeliveryOfficeName
            homepage:               ldap: wWWHomePage
            city:                   ldap: l
            state:                  ldap: state
            post:                   ldap: postOfficeBox
            postalcode:             ldap: postalCode
            address:                ldap: streetAddress
            company:                ldap: company
            department:             ldap: department
            jobtitle:               ldap: title
            comments:               ldap: info
            homedir:                ldap: homeDirectory
            profiledir:             ldap: profilePath
            scriptpath:             ldap: scriptPath
        :user                       The existing domain user entry, it's DN or login;
        :kwargs                     Corresponding attributes to be modified;
        :returns                    True if succeed, False otherwise;
        """
        if isinstance(user, str) and not self._is_alike_dn(user):
            user = self.get_user_entry(user, attrs=[DN])
        if not user:
            return False
        dn = self._dn(user)
        if not dn:
            return False
        uac = self._e_val(user, 'userAccountControl', UAC_NA)
        if uac == UAC_NA or not uac & UAC_NORMAL_ACCOUNT:
            return False
        changes = {}
        uac_changed = False
        for k in kwargs:
            if k not in LDAP_SIMPLE_ATTR:
                continue
            ldap_k = LDAP_SIMPLE_ATTR[k]
            ldap_v = kwargs[k]
            if not ldap_v:
                changes[ldap_k] = [(ldap3.MODIFY_DELETE, [])]
            else:
                changes[ldap_k] = [(ldap3.MODIFY_REPLACE, [str(kwargs[k])])]
        if 'req_pwd_change' in kwargs:
            value = bool(kwargs['req_pwd_change'])
            if value:
                kwargs['pwd_infinite'] = False
        if 'name' in kwargs:
            changes['displayName'] = [(ldap3.MODIFY_REPLACE, [str(kwargs['name'])])]
        if 'login' in kwargs:
            changes['sAMAccountName'] = [(ldap3.MODIFY_REPLACE, [str(kwargs['login'])])]
            pn = self._e_val(user, 'userPrincipalName', "")
            if pn and isinstance(pn, str):
                pn_ = pn.split('@')
                if len(pn_) == 2:
                    pn_un, pn_realm = pn_
                    new_pn = "%s@%s" % (str(kwargs['login']), pn_realm)
                    changes['userPrincipalName'] = [(ldap3.MODIFY_REPLACE, [new_pn])]
        if 'pwd_infinite' in kwargs:
            value = bool(kwargs['pwd_infinite'])
            if value and not uac & UAC_DONT_EXPIRE_PASSWORD:
                uac_changed = True
                uac = uac | UAC_DONT_EXPIRE_PASSWORD
            elif not value and uac & UAC_DONT_EXPIRE_PASSWORD:
                uac_changed = True
                uac = uac - UAC_DONT_EXPIRE_PASSWORD
        if 'smartcard_req' in kwargs:
            value = bool(kwargs['smartcard_req'])
            if value and not uac & UAC_SMARTCARD_REQUIRED:
                uac_changed = True
                uac = uac | UAC_SMARTCARD_REQUIRED
            elif not value and uac & UAC_SMARTCARD_REQUIRED:
                uac_changed = True
                uac = uac - UAC_SMARTCARD_REQUIRED
        if 'req_pwd_change' in kwargs:
            value = bool(kwargs['req_pwd_change'])
            pwd_last_set = self._e_val(user, 'pwdLastSet', None)
            if value and pwd_last_set is not False:
                changes['pwdLastSet'] = [(ldap3.MODIFY_REPLACE, [0])]
            elif not value and pwd_last_set is False:
                changes['pwdLastSet'] = [(ldap3.MODIFY_REPLACE, [-1])]
        if 'primary_group' in kwargs:
            group = self.get_group_entry(kwargs['primary_group'])
            if group is False:
                return False
            group_sid = self._e_val(group, 'objectSid', None)
            if not group_sid:
                return False
            if not str(group_sid).startswith(self.domain_sid):
                return False
            pgid = group_sid[len(self.domain_sid)+1:]
            changes['primaryGroupID'] = [(ldap3.MODIFY_REPLACE, [pgid])]

        if uac_changed:
            changes['userAccountControl'] = [(ldap3.MODIFY_REPLACE, [uac])]
        if not changes:
            return True
        r = self.cn.modify(dn, changes)
        if 'name' in kwargs and r:
            new_dn = "CN=%s" % kwargs['name']
            r = self.cn.modify_dn(dn, new_dn)
        return r

    def rename_user(self, user, new_login):
        """ Renames the existing domain user -- changes his/her login (sAMAccountName)
        to the new value.
        :user                       The existing domain user entry, it's DN or login;
        :new_login                  String containing new login for that user;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(user, str) and not self._is_alike_dn(user):
            user = self.get_user_entry(user, attrs=[DN])
        if not user:
            return False
        return self.update_user(user, login=new_login)

    def update_user_password(self, user, new_password):
        """
        :user                       The existing domain user entry, it's DN or login;
        :new_password               String containing new user's password;
        :returns                    True if succeed, False otherwise.
        """
        if isinstance(user, str) and not self._is_alike_dn(user):
            user = self.get_user_entry(user, attrs=[DN])
        dn = self._dn(user)
        if not dn:
            return False
        return ad_modify_password(self.cn, dn, new_password, None)

    # -----------------------------------------------------------------------------------------------------------------

    def get_computers_entries(self, attrs=None):
        """
        :attrs                      A set of LDAP attributes of the computers' entries to be
                                    returned in the each entry; all attributes returns if
                                    not set;
        :returns                    A list of all computers entries of the domain if
                                    succeed, False otherwise.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if not self.cn.search(self._realm, '(objectclass=computer)', attributes=attrs) \
                or self.cn.result['result'] != 0:
            return False
        return list(self.cn.entries)

    def get_computers_list(self):
        """
        :returns                    A sorted list of computer names defined in the domain if
                                    succeed, False otherwise. Example:
                                    ['ADC1', 'ADC2', 'HOST1', 'HOST2', 'PC1', ...]
        """
        entries = self.get_computers_entries(attrs=[DN, 'name'])
        return sorted([self._e_name(e) for e in entries], key=lambda x: str(x).lower()) \
            if entries is not False and isinstance(entries, list) \
            else False

    def get_computer_entry(self, name, attrs=None):
        """
        :name                       The name of the computer which about to be got or it's DN;
        :attrs                      A set of LDAP attributes of the computer entry to be
                                    returned in the entry; all attributes returns if
                                    not set;
        :returns                    The computer entry if succeed, False otherwise.
        """
        if attrs is None:
            attrs = [ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES]
        elif isinstance(attrs, (list, tuple)) and DN not in attrs:
            attrs.append(DN)
        if self._is_alike_dn(name):
            return self.get_object_entry(name, attrs=attrs)
        if not self.cn.search(
                self._realm,
                '(&(objectClass=computer)(name=%s))' % name,
                attributes=attrs) or self.cn.result['result'] != 0 or len(self.cn.entries) == 0:
            return False
        return self.cn.entries[0]

    def get_computer_memberof(self, computer, simple=False):
        """
        :computer                   The existing domain computer entry, it's DN or name;
        :returns                    A list of groups names to which this computer belongs to
                                    if succeed, False otherwise.
        """
        if isinstance(computer, str) and not self._is_alike_dn(computer):
            computer = self.get_computer_entry(computer, attrs=[DN])
        if not computer:
            return False
        return self.get_object_memberof(computer, simple=simple)

    def add_computer(self, name, fqdn=None, branch='Computers', **kwargs):
        """ Adds new computer to the domain. Note that this method only creates a
        LDAP record, but doing nothing with specified computer itself (not joins
        computer to the domain at computer OS side)
        :name                       Name of the new computer;
        :fqdn                       If set - DNS name of the new computer; otherwise
                                    DNS name will be generated automatically basing
                                    on the computer name and realm;
        :branch                     Branch (OU) where the new computer is place to;
        :kwargs                     A set of computer attributes (see 'update_computer');
        :returns                    True if succeed, False otherwise.
        """
        branch = self._get_branch(branch)
        if fqdn is None:
            fqdn = "%s.%s" % (name.lower(), self.ldap_realm.lower())
        object_class = ['top', 'person', 'organizationalPerson', 'user', 'computer']
        attrs = {
            'dNSHostName': fqdn,
            'userAccountControl': UAC_WORKSTATION_TRUST_ACCOUNT,
            'sAMAccountName': "%s$" % name
        }
        if 'description' in kwargs and kwargs['description']:
            attrs['description'] = kwargs['description']
        if 'os_system' in kwargs and kwargs['os_system']:
            attrs['operatingSystem'] = kwargs['os_system']
        if 'os_version' in kwargs and kwargs['os_version']:
            attrs['operatingSystemVersion'] = kwargs['os_version']
        if 'os_servicepack' in kwargs and kwargs['os_servicepack']:
            attrs['operatingSystemServicePack'] = kwargs['os_servicepack']
        if 'os_hotfix' in kwargs and kwargs['os_hotfix']:
            attrs['operatingSystemHotfix'] = kwargs['os_hotfix']
        dn = "cn=%s,%s" % (name, branch)
        return self.cn.add(dn, object_class, attrs) and self.cn.result['result'] == 0

    def delete_computer(self, computer):
        """
        Deletes existing domain computer
        :computer               The existing domain computer entry, it's DN or name;
        :returns                True if succeed, False otherwise
        """
        if isinstance(computer, str) and not self._is_alike_dn(computer):
            computer = self.get_computer_entry(computer, attrs=[DN])
        if not computer:
            return False
        return self.delete_object(computer)

    def update_computer(self, computer, **kwargs):
        """
        Updates computer entry in the domain. Available **kwargs options (and their
        matching LDAP attributes) are:
            name:               ldap: CN (DN)
            fqdn:               ldap: dNSHostName
            description:        ldap: description
            os_system:          ldap: operatingSystem
            os_version:         ldap: operatingSystemVersion
            os_servicepack:     ldap: operatingSystemServicePack
            os_hotfix:          ldap: operatingSystemHotfix
            primary_group:      ldap: primaryGroupID (resolving group name to short SID)
        :computer               The existing domain computer entry, it's DN or name;
        :returns                True if succeed, False otherwise.
        """
        if isinstance(computer, str) and not self._is_alike_dn(computer):
            computer = self.get_computer_entry(computer, attrs=[DN])
        dn = self._dn(computer)
        if not dn:
            return False
        changes = {}
        for k in kwargs:
            if k not in LDAP_SIMPLE_ATTR:
                continue
            ldap_k = LDAP_SIMPLE_ATTR[k]
            ldap_v = kwargs[k]
            if not ldap_v:
                changes[ldap_k] = [(ldap3.MODIFY_DELETE, [])]
            else:
                changes[ldap_k] = [(ldap3.MODIFY_REPLACE, [str(kwargs[k])])]
        if 'primary_group' in kwargs:
            group = self.get_group_entry(kwargs['primary_group'])
            if group is False:
                return False
            group_sid = self._e_val(group, 'objectSid', None)
            if not group_sid:
                return False
            if not str(group_sid).startswith(self.domain_sid):
                return False
            pgid = group_sid[len(self.domain_sid)+1:]
            changes['primaryGroupID'] = [(ldap3.MODIFY_REPLACE, [pgid])]
        if changes:
            if not self.cn.modify(dn, changes):
                return False
        if 'name' in kwargs:
            new_dn = "CN=%s" % kwargs['name']
            return self.cn.modify_dn(dn, new_dn)
        return True

    def rename_computer(self, computer, new_name, new_fqdn=None, rename_fqdn=True):
        """
        Renames existing computer to the new name.
        :computer                   The existing computer entry, it's DN or name;
        :new_name                   New name of the computer;
        :new_fqdn                   If set - the given 'new_fqdn' will be used to update
                                    DNS name attribute in the computer entry instead of
                                    generating this DNS name from the new computer name
                                    and used realm;
        :rename_fqdn:               If set to 'True' (default) - the DNS name attribute
                                    in the computer entry will be updated too, if set
                                    to 'False' - the DNS name will be kept while computer
                                    name been renamed.
        :returns                    True if succeed, False otherwise
        """
        if isinstance(computer, str) and not self._is_alike_dn(computer):
            computer = self.get_computer_entry(computer, attrs=[DN])
        dn = self._dn(computer)
        if not dn:
            return False
        new_name = new_name.upper()
        changes = {'sAMAccountName': [(ldap3.MODIFY_REPLACE, ["%s$" % new_name])]}
        if new_fqdn:
            changes['dNSHostName'] = [(ldap3.MODIFY_REPLACE, [new_fqdn.lower()])]
        elif rename_fqdn:
            cur_fqdn = self._e_val(computer, 'dNSHostName', None)
            if cur_fqdn is not None and isinstance(cur_fqdn, str):
                _fqdn = cur_fqdn.split('.')
                new_fqdn = "%s.%s" % (new_name, ".".join(_fqdn[1:])) if len(_fqdn) > 1 else new_name
                changes['dNSHostName'] = [(ldap3.MODIFY_REPLACE, [new_fqdn.lower()])]
        r = self.cn.modify(dn, changes)
        if not r:
            return False
        new_dn = "CN=%s" % new_name
        return self.cn.modify_dn(dn, new_dn)


