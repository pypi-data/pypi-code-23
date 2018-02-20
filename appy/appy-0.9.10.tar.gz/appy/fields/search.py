# -*- coding: utf-8 -*-
# Copyright (C) 2007-2018 Gaetan Delannay

# This file is part of Appy.

# Appy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Appy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Appy. If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------
from appy import Object as O
from appy.px import Px
from appy.gen import utils as gutils
from appy.gen.indexer import defaultIndexes
from appy.gen.navigate import Batch
from appy.shared import utils as sutils
from group import Group

# Error messages ---------------------------------------------------------------
WRONG_FIELD = 'Field "%s" does not exist on %s'

# ------------------------------------------------------------------------------
class Mode:
    '''Search results can be displayed in various "modes": as a list, grid,
       calendar, etc. This class is the abstract base class for such modes.
       A concrete Mode instance is created very time search results must be
       computed.'''
    # The default mode(s) for displaying instances of any Appy class
    default = ('list',)
    # All available predefined concrete modes
    concrete = ('list', 'grid', 'calendar')

    @staticmethod
    def get(klass, className, uiSearch, inPopup, tool, req, dir):
        '''Create and return the Mode instance corresponding to the current
           result mode to apply to a list of p_klass instances.'''
        name = req.get('resultMode') or uiSearch.getModes(klass, tool)[0]
        # Extract the number of columns, potentially present in "grid" mode
        cols = None
        if '_' in name:
            name, cols = name.rsplit('_', 1)
        # Determine the concrete mode class
        if name in Mode.concrete:
            custom = False
            modeClass = eval(name.capitalize())
        else:
            custom = True
            modeClass = Custom
        # Create the Mode instance
        r = modeClass(klass, className, uiSearch, inPopup, tool)
        # Complete it
        if cols: r.cols = int(cols)
        if custom:
            # The custom PX is named "name" on p_klass
            r.px = getattr(klass, name)
        r.init(req, dir)
        return r

    @staticmethod
    def getText(name, _):
        '''Gets the i18n text corresponding to mode named p_name'''
        if name in Mode.concrete: return _('result_mode_%s' % name)
        return _('custom_%s' % name)

    def __init__(self, klass, className, uiSearch, inPopup, tool):
        # The class from which we will search instances
        self.klass = klass
        self.className = className
        # The tied UI search
        self.uiSearch = uiSearch
        # Are we in a popup ?
        self.inPopup = inPopup
        # The (z)tool
        self.tool = tool
        # The ID of the tag that will be ajax-filled with search results
        self.ajaxHookId = 'queryResult'
        # Matched objects
        self.objects = None
        # A Batch instance, when only a sub-set of the result set is shown at
        # once.
        self.batch = None
        # Are we sure the result is empty ? (ie, objects could be empty but
        # matched objects could be absent due to filters)
        self.empty = True
        # URL for triggering a new search
        self.newSearchUrl = None
        # The target for "a" tags
        self.target = tool.getLinksTargetInfo(klass)

    def init(self, req, dir):
        '''Every concrete class may have a specific initialization part'''

    def getAjaxData(self):
        '''Initializes an AjaxData object on the DOM node corresponding to the
           ajax hook for this search result.'''
        # For performing a complete Ajax request, "className" is not needed
        # because included in the PX name. But it is requested by sub-Ajax
        # queries at the row level.
        search = self.uiSearch
        name = search.name
        params = {'className': self.className, 'search': name,
                  'popup': self.inPopup and '1' or '0'}
        # Add initiator-specific params
        if search.initiator:
            initatorParams = search.initiator.getAjaxParams()
            if initatorParams: params.update(initatorParams)
        # Concrete classes may add more parameters
        self.updateAjaxParameters(params)
        # Convert params into a JS dict
        params = sutils.getStringFrom(params)
        px = '%s:%s:pxResult' % (self.className, name)
        return "new AjaxData('%s', '%s', %s, null, '%s')" % \
               (self.ajaxHookId, px, params, self.tool.absolute_url())

    def updateAjaxParameters(self, params):
        '''To be overridden by subclasses for adding Ajax parameters
           (see m_getAjaxData above)'''

    def getAjaxDataRow(self, zobj, **params):
        '''Initializes an AjaxData object on the DOM node corresponding to
           p_zobj = a row within the list of results.'''
        return "new AjaxData('%s', 'pxViewAsResultFromAjax', %s, '%s', '%s')"% \
               (zobj.id, sutils.getStringFrom(params), self.ajaxHookId,
                zobj.absolute_url())

class List(Mode):
    '''Displays search results as a table containing one row per object'''
    px = Px('''
     <table class=":ztool.getResultCss(className, layoutType)" width="100%">
      <!-- Headers, with filters and sort arrows -->
      <tr if="showHeaders">
       <th if="mode.checkboxes" class="cbCell"
           style=":'display:%s' % mode.cbDisplay">
        <img src=":url('checkall')" class="clickable"
             title=":_('check_uncheck')"
             onclick=":'toggleAllCbs(%s)' % q(mode.checkboxesId)"/>
       </th>
       <th for="column in mode.columns"
           var2="field=column.field;
                 sortable=field.isSortable(usage='search')"
           width=":column.width" align=":column.align">
        <x>::ztool.truncateText(_(field.labelId))</x>
        <!-- Sort icons -->
        <x if="sortable and (mode.batch.total &gt; 1)">
         <img if="(mode.sortKey != field.name) or (mode.sortOrder == 'desc')"
              onclick=":'askBunchSorted(%s, %s, %s)' % \
                        (q(mode.ajaxHookId), q(field.name), q('asc'))"
              src=":url('sortDown')" class="clickable"/>
         <img if="(mode.sortKey != field.name) or (mode.sortOrder == 'asc')"
              onclick=":'askBunchSorted(%s, %s, %s)' % \
                        (q(mode.ajaxHookId), q(field.name), q('desc'))"
              src=":url('sortUp')" class="clickable"/>
        </x>
        <!-- Filter widget -->
        <x if="field.filterPx and ((mode.batch.total &gt; 1) or \
               mode.filters)">:getattr(field, field.filterPx)</x>
        <x>:tool.pxShowDetails</x>
       </th>
      </tr>

      <!-- Results -->
      <tr if="not mode.objects">
       <td colspan=":len(mode.columns)+1">:_('query_no_result')</td>
      </tr>
      <x for="zobj in mode.objects"
         var2="rowCss=loop.zobj.odd and 'even' or 'odd';
              @currentNumber=currentNumber + 1">:zobj.appy().pxViewAsResult</x>
     </table>
     <!-- The button for selecting objects and closing the popup -->
     <div if="inPopup and mode.cbShown" align=":dleft">
      <input type="button"
             var="label=_('object_link_many'); css=ztool.getButtonCss(label)"
             value=":label" class=":css" style=":url('linkMany', bg=True)"
             onclick=":uiSearch.initiator.jsSelectMany(\
                   q, mode.sortKey, mode.sortOrder, mode.getFiltersString())"/>
     </div>
     <!-- Init checkboxes if present -->
     <script if="mode.checkboxes">:'initCbs(%s)' % q(mode.checkboxesId)</script>
     <script>:'initFocus(%s)' % q(mode.ajaxHookId)</script>''')

    def init(self, req, dir):
        '''List-specific initialization'''
        search = self.uiSearch
        tool = self.tool
        # The search may be triggered via a Ref field
        self.refObject, self.refField = tool.getRefInfo()
        # [Custom searches only] build the URL allowing to trigger a new search
        if search.name == 'customSearch':
            # Build the "Ref" part for this URL
            obj = self.refObject
            part = obj and ('&ref=%s:%s' % (obj.id, self.refField)) or ''
            self.newSearchUrl = '%s/search?className=%s%s' % \
                                (tool.absolute_url(), self.className, part)
        # Build query parameters (start number, sort and filter)
        start = int(req.get('startNumber', '0'))
        self.sortKey = req.get('sortKey', '')
        self.sortOrder = req.get('sortOrder', 'asc')
        self.filters = sutils.getDictFrom(req.get('filters'))
        # Execute the query
        r = tool.executeQuery(self.className, search=search.search,
          startNumber=start, remember=True, sortBy=self.sortKey,
          sortOrder=self.sortOrder, filters=self.filters,
          refObject=self.refObject, refField=self.refField)
        # Unwrap result elements
        self.objects = r.objects
        # Create a Batch instance
        self.batch = Batch(self.ajaxHookId, r.totalNumber, len(r.objects),
                           size=r.batchSize, start=start)
        # Show sub-titles ?
        self.showSubTitles = req.get('showSubTitles', 'true') == 'true'
        # Every mached object may be selected via a checkbox
        self.rootHookId = search.getRootHookId()
        self.checkboxes = search.checkboxes
        self.checkboxesId = self.rootHookId + '_objs'
        self.cbShown = search.showCheckboxes()
        self.cbDisplay = self.cbShown and 'table-cell' or 'none'
        # Determine result emptiness
        self.empty = not self.objects and not self.filters
        # Compute info related to every column in the list
        self.columnLayouts = self.getColumnLayouts()
        self.columns = tool.getColumnsSpecifiers(self.className,
                                                 self.columnLayouts, dir)

    def updateAjaxParameters(self, params):
        '''List-specific ajax parameters'''
        params.update(
          {'startNumber': self.batch.start, 'filters': self.filters,
           'sortKey': self.sortKey, 'sortOrder': self.sortOrder,
           'checkboxes': self.checkboxes, 'checkboxesId': self.checkboxesId,
           'cbDisplay': self.cbDisplay, 'totalNumber': self.batch.total})

    def getColumnLayouts(self):
        '''Returns the column layouts'''
        r = None
        tool = self.tool
        name = self.uiSearch.name
        # Try first to retrieve this info from a potential source Ref field
        obj = self.refObject
        if obj:
            r = obj.getAppyType(self.refField).shownInfo
        elif ',' in name:
            objId, fieldName, dummy = name.split(',')
            # Object may be temporary
            obj = tool.getObject(objId) or tool.getObject(objId, temp=True)
            field = obj.getAppyType(fieldName)
            if field.type == 'Ref':
                r = field.shownInfo
        if r: return r
        # Try to retrieve this info via search.shownInfo
        r = self.uiSearch.search.shownInfo
        if r: return r
        # Try now to retrieve this info via the class' "listColumns"
        k = tool.getAppyClass(self.className)
        if not hasattr(k, 'listColumns'): return ('title',)
        if callable(k.listColumns): return k.listColumns(tool.appy())
        return k.listColumns

    def getFiltersString(self):
        '''Converts dict self.filters into its string representation'''
        filters = self.filters
        if not filters: return ''
        r = []
        for k, v in filters.iteritems():
            r.append('%s:%s' % (k, v))
        return ','.join(r)

    def getNavInfo(self, number):
        '''Gets the navigation string corresponding to the element having this
           p_number within the list of results.'''
        return 'search.%s.%s.%d.%d' % (self.className, self.uiSearch.name, \
                                    self.batch.start + number, self.batch.total)

class Grid(List):
    '''Displays search results as a table containing one cell per object'''
    px = Px('''
     <table width="100%">
      <tr for="row in ztool.splitList(mode.objects, mode.cols)" valign="middle">
       <td for="zobj in row" width=":'%d%%' % (100/mode.cols)" align="center"
           style="padding-top: 25px"
           var2="obj=zobj.appy(); mayView=zobj.mayView()">
        <x var="@currentNumber=currentNumber + 1"
           for="column in mode.columns"
           var2="field=column.field">:field.pxRenderAsResult</x>
       </td>
      </tr>
     </table>''')

    def __init__(self, *args):
        List.__init__(self, *args)
        # The number of columns for the grid
        self.cols = 4

class Calendar(Mode):
    '''Displays search results in a monthly calendar view'''
    px = Px('''<x var="layoutType='view';
                       field=tool.getField('calendar')">:field.pxView</x>''')

    def __init__(self, *args):
        Mode.__init__(self, *args)
        # For this calendar view to work properly, objects to show inside it
        # must have the following attributes:
        # ----------------------------------------------------------------------
        # date    | an indexed and required Date field with format =
        #         | Date.WITH_HOUR storing the object's start date and hour;
        # ----------------------------------------------------------------------
        # endDate | a not necessarily required Date field with format =
        #         | Date.WITH_HOUR storing the object's end date and hour.
        # ----------------------------------------------------------------------

    def init(self, req, dir):
        '''Creates a stub calendar field'''
        # Always consider the result as not empty. This way, the calendar is
        # always shown, even if no object is visible.
        self.empty = False
        # The matched objects, keyed by day. For every day, a list of entries to
        # show. Every entry is a 2-tuple (s_entryType, Object) allowing to
        # display an object at this day. s_entryType can be:
        # ----------------------------------------------------------------------
        #  "start"  | the object starts and ends at this day: display its start
        #           | hour and title;
        # ----------------------------------------------------------------------
        #  "start+" | the object starts at this day but ends at another day:
        #           | display its start hour, title and some sign indicating
        #           | that it spans on another day;
        # ----------------------------------------------------------------------
        #  "end"    | the object started at a previous day and ends at this day.
        #           | Display its title and a sign indicating this fact;
        # ----------------------------------------------------------------------
        #  "pass"   | The object started at a previous day and ends at a future
        #           | day.
        # ----------------------------------------------------------------------
        self.objects = {} # ~{s_YYYYmmdd: [(s_entryType, Object)]}~
        # Formats for keys representing dates
        self.dayKey = '%Y%m%d'
        # Format for representing hours in the UI
        self.hourFormat = '%H:%M'

    # For every hereabove-defined entry type, this dict stores info about how
    # to render events having this type. For every type:
    # --------------------------------------------------------------------------
    # start      | bool | Must we show the event's start hour or not ?
    # end        | bool | Must we show the event's end hour or not ?
    # css        | str  | The CSS class to add the table event tag
    # past       | bool | True if the event spanned more days in the past
    # future     | bool | True if the event spans more days in the future
    # --------------------------------------------------------------------------
    entryTypes = {
     'start':  O(start=True,  end=True,  css=None,      past=None, future=None),
     'start+': O(start=True,  end=False, css='calMany', past=None, future=True),
     'end':    O(start=False, end=True,  css='calMany', past=True, future=None),
     'pass':   O(start=False, end=False, css='calMany', past=True, future=True),
    }

    def addEntry(self, dateKey, entry):
        '''Adds an p_entry as created by m_addEntries below into self.objects
           @key p_dateKey.'''
        r = self.objects
        if dateKey not in r:
            r[dateKey] = [entry]
        else:
            r[dateKey].append(entry)

    def addEntries(self, obj):
        '''Add, in self.objects, entries corresponding to p_obj. If p_obj spans
           a single day, a single entry of the form ("start", p_obj) is added at
           the key corresponding to this day. Else, a series of entries are
           added, each of the form (s_entryType, p_obj), with the same object,
           for every day in p_obj's timespan.

           For example, for an p_obj starting at "1975/12/11 12:00" and ending
           at "1975/12/13 14:00" will produce the following entries:
              key "19751211"  >  value ("start+", obj)
              key "19751212"  >  value ("pass", obj)
              key "19751213"  >  value ("end", obj)
        '''
        # Get p_obj's start and end dates
        start = obj.date
        startKey = start.strftime(self.dayKey)
        end = obj.endDate
        endKey = end and end.strftime(self.dayKey) or None
        # Shorthand for self.objects
        r = self.objects
        if not endKey or (endKey == startKey):
            # A single entry must be added for p_obj, at the start date
            self.addEntry(startKey, ("start", obj))
        else:
            # Add one entry at the start day
            self.addEntry(startKey, ("start+", obj))
            # Add "pass" entries for every day between the start and end days
            next = start + 1
            nextKey = next.strftime(self.dayKey)
            while nextKey != endKey:
                # Add a "pass" event
                self.addEntry(nextKey, ('pass', obj))
                # Go the the next day
                next += 1
                nextKey = next.strftime(self.dayKey)
            # Add an "end" entry at the end day
            self.addEntry(endKey, ('end', obj))

    def search(self, first, grid):
        '''Performs the query, limited to the date range defined by p_grid'''
        # Performs the query, restricted to the visible date range
        last = grid[-1][-1]
        dateSearch = Search(date=(first, last), sortBy='date', sortOrder='asc')
        res = self.tool.executeQuery(self.className,
          search=self.uiSearch.search, maxResults='NO_LIMIT',
          search2=dateSearch)
        # Produce, in self.objects, the dict of matched objects
        for zobj in res.objects:
            self.addEntries(zobj.appy())

    def dumpObjectsAt(self, date):
        '''Returns info about the object(s) that must be shown in the cell
           corresponding to p_date.'''
        # There may be no object dump at this date
        dateStr = date.strftime(self.dayKey)
        if dateStr not in self.objects: return
        # Objects exist
        r = []
        types = self.entryTypes
        url = self.tool.getIncludeUrl
        for entryType, obj in self.objects[dateStr]:
            # Dump the event hour and title. The back hook allows to refresh the
            # whole calendar view when coming back from the popup.
            eType = types[entryType]
            # What CSS class(es) to apply ?
            css = eType.css and ('calEvt %s' % eType.css) or 'calEvt'
            # Show start and/or end hour ?
            eHour = sHour = ''
            if eType.start:
                sHour = '<td width="2em">%s</td>' % \
                        obj.date.strftime(self.hourFormat)
            if eType.end:
                endDate = obj.endDate
                if endDate:
                    eHour = ' <abbr title="%s">¬</abbr>' % \
                            endDate.strftime(self.hourFormat)
            # Display indicators that the event spans more days
            past = eType.past and '⇠ ' or ''
            future = eType.future and ' ⇢' or ''
            # The event title
            title = obj.o.getListTitle(target=self.target, inPopup=True,
              backHook='configcalendar', maxChars=24)
            # Produce the complete entry
            r.append('<table class="%s"><tr valign="top">%s<td>%s%s%s%s</td>'\
                     '</tr></table>' % (css, sHour, past, title, future, eHour))
        return '\n'.join(r)

class Custom(Mode):
    '''Displays search results via a custom PX'''
    def init(self, req, dir):
        '''By default, the Custom mode performs full (unpaginated) searches'''
        r = self.tool.executeQuery(self.className, search=self.uiSearch.search,
                                   maxResults='NO_LIMIT')
        # Initialise Mode's mandatory fields
        self.objects = [z.appy() for z in r.objects]
        self.empty = not self.objects

# ------------------------------------------------------------------------------
class ColSet:
    '''Represents a named set of columns to show when displaying Search results
       (or also Refs).'''
    def __init__(self, identifier, label, columns, specs=False):
        # A short identifier for the set
        self.identifier = identifier
        # The i18n label to use for giving a human-readable name to the set
        self.label = label
        # The list/tuple of columns, expressed as strings. Every string must
        # contain a field name, but can be completed (after a char *) by column
        # width and alignment, as in "state*100px|". The "width" part, just
        # after the *, can hold anything that can be set in a "width" HTML
        # attribute. The last char represents the alignment:
        #   ";"   left-aligned (the default);
        #   "|"   centered;
        #   "!"   right-aligned.
        if not specs:
            self.columns = columns
        else:
            # "specs" is the internal representation of "columns". Do not
            # specify "specs=True". It will contain a list of Object instances
            # instead of strings. Every such instance has splitted string info
            # into fields "field", "width" and "align".
            self.specs = columns

# ------------------------------------------------------------------------------
class Search:
    '''Used for specifying a search for a given class'''
    ColSet = ColSet # Make this class available as "Search.ColSet"
    initiator = None # Is it not possible to create an object from a search

    def __init__(self, name=None, group=None, sortBy='', sortOrder='asc',
                 maxPerPage=30, default=False, colspan=1, translated=None,
                 show=True, showActions=True, translatedDescr=None,
                 checkboxes=False, checkboxesDefault=True, klass=None,
                 resultModes=None, shownInfo=None, **fields):
        # "name" is mandatory, excepted in some special cases (ie, when used as
        # "select" param for a Ref field).
        self.name = name
        # Searches may be visually grouped in the portlet
        self.group = Group.get(group)
        self.sortBy = sortBy
        self.sortOrder = sortOrder
        self.maxPerPage = maxPerPage
        # If this search is the default one, it will be triggered by clicking
        # on main link.
        self.default = default
        self.colspan = colspan
        # If a translated name or description is already given here, we will
        # use it instead of trying to translate from labels.
        self.translated = translated
        self.translatedDescr = translatedDescr
        # Condition for showing or not this search
        self.show = show
        # Condition for showing or not actions on every result of this search.
        # Can be: True, False or "inline". If True, actions will appear in a
        # "div" tag, below the object title; if "inline", they will appear
        # besides it, producing a more compact list of results.
        self.showActions = showActions
        # In the dict below, keys are indexed field names or names of standard
        # indexes, and values are search values.
        self.fields = fields
        # Do we need to display checkboxes for every object of the query result?
        self.checkboxes = checkboxes
        # Default value for checkboxes
        self.checkboxesDefault = checkboxesDefault
        # Most of the time, we know what is the class whose instances must be
        # searched. When it is not the case, the p_klass can be explicitly
        # specified.
        self.klass = klass
        # There can be various ways to display query results
        self.resultModes = resultModes
        # Similar to the homonym Ref attribute, "shownInfo" defines the columns
        # that must be shown on lists of result objects (mode "List" only). If
        # not specified, class's "listColumns" attributes is used.
        self.shownInfo = shownInfo

    @staticmethod
    def getIndexName(name, klass, usage='search'):
        '''Gets the name of the Zope index that corresponds to p_name. Indexes
           can be used for searching (p_usage="search"), for filtering
           ("filter") or for sorting ("sort"). The method returns None if the
           field named p_name can't be used for p_usage.'''
        # Manage indexes that do not have a corresponding field
        if name == 'created': return 'Created'
        elif name == 'modified': return 'Modified'
        elif name in defaultIndexes: return name
        else:
            # Manage indexes corresponding to fields
            field = getattr(klass, name, None) 
            if field: return field.getIndexName(usage)
            raise Exception(WRONG_FIELD % (name, klass.__bases__[-1].__name__))

    @staticmethod
    def getSearchValue(fieldName, fieldValue, klass):
        '''Returns a transformed p_fieldValue for producing a valid search
           value as required for searching in the index corresponding to
           p_fieldName.'''
        # Get the field corresponding to p_fieldName
        field = getattr(klass, fieldName, None)
        if field and callable(field): field = None
        if (field and (field.getIndexType() == 'TextIndex')) or \
           (fieldName == 'SearchableText'):
            # For TextIndex indexes. We must split p_fieldValue into keywords.
            res = gutils.Keywords(fieldValue).get()
        elif isinstance(fieldValue, basestring) and fieldValue.endswith('*'):
            v = fieldValue[:-1]
            # Warning: 'z' is higher than 'Z'!
            res = {'query':(v,v+'z'), 'range':'min:max'}
        elif type(fieldValue) in sutils.sequenceTypes:
            if fieldValue and isinstance(fieldValue[0], basestring):
                # We have a list of string values (ie: we need to
                # search v1 or v2 or...)
                res = fieldValue
            else:
                # We have a range of (int, float, DateTime...) values
                minv, maxv = fieldValue
                rangev = 'minmax'
                queryv = fieldValue
                if minv == None:
                    rangev = 'max'
                    queryv = maxv
                elif maxv == None:
                    rangev = 'min'
                    queryv = minv
                res = {'query':queryv, 'range':rangev}
        else:
            res = fieldValue
        return res

    def updateSearchCriteria(self, criteria, klass, advanced=False):
        '''This method updates dict p_criteria with all the search criteria
           corresponding to this Search instance. If p_advanced is True,
           p_criteria correspond to an advanced search, to be stored in the
           session: in this case we need to keep the Appy names for parameters
           sortBy and sortOrder (and not "resolve" them to Zope's sort_on and
           sort_order).'''
        # Beyond parameters required for performing a search, also store, in
        # p_criteria, other Search parameters if we need to reify a Search
        # instance for performing an advanced search.
        if advanced:
            criteria['showActions'] = self.showActions
            criteria['resultModes'] = self.resultModes
            criteria['shownInfo'] = self.shownInfo
        # Put search criteria in p_criteria
        for name, value in self.fields.iteritems():
            # Management of searches restricted to objects linked through a
            # Ref field: not implemented yet.
            if name == '_ref': continue
            # Make the correspondence between the name of the field and the
            # name of the corresponding index, excepted if p_advanced is True:
            # in that case, the correspondence will be done later.
            if not advanced:
                indexName = Search.getIndexName(name, klass)
                # Express the field value in the way needed by the index
                criteria[indexName] = Search.getSearchValue(name, value, klass)
            else:
                criteria[name] = value
        # Add a sort order if specified
        if self.sortBy:
            c = criteria
            if not advanced:
                c['sort_on']=Search.getIndexName(self.sortBy,klass,usage='sort')
                c['sort_order']= (self.sortOrder=='desc') and 'reverse' or None
            else:
                c['sortBy'] = self.sortBy
                c['sortOrder'] = self.sortOrder

    def isShowable(self, klass, tool):
        '''Is this Search instance (defined in p_klass) showable ?'''
        if self.show.__class__.__name__ == 'staticmethod':
            return gutils.callMethod(tool, self.show, klass=klass)
        return self.show

    def getSessionKey(self, className, full=True):
        '''Returns the name of the key, in the session, where results for this
           search are stored when relevant. If p_full is False, only the suffix
           of the session key is returned (ie, without the leading
           "search_").'''
        res = (self.name == 'allSearch') and className or self.name
        if not full: return res
        return 'search_%s' % res

    mergeFields = ('sortBy', 'sortOrder', 'showActions')
    def merge(self, other):
        '''Merge parameters from another search in p_other'''
        self.fields.update(other.fields)
        for name in self.mergeFields: setattr(self, name, getattr(other, name))

    def run(self, tool):
        '''Executes this query. Works only when self.klass exists.'''
        if not self.klass:
            raise Exception('Running this query requires self.klass')
        return tool.search(self.klass, sortBy=self.sortBy,
                           sortOrder=self.sortOrder, **self.fields)

# Initiators for searches whose results are shown in popups --------------------
class Initiator:
    '''When a query is rendered in a popup, the "initiator", in the main page,
       can be:
       * (a) some object, in view or edit mode, displaying a given Ref field
             for which the popup is used to select one or more objects to link;
       * (b) some class for which we must create an instance from a template;
             the popup is used to select such a template object.

       This class is the abstract class for 2 concrete initiator classes:
       RefInitiator (for case a) and TemplateInitiator (for case b).
    '''

class RefInitiator(Initiator):
    def __init__(self, obj, field, fieldName, mode):
        # The initiator object
        self.obj = obj
        # The initiator field
        self.field = field
        # As usual, the field name can be different from field.name if it is a
        # sub-field within a List field
        self.fieldName = fieldName
        # The mode can be:
        # - "repl" if the objects selected in the popup will replace already
        #          tied objects;
        # - "add"  if those objects will be added to the already tied ones.
        self.mode = mode
        # "hook" is the ID of the initiator field's XHTML tag
        self.hook = '%s_%s' % (obj.id, fieldName)
        # The root Ajax hook ID in the popup
        self.popupHook = '%s_popup' % self.hook

    def showCheckboxes(self):
        '''We must show object checkboxes if self.field is multivalued: indeed,
           in this case, several objects can be selected in the popup.'''
        return self.field.isMultiValued()

    def jsSelectOne(self, q, cbId):
        '''Generates the Javascript code to execute when a single object is
           selected in the popup.'''
        return 'onSelectObject(%s,%s,%s)' % \
               (q(cbId), q(self.hook), q(self.obj.url))

    def jsSelectMany(self, q, sortKey, sortOrder, filters):
        '''Generates the Javascript code to execute when several objects are
           selected in the popup.'''
        return 'onSelectObjects(%s,%s,%s,%s,%s,%s,%s)' % \
          (q(self.popupHook), q(self.hook), q(self.obj.url), q(self.mode), \
           q(sortKey), q(sortOrder), q(filters))

    def getAjaxParams(self):
        '''Get initiator-specific parameters for retriggering the Ajax
           request for refreshing objects in the popup.'''
        return

class TemplateInitiator(Initiator):
    MANY_ERROR = 'Cannot select several objects from a template initiator.'

    def __init__(self, className, formName, insert, sourceField):
        # The class from which we must create an instance based on a template
        # that we will choose in the popup. Indeed, the instance to create may
        # be from a different class that the instances shown in the popup.
        self.className = className
        # The name of the form that will be submitted for creating the object
        # once a template will have been selected in the popup.
        self.formName = formName
        # The root Ajax hook ID in the popup
        self.popupHook = '%s_popup' % className
        # If the object to create must be inserted at a given place in a Ref
        # field, this can be specified in p_insert.
        self.insert = insert or ''
        # The source field
        self.sourceField = sourceField

    def showCheckboxes(self):
        '''We must hide object checkboxes: only one template object can be
           selected.'''
        return

    def jsSelectOne(self, q, cbId):
        '''Generates the Javascript code to execute when a single object is
           selected in the popup.'''
        return 'onSelectTemplateObject(%s,%s,%s)' % \
               (q(cbId), q(self.formName), q(self.insert))

    def jsSelectMany(self, q, sortKey, sortOrder, filters):
        raise Exception(self.MANY_ERROR)

    def getAjaxParams(self):
        res = {'fromClass': self.className, 'formName': self.formName}
        if self.insert:
            res['insert'] = self.insert
        if self.sourceField:
            res['sourceField'] = self.sourceField
        return res

# ------------------------------------------------------------------------------
class UiSearch:
    '''Instances of this class are generated on-the-fly for manipulating a
       Search instance from the User Interface.'''
    # Tied sub-classes
    Mode = Mode
    Calendar = Calendar
    RefInitiator = RefInitiator
    TemplateInitiator = TemplateInitiator

    # Rendering a search
    pxView = Px('''
     <div class="portletSearch">
      <a href=":'%s?className=%s&amp;search=%s' % \
                 (queryUrl, className, search.name)"
         class=":(search.name == currentSearch) and 'current' or ''"
         onclick="clickOn(this)"
         title=":search.translatedDescr">:search.translated</a>
     </div>''')

    # Render search results
    pxResult = Px('''
     <div var="layoutType='view';
               className=req['className'];
               klass=ztool.getAppyClass(className);
               uiSearch=ztool.getSearch(className, req['search'], ui=True);
               mode=uiSearch.Mode.get(klass, className, uiSearch, inPopup, \
                                      ztool, req, dir);
               batch=mode.batch;
               showNewSearch=showNewSearch|True;
               showHeaders=showHeaders|True"
          id=":mode.ajaxHookId">
      <script>:mode.getAjaxData()</script>

      <x if="not mode.empty">
       <!-- Pod templates -->
       <table var="fields=ztool.getResultPodFields(className)"
              if="not inPopup and mode.objects and fields" align=":dright">
        <tr>
         <td var="zobj=mode.objects[0]; obj=zobj.appy()"
             for="field in fields" var2="fieldName=field.name"
             class=":not loop.field.last and 'pod' or ''">:field.pxRender</td>
        </tr>
       </table>

       <!-- Title -->
       <p if="not inPopup"><x>::uiSearch.translated</x>
        <x if="mode.batch">(<span class="discreet">:mode.batch.total</span>)</x>
        <x if="showNewSearch and mode.newSearchUrl">&nbsp;&mdash;&nbsp;<i>
         <a href=":mode.newSearchUrl">:_('search_new')</a></i></x>
       </p>
       <table width="100%">
        <tr valign="top">
         <!-- Search description -->
         <td if="uiSearch.translatedDescr">
          <span class="discreet">:uiSearch.translatedDescr</span><br/>
         </td>
         <!-- (Top) navigation -->
         <td if="mode.batch"
             align=":dright" width="200px">:mode.batch.pxNavigate</td>
        </tr>
       </table>

       <!-- Results -->
       <x var="currentNumber=0">:mode.px</x>

       <!-- (Bottom) navigation -->
       <x if="mode.batch">:mode.batch.pxNavigate</x>
      </x>

      <!-- No result -->
      <x if="mode.empty">
       <x>:_('query_no_result')</x>
       <x if="showNewSearch and mode.newSearchUrl"><br/><i class="discreet">
         <a href=":mode.newSearchUrl">:_('search_new')</a></i></x>
      </x>
    </div>''')

    def __init__(self, search, className, tool, initiator=None, name=None):
        self.search = search
        # "name" can be more than the p_search name, ie, if the search is
        # defined in a field.
        self.name = name or search.name
        self.type = 'search'
        self.colspan = search.colspan
        self.className = className
        # Property "display" of the div tag containing actions for every search
        # result.
        self.showActions = search.showActions
        if search.showActions == True: self.showActions = 'block'
        if search.translated:
            self.translated = search.translated
            self.translatedDescr = search.translatedDescr or ''
        else:
            # The label may be specific in some special cases
            labelDescr = ''
            if search.name == 'allSearch': label = '%s_plural' % className
            elif search.name == 'customSearch': label = 'search_results'
            elif (not search.name or search.klass): label = None
            else:
                label = '%s_search_%s' % (className, search.name)
                labelDescr = label + '_descr'
            _ = tool.translate
            self.translated = label and _(label) or ''
            self.translatedDescr = labelDescr and _(labelDescr) or ''
        # Strip the description (a single space may be present)
        self.translatedDescr = self.translatedDescr.strip()
        # An initiator instance if the query is in a popup
        self.initiator = initiator
        # When query results are shown in a popup, checkboxes must be present
        # even when not shown. Indeed, we want them in the DOM because object
        # ids are stored on it.
        if initiator:
            self.checkboxes = True
            self.checkboxesDefault = False
        else:
            self.checkboxes = search.checkboxes
            self.checkboxesDefault = search.checkboxesDefault

    def getRootHookId(self):
        '''If there is an initiator, return the hook as defined by it. Else,
           return the name of the search.'''
        if not self.initiator:
            return self.search.name or 'search'
        else:
            return self.initiator.popupHook

    def showCheckboxes(self):
        '''When must checkboxes be shown ?'''
        if not self.initiator: return self.checkboxes
        return self.initiator.showCheckboxes()

    def getCbJsInit(self, hookId):
        '''Returns the code that creates JS data structures for storing the
           status of checkboxes for every result of this search.'''
        default = self.checkboxesDefault and 'unchecked' or 'checked'
        return '''var node=findNode(this, '%s');
                  node['_appy_objs_cbs'] = {};
                  node['_appy_objs_sem'] = '%s';''' % (hookId, default)

    def getModes(self, klass, tool):
        '''Gets all the modes applicable when displaying query results (being
           instances of p_klass) via this search (p_self). r_ is a list of names
           and not a list of Mode instances.'''
        r = self.search.resultModes or \
            getattr(klass, 'resultModes', Mode.default)
        if callable(r): r = r(tool.appy())
        return r
# ------------------------------------------------------------------------------
