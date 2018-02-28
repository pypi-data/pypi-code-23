# -*- coding: utf-8 -*-

import ttk
from .. import stretchSticky
from basePane import BasePane
from .. import signals
from pisim.dataLoadStore import salario
from ..commonEntry import IntPositiveEntry, PercentageNotNegativeEntry, \
                          FloatPositiveEntry
from ..infoWindows.salarioInfoWin import SalarioInfoWin


class SalarioPane(BasePane):
    def __init__(self, master, *args, **kwargs):
        BasePane.__init__(self, master, salario.SalarioDescIo(),
                          *args, **kwargs)

    def _infoCmd(self):
        w = SalarioInfoWin(self, 'Salario')
        self.wait_window(w.master)

    def _setupArea_AboveDescList(self, master):
        pass

    def _setupArea_UserWidgets(self, master):
        lFrame1 = ttk.LabelFrame(master, text='Salario')
        lFrame1.columnconfigure(0, weight=1)
        lFrame1.columnconfigure(1, weight=1)
        lFrame1.grid(row=0, column=0, sticky=stretchSticky)

        lFrame2 = ttk.LabelFrame(master, text='Rivalutazione')
        lFrame2.columnconfigure(0, weight=1)
        lFrame2.columnconfigure(1, weight=1)
        lFrame2.grid(row=1, column=0, sticky=stretchSticky)

        ttk.Label(lFrame1, text='Lordo annuo', justify=ttk.Tkinter.LEFT).grid(
            row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame1, text='Minimo contrattuale, mese',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=1, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame2, text='Annua (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame2, text='Periodicita\' (#anni)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=1, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'lordoAnnuo',
            FloatPositiveEntry(
                lFrame1,
                description='Stipendio lordo annuo'))
        self.infoDict['widgets']['lordoAnnuo'].grid(
            row=0, column=1, sticky=stretchSticky)

        self.addWidget(
            'minContrattoMese',
            FloatPositiveEntry(
                lFrame1,
                description='Minimo contrattuale, mese'))
        self.infoDict['widgets']['minContrattoMese'].grid(
            row=1, column=1, sticky=stretchSticky)

        self.addWidget(
            'rivalutazione.valore',
            PercentageNotNegativeEntry(
                lFrame2,
                description='Rivalutazione annua (%)'))
        self.infoDict['widgets']['rivalutazione.valore'].grid(
            row=0, column=1, sticky=stretchSticky)

        self.addWidget(
            'rivalutazione.frequenza',
            IntPositiveEntry(
                lFrame2,
                description='Periodicità (#anni) rivalutazione'))
        self.infoDict['widgets']['rivalutazione.frequenza'].grid(
            row=1, column=1, sticky=stretchSticky)

        andNode = signals.And()
        for w in ['lordoAnnuo', 'minContrattoMese', 'rivalutazione.valore',
                  'rivalutazione.frequenza']:
            self.infoDict['widgets'][w].join(toNode=andNode)
        andNode.join(toNode=self._fieldsSetValidityStatusDispatcher)
