"""Admin Methods for AgilePoint API"""
import json
from ._utils import handle_response, validate_args
# pylint: disable=too-many-public-methods

class Admin(object):
    """Admin Methods for AgilePoint API"""
    def __init__(self, agilepoint):
        self.admin = agilepoint.agilepoint.Admin
        self.agilepoint = agilepoint

    def activate_delegation(self, delegationid):
        """Activates a delegation.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodActivateDelegation.html

        Path Args: delegationID
        Required Body Args: None
        Optional Body Args: None
        Response: Bool"""
        resp = self.admin.ActivateDelegation(delegationid).POST()
        return handle_response('bool', resp)

    def add_delegation(self, **kwargs):
        """Creates a rule for delegating one user's tasks to another user.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodAddDelegation.html

        Path Args: None
        Required Body Args: FromUser, ToUser, StartDate, EndDate, Description
        Optional Body Args: None
        Response: JSON"""
        req_args = ['FromUser', 'ToUser', 'StartDate', 'EndDate', 'Description']
        validate_args(kwargs, req_args)
        resp = self.admin.AddDelegation.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def add_email_template(self, **kwargs):
        """Adds an email template to the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodAddEMailTemplate.html

        Path Args: None
        Required Body Args: TemplateOwnerID, MailTemplateXML
        Optional Body Args: None
        Response: text"""
        req_args = ['TemplateOwnerID', 'MailTemplateXML']
        validate_args(kwargs, req_args)
        resp = self.admin.AddEMailTemplate.POST(data=json.dumps(kwargs))
        return handle_response('text', resp)

    def add_group(self, **kwargs):
        """Adds a group to the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodAddGroup.html

        Path Args: None
        Required Body Args: GroupName, ResponsibleUser
        Optional Body Args: Enabled, Description"""
        req_args = ['GroupName', 'ResponsibleUser']
        validate_args(kwargs, req_args)
        resp = self.admin.AddGroup.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def add_group_member(self, **kwargs):
        """Adds a user as a member of a group.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodAddGroupMember.html

        Path Args: None
        Required Body Args: Description, Enabled, GroupName, UserName
        Optional Body Args: ClientData"""
        req_args = ['Description', 'Enabled', 'GroupName', 'UserName']
        validate_args(kwargs, req_args)
        resp = self.admin.AddGroupMember.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def add_role(self, **kwargs):
        """Adds a role to the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodAddRole.html

        Path Args: None
        Required Body Args: RoleName, Description, Rights, Enabled
        Optional Body Args: None"""
        req_args = ['RoleName', 'Description', 'Rights', 'Enabled']
        validate_args(kwargs, req_args)
        resp = self.admin.AddRole.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def add_role_member(self, **kwargs):
        """Adds a user or a group to a role.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodAddRoleMember.html

        Path Args: None
        Required Body Args: Assignee, AssigneeType, ClientData, ObjectID,
                            ObjectType, RoleName
        Optional Body Args: None"""
        req_args = ['Assignee', 'AssigneeType', 'ClientData', 'ObjectID',
                    'ObjectType', 'RoleName']
        validate_args(kwargs, req_args)
        resp = self.admin.AddRoleMember.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def cancel_delegation(self, delegationid):
        """Cancels a currently operating delegation.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCancelDelegation.html

        Path Args: delegationID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.CancelDelegation(delegationid).POST()
        return handle_response('bool', resp)

    def get_access_right_names(self):
        """Retrieves the names of all the access rights in the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetAccessRightNames.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetAccessRightNames.GET()
        return handle_response('json', resp)

    def get_access_rights(self, **kwargs):
        """Retrieves the access rights for a specified user.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetAccessRights.html

        Path Args: None
        Required Body Args: userName
        Optional Body Args: None"""
        req_args = ['userName']
        validate_args(kwargs, req_args)
        resp = self.admin.GetAccessRights.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_all_email_templates(self):
        """Retrieves all the global email templates from the server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetAllEMailTemplates.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetAllEMailTemplates.GET()
        return handle_response('json', resp)

    def get_database_info(self):
        """Retrieves the database information of the current server configuration.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetDatabaseInfo.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetDatabaseInfo.GET()
        return handle_response('json', resp)

    def get_delegation(self, delegationid):
        """Retrieves a delegation object.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetDelegation.html

        Path Args: delegationID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetDelegation(delegationid).GET()
        return handle_response('json', resp)

    def get_delegations(self, delegationid, **kwargs):
        """Retrieves a list of delegation objects that match the specified parameters.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetDelegation.html

        Path Args: delegationID
        Required Body Args: None
        Optional Body Args: FromUser, ToUser, Status"""
        opt_args = ['FromUser', 'ToUser', 'Status']
        validate_args(kwargs, opt_args=opt_args)
        resp = self.admin.GetDelegations(delegationid).POST(
            data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_domain_group_members(self, **kwargs):
        """Retrieves the members of a domain group.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetDomainGroupMembers.html

        Path Args: None
        Required Body Args: groupDistinguishedName
        Optional Body Args: None"""
        req_args = ['groupDistinguishedName']
        validate_args(kwargs, req_args)
        resp = self.admin.GetDomainGroupMembers.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_domain_groups(self, **kwargs):
        """Retrieves all the domain group objects.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetDomainGroups.html

        Path Args: None
        Required Body Args: Filter, LDAPPath
        Optional Body Args: None"""
        req_args = ['Filter', 'LDAPPath']
        validate_args(kwargs, req_args)
        resp = self.admin.GetDomainGroups.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_domain_name(self):
        """Retrieves the domain name to which AgilePoint Server connects.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetDomainName.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetDomainName.GET()
        return handle_response('json', resp)

    def get_domain_users(self, **kwargs):
        """Retrieves all the user information in the domain that AgilePoint
        Server connects. It could be a local Windows system user, or a domain
        controller on the network.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetDomainUsers.html

        Path Args: None
        Required Body Args: Filter, LDAPPath
        Optional Body Args: None"""
        req_args = ['Filter', 'LDAPPath']
        validate_args(kwargs, req_args)
        resp = self.admin.GetDomainUsers.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_email_template(self, mailtemplateid):
        """Retrieves an email templates with the specified template name from
        the server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetEMailTemplate.html

        Path Args: mailTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetEMailTemplate(mailtemplateid).GET()
        return handle_response('json', resp)

    def get_group(self, groupname):
        """Retrieves a group object with the specified group name.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetGroup.html

        Path Args: groupName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetGroup(groupname).GET()
        return handle_response('json', resp)

    def get_group_members(self, groupname):
        """Retrieves the members of a specified group.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetGroupMembers.html

        Path Args: groupName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetGroupMembers(groupname).GET()
        return handle_response('json', resp)

    def get_groups(self):
        """Retrieves all the group objects in the system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetGroups.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetGroups.GET()
        return handle_response('json', resp)

    def get_locale(self):
        """Retrieves the default locale for the AgilePoint Server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetLocale.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetLocale.GET()
        return handle_response('json', resp)

    def get_register_user(self, **kwargs):
        """Retrieves the user information for the registered user.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetRegisterUser.html

        Path Args: None
        Required Body Args: userName
        Optional Body Args: None"""
        req_args = ['userName']
        validate_args(kwargs, req_args)
        resp = self.admin.GetRegisterUser.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_register_users(self):
        """Retrieves all registered users.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetRegisterUsers.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetRegisterUsers.GET()
        return handle_response('json', resp)

    def get_role(self, rolename):
        """Retrieves a role object by name.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetRole.html

        Path Args: roleName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetRole(rolename).GET()
        return handle_response('json', resp)

    def get_roles(self):
        """Retrieves a list of all roles in the system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetRoles.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetRoles.GET()
        return handle_response('json', resp)

    def get_sender_email_address(self):
        """Retrieves the sender email address of the AgilePoint Server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetSenderEMailAddress.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetSenderEMailAddress.GET()
        return handle_response('json', resp)

    def get_smtp_server(self):
        """Retrieves the SMTP server of the current server configuration.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetSmtpServer.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetSmtpServer.GET()
        return handle_response('json', resp)

    def get_sys_perf_info(self):
        """Retrieves system performance information for AgilePoint Server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetSysPerfInfo.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetSysPerfInfo.GET()
        return handle_response('json', resp)

    def get_system_user(self):
        """Retrieves the name of the system user.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetSystemUser.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.GetSystemUser.GET()
        return handle_response('json', resp)

    def query_register_users_using_sql(self, **kwargs):
        """Query the list of registered users in AgilePoint.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryRegisterUsersUsingSQL.html

        Path Args: None
        Required Body Args: sqlWhereClause
        Optional Body Args: None"""
        req_args = ['sqlWhereClause']
        validate_args(kwargs, req_args)
        resp = self.admin.QueryRegisterUsersUsingSQL.POST(
            data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_role_members(self, rolename):
        """Retrieves the members assigned to a role that match a specified SQL
        statement.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryRoleMembers.html

        Path Args: roleName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.QueryRoleMembers(rolename).POST()
        return handle_response('json', resp)

    def register_user(self, **kwargs):
        """Registers a user on the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRegisterUser.html

        Path Args: None
        Required Body Args: UserName, FullName
        Optional Body Args: Department, EMailAddress, Locale, Manager,
                            OnlineContact, RefID, RegisteredDate, TimeZone,
                            Title, UALExpirationDate, UALNeverExpires
        Response: Bool"""
        req_args = ['UserName', 'FullName']
        opt_args = ['Department', 'EMailAddress', 'FullName', 'Locale',
                    'Manager', 'OnlineContact', 'RefID', 'RegisteredDate',
                    'TimeZone', 'Title', 'UALExpirationDate', 'UALNeverExpires',
                    'UserName']
        validate_args(kwargs, req_args, opt_args)
        resp = self.admin.RegisterUser.POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def remove_delegation(self, delegationid):
        """Removes a delegation from the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRemoveDelegation.html

        Path Args: delegationID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.RemoveDelegation(delegationid).POST()
        return handle_response('bool', resp)

    def remove_group(self, groupname):
        """Removes a group from the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRemoveGroup.html

        Path Args: delegationID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.RemoveGroup(groupname).POST()
        return handle_response('bool', resp)

    def remove_group_member(self, **kwargs):
        """Removes a member from a group.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRemoveGroupMember.html

        Path Args: None
        Required Body Args: GroupName, UserName
        Optional Body Args: None"""
        req_args = ['GroupName', 'UserName']
        validate_args(kwargs, req_args)
        resp = self.admin.RemoveGroupMember.POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def remove_role_member(self, **kwargs):
        """Removes a user or a group from a specified role.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRemoveRoleMember.html

        Path Args: None
        Required Body Args: Assignee, AssigneeType, ObjectID, RoleName
        Optional Body Args: None"""
        req_args = ['Assignee', 'AssigneeType', 'ObjectID', 'RoleName']
        validate_args(kwargs, req_args)
        resp = self.admin.RemoveRoleMember.POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def remove_role(self, rolename):
        """Removes a role from the AgilePoint system.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRemoveRole.html

        Path Args: roleName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.admin.RemoveRole(rolename).POST()
        return handle_response('bool', resp)

    def unregister_user(self, **kwargs):
        """Removes a user's registration from the AgilePoint system. Note that
        this call does not remove the user from the local Windows system or the
        domain controller.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUnregisterUser.html

        Path Args: None
        Required Body Args: userName
        Optional Body Args: None"""
        req_args = ['userName']
        validate_args(kwargs, req_args)
        resp = self.admin.UnregisterUser.POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def update_delegation(self, **kwargs):
        """Updates a delegation object that has already been created.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateDelegation.html

        Path Args: None
        Required Body Args: DelegationID
        Optional Body Args: DelegationID, FromUser, ToUser, StartDate, EndDate,
                            Description, Status"""
        req_args = ['DelegationID', 'FromUser', 'ToUser', 'StartDate',
                    'EndDate', 'Description', 'Status']
        validate_args(kwargs, req_args)
        resp = self.admin.UpdateDelegation.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def update_email_template(self, **kwargs):
        """Updates an email template in the AgilePoint database.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateEMailTemplate.html

        Path Args: None
        Required Body Args: MailTemplateID, MailTemplateXML,
                            TemplateModifiedUserName
        Optional Body Args: None"""
        req_args = ['MailTemplateID', 'MailTemplateXML',
                    'TemplateModifiedUserName']
        validate_args(kwargs, req_args)
        resp = self.admin.UpdateEMailTemplate.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def update_group(self, **kwargs):
        """Updates information for a group.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateGroup.html

        Path Args: None
        Required Body Args: Description, Enabled, GroupName, ResponsibleUser
        Optional Body Args: None"""
        req_args = ['Description', 'Enabled', 'GroupName', 'ResponsibleUser']
        validate_args(kwargs, req_args)
        resp = self.admin.UpdateGroup.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def update_register_user(self, **kwargs):
        """Updates user data for a registered user.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateRegisterUser.html

        Path Args: None
        Required Body Args: UserName
        Optional Body Args: Department, Disabled, EMailAddress, FullName,
                            Level, Locale, Manager, OnlineContact, RefID,
                            RegisteredDate, SupportedLanguage, TimeZone, Title,
                            UALExpirationDate, UALNeverExpires, UserName,
                            UserOrgInfo, WorkCalendarID"""
        req_args = ['UserName']
        opt_args = ['Department', 'Disabled', 'EMailAddress', 'FullName',
                    'Level', 'Locale', 'Manager', 'OnlineContact', 'RefID',
                    'RegisteredDate', 'SupportedLanguage', 'TimeZone', 'Title',
                    'UALExpirationDate', 'UALNeverExpires', 'UserName',
                    'UserOrgInfo', 'WorkCalendarID']
        validate_args(kwargs, req_args, opt_args)
        resp = self.admin.UpdateRegisterUser.POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def update_role(self, **kwargs):
        """Updates information for a role.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateRole.html

        Path Args: None
        Required Body Args: Description, Enabled, Rights, RoleName
        Optional Body Args: None"""
        req_args = ['Description', 'Enabled', 'Rights', 'RoleName']
        validate_args(kwargs, req_args)
        resp = self.admin.UpdateRole.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)
