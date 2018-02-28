# -*- coding: utf-8 -*-

import ttk
from .. import stretchSticky
from basePane import BasePane
from .. import signals
from pisim.dataLoadStore import pensione
from ..commonEntry import IntPositiveEntry, PercentagePositiveEntry
from ..infoWindows.pensioneInfoWin import PensioneInfoWin


class PensionePane(BasePane):
    def __init__(self, master, *args, **kwargs):
        BasePane.__init__(self, master, pensione.PensioneDescIo(),
                          *args, **kwargs)

    def _infoCmd(self):
        w = PensioneInfoWin(self, 'Pensione')
        self.wait_window(w.master)

    def _setupArea_AboveDescList(self, master):
        pass

    def _setupArea_UserWidgets(self, master):
        ttk.Label(master, text='Età pensionamento',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(master, text='Tasso di sostituzione (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=1, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'etaPensionamento',
            IntPositiveEntry(
                master,
                description="Età pensionamento"))
        self.infoDict['widgets']['etaPensionamento'].grid(
            row=0, column=1, sticky=stretchSticky)

        self.addWidget(
            'tassoSostituzione',
            PercentagePositiveEntry(
                master,
                description='Tasso di sostituzione (%)'))
        self.infoDict['widgets']['tassoSostituzione'].grid(
            row=1, column=1, sticky=stretchSticky)

        andNode = signals.And()
        for w in ['etaPensionamento', 'tassoSostituzione']:
            self.infoDict['widgets'][w].join(toNode=andNode)
        andNode.join(toNode=self._fieldsSetValidityStatusDispatcher)
