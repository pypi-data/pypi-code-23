# ------------------------------------------------------------------------------
from appy.px import Px

# Input field for going to element number x. This PX is common to classes
# Siblings and Batch defined hereafter.
pxGotoNumber = Px('''
 <x var2="label=_('goto_number');
          gotoName='%s_%s_goto' % (obj.id, field.name);
          popup=inPopup and '1' or '0'">
  <span class="discreet" style="padding-left: 5px">:label</span>
  <input type="text" size=":len(str(total)) or 1" onclick="this.select()"
         onkeydown=":'if (event.keyCode==13) document.getElementById' \
                     '(%s).click()' % q(gotoName)"/><img
         id=":gotoName" name=":gotoName"
         class="clickable" src=":url('gotoNumber')" title=":label"
         onclick=":'gotoTied(%s,%s,this.previousSibling,%s,%s)' % \
             (q(sourceUrl), q(field.name), total, q(popup))"/></x>''')

# ------------------------------------------------------------------------------
class Siblings:
    '''Abstract class containing information for navigating from one object to
       its siblings.'''
    siblingTypes = ('previous', 'next', 'first', 'last')

    # Buttons for going to siblings of the current object
    pxGotoNumber = pxGotoNumber
    pxNavigate = Px('''
      <!-- Go to the source URL (search or referred object) -->
      <a if="not inPopup" href=":self.sourceUrl"><img
         var="goBack='%s - %s' % (self.getBackText(), _('goto_source'))"
         src=":url('gotoSource')" title=":goBack"/></a>

      <!-- Go to the first or previous page -->
      <a if="self.firstUrl" href=":self.firstUrl"><img title=":_('goto_first')"
         src=":url('arrowsLeft')"/></a><a
         if="self.previousUrl" href=":self.previousUrl"><img
         title=":_('goto_previous')" src=":url('arrowLeft')"/></a>

      <!-- Explain which element is currently shown -->
      <span class="discreet"> 
       <x>:self.number</x> <b>//</b> 
       <x>:self.total</x> </span>

      <!-- Go to the next or last page -->
      <a if="self.nextUrl" href=":self.nextUrl"><img title=":_('goto_next')"
         src=":url('arrowRight')"/></a><a
         if="self.lastUrl" href=":self.lastUrl"><img title=":_('goto_last')"
         src=":url('arrowsRight')"/></a>

      <!-- Go to the element number... -->
      <x if="self.showGotoNumber()"
         var2="field=self.field; sourceUrl=self.sourceObject.absolute_url();
               total=self.total"><br/><x>:self.pxGotoNumber</x></x>''')

    @staticmethod
    def get(nav, tool, inPopup):
        '''This method analyses the navigation info p_nav and returns the
           corresponding concrete Siblings instance.'''
        elems = nav.split('.')
        params = elems[1:]
        if elems[0] == 'ref': return RefSiblings(tool, inPopup, *params)
        elif elems[0] == 'search': return SearchSiblings(tool, inPopup, *params)

    def computeStartNumber(self):
        '''Returns the start number of the batch where the current element
           lies.'''
        # First index starts at O, so we calibrate self.number
        number = self.number - 1
        batchSize = self.getBatchSize()
        res = 0
        while (res < self.total):
            if (number < res + batchSize): return res
            res += batchSize
        return res

    def __init__(self, tool, inPopup, number, total):
        self.tool = tool
        self.request = tool.REQUEST
        # Are we in a popup window or not?
        self.inPopup = inPopup
        # The number of the current element
        self.number = int(number)
        # The total number of siblings
        self.total = int(total)
        # Do I need to navigate to first, previous, next and/or last sibling ?
        self.previousNeeded = False # Previous ?
        self.previousIndex = self.number - 2
        if (self.previousIndex > -1) and (self.total > self.previousIndex):
            self.previousNeeded = True
        self.nextNeeded = False     # Next ?
        self.nextIndex = self.number
        if self.nextIndex < self.total: self.nextNeeded = True
        self.firstNeeded = False    # First ?
        self.firstIndex = 0
        if self.previousIndex > 0: self.firstNeeded = True
        self.lastNeeded = False     # Last ?
        self.lastIndex = self.total - 1
        if (self.nextIndex < self.lastIndex): self.lastNeeded = True
        # Compute the UIDs of the siblings of the current object
        self.siblings = self.getSiblings()
        # Compute back URL and URLs to siblings
        self.sourceUrl = self.getSourceUrl()
        siblingNav = self.getNavKey()
        siblingPage = self.request.get('page', 'main')
        for urlType in self.siblingTypes:
            exec 'needIt = self.%sNeeded' % urlType
            urlKey = '%sUrl' % urlType
            setattr(self, urlKey, None)
            if not needIt: continue
            exec 'index = self.%sIndex' % urlType
            uid = None
            try:
                # self.siblings can be a list (ref) or a dict (search)
                uid = self.siblings[index]
            except KeyError: continue
            except IndexError: continue
            if not uid: continue
            sibling = self.tool.getObject(uid)
            if not sibling: continue
            setattr(self, urlKey, sibling.getUrl(nav=siblingNav % (index + 1),
                                             page=siblingPage, inPopup=inPopup))

# ------------------------------------------------------------------------------
class RefSiblings(Siblings):
    '''Class containing information for navigating from one object to another
       within tied objects from a Ref field.'''
    prefix = 'ref'

    def __init__(self, tool, inPopup, sourceUid, fieldName, number, total):
        # The source object of the Ref field
        self.sourceObject = tool.getObject(sourceUid)
        # The Ref field in itself
        self.field = self.sourceObject.getAppyType(fieldName)
        # Call the base constructor
        Siblings.__init__(self, tool, inPopup, number, total)

    def getNavKey(self):
        '''Returns the general navigation key for navigating to another
           sibling.'''
        return self.field.getNavInfo(self.sourceObject, None, self.total)

    def getBackText(self):
        '''Computes the text to display when the user want to navigate back to
           the list of tied objects.'''
        _ = self.tool.translate
        return '%s - %s' % (self.sourceObject.Title(), _(self.field.labelId))

    def getBatchSize(self):
        '''Returns the maximum number of shown objects at a time for this
           ref.'''
        return self.field.maxPerPage

    def getSiblings(self):
        '''Returns the siblings of the current object.'''
        return getattr(self.sourceObject, self.field.name, ())

    def getSourceUrl(self):
        '''Computes the URL allowing to go back to self.sourceObject's page
           where self.field lies and shows the list of tied objects, at the
           batch where the current object lies.'''
        # Allow to go back to the batch where the current object lies
        field = self.field
        startNumberKey = '%s_%s_objs_startNumber' % \
                         (self.sourceObject.id,field.name)
        startNumber = str(self.computeStartNumber())
        return self.sourceObject.getUrl(**{startNumberKey:startNumber,
                                           'page':field.pageName, 'nav':'no'})

    def showGotoNumber(self):
        '''Show "goto number" if the Ref field is numbered.'''
        return self.field.isNumbered(self.sourceObject)

# ------------------------------------------------------------------------------
class SearchSiblings(Siblings):
    '''Class containing information for navigating from one object to another
       within results of a search.'''
    prefix = 'search'

    def __init__(self, tool, inPopup, className, searchName, number, total):
        # The class determining the type of searched objects
        self.className = className
        # Get the search object
        self.searchName = searchName
        self.uiSearch = tool.getSearch(className, searchName, ui=True)
        self.search = self.uiSearch.search
        Siblings.__init__(self, tool, inPopup, number, total)

    def getNavKey(self):
        '''Returns the general navigation key for navigating to another
           sibling.'''
        return 'search.%s.%s.%%d.%d' % (self.className, self.searchName,
                                        self.total)

    def getBackText(self):
        '''Computes the text to display when the user want to navigate back to
           the list of searched objects.'''
        return self.uiSearch.translated

    def getBatchSize(self):
        '''Returns the maximum number of shown objects at a time for this
           search.'''
        return self.search.maxPerPage

    def getSiblings(self):
        '''Returns the siblings of the current object. For performance reasons,
           only a part of the is stored, in the session object.'''
        session = self.request.SESSION
        searchKey = self.search.getSessionKey(self.className)
        if session.has_key(searchKey): res = session[searchKey]
        else: res = {}
        if (self.previousNeeded and not res.has_key(self.previousIndex)) or \
           (self.nextNeeded and not res.has_key(self.nextIndex)):
            # The needed sibling UID is not in session. We will need to
            # retrigger the query by querying all objects surrounding this one.
            newStartNumber = (self.number-1) - (self.search.maxPerPage / 2)
            if newStartNumber < 0: newStartNumber = 0
            self.tool.executeQuery(self.className, search=self.search,
                                   startNumber=newStartNumber, remember=True)
            res = session[searchKey]
        # For the moment, for first and last, we get them only if we have them
        # in session.
        if not res.has_key(0): self.firstNeeded = False
        if not res.has_key(self.lastIndex): self.lastNeeded = False
        return res

    def getSourceUrl(self):
        '''Computes the (non-Ajax) URL allowing to go back to the search
           results, at the batch where the current object lies, or to the
           originating field if the search was triggered from a field.'''
        if ',' in self.searchName:
            # Go back to the originating field
            id, name, mode = self.searchName.split(',')
            obj = self.tool.getObject(id, appy=True)
            field = obj.getField(name)
            return '%s?page=%s' % (obj.url, field.page.name)
        else:
            params = 'className=%s&search=%s&startNumber=%d' % \
                    (self.className, self.searchName, self.computeStartNumber())
            ref = self.request.get('ref', None)
            if ref: params += '&ref=%s' % ref
            return '%s/query?%s' % (self.tool.absolute_url(), params)

    def showGotoNumber(self): return

# ------------------------------------------------------------------------------
class Batch:
    '''Class for navigating between parts (=batches) within lists of objects'''
    def __init__(self, hook, total, length, size=30, start=0):
        # The ID of the DOM node containing the list of objects
        self.hook = hook
        # The total number of objects
        self.total = total
        # The effective number of objects in the current batch
        self.length = length
        # The maximum number of objects shown at once (in the batch). If p_size
        # is None, all objects are shown.
        self.size = size
        # The index of the first object in the current batch
        self.start = start

    def update(self, **kwargs):
        '''Update p_self's attributes with values from p_kwargs'''
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    def __repr__(self):
        return '<Batch hook=%s,start=%s,length=%s,size=%s,total=%s>' % \
               (self.hook, self.start, self.length, self.size, self.total) 

    # Icons for navigating among a list of objects: next, back, first, last...
    pxGotoNumber = pxGotoNumber
    pxNavigate = Px('''
     <div if="batch.total &gt; batch.size" align=":dright"
          var2="hook=q(batch.hook); size=q(batch.size)">

      <!-- Go to the first page -->
      <img if="(batch.start != 0) and (batch.start != batch.size)"
           class="clickable" src=":url('arrowsLeft')" title=":_('goto_first')"
           onclick=":'askBunch(%s,%s,%s)'% (hook, q(0), size)"/>

      <!-- Go to the previous page -->
      <img var="sNumber=batch.start - batch.size" if="batch.start != 0"
           class="clickable" src=":url('arrowLeft')" title=":_('goto_previous')"
           onclick=":'askBunch(%s,%s,%s)' % (hook, q(sNumber), size)"/>

      <!-- Explain which elements are currently shown -->
      <span class="discreet"> 
       <x>:batch.start + 1</x> <img src=":url('to')"/> 
       <x>:batch.start + batch.length</x> <b>//</b> <x>:batch.total</x>
      </span>

      <!-- Go to the next page -->
      <img var="sNumber=batch.start + batch.size" if="sNumber &lt; batch.total"
           class="clickable" src=":url('arrowRight')" title=":_('goto_next')"
           onclick=":'askBunch(%s,%s,%s)' % (hook, q(sNumber), size)"/>

      <!-- Go to the last page -->
      <img var="lastPageIsIncomplete=batch.total % batch.size;
                nbOfCompletePages=batch.total / batch.size;
                nbOfCountedPages=lastPageIsIncomplete and \
                                 nbOfCompletePages or nbOfCompletePages-1;
                sNumber= nbOfCountedPages * batch.size"
           if="(batch.start != sNumber) and \
               (batch.start != (sNumber-batch.size))" class="clickable"
           src=":url('arrowsRight')" title=":_('goto_last')"
           onclick=":'askBunch(%s,%s,%s)' % (hook, q(sNumber), size)"/>

      <!-- Go to the element number... -->
      <x var="gotoNumber=gotoNumber|False" if="gotoNumber"
         var2="sourceUrl=obj.url; total=batch.total">:batch.pxGotoNumber</x>
     </div>''')
# ------------------------------------------------------------------------------
