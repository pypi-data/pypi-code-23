# -*- coding: utf-8 -*-

import ttk
import tkFont
from .. import stretchSticky
import webbrowser


class BaseInfoWin(ttk.Frame):
    class Tags():
        TITLE = 'title'
        SUBTITLE = 'subtitle'
        FIELDNAME = 'fieldName'
        FIELDDESCR = 'fieldDescr'
        ACTIONNAME = 'actionName'
        ACTIONDESCR = 'actionDescr'
        HEADLINE = 'headline'
        NORMAL = 'normal'
        DOTLIST1 = 'dotList1'
        HYPERLINK = 'hyperlink'

    def __init__(self, master, moduleName):
        ttk.Frame.__init__(self, ttk.Tkinter.Toplevel(master),
                           padding=(5, 5, 5, 5))

        self.infoText = None

        # Text widget dimensions
        self._textWidth = 80
        self._textHeight = 25

        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        top.resizable(False, False)
        top.transient()

        self.grid(sticky=stretchSticky)

        top.title('Info - {}'.format(moduleName))
        top.bind('<KeyPress-Escape>', self._keyBtnPress)
        top.bind('<KeyPress-Return>', self._keyBtnPress)
        top.bind('<KeyPress-Down>', self._downKeyPress)
        top.bind('<KeyPress-Up>', self._upKeyPress)
        top.bind('<KeyPress-Next>', self._pgDownKeyPress)
        top.bind('<KeyPress-Prior>', self._pgUpKeyPress)

        self.grab_set()

        self.createWidgets()

        # Show text
        self._dumpTxt()

        # Turning the Text widget to read-only mode
        self.infoText.configure(state=ttk.Tkinter.DISABLED)

        # Moving the focus to this window
        top.focus_set()

    def _okCommand(self):
        self.winfo_toplevel().destroy()

    def _keyBtnPress(self, event):
        self.winfo_toplevel().destroy()

    def _downKeyPress(self, event):
        self.infoText.yview(ttk.Tkinter.SCROLL, 1, ttk.Tkinter.UNITS)

    def _upKeyPress(self, event):
        self.infoText.yview(ttk.Tkinter.SCROLL, -1, ttk.Tkinter.UNITS)

    def _pgDownKeyPress(self, event):
        self.infoText.yview(ttk.Tkinter.SCROLL, 1, ttk.Tkinter.PAGES)

    def _pgUpKeyPress(self, event):
        self.infoText.yview(ttk.Tkinter.SCROLL, -1, ttk.Tkinter.PAGES)

    def _followHyperlink(self, event):
        # Implementation of this method follows the solution outlined here:
        # https://stackoverflow.com/questions/40940397/tkinter-text-widget-use-clicked-text-in-event-function

        # get the index of the mouse click
        index = event.widget.index("@{},{}".format(event.x, event.y))

        # get the range of text for the HYPERLINK tag
        tag_indices = list(event.widget.tag_ranges(BaseInfoWin.Tags.HYPERLINK))

        for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
            # check if the tag matches the mouse click index
            if event.widget.compare(start, '<=', index) and \
               event.widget.compare(index, '<', end):

                # get the string below the tag (actual URL)
                url = event.widget.get(start, end).strip()

                # Go to the URL
                webbrowser.open_new(url)

                break

    def _dumpTxt(self):
        raise NotImplementedError

    def createWidgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.grid(sticky=stretchSticky)

        yScroll = ttk.Scrollbar(frame, orient=ttk.Tkinter.VERTICAL)
        yScroll.grid(column=1, row=0, sticky=ttk.Tkinter.N+ttk.Tkinter.S)

        self.infoText = ttk.Tkinter.Text(
            frame,
            width=self._textWidth,
            height=self._textHeight,
            tabs=('1c', '2c', '3c', '4c'),
            takefocus=0,
            wrap=ttk.Tkinter.WORD)
        self.infoText.grid(row=0, column=0, sticky=stretchSticky)
        self.infoText['yscrollcommand'] = yScroll.set
        yScroll['command'] = self.infoText.yview

        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.grid(row=1, column=0,
                   sticky=ttk.Tkinter.W+ttk.Tkinter.S+ttk.Tkinter.E)

        ttk.Button(frame, text='Ok', command=self._okCommand).grid()

        # Setting Text's tags
        self.infoText.tag_config(
            BaseInfoWin.Tags.TITLE,
            font=tkFont.Font(weight='bold'),
            justify=ttk.Tkinter.CENTER)
        self.infoText.tag_config(
            BaseInfoWin.Tags.SUBTITLE,
            font=tkFont.Font(slant='italic'),
            justify=ttk.Tkinter.CENTER)
        self.infoText.tag_config(
            BaseInfoWin.Tags.HEADLINE,
            font=tkFont.Font(weight='bold'), spacing1='0.3c')
        self.infoText.tag_config(
            BaseInfoWin.Tags.FIELDNAME,
            font=tkFont.Font(slant='italic', underline=1),
            spacing1='0.2c', lmargin1='0.25c')
        self.infoText.tag_config(
            BaseInfoWin.Tags.FIELDDESCR,
            lmargin1='0.75c', lmargin2='0.75c')
        self.infoText.tag_config(
            BaseInfoWin.Tags.ACTIONNAME,
            font=tkFont.Font(slant='italic', underline=1),
            spacing1='0.2c', lmargin1='0.25c')
        self.infoText.tag_config(
            BaseInfoWin.Tags.ACTIONDESCR,
            lmargin1='0.75c', lmargin2='0.75c')
        self.infoText.tag_config(
            BaseInfoWin.Tags.NORMAL,
            lmargin1='0.25c', lmargin2='0.25c')
        self.infoText.tag_config(
            BaseInfoWin.Tags.DOTLIST1,
            lmargin1='0.25c', lmargin2='0.75c', tabs=('0.75c',))
        self.infoText.tag_config(
            BaseInfoWin.Tags.HYPERLINK,
            underline=1, foreground='blue')

        self.infoText.tag_bind(
            BaseInfoWin.Tags.HYPERLINK, '<Button-1>', self._followHyperlink)

        # Placing the window
        top = self.winfo_toplevel()
        top.update_idletasks()
        w = top.winfo_screenwidth()
        h = top.winfo_screenheight()
        winSize = [int(_) for _ in top.geometry().split('+')[0].split('x')]
        x = w/4 - winSize[0]/4
        y = h/4 - winSize[1]/4
        top.geometry("{:d}x{:d}+{:d}+{:d}".format(*(winSize+[x, y])))
