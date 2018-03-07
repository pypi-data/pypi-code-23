# encoding: utf-8

from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from c2.search.fuzzy import c2SearchFuzzyMassage as _
from c2.search.fuzzy.words_for_fuzzy_tool import USE_SQL

if USE_SQL:
    from c2.search.fuzzy.sql_connection import DB_CONNECTION_NAME, get_db_status, create_db_table


class IFuzzySearchPanel(ISiteRoot):
    """
    """

class FuzzySearchPanel(BrowserView):
    implements(IFuzzySearchPanel)

    template = ViewPageTemplateFile('controlpanel.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.fuzzy_tool = getToolByName(self.context, 'words_for_fuzzy')
        if self.request.form.get('form.submit.rebuild') == '1':
            self._rebuild()
        if self.request.form.get('form.submit.createdb') == '1':
            self._create_db_table()
        return self.template()

    def count(self):
        fuzzy_tool = self.fuzzy_tool
        return fuzzy_tool.length()

    def _rebuild(self):
        fuzzy_tool = self.fuzzy_tool
        fuzzy_tool.rebuild()
        self.context.plone_utils.addPortalMessage(_(u'Rebuild done'))


    def use_sql_db(self):
        return USE_SQL

    def _create_db_table(self):
        messages = IStatusMessage(self.request)
        db_status = get_db_status(DB_CONNECTION_NAME)
        db_no_error = db_status[0]
        session = db_status[1]
        if db_no_error and not session:
            res = create_db_table(DB_CONNECTION_NAME)
            if res:
                messages.add(u"DB Table created", type=u"info")
            else:
                messages.add(u"Got DB connection error", type=u"error")
        else:
            messages.add(u"DB Table already has created", type=u"error")

    def chk_db_talbe(self):
        db_status = get_db_status(DB_CONNECTION_NAME)
        return {"db_status" : db_status[0],
                "db_session" : db_status[1],
               "db_status_msg" : db_status[2],}



