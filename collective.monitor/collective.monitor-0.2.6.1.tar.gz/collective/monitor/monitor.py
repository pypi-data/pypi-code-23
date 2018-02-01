# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from Products.ZNagios.zcmonitor import beautify_return_values
from Zope2 import app as App
from cStringIO import StringIO
from zc.z3monitor.interfaces import IZ3MonitorPlugin
from zope.component import getUtility, getUtilitiesFor
from zope.component.hooks import setSite
from zope.component.interfaces import ComponentLookupError

import os
import pkg_resources


def get_plone_site(connection, plone_path=None):
    """Return plone site."""
    container = App()
    # app = container.unrestrictedTraverse('/')
    if plone_path:
        plone_paths = [path for path in plone_path.split(os.sep) if path]
        for path_name in plone_paths:
            container = container.get(path_name)
        plone_site = container
        if not plone_site:
            msg = "Error, path '{0}' do not exist".format(plone_path)
            connection.write(str(msg))
            container._p_jar.close()
            return False
        if plone_site.meta_type != 'Plone Site':
            msg = "Error, path {0} is not a plone site, it's {1}".format(plone_path, plone_site.meta_type)
            connection.write(str(msg))
            container._p_jar.close()
            return False
        else:
            return container, plone_site
    else:
        result = False
        for obj in container.values():
            if obj.meta_type == 'Folder':  # if plonesite come from mount point
                for plone in obj.values():
                    if plone.meta_type == 'Plone Site':
                        result = plone
            else:
                if obj.meta_type == 'Plone Site' and not result:
                    result = obj
        return container, result


def get_users(context, obj=True):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    users = []
    for user in portal.acl_users.searchUsers():
        if user['pluginid'] == 'source_users':
            if obj:
                users.append(portal.portal_membership.getMemberById(user['userid']))
            else:
                users.append(user['userid'])
    return users


def count_users(connection, plone_path=None):
    """the total amount of users in your plone site"""
    app, plone_site = get_plone_site(connection, plone_path)
    if plone_site:
        setSite(plone_site)
        users = get_users(plone_site)
        connection.write(str(len(users)))
        app._p_jar.close()


def count_valid_users(connection, plone_path=None):
    """Count all users connected since 90 days"""
    app, plone_site = get_plone_site(connection, plone_path)
    if plone_site:
        setSite(plone_site)
        users = get_users(plone_site)
        valid_users = []
        for user in users:
            if user.getProperty('last_login_time') > (DateTime() - 90):
                valid_users.append(user)
        connection.write(str(len(valid_users)))
        app._p_jar.close()


def check_smtp(connection, plone_path=None):
    """Check if SMTP is initialize, return number of errors found."""
    app, plone_site = get_plone_site(connection, plone_path)
    if plone_site:
        setSite(plone_site)
        try:
            mail_host = getUtility(IMailHost)
        except ComponentLookupError:
            mail_host = getattr(plone_site, 'MailHost')
        mail_errors = []
        if not mail_host.smtp_host:
            mail_errors.append('incorrect host: {0}'.format(mail_host.smtp_host))
        if mail_host.smtp_port != 25:
            mail_errors.append('incorrect port')
        if (getattr(mail_host, 'smtp_userid', None) and mail_host.smtp_userid) or (
                getattr(mail_host, 'smtp_uid', None) and mail_host.smtp_uid):
            mail_errors.append('user entered')
        if (getattr(mail_host, 'smtp_pass', None) and mail_host.smtp_pass) or (
                getattr(mail_host, 'smtp_pwd', None) and mail_host.smtp_pwd):
            mail_errors.append('password entered')
        if not plone_site.email_from_address or plone_site.email_from_address == 'postmaster@localhost':
            mail_errors.append('bad mail')
        connection.write(str(len(mail_errors)))
        app._p_jar.close()


def check_upgrade_steps(connection, plone_path=None):
    """Check if all upgrade steps are ran."""
    app, plone_site = get_plone_site(connection, plone_path)
    not_upgraded = 0
    if plone_site:
        setSite(plone_site)
        ps = plone_site.portal_setup
        # qit = plone_site.portal_quickinstaller
        for profile_id in ps.listProfilesWithUpgrades():
            is_installed = ps.getLastVersionForProfile(profile_id) != 'unknown'
            if is_installed:
                # latest_upgrade_step = qit.getLatestUpgradeStep(profile_id)
                # if latest_upgrade_step != 'unknown':
                upgrades = ps.listUpgrades(profile_id)
                if upgrades:
                    not_upgraded += 1

        connection.write(str(not_upgraded))
    app._p_jar.close()


def creation_date_plonesite(dconnection, unix_time=True, plone_path=None):
    """Get creation date of plonesite object."""
    app, plone_site = get_plone_site(dconnection, plone_path)
    if plone_site:
        setSite(plone_site)
        creation_date = plone_site.creation_date
        if str2bool(unix_time):
            dconnection.write(str(creation_date.timeTime()))
        else:
            dconnection.write(str(creation_date.ISO()))
    app._p_jar.close()


def last_login_time(dconnection, unix_time=True, plone_path=None):
    """Get last login time user."""
    app, plone_site = get_plone_site(dconnection, plone_path)
    if plone_site:
        setSite(plone_site)
        users = get_users(plone_site)
        last_login = ""
        for user in users:
            if not last_login:
                last_login = user.getProperty("last_login_time")
            if user.getProperty("last_login_time") > last_login:
                last_login = user.getProperty("last_login_time")
        if not last_login:
            last_login = plone_site.creation_date
        if str2bool(unix_time):
            dconnection.write(str(last_login.timeTime()))
        else:
            dconnection.write(str(last_login.ISO()))
    app._p_jar.close()


def last_modified_plone_object_time(dconnection, unix_time=True, plone_path=None):
    """Get last modified plone object time."""
    app, plone_site = get_plone_site(dconnection, plone_path)
    if plone_site:
        setSite(plone_site)
        pc = plone_site.portal_catalog
        query = {}
        query['path'] = '/'.join(plone_site.getPhysicalPath())
        query['sort_on'] = 'modified'
        query['sort_order'] = 'reverse'
        query['sort_limit'] = 1
        brain = pc(query)[0]
        if str2bool(unix_time):
            dconnection.write(str(brain.modified.timeTime()))
        else:
            dconnection.write(str(brain.modified.ISO()))
    app._p_jar.close()


def last_modified_zope_object_time(dconnection, unix_time=True, plone_path=None):
    """Get last modified zope object time."""
    from zope.globalrequest import setRequest
    from Testing import makerequest
    app = App()
    app = makerequest.makerequest(app)
    # support plone.subrequest
    app.REQUEST['PARENTS'] = [app]
    setRequest(app.REQUEST)
    container = app.unrestrictedTraverse('/')
    undoable_transactions = container.undoable_transactions()
    if len(undoable_transactions) > 1:
        last_modified = undoable_transactions[0]['time']
        if str2bool(unix_time):
            dconnection.write(str(last_modified.timeTime()))
        else:
            dconnection.write(str(last_modified.ISO()))
    app._p_jar.close()


def dates(dconnection, plone_path=None):
    """Return all date probes."""
    date_probes = [
        'creation_date_plonesite',
        'last_login_time',
        'last_modified_plone_object_time',
        'last_modified_zope_object_time',
    ]
    for name, probe in getUtilitiesFor(IZ3MonitorPlugin):
        if name not in date_probes:
            continue
        tempStream = StringIO()
        probe(tempStream)
        beautify_return_values(dconnection, tempStream, name)


def str2bool(v):
    if bool(v):
        return v
    return v.lower() in ('yes', 'true', 't', '1')


def eggs(econnection, plone_path=None):
    """
    return a list with all eggs installed ant it version
    XXX improve check if egg is a plone egg.
    """
    app, plone_site = get_plone_site(econnection, plone_path)
    if plone_site:
        setSite(plone_site)
        qi = getattr(plone_site, 'portal_quickinstaller')
        ps = getattr(plone_site, 'portal_setup')
        from Products.CMFPlone.interfaces import IPloneSiteRoot
        profiles = ps.listProfileInfo(IPloneSiteRoot)
        # profiles = ps.listProfileInfo()

        products = set([prof['product'] for prof in profiles])

        # from Products.CMFPlone.interfaces import INonInstallable
        # from zope.component import getAllUtilitiesRegisteredFor
        # non_installable_non_flatten = [profile.getNonInstallableProfiles() for profile in getAllUtilitiesRegisteredFor(INonInstallable)]
        # non_installable = [item for sublist in non_installable_non_flatten for item in sublist]

        packages_installed = [pack['id'] for pack in qi.listInstalledProducts()]
        eggs = []
        pkg_list = pkg_resources.Environment()
        for pkg_name in pkg_list:
            pkg = pkg_resources.Environment()[pkg_name]
            if len(pkg) == 1:
                egg = {}
                egg['name'] = pkg[0].project_name
                egg['version'] = pkg[0].version
            else:
                # mutliple version of this package installed
                versions = []
                for p in pkg:
                    egg = {}
                    egg['name'] = p.project_name
                    versions.append(p.version)
                egg['version'] = versions

            if egg['name'] in packages_installed:
                egg['installed'] = True
            else:
                egg['installed'] = False

            if egg['name'] in products:
                egg['plone'] = True
            else:
                egg['plone'] = False

            eggs.append(egg)

        econnection.write(str(eggs))
    app._p_jar.close()
