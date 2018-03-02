##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: custom.py 4694 2017-12-27 03:43:47Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy

from z3c.template.template import getPageTemplate

SKIP = object()


###############################################################################
#
# simple scroller

j01_simple_scroller_template = """
<script type="text/javascript">
  $(document).ready(function(){
    $("%(expression)s").mCustomScrollbar({%(settings)s
    });
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
  });
</script>
"""

j01_simple_scroller_adhoc_template = """
<script type="text/javascript">
  $("%(expression)s").mCustomScrollbar({%(settings)s
  });
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


def getSubConfig(data):
    """Get sub config"""
    lines = []
    append = lines.append
    for key, value in data.items():
        if value == SKIP:
            continue
        if key in ['callbacks']:
            if not value:
                # skip if empty, use default defined in JS
                pass
            else:
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


def getSimpleScrollerJavaScript(data, ready=True, template=None):
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
        if key in ['mouseWheel', 'scrollButtons', 'keyboard', 'advanced']:
            if not value:
                # skip if empty, use default defined in JS
                pass
            else:
                sub = getSubConfig(value)
                append("\n    %s: {%s\n    }" % (key, sub))
        elif key in ['callbacks']:
            # apply as javascript function code
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
            append("\n    %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    settings = ','.join(lines)

    if template is None and ready:
        # render with document ready. This is the default option and allows to
        # include the javascript in the footer. But it can't render pager
        # loaded with JSON-RPC
        template = j01_simple_scroller_template
    elif template is None:
        # render inplace. This option must get used if the page containing the
        # pager get loaded with JSON-RPC
        template = j01_simple_scroller_adhoc_template

    return template % ({
        'expression': scrollerExpression,
        'settings': settings,
        })


class MCustomScrollbar(object):
    """Scroller based on MCustomScrollbar without batching

    NOTE: this implementation MUST allways return all items.

    NOTE: No item will get reloaded, see SimpleScroller in simply.py for live
    search support

    NOTE: the scrolling element needs to provide a css height or max-heigt
    otherwise the scroller does not work with the mCustomSCrollbar plugin

    """
    j01ScrollerTemplate = getPageTemplate('j01Scroller')

    # internals
    cursor = None
    j01ScrollerTotal = 0
    _j01ScrollerURL = None

    # setup
    j01ScrollerDocumentReady = True
    j01ScrollerExpression = '#j01Scroller'
    # javascript template
    j01ScrollerJavaScriptTemplate = None

    # sorting
    j01ScrollerSortName = None
    j01ScrollerSortOrder = -1

    # search query support
    j01ScrollerQuery = None

    # search support
    j01ScrollerSearchWidgetExpression = None

    # config
    j01ScrollerTheme = 'dark-3'
    j01ScrollerScrollbarPosition = 'inside' # or outside
    j01ScrollerScrollInertia = 100
    j01ScrollerAlwaysVisible = True
    j01ScrollerAlwaysShowScrollbar = 0
    j01ScrollerAutoHideScrollbar = SKIP
    j01ScrollerAutoExpandScrollbar = SKIP
    j01ScrollerSnapAmount = SKIP
    j01ScrollerSnapOffset = SKIP

    # sub config
    j01ScrollerMouseWheels = {'enable': True, 'preventDefault': True}
    j01ScrollerScrollButtons = {'enable': True}
    j01ScrollerKeyboards = SKIP
    j01ScrollerAdvanceds = SKIP
    j01ScrollerCallbacks = SKIP

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
    def showJ01Scroller(self):
        return self.j01ScrollerTotal > 0

    # javascript
    @property
    def j01ScrollerConfiguration(self):
        conf = {
            # setup
            'scrollerExpression': self.j01ScrollerExpression,
            # config
            'theme': self.j01ScrollerTheme,
            'scrollbarPosition': self.j01ScrollerScrollbarPosition,
            'scrollInertia': self.j01ScrollerScrollInertia,
            'alwaysVisible': self.j01ScrollerAlwaysVisible,
            'alwaysShowScrollbar': self.j01ScrollerAlwaysShowScrollbar,
            'autoHideScrollbar': self.j01ScrollerAutoHideScrollbar,
            'autoExpandScrollbar': self.j01ScrollerAutoExpandScrollbar,
            'snapAmount': self.j01ScrollerSnapAmount,
            'snapOffset': self.j01ScrollerSnapOffset,
            }
        # sub config
        if self.j01ScrollerMouseWheels:
            conf['mouseWheel'] = self.j01ScrollerMouseWheels
        if self.j01ScrollerScrollButtons:
            conf['scrollButtons'] = self.j01ScrollerScrollButtons
        if self.j01ScrollerKeyboards:
            conf['keyboard'] = self.j01ScrollerKeyboards
        if self.j01ScrollerAdvanceds:
            conf['advanced'] = self.j01ScrollerAdvanceds
        if self.j01ScrollerCallbacks:
            conf['callbacks'] = self.j01ScrollerCallbacks
        return conf

    @property
    def j01ScrollerJavaScript(self):
        if self.showJ01Scroller or self.j01ScrollerSearchWidgetExpression:
            return getSimpleScrollerJavaScript(self.j01ScrollerConfiguration,
                self.j01ScrollerDocumentReady,
                self.j01ScrollerJavaScriptTemplate)
        else:
            return u''
