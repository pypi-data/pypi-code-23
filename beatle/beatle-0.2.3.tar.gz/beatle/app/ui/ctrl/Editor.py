# -*- coding: utf-8 -*-
# by mel

# Custom editor wrapper for C++/python of wx.Scintilla control
import re

import wx
import wx.stc as stc

from beatle.ctx import THE_CONTEXT as context

MARGIN_LINE_NUMBERS = 0
MARK_MARGIN = 1
MARGIN_FOLD = 2

stc.STC_MASK_MARKERS = ~stc.STC_MASK_FOLDERS

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


class Editor(stc.StyledTextCtrl):
    """Common editor class"""
    # deprecated: to remove
    lex = {
        'text': stc.STC_LEX_NULL,
        'c++': stc.STC_LEX_CPP,
        'python': stc.STC_LEX_PYTHON,
        'sql': stc.STC_LEX_SQL,
        'bash': stc.STC_LEX_BASH,
        'css': stc.STC_LEX_CSS,
        'html': stc.STC_LEX_HTML,
        'mathlab': stc.STC_LEX_MATLAB,
        'octave': stc.STC_LEX_OCTAVE,
        'xml': stc.STC_LEX_XML,
        'apache': stc.STC_LEX_CONF,
        'make': stc.STC_LEX_MAKEFILE,
        'nasm': stc.STC_LEX_ASM,
        'vhdl': stc.STC_LEX_VHDL
        }

    def __init__(self, parent, id=wx.ID_ANY, **kwargs):
        """Initialize control"""
        style = kwargs.get('style', wx.HSCROLL | wx.VSCROLL)
        super(Editor, self).__init__(parent, id, wx.DefaultPosition,
            wx.DefaultSize,style)
        if not style & wx.HSCROLL:
            self.SetUseHorizontalScrollBar(False)
        if not style & wx.VSCROLL:
            self.SetUseVerticalScrollBar(False)
        self._auto = kwargs.get('auto', '')
        self.search_text = ''
        self._bookmarks = kwargs.get('bookmarks', {})
        self._breakpoints = kwargs.get('breakpoints', {})
        self._enable_breakpoints = False
        self._enable_bookmarks = False
        self.popup_handler = None
        self.parent = parent
        self.handler = kwargs.get('handler', None)
        if self.handler:
            # New version, handler carry specialized setup
            self.handler.Initialize(self)

    def EnableBreakpoints(self, enable=True):
        """Control if breakpoints are enabled"""
        if self._enable_breakpoints:
            if not enable:
                for br in self._breakpoints:
                    self.MarkerDelete(br, MARK_BREAKPOINT)
        else:
            if enable:
                for br in self._breakpoints:
                    self.MarkerAdd(br, MARK_BREAKPOINT)
        self._enable_breakpoints = enable

    def EnableBookmarks(self, enable=True):
        """Control if bookmarks are enabled"""
        if self._enable_bookmarks:
            if not enable:
                for br in self._bookmarks:
                    self.MarkerDelete(br, MARK_BOOKMARK)
        else:
            if enable:
                for br in self._bookmarks:
                    self.MarkerAdd(br, MARK_BOOKMARK)
        self._enable_bookmarks = enable

    def HandleBreakpoints(self, breakpoints):
        """This method can be only used while the breakpoints
        are disabled and is used for replacing the breakpoint dictionnary
        whith the project dictionnary."""
        assert not self._enable_breakpoints
        self._breakpoints = breakpoints

    def HandleBookmarks(self, bookmarks):
        """This method can be only used while the bookmarks
        are disabled and is used for replacing the bookmarks dictionnary
        whith the project dictionnary."""
        assert not self._enable_bookmarks
        self._bookmarks = bookmarks

    def SetBreakpoints(self, breakpoints):
        """Set the breakpoints"""
        if self._enable_breakpoints:
            remove = [br for br in self._breakpoints if br not in breakpoints]
            add = [br for br in breakpoints if br not in self._breakpoints]
            for br in remove:
                self.MarkerDelete(br, MARK_BREAKPOINT)
            for br in add:
                self.MarkerAdd(br, MARK_BREAKPOINT)
        self._breakpoints = breakpoints

    def GetLineStartPosition(self, line):
        """Get the starting position of the given line
        @param line: int
        @return: int
        """
        if line > 0:
            spos = self.GetLineEndPosition(line - 1)
            if self.GetLine(line).endswith("\r\n"):
                spos += 2
            else:
                spos += 1
        else:
            spos = 0
        return spos

    def GotoLine(self, line, select=False):
        """Called for goto to line"""
        super(Editor, self).GotoLine(line)
        if select:
            pos = self.GetLineEndPosition(line)
            if line > 0:
                start = self.GetLineEndPosition(line - 1) + 1
            else:
                start = 0
            self.SetSelectionStart(start)
            self.SetSelectionEnd(pos)

    def Select(self, sline, scol, eline, ecol):
        """Select a range"""
        super(Editor, self).GotoLine(sline)
        start = self.GetLineStartPosition(sline) + scol
        end = self.GetLineStartPosition(eline) + ecol
        self.SetSelectionStart(start)
        self.SetSelectionEnd(end)

    def IsModified(self):
        """Emulate unmodifiable flag using undo stack"""
        return self.CanUndo()

    def ResetModified(self):
        """Emulate unmodifiable flag using undo stack"""
        #p = self.GetCurrentPos()
        #self.SetSavePoint()
        #self.GotoPos(p)
        self.EmptyUndoBuffer()

    def Initialize(self, types=[]):
        """Initialize editor"""
        # a sample list of keywords,
        if self.handler:
            self.SetKeyWords(0, self.handler.keywords)
        l = self._language
        if l == 'c++':
            self._keywords = "alignas alignof and and_eq asm auto "\
                "bitand bitor break case catch class "\
                "compl const constexpr const_cast continue decltype default "\
                "delete do dynamic_cast else enum explicit export extern "\
                "false for final friend goto if inline mutable namespace "\
                "new noexcept not not_eq nullptr operator or or_eq private "\
                " protected public register reinterpret_cast return signed "\
                "sizeof static static_assert static_cast struct switch template "\
                "this thread_local throw true try typedef typeid typename "\
                "union unsigned using virtual void volatile wchar_t while "\
                "xor xor_eq"
            self.SetKeyWords(0, self._keywords)
            self._types = ""

            for k in types:
                if "unsigned" in k:
                    continue
                if "long" in k:
                    continue
                self._types += k + " "
            self._types += "long unsigned "
            s = (self._types + self._keywords).split(' ')
            s.sort()
            self._auto = ""
            for k in s:
                self._auto += " " + k
            self.SetKeyWords(1, self._types)
        elif l == 'python':
            import keyword
            self._keywords = ' '.join(keyword.kwlist)
            self.SetKeyWords(0, self._keywords)
            self.SetKeyWords(1, 'self None True False arg kwarg super')
        self.EmptyUndoBuffer()
        self.SetSavePoint()
        self.SetUndoCollection(True)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(wx.EVT_KEY_UP, self.OnKey)
        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateEditUI)

    @property
    def breakpoint(self):
        """check if the line holds breakpoint"""
        if not self._enable_breakpoints:
            return False
        line = self.GetCurrentLine()
        return line in self._breakpoints

    def ToggleBreakpoint(self, arg):
        """Toggle breakpoint at some line"""
        if not self._enable_breakpoints:
            return
        if isinstance(arg, wx.Event):
            line = self.GetCurrentLine()
        else:
            line = arg or self.GetCurrentLine()
        if line in self._breakpoints:
            del self._breakpoints[line]
            self.MarkerDelete(line, MARK_BREAKPOINT)
        else:
            self._breakpoints[line] = None
            self.MarkerAdd(line, MARK_BREAKPOINT)

    def ToggleBookmark(self, arg):
        """Toggle the bookmark at some line"""
        if not self._enable_bookmarks:
            return
        if isinstance(arg, wx.Event):
            line = self.GetCurrentLine()
        else:
            line = arg or self.GetCurrentLine()
        if line in self._bookmarks:
            del self._bookmarks[line]
            assert self.MarkerGet(line)
            self.MarkerDelete(line, MARK_BOOKMARK)
        else:
            self._bookmarks[line] = '<<describe the bookmark here>>'
            self.MarkerAdd(line, MARK_BOOKMARK)

    def NextBookmark(self, event):
        """Goto next bookmark"""
        line = self.GetCurrentLine()
        if self.MarkerGet(line):
                line += 1
        mark = self.MarkerNext(line, 1)
        if mark == wx.NOT_FOUND:
            mark = self.MarkerNext(0, 1)
        if mark != wx.NOT_FOUND:
            self.GotoLine(mark)

    def PrevBookmark(self, event):
        """Goto previous bookmark"""
        line = self.GetCurrentLine()
        if self.MarkerGet(line):
            line -= 1
        mark = self.MarkerPrevious(line, 1)
        if mark == wx.NOT_FOUND:
            mark = self.MarkerPrevious(self.GetLineCount(), 1)
        if mark != wx.NOT_FOUND:
            self.GotoLine(mark)

    def Find(self, event):
        """Find command"""
        # note: search flags
        # SCFIND_MATCHCASE	A match only occurs with text that matches the case of the search string.
        # SCFIND_WHOLEWORD	A match only occurs if the characters before and after are not word characters.
        # SCFIND_WORDSTART	A match only occurs if the character before is not a word character.
        # SCFIND_REGEXP	The search string should be interpreted as a regular expression.
        # SCFIND_POSIX Treat regular expression in a more POSIX compatible manner by interpreting bare
        #              ( and ) for tagged sections rather than \( and \).
        # SCFIND_CXX11REGEX Replaces scintilla regex with <regex> when compiled with CX11_REGEX
        #                   (goto http://www.scintilla.org/ScintillaDoc.html#searchFlags for details)
        from app.ui.dlg import FindText
        dlg = FindText(context.frame)
        if dlg.ShowModal() == wx.ID_OK:
            self.search_text = dlg.seach_text
            self.GotoLine(0)
            self.SearchAnchor()
            self.FindNext(event)

    def FindNext(self, event):
        """Find next command"""
        if self.search_text:
            pos = self.SearchNext(STC_FIND_MATCHCASE, self.search_text)
            if pos != wx.NOT_FOUND:
                epos = pos + len(self.search_text)
                self.GotoPos(pos + 1)
                self.SearchAnchor()
                self.SetSelection(pos, epos)

    def FindPrevious(self, event):
        """Find previous command"""
        if self.search_text:
            pos = self.SearchPrev(STC_FIND_MATCHCASE, self.search_text)
            if pos != wx.NOT_FOUND:
                epos = pos + len(self.search_text)
                self.GotoPos(pos + 1)
                self.SearchAnchor()
                self.SetSelection(pos, epos)

    def DeleteAllBookmarks(self):
        """Remove all book marks"""
        self.MarkerDeleteAll(MARK_MARGIN)

    def OnMarginClick(self, event):
        """Handles margin click"""
        if event.GetMargin() == MARGIN_FOLD:
            # fold or unfold
            lineClick = self.LineFromPosition(event.GetPosition())
            levelClick = self.GetFoldLevel(lineClick)
            if levelClick & stc.STC_FOLDLEVELHEADERFLAG:
                self.ToggleFold(lineClick)
            return
        # toggle bookmark
        lineClick = self.LineFromPosition(event.GetPosition())
        self.ToggleBookmark(lineClick)

    def OnUpdateEditUI(self, event):
        """Handles pos changed"""
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)
        # check before
        if charBefore and chr(charBefore) in "[]{}()":
            if styleBefore == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos - 1
        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)
            if charAfter and chr(charAfter) in "[]{}()":
                if styleAfter == stc.STC_P_OPERATOR:
                    braceAtCaret = caretPos
        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)
        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

    def AutoIndent(self, intro):
        """Compute autoindent after key"""
        caretPos = self.GetCurrentPos()
        lnno = self.GetCurrentLine()
        if caretPos == 0 or lnno == 0:
            return
        if intro:
            lnpp = self.GetLineEndPosition(lnno - 1)
            iden = self.GetLineIndentation(lnno - 1)
            pre = self.GetCharAt(lnpp - 1)
            if chr(pre) in "[{(:":
                iden = iden + self.GetTabWidth()
            self.SetLineIndentation(lnno, iden)
            self.GotoPos(self.GetLineEndPosition(lnno))
        else:
            pre = self.GetCharAt(caretPos - 1)
            if chr(pre) in "]})":
                braceAtCaret = caretPos - 1
                braceOpposite = self.BraceMatch(braceAtCaret)
                iden = self.GetLineIndentation(
                    self.LineFromPosition(braceOpposite))
                if iden != self.GetLineIndentation(lnno):
                    self.SetLineIndentation(lnno, iden)
                    self.GotoPos(self.GetLineEndPosition(lnno))

    def OnKey(self, event):
        """Handle a scintylla event"""
        (start, end) = self.GetSelection()
        if start < end:
            return
        k = event.GetKeyCode()
        if k in [wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN]:
            self.AutoIndent(True)
            return
        elif k in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE, wx.WXK_CLEAR]:
            #self.CharRight()
            #self.DeleteBack()
            return
        elif k == wx.WXK_SPACE and event.ControlDown():
            self.popup_handler and self.popup_handler.Popup(self)
        if len(self._auto) == 0:
            event.Skip()
            return
        elif self.AutoCompActive():
            return
        self.AutoIndent(False)
        # check join letters for popup
        caretPos = self.GetCurrentPos()
        if caretPos > 2:
            text, pos = self.GetCurLine()
            text = text[:pos]
            rtext = text[::-1]
            match = re.search(r'(?P<text>(\.|\-|\>\-)?[_A-Za-z0-9]*)\s*', rtext)
            if match:
                s = match.group('text')[::-1]
                if len(s) == 0:
                    return
                if self.popup_handler and k in [ord('.'), ord('>'), ord('<')]:
                    if s[-1] == '.':
                        self.popup_handler.Popup(self, s[:-1])
                        return
                    if len(s) < 2:
                        return
                    if s[-2:] == '->':
                        self.popup_handler.Popup(self, s[:-2])
                        return
                if len(s) > 2:
                    self.AutoCompShow(len(s), self._auto)


