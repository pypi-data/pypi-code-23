# -*- coding: utf-8 -*-


from wx.stc import *

from beatle.lib.handlers import EditorHandlerBase
from beatle.app import resources as rc

MARGIN_LINE_NUMBERS = 0
MARK_MARGIN = 1
MARGIN_FOLD = 2

STC_MASK_MARKERS = ~STC_MASK_FOLDERS

MARK_BOOKMARK = 0
MARK_BREAKPOINT = 1
DEBUG_CURRENT = 32

#missing indicators
STC_INDIC_FULLBOX = 16

#undefined wrappers
SCI_ANNOTATIONSETTEXT = 2540
SCI_ANNOTATIONGETTEXT = 2541
SCI_ANNOTATIONSETSTYLE = 2542
SCI_ANNOTATIONGETSTYLE = 2543
SCI_ANNOTATIONSETSTYLES = 2544
SCI_ANNOTATIONGETSTYLES = 2545
SCI_ANNOTATIONGETLINES = 2546
SCI_ANNOTATIONCLEARALL = 2547
ANNOTATION_HIDDEN = 0
ANNOTATION_STANDARD = 1
ANNOTATION_BOXED = 2
SCI_ANNOTATIONSETVISIBLE = 2548
SCI_ANNOTATIONGETVISIBLE = 2549
SCI_ANNOTATIONSETSTYLEOFFSET = 2550
SCI_ANNOTATIONGETSTYLEOFFSET = 2551

SCI_STYLESETCHANGEABLE = 2099
STC_FIND_MATCHCASE = 4
STC_FIND_POSIX = 4194304
STC_FIND_REGEXP = 2097152
STC_FIND_WHOLEWORD = 2
STC_FIND_WORDSTART = 1048576


BOOKMARK_TOGGLE  = 30000
BOOKMARK_UP      = 30001
BOOKMARK_DOWN    = 30002
BREAKPOINT_TOGGLE= 30003
FIND = 30004
FIND_NEXT = 30005
FIND_PREV = 30006

import keyword


class EditorHandler(EditorHandlerBase):
    """Declares SQL editor handler"""

    keyword_list = keyword.kwlist
    keyword_list2 = []

    style_items = [
        (STC_P_DEFAULT, 'default'),
        (MARGIN_FOLD, "fold margin"),
    ]

    style = {
        'default': "fore:#000000, back:#FFFFFF",
        "fold margin": "back:#CBCBCB",
    }

    def __init__(self, **kwargs):
        """Init"""
        self._fileObj = kwargs['obj']
        kwargs['lexer'] = STC_LEX_NULL
        kwargs['text'] = self._fileObj.GetText()
        kwargs['read_only'] = self._fileObj._readOnly
        super(EditorHandler, self).__init__(**kwargs)

    def SetupMargins(self, editor):
        """Setup margins"""
        #Enable code folding
        editor.SetMarginType(MARK_MARGIN, STC_MARGIN_SYMBOL)
        editor.SetMarginType(MARGIN_LINE_NUMBERS, STC_MARGIN_NUMBER)
        editor.SetMarginWidth(MARK_MARGIN, 11)
        editor.SetMarginMask(MARK_MARGIN, STC_MASK_MARKERS)
        editor.SetMarginSensitive(MARK_MARGIN, True)
        editor.SetMarginWidth(MARGIN_LINE_NUMBERS, 50)
        editor.SetMarginSensitive(MARGIN_LINE_NUMBERS, True)

    def SetupMarkers(self, editor):
        """Setup markers"""
        editor.MarkerDefineBitmap(MARK_BOOKMARK, wx.BitmapFromXPMData(rc._bookmark))

    def SetProperties(self, editor):
        """Set other properties"""
        # Properties found from http://www.scintilla.org/SciTEDoc.html
        editor.SetProperty("tabsize", "4")
        editor.SetProperty("use.tabs", "1")
        editor.SetUseTabs(True)
        editor.SetTabWidth(4)
        editor.SetWrapMode(True)

    def SetupEvents(self, editor):
        """Set event handling"""
        editor.CmdKeyAssign(ord('+'), STC_SCMOD_CTRL, STC_CMD_ZOOMIN)
        editor.CmdKeyAssign(ord('-'), STC_SCMOD_CTRL, STC_CMD_ZOOMOUT)
        editor.Bind(wx.EVT_MENU, editor.ToggleBookmark, id=BOOKMARK_TOGGLE)
        editor.Bind(wx.EVT_MENU, editor.PrevBookmark, id=BOOKMARK_UP)
        editor.Bind(wx.EVT_MENU, editor.NextBookmark, id=BOOKMARK_DOWN)
        editor.Bind(wx.EVT_MENU, editor.Find, id=FIND)
        editor.Bind(wx.EVT_MENU, editor.FindNext, id=FIND_NEXT)
        editor.Bind(wx.EVT_MENU, editor.FindPrevious, id=FIND_PREV)
        editor.Bind(EVT_STC_MARGINCLICK, editor.OnMarginClick)
        editor.Bind(wx.EVT_KEY_UP, editor.OnKey)
        editor.Bind(EVT_STC_UPDATEUI, editor.OnUpdateEditUI)

        aTable = wx.AcceleratorTable([
            #wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F9, BREAKPOINT_TOGGLE), <- mus be handled by the view
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F2, BOOKMARK_TOGGLE),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_UP, BOOKMARK_UP),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_DOWN, BOOKMARK_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('F'), FIND),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F3, FIND_NEXT),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_F3, FIND_PREV),
        ])
        editor.SetAcceleratorTable(aTable)

    def Initialize(self, editor):
        """Base initialization"""
        editor.StyleClearAll()
        editor.SetLexer(self.lexer)
        editor.SetCodePage(STC_CP_UTF8)
        editor.SetStyleBits(editor.GetStyleBitsNeeded())
        self.init_fonts(editor)
        editor.HandleBookmarks(self._fileObj.bookmarks)
        editor.EnableBreakpoints(False)
        editor.EnableBookmarks(True)

        # this feature is really ugly! (80 columns gray marker)
        #
        self.SetProperties(editor)
        self.SetupEvents(editor)

        super(EditorHandler, self).Initialize(editor)
