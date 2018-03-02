##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: simple.py 4791 2018-03-02 07:45:05Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy

from z3c.template.template import getPageTemplate

SKIP = object()


###############################################################################
#
# simple scroller

SIMPLE_SCROLLER_PAGER = """
<script type="text/javascript">
  var j01SHeight = $("%(expression)s").height();
  $("%(expression)sFirst").click(function() {
    $("%(expression)s").mCustomScrollbar('scrollTo', 'top');
    return false;
  });
  $("%(expression)sPrevious").click(function() {
    var val = '+=' + j01SHeight
    $("%(expression)s").mCustomScrollbar('scrollTo', val);
    return false;
  });
  $("%(expression)sNext").click(function() {
    var val = '-=' + j01SHeight
    $("%(expression)s").mCustomScrollbar('scrollTo', val);
    return false;
  });
  $("%(expression)sLast").click(function() {
    $("%(expression)s").mCustomScrollbar('scrollTo', 'bottom');
    return false;
  });
</script>
"""

def getSimpleScrollerPagerJavaScript(data, template=None):
    """Simple scroller pager"""
    if template is None:
        return ''
    else:
        try:
            scrollerExpression = data.pop('scrollerExpression')
        except KeyError, e:
            scrollerExpression = '#j01Scroller'

        return template % ({
            'expression': scrollerExpression,
            })


# render with document ready. This is the default option and allows to
# include the javascript in the footer. But it can't render pager
# loaded with JSON-RPC
SIMPLE_SCROLLER_TEMPLATE = """
<script type="text/javascript">
  $(document).ready(function(){
    $("%(expression)s").j01SimpleScroller({%(configuration)s
    });
  });
</script>
"""

# render inplace. This option must get used if the page containing the
# pager get loaded with JSON-RPC
SIMPLE_SCROLLER_ADHOC_TEMPLATE = """
<script type="text/javascript">
  $("%(expression)s").j01SimpleScroller({%(configuration)s
  });
</script>
"""

def getScrollerSubSettings(data):
    """Get scroller sub settings"""
    lines = []
    append = lines.append
    for key, value in data.items():
        if value == SKIP:
            continue
        if value is True:
            append("\n            %s: true" % key)
        elif value is False:
            append("\n            %s: false" % key)
        elif value is None:
            append("\n            %s: null" % key)
        elif isinstance(value, int):
            append("\n            %s: %s" % (key, value))
        elif isinstance(value, basestring):
            append("\n            %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    return ','.join(lines)


def getScrollerSettings(data):
    """Scroller generator knows how to generate the javascript options."""
    lines = []
    append = lines.append
    for key, value in data.items():
        if value == SKIP:
            continue
        if key in ['mouseWheel', 'scrollButtons', 'keyboard', 'advanced']:
            if value:
                # skip if empty, use default defined in JS
                sub = getScrollerSubSettings(value)
                append("\n        %s: {%s\n        }" % (key, sub))
        elif key in ['callbacks']:
            if value:
                # apply as javascript function code
                append("\n        %s: %s" % (key, value))
        elif value is True:
            append("\n        %s: true" % key)
        elif value is False:
            append("\n        %s: false" % key)
        elif value is None:
            append("\n        %s: null" % key)
        elif isinstance(value, int):
            append("\n        %s: %s" % (key, value))
        elif isinstance(value, basestring):
            append("\n        %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    return ','.join(lines)


def getSimpleScrollerJavaScript(data, template=SIMPLE_SCROLLER_ADHOC_TEMPLATE):
    """Scroller generator knows how to generate the javascript options."""
    try:
        scrollerExpression = data.pop('scrollerExpression')
    except KeyError, e:
        scrollerExpression = '#j01Scroller'
    lines = []
    append = lines.append
    for key, value in data.items():
        if value == SKIP:
            continue
        elif key == 'settings':
            sub = getScrollerSettings(value)
            append("\n    %s: {%s\n    }" % (key, sub))
        elif key in ['onAfterRender']:
            if value:
                append("\n    %s: %s" % (key, value))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, basestring):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, str(value)))
            else:
                append("\n    %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    configuration = ','.join(lines)
    return template % ({
        'expression': scrollerExpression,
        'configuration': configuration,
        })


class SimpleScroller(object):
    """Simple scroller based on MCustomScrollbar without jsonrpc batching
    but with optional search widget support

    NOTE: this implementation MUST allways return all items no batching support.

    NOTE: Register a j01ScrollerItemsTemplate or implement your own
          j01ScrollerItems property and return the scroller html result

    NOTE: the scrolling element needs to provide a css height or max-heigt
    otherwise the scroller does not work with the mCustomSCrollbar plugin

    """
    j01ScrollerTemplate = getPageTemplate('j01Scroller')

    # internals
    cursor = None
    j01ScrollerTotal = 0
    _j01ScrollerURL = None

    # setup
    j01ScrollerExpression = '#j01Scroller'

    # load content
    j01ScrollerContentViewName = 'index.html'
    j01ScrollerContentMethodName ='j01LoadContent'
    j01ScrollerContentTargetExpression = '#right'

    # javascript template
    j01ScrollerJavaScriptTemplate = SIMPLE_SCROLLER_ADHOC_TEMPLATE
    # optional pager template
    j01ScrollerPagerJavaScriptTemplate = SIMPLE_SCROLLER_PAGER

    # sorting
    j01ScrollerSortName = None
    j01ScrollerSortOrder = None
    j01ScrollerQuery = None

    # mScroller config
    j01ScrollerTheme = 'dark-3'
    j01ScrollerScrollbarPosition = 'inside' # or outside
    j01ScrollerScrollInertia = 100
    j01ScrollerAlwaysShowScrollbar = 0
    j01ScrollerAutoHideScrollbar = SKIP
    j01ScrollerAutoExpandScrollbar = SKIP
    j01ScrollerSnapAmount = SKIP
    j01ScrollerSnapOffset = SKIP

    # mScroller sub config
    j01ScrollerMouseWheels = {'enable': True, 'preventDefault': True}
    j01ScrollerScrollButtons = {'enable': True}
    j01ScrollerEvents = SKIP
    j01ScrollerKeyboards = SKIP
    j01ScrollerAdvanceds = SKIP
    j01ScrollerCallbacks = SKIP

    # search config
    j01ScrollerSearchResultExpression = '#j01ScrollerResult'
    j01ScrollerSearchWidgetExpression = '#form-widgets-search'
    j01ScrollerSearchMethodName = 'getJ01SimpleScrollerResult'
    j01ScrollerSearchOnAfterRender = None
    j01ScrollerSearchMinQueryLenght = 2
    j01ScrollerSearchMaxReSearch = 0

    # shared context support
    @property
    def j01ScrollerContext(self):
        """Returns the (container) context for setup items"""
        return self.context

    @property
    def j01ScrollerURL(self):
        if self._j01ScrollerURL is None:
            self._j01ScrollerURL = absoluteURL(self.j01ScrollerContext,
                self.request)
        return self._j01ScrollerURL

    @property
    def j01ScrollerContentURL(self):
        return self.j01ScrollerURL

    @property
    def j01ScrollerSearchURL(self):
        return self.j01ScrollerURL

    # scroller data
    def getScrollerCursor(self, sortName=None, sortOrder=None,
        searchText=None, fields=None, skipFilter=False):
        """This method must return an iterator including a count method

        Note: your method should use the sort name, sort order and search text
        if required.
        """
        # NOTE, allways make sure that the user can't use undefined
        # sortName, sortOrder. Your cursor custom getScrollerCursor method
        # must implement such a constraint !!!
        return self.j01ScrollerContext.getScrollerCursor(sortName, sortOrder,
            searchText, fields, skipFilter)

    @property
    def j01ScrollerArguments(self):
        """Get new or default page batch data method arguments"""
        sortName = self.request.get('n', self.j01ScrollerSortName)
        sortOrder = self.request.get('o', self.j01ScrollerSortOrder)
        searchString = self.request.get('s', self.j01ScrollerSearchString)
        # sortOrder
        if sortOrder == '1':
            sortOrder = 1
        else:
            sortOrder = -1
        return sortName, sortOrder, searchString

    def setUpJ01Scroller(self, sortName, sortOrder, searchString):
        """This method must set the cursor and j01ScrollerTotal counter"""
        cursor = self.getScrollerCursor(sortName, sortOrder, searchString)
        self.cursor = removeSecurityProxy(cursor)
        self.j01ScrollerTotal = self.cursor.count()

    @property
    def j01ScrollerValues(self):
        """Return the cached scroller values"""
        return self.cursor

    # scroller
    @property
    def j01Scroller(self):
        """Return scroller content (by default based on template)

        Note: we setup the j01Scroller content not during update the page,
        we just do it right before we use them during the render call. This
        allows us to manipulate all relevant scroller attributes during form
        processing or anything else happens during update call. Feel free to
        setup the scroller data earlier in your implementation. As you can see,
        by default, if the cursor is not None, we will skip the scroller data
        setup.
        """
        if self.cursor is None:
            # setup scroller cursor and total
            self.j01ScrollerSortName, self.j01ScrollerSortOrder, \
                self.j01ScrollerSearchString = self.j01ScrollerArguments
            self.setUpJ01Scroller(self.j01ScrollerSortName,
                self.j01ScrollerSortOrder, self.j01ScrollerSearchString)
        return self.j01ScrollerTemplate()

    @property
    def j01ScrollerItems(self):
        """Return scroller items

        By default we only use a template which is rendering the items.
        """
        return self.j01ScrollerItemsTemplate()

    @property
    def showJ01Scroller(self):
        return self.j01ScrollerTotal > 0 or \
            self.j01ScrollerSearchWidgetExpression is not None

    @property
    def showJ01ScrollerPager(self):
        return self.showJ01Scroller and \
            self.j01ScrollerPagerJavaScriptTemplate is not None

    # javascript
    @property
    def j01ScrollerPagerConfiguration(self):
        return {
            # setup
            'scrollerExpression': self.j01ScrollerExpression,
            }

    @property
    def j01ScrollerSettings(self):
        settings = {
            # config
            'theme': self.j01ScrollerTheme,
            'scrollbarPosition': self.j01ScrollerScrollbarPosition,
            'scrollInertia': self.j01ScrollerScrollInertia,
            'alwaysShowScrollbar': self.j01ScrollerAlwaysShowScrollbar,
            'autoHideScrollbar': self.j01ScrollerAutoHideScrollbar,
            'autoExpandScrollbar': self.j01ScrollerAutoExpandScrollbar,
            'snapAmount': self.j01ScrollerSnapAmount,
            'snapOffset': self.j01ScrollerSnapOffset,
            }
        # sub config
        if self.j01ScrollerMouseWheels:
            settings['mouseWheel'] = self.j01ScrollerMouseWheels
        if self.j01ScrollerScrollButtons:
            settings['scrollButtons'] = self.j01ScrollerScrollButtons
        if self.j01ScrollerEvents:
            settings['events'] = self.j01ScrollerEvents
        if self.j01ScrollerKeyboards:
            settings['keyboard'] = self.j01ScrollerKeyboards
        if self.j01ScrollerAdvanceds:
            settings['advanced'] = self.j01ScrollerAdvanceds
        if self.j01ScrollerCallbacks:
            settings['callbacks'] = self.j01ScrollerCallbacks
        return settings

    @property
    def j01ScrollerConfiguration(self):
        conf = {
            # load content
            'loadContentURL': self.j01ScrollerContentURL,
            'loadContentViewName': self.j01ScrollerContentViewName,
            'loadContentMethodName': self.j01ScrollerContentMethodName,
            'loadContentTargetExpression': self.j01ScrollerContentTargetExpression,
            # search
            'searchURL': self.j01ScrollerSearchURL,
            'searchMethodName': self.j01ScrollerSearchMethodName,
            'searchResultExpression': self.j01ScrollerSearchResultExpression,
            'searchWidgetExpression': self.j01ScrollerSearchWidgetExpression,
            'sortName': self.j01ScrollerSortName,
            'sortOrder': self.j01ScrollerSortOrder,
            'minQueryLenght': self.j01ScrollerSearchMinQueryLenght,
            'maxReSearch': self.j01ScrollerSearchMaxReSearch,
            'onAfterRender': self.j01ScrollerSearchOnAfterRender,
        }
        settings = self.j01ScrollerSettings
        if settings is not None:
            conf['settings'] = settings
        return conf

    @property
    def j01SimpleScrollerPagerJavaScript(self):
        """Returns the optional pager javascript code or an empty string"""
        if self.showJ01ScrollerPager:
            return getSimpleScrollerPagerJavaScript(
                self.j01ScrollerPagerConfiguration,
                self.j01ScrollerPagerJavaScriptTemplate)
        else:
            return ''

    @property
    def j01SimpleScrollerJavaScript(self):
        """Returns the scroller javascript code or an empty string"""
        if self.showJ01Scroller:
            return getSimpleScrollerJavaScript(self.j01ScrollerConfiguration,
                self.j01ScrollerJavaScriptTemplate)
        else:
            return ''

    @property
    def j01ScrollerJavaScript(self):
        """Returns the scroller and apger javascript code or an empty string"""
        return self.j01SimpleScrollerJavaScript + \
            self.j01SimpleScrollerPagerJavaScript

    def j01ScrollerUpdate(self):
        """Update additional scroller page and jsonrpc data

        This is the only shared method which get called based on a browser and
        jsonrpc request. This means you should use this method if you need to
        setup properties which you normaly whould do in a BrowserPage update
        method.

        """
        pass

    def update(self):
        self.j01ScrollerUpdate()
        super(SimpleScroller, self).update()
