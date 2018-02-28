# -*- coding: utf-8 -*-

import ttk
from .. import stretchSticky
from basePane import BasePane
from .. import signals
from pisim.dataLoadStore import inflazione
from ..commonEntry import PercentageNotNegativeEntry
from ..infoWindows.inflazioneInfoWin import InflazioneInfoWin


class InflazionePane(BasePane):
    def __init__(self, master, *args, **kwargs):
        BasePane.__init__(self, master, inflazione.InflazioneDescIo(),
                          *args, **kwargs)

    def _infoCmd(self):
        w = InflazioneInfoWin(self, 'Inflazione')
        self.wait_window(w.master)

    def _setupArea_AboveDescList(self, master):
        pass

    def _setupArea_UserWidgets(self, master):
        ttk.Label(master, text='Tasso Medio (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(master, text='Variazione (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=1, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'tassoMedio',
            PercentageNotNegativeEntry(
                master,
                description='Tasso Medio (%)'))
        self.infoDict['widgets']['tassoMedio'].grid(
            row=0, column=1, sticky=stretchSticky)

        self.addWidget(
            'variazione',
            PercentageNotNegativeEntry(
                master,
                description='Variazione (%)'))
        self.infoDict['widgets']['variazione'].grid(
            row=1, column=1, sticky=stretchSticky)

        andNode = signals.And()
        for w in ['tassoMedio', 'variazione']:
            self.infoDict['widgets'][w].join(toNode=andNode)
        andNode.join(toNode=self._fieldsSetValidityStatusDispatcher)
