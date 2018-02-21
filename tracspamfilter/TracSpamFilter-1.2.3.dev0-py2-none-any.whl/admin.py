# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Edgewall Software
# Copyright (C) 2015 Dirk Stöcker <trac@dstoecker.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.
#
# Author: Dirk Stöcker <trac@dstoecker.de>

import urllib2

from trac.admin import IAdminPanelProvider
from trac.config import BoolOption, IntOption
from trac.core import Component, implements
from trac.web.api import HTTPNotFound
from trac.web.chrome import (
    ITemplateProvider, add_link, add_script, add_script_data, add_stylesheet)

from tracspamfilter.api import _, gettext, ngettext
from tracspamfilter.filters.akismet import AkismetFilterStrategy
from tracspamfilter.filters.blogspam import BlogSpamFilterStrategy
from tracspamfilter.filters.botscout import BotScoutFilterStrategy
from tracspamfilter.filters.fspamlist import FSpamListFilterStrategy
from tracspamfilter.filters.stopforumspam import StopForumSpamFilterStrategy
from tracspamfilter.filtersystem import FilterSystem
from tracspamfilter.model import LogEntry, Statistics
try:
    from tracspamfilter.filters.bayes import BayesianFilterStrategy
except ImportError:  # SpamBayes not installed
    BayesianFilterStrategy = None
try:
    from tracspamfilter.filters.httpbl import HttpBLFilterStrategy
    from tracspamfilter.filters.ip_blacklist import IPBlacklistFilterStrategy
    from tracspamfilter.filters.url_blacklist import URLBlacklistFilterStrategy
except ImportError:  # DNS python not installed
    HttpBLFilterStrategy = None
    IPBlacklistFilterStrategy = None
    URLBlacklistFilterStrategy = None
try:
    from tracspamfilter.filters.mollom import MollomFilterStrategy
except ImportError:  # Mollom not installed
    MollomFilterStrategy = None


class SpamFilterAdminPageProvider(Component):
    """Web administration panel for configuring and monitoring the spam
    filtering system.
    """

    implements(ITemplateProvider)
    implements(IAdminPanelProvider)

    MAX_PER_PAGE = 10000
    MIN_PER_PAGE = 5
    DEF_PER_PAGE = IntOption('spam-filter', 'spam_monitor_entries', '100',
            "How many monitor entries are displayed by default "
            "(between 5 and 10000).", doc_domain='tracspamfilter')

    train_only = BoolOption('spam-filter', 'show_train_only', False,
            "Show the buttons for training without deleting entry.",
            doc_domain='tracspamfilter')

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'SPAM_CONFIG' in req.perm:
            yield ('spamfilter', _("Spam Filtering"),
                   'config', _("Configuration"))
        if 'SPAM_MONITOR' in req.perm:
            yield ('spamfilter', _("Spam Filtering"),
                   'monitor', _("Monitoring"))

    def render_admin_panel(self, req, cat, page, path_info):
        if page == 'config':
            if req.method == 'POST':
                if self._process_config_panel(req):
                    req.redirect(req.href.admin(cat, page))
            data = self._render_config_panel(req, cat, page)
        else:
            if req.method == 'POST':
                if self._process_monitoring_panel(req):
                    req.redirect(req.href.admin(cat, page,
                                                page=req.args.getint('page'),
                                                num=req.args.getint('num')))
            if path_info:
                data = self._render_monitoring_entry(req, cat, page, path_info)
                page = 'entry'
            else:
                data = self._render_monitoring_panel(req, cat, page)
                data['allowselect'] = True
                data['monitor'] = True
                add_script_data(req, {
                    'bayestext': _("SpamBayes determined spam probability "
                                   "of %s%%"),
                    'sel100text': _("Select 100.00%% entries") % (),
                    'sel90text': _("Select &gt;90.00%% entries") % (),
                    'sel10text': _("Select &lt;10.00%% entries") % (),
                    'sel0text': _("Select 0.00%% entries") % (),
                    'selspamtext': _("Select Spam entries"),
                    'selhamtext': _('Select Ham entries')
                })
                add_script(req, 'spamfilter/adminmonitor.js')
                add_script_data(req, {'toggleform': 'spammonitorform'})
                add_script(req, 'spamfilter/toggle.js')

        add_stylesheet(req, 'spamfilter/admin.css')
        data['accmgr'] = 'ACCTMGR_USER_ADMIN' in req.perm
        return 'admin_spam%s.html' % page, data

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('spamfilter', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    # Internal methods

    def _render_config_panel(self, req, cat, page):
        req.perm.require('SPAM_CONFIG')
        filter_system = FilterSystem(self.env)

        strategies = []
        for strategy in filter_system.strategies:
            for variable in dir(strategy):
                if variable.endswith('karma_points'):
                    strategies.append({
                        'name': strategy.__class__.__name__,
                        'karma_points': getattr(strategy, variable),
                        'variable': variable,
                        'karma_help': gettext(getattr(strategy.__class__,
                                                      variable).__doc__)
                    })

        add_script(req, 'spamfilter/adminconfig.js')
        return {
            'strategies': sorted(strategies, key=lambda x: x['name']),
            'min_karma': filter_system.min_karma,
            'authenticated_karma': filter_system.authenticated_karma,
            'attachment_karma': filter_system.attachment_karma,
            'register_karma': filter_system.register_karma,
            'trust_authenticated': filter_system.trust_authenticated,
            'logging_enabled': filter_system.logging_enabled,
            'nolog_obvious': filter_system.nolog_obvious,
            'purge_age': filter_system.purge_age,
            'spam_monitor_entries_min': self.MIN_PER_PAGE,
            'spam_monitor_entries_max': self.MAX_PER_PAGE,
            'spam_monitor_entries': self.DEF_PER_PAGE
        }

    def _process_config_panel(self, req):
        req.perm.require('SPAM_CONFIG')

        spam_config = self.config['spam-filter']

        min_karma = req.args.as_int('min_karma')
        if min_karma is not None:
            spam_config.set('min_karma', min_karma)

        attachment_karma = req.args.as_int('attachment_karma')
        if attachment_karma is not None:
            spam_config.set('attachment_karma', attachment_karma)

        register_karma = req.args.as_int('register_karma')
        if register_karma is not None:
            spam_config.set('register_karma', register_karma)

        authenticated_karma = req.args.as_int('authenticated_karma')
        if authenticated_karma is not None:
            spam_config.set('authenticated_karma', authenticated_karma)

        for strategy in FilterSystem(self.env).strategies:
            for variable in dir(strategy):
                if variable.endswith('karma_points'):
                    key = strategy.__class__.__name__ + '_' + variable
                    points = req.args.get(key)
                    if points is not None:
                        option = getattr(strategy.__class__, variable)
                        self.config.set(option.section, option.name, points)

        logging_enabled = 'logging_enabled' in req.args
        spam_config.set('logging_enabled', logging_enabled)

        nolog_obvious = 'nolog_obvious' in req.args
        spam_config.set('nolog_obvious', nolog_obvious)

        trust_authenticated = 'trust_authenticated' in req.args
        spam_config.set('trust_authenticated', trust_authenticated)

        if logging_enabled:
            purge_age = req.args.as_int('purge_age')
            if purge_age is not None:
                spam_config.set('purge_age', purge_age)

        spam_monitor_entries = req.args.as_int('spam_monitor_entries',
                                               min=self.MIN_PER_PAGE,
                                               max=self.MAX_PER_PAGE)
        if spam_monitor_entries is not None:
            spam_config.set('spam_monitor_entries', spam_monitor_entries)

        self.config.save()
        return True

    def _render_monitoring_panel(self, req, cat, page):
        req.perm.require('SPAM_MONITOR')

        pagenum = req.args.as_int('page', 1) - 1

        pagesize = req.args.as_int('num', self.DEF_PER_PAGE,
                                   min=self.MIN_PER_PAGE,
                                   max=self.MAX_PER_PAGE)

        total = LogEntry.count(self.env)

        if total < pagesize:
            pagenum = 0
        elif total <= pagenum * pagesize:
            pagenum = (total - 1) / pagesize

        offset = pagenum * pagesize
        entries = list(LogEntry.select(self.env, limit=pagesize,
                                       offset=offset))
        if pagenum > 0:
            add_link(req, 'prev',
                     req.href.admin(cat, page, page=pagenum, num=pagesize),
                     _("Previous Page"))
        if offset + pagesize < total:
            add_link(req, 'next',
                     req.href.admin(cat, page, page=pagenum + 2, num=pagesize),
                     _("Next Page"))

        return {
            'enabled': FilterSystem(self.env).logging_enabled,
            'entries': entries,
            'offset': offset + 1,
            'page': pagenum + 1,
            'num': pagesize,
            'total': total,
            'train_only': self.train_only
        }

    def _render_monitoring_entry(self, req, cat, page, entry_id):
        req.perm.require('SPAM_MONITOR')

        entry = LogEntry.fetch(self.env, entry_id)
        if not entry:
            raise HTTPNotFound(_("Log entry not found"))

        previous = entry.get_previous()
        if previous:
            add_link(req, 'prev', req.href.admin(cat, page, previous.id),
                     _("Log Entry %(id)s", id=previous.id))
        add_link(req, 'up', req.href.admin(cat, page), _("Log Entry List"))
        next = entry.get_next()
        if next:
            add_link(req, 'next', req.href.admin(cat, page, next.id),
                     _("Log Entry %(id)s", id=next.id))

        return {'entry': entry, 'train_only': self.train_only}

    def _process_monitoring_panel(self, req):
        req.perm.require('SPAM_TRAIN')

        filtersys = FilterSystem(self.env)

        spam = 'markspam' in req.args or 'markspamdel' in req.args
        train = spam or 'markham' in req.args or 'markhamdel' in req.args
        delete = 'delete' in req.args or 'markspamdel' in req.args or \
                 'markhamdel' in req.args or 'deletenostats' in req.args
        deletestats = 'delete' in req.args

        if train or delete:
            entries = req.args.getlist('sel')
            if entries:
                if train:
                    filtersys.train(req, entries, spam=spam, delete=delete)
                elif delete:
                    filtersys.delete(req, entries, deletestats)

        if 'deleteobvious' in req.args:
            filtersys.deleteobvious(req)

        return True


class ExternalAdminPageProvider(Component):
    """Web administration panel for configuring the External spam filters."""

    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'SPAM_CONFIG' in req.perm:
            yield ('spamfilter', _("Spam Filtering"),
                   'external', _("External Services"))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('SPAM_CONFIG')

        data = {}
        spam_config = self.config['spam-filter']

        akismet = AkismetFilterStrategy(self.env)
        stopforumspam = StopForumSpamFilterStrategy(self.env)
        botscout = BotScoutFilterStrategy(self.env)
        fspamlist = FSpamListFilterStrategy(self.env)

        ip_blacklist_default = ip6_blacklist_default = \
            url_blacklist_default = None
        if HttpBLFilterStrategy:
            ip_blacklist = IPBlacklistFilterStrategy(self.env)
            ip_blacklist_default = ip_blacklist.servers_default
            ip6_blacklist_default = ip_blacklist.servers6_default
            url_blacklist = URLBlacklistFilterStrategy(self.env)
            url_blacklist_default = url_blacklist.servers_default
        mollom = 0
        if MollomFilterStrategy:
            mollom = MollomFilterStrategy(self.env)
        blogspam = BlogSpamFilterStrategy(self.env)

        if req.method == 'POST':
            if 'cancel' in req.args:
                req.redirect(req.href.admin(cat, page))

            akismet_api_url = req.args.get('akismet_api_url')
            akismet_api_key = req.args.get('akismet_api_key')
            mollom_api_url = req.args.get('mollom_api_url')
            mollom_public_key = req.args.get('mollom_public_key')
            mollom_private_key = req.args.get('mollom_private_key')
            stopforumspam_api_key = req.args.get('stopforumspam_api_key')
            botscout_api_key = req.args.get('botscout_api_key')
            fspamlist_api_key = req.args.get('fspamlist_api_key')
            httpbl_api_key = req.args.get('httpbl_api_key')
            ip_blacklist_servers = req.args.get('ip_blacklist_servers')
            ip6_blacklist_servers = req.args.get('ip6_blacklist_servers')
            url_blacklist_servers = req.args.get('url_blacklist_servers')
            blogspam_api_url = req.args.get('blogspam_api_url')
            blogspam_skip_tests = req.args.get('blogspam_skip_tests')
            use_external = 'use_external' in req.args
            train_external = 'train_external' in req.args
            skip_external = req.args.get('skip_external')
            stop_external = req.args.get('stop_external')
            skip_externalham = req.args.get('skip_externalham')
            stop_externalham = req.args.get('stop_externalham')
            try:
                verified_key = akismet.verify_key(req, akismet_api_url,
                                                  akismet_api_key)
                if akismet_api_key and not verified_key:
                    data['akismeterror'] = 'The API key is invalid'
                    data['error'] = 1
            except urllib2.URLError, e:
                data['alismeterror'] = e.reason[1]
                data['error'] = 1

            if mollom:
                try:
                    verified_key = mollom.verify_key(req, mollom_api_url,
                                                     mollom_public_key,
                                                     mollom_private_key)
                except urllib2.URLError, e:
                    data['mollomerror'] = e.reason[1]
                    data['error'] = 1
                else:
                    if mollom_public_key and mollom_private_key and \
                            not verified_key:
                        data['mollomerror'] = 'The API keys are invalid'
                        data['error'] = 1

            if not data.get('error', 0):
                spam_config.set('akismet_api_url', akismet_api_url)
                spam_config.set('akismet_api_key', akismet_api_key)
                spam_config.set('mollom_api_url', mollom_api_url)
                spam_config.set('mollom_public_key', mollom_public_key)
                spam_config.set('mollom_private_key', mollom_private_key)
                spam_config.set('stopforumspam_api_key', stopforumspam_api_key)
                spam_config.set('botscout_api_key', botscout_api_key)
                spam_config.set('fspamlist_api_key', fspamlist_api_key)
                spam_config.set('httpbl_api_key', httpbl_api_key)
                if HttpBLFilterStrategy:
                    if ip_blacklist_servers != ip_blacklist_default:
                        spam_config.set('ip_blacklist_servers',
                                        ip_blacklist_servers)
                    else:
                        spam_config.remove('ip_blacklist_servers')
                    if ip6_blacklist_servers != ip6_blacklist_default:
                        spam_config.set('ip6_blacklist_servers',
                                        ip6_blacklist_servers)
                    else:
                        spam_config.remove('ip6_blacklist_servers')
                    if url_blacklist_servers != url_blacklist_default:
                        spam_config.set('url_blacklist_servers',
                                        url_blacklist_servers)
                    else:
                        spam_config.remove('url_blacklist_servers')

                spam_config.set('blogspam_json_api_url',
                                blogspam_api_url)
                spam_config.set('blogspam_json_skip_tests',
                                blogspam_skip_tests)
                spam_config.set('use_external', use_external)
                spam_config.set('train_external', train_external)
                spam_config.set('skip_external', skip_external)
                spam_config.set('stop_external', stop_external)
                spam_config.set('skip_externalham', skip_externalham)
                spam_config.set('stop_externalham', stop_externalham)
                self.config.save()
                req.redirect(req.href.admin(cat, page))

        else:
            filter_system = FilterSystem(self.env)
            use_external = filter_system.use_external
            train_external = filter_system.train_external
            skip_external = filter_system.skip_external
            stop_external = filter_system.stop_external
            skip_externalham = filter_system.skip_externalham
            stop_externalham = filter_system.stop_externalham
            blogspam_api_url = blogspam.api_url
            blogspam_skip_tests = ','.join(blogspam.skip_tests)
            akismet_api_url = akismet.api_url
            akismet_api_key = akismet.api_key
            mollom_public_key = mollom_private_key = mollom_api_url = None
            if MollomFilterStrategy:
                mollom_api_url = mollom.api_url
                mollom_public_key = mollom.public_key
                mollom_private_key = mollom.private_key
            stopforumspam_api_key = stopforumspam.api_key
            botscout_api_key = botscout.api_key
            fspamlist_api_key = fspamlist.api_key
            httpbl_api_key = spam_config.get('httpbl_api_key')
            ip_blacklist_servers = spam_config.get('ip_blacklist_servers')
            ip6_blacklist_servers = spam_config.get('ip6_blacklist_servers')
            url_blacklist_servers = spam_config.get('url_blacklist_servers')

        if HttpBLFilterStrategy:
            data['blacklists'] = 1
            data['ip_blacklist_default'] = ip_blacklist_default
            data['ip6_blacklist_default'] = ip6_blacklist_default
            data['url_blacklist_default'] = url_blacklist_default
        if MollomFilterStrategy:
            data['mollom'] = 1
            data['mollom_public_key'] = mollom_public_key
            data['mollom_private_key'] = mollom_private_key
            data['mollom_api_url'] = mollom_api_url
        data['blogspam_api_url'] = blogspam_api_url
        data['blogspam_skip_tests'] = blogspam_skip_tests
        data['blogspam_methods'] = blogspam.getmethods()

        data.update({
            'akismet_api_key': akismet_api_key,
            'akismet_api_url': akismet_api_url,
            'httpbl_api_key': httpbl_api_key,
            'stopforumspam_api_key': stopforumspam_api_key,
            'botscout_api_key': botscout_api_key,
            'fspamlist_api_key': fspamlist_api_key,
            'use_external': use_external,
            'train_external': train_external,
            'skip_external': skip_external,
            'stop_external': stop_external,
            'skip_externalham': skip_externalham,
            'stop_externalham': stop_externalham,
            'ip_blacklist_servers': ip_blacklist_servers,
            'ip6_blacklist_servers': ip6_blacklist_servers,
            'url_blacklist_servers': url_blacklist_servers
        })

        add_script(req, 'spamfilter/adminexternal.js')
        add_stylesheet(req, 'spamfilter/admin.css')
        return 'admin_external.html', data


class BayesAdminPageProvider(Component):
    """Web administration panel for configuring the Bayes spam filter."""

    if BayesianFilterStrategy:
        implements(IAdminPanelProvider)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'SPAM_CONFIG' in req.perm:
            yield 'spamfilter', _("Spam Filtering"), 'bayes', _("Bayes")

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('SPAM_CONFIG')

        bayes = BayesianFilterStrategy(self.env)
        hammie = bayes._get_hammie()
        data = {}

        if req.method == 'POST':
            if 'train' in req.args:
                bayes.train(None, None, req.args['bayes_content'], '127.0.0.1',
                            spam='spam' in req.args['train'].lower())
                req.redirect(req.href.admin(cat, page))

            elif 'test' in req.args:
                bayes_content = req.args['bayes_content']
                data['content'] = bayes_content
                try:
                    data['score'] = hammie.score(bayes_content.encode('utf-8'))
                except Exception, e:
                    self.log.warn('Bayes test failed: %s', e, exc_info=True)
                    data['error'] = unicode(e)

            else:
                if 'reset' in req.args:
                    self.log.info('Resetting SpamBayes training database')
                    self.env.db_transaction("DELETE FROM spamfilter_bayes")
                elif 'reduce' in req.args:
                    self.log.info('Reducing SpamBayes training database')
                    bayes.reduce()

                min_training = req.args.as_int('min_training')
                if min_training is not None and \
                        min_training != bayes.min_training:
                    self.config.set('spam-filter', 'bayes_min_training',
                                    min_training)
                    self.config.save()

                min_dbcount = req.args.as_int('min_dbcount')
                if min_dbcount is not None and \
                        min_dbcount != bayes.min_dbcount:
                    self.config.set('spam-filter', 'bayes_min_dbcount',
                                    min_dbcount)
                    self.config.save()

                req.redirect(req.href.admin(cat, page))
        ratio = ''
        nspam = hammie.bayes.nspam
        nham = hammie.bayes.nham
        if nham and nspam:
            if nspam > nham:
                ratio = _("(ratio %.1f : 1)") % (float(nspam) / float(nham))
            else:
                ratio = _("(ratio 1 : %.1f)") % (float(nham) / float(nspam))

        dblines, dblines_spamonly, dblines_hamonly, dblines_reduce = \
            bayes.dblines()
        dblines_mixed = dblines - dblines_hamonly - dblines_spamonly
        data.update({
            'min_training': bayes.min_training,
            'min_dbcount': bayes.min_dbcount,
            'dblines': dblines,
            'dblinesreducenum': dblines_reduce,
            'dblinesspamonly':
                ngettext("%(num)d spam", "%(num)d spam", dblines_spamonly),
            'dblineshamonly':
                ngettext("%(num)d ham", "%(num)d ham", dblines_hamonly),
            'dblinesreduce':
                ngettext("%(num)d line", "%(num)d lines", dblines_reduce),
            'dblinesmixed':
                ngettext("%(num)d mixed", "%(num)d mixed", dblines_mixed),
            'nspam': nspam,
            'nham': nham,
            'ratio': ratio
        })

        add_script_data(req, {'hasdata': True if nham + nspam > 0 else False})
        add_script(req, 'spamfilter/adminbayes.js')
        add_stylesheet(req, 'spamfilter/admin.css')
        return 'admin_bayes.html', data


class StatisticsAdminPageProvider(Component):
    """Web administration panel for spam filter statistics."""

    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'SPAM_CONFIG' in req.perm:
            yield ('spamfilter', _("Spam Filtering"),
                   'statistics', _("Statistics"))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('SPAM_CONFIG')

        stats = Statistics(self.env)

        if req.method == 'POST':
            if 'clean' in req.args:
                stats.clean(req.args['strategy'])
            elif 'cleanall' in req.args:
                stats.cleanall()
            req.redirect(req.href.admin(cat, page))

        strategies, overall = stats.getstats()

        data = {'strategies': strategies, 'overall': overall}

        add_stylesheet(req, 'spamfilter/admin.css')
        return 'admin_statistics.html', data
