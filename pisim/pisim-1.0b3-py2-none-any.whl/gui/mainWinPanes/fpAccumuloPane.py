# -*- coding: utf-8 -*-

import ttk
from .. import stretchSticky
from basePane import BasePane
from .. import signals
from pisim.dataLoadStore.fondoPensione import accumulo
from ..commonEntry import EnhEntryBase, FloatNotNegativeEntry, \
                          PercentageNotNegativeEntry
from ..infoWindows.fpAccumuloInfoWin import FpAccumuloInfoWin


class NotEmptyEntry(EnhEntryBase):
    def _checkValue(self, *args):
        return self.var.get() != ''


class FpAccumuloPane(BasePane):
    def __init__(self, master, *args, **kwargs):
        BasePane.__init__(self, master, None, *args, **kwargs)

    def _infoCmd(self):
        w = FpAccumuloInfoWin(self, 'F.P. Accumulo')
        self.wait_window(w.master)

    def _fpChange(self, *args):
        if self.infoDict['widgets']['fpSelectedName'].var.read():
            self._ioModule = accumulo.FpAccumuloDescIo(
                self.infoDict['vars']['fpSelecteRowId'].get())
        else:
            self._ioModule = None
        self.loadDescriptorsList()

    def _setupArea_AboveDescList(self, master):
        master.rowconfigure(0, weight=0)

        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(sticky=ttk.Tkinter.E+ttk.Tkinter.W+ttk.Tkinter.N)

        self.infoDict['widgets']['fpSelectedName'] = NotEmptyEntry(
            master=frame,
            name='fpSelectedName',
            description='Nome fondo pensione selezionato',
            state=ttk.Tkinter.DISABLED,
            justify=ttk.Tkinter.CENTER)
        self.infoDict['widgets']['fpSelectedName'].grid(sticky=stretchSticky)
        self.infoDict['vars']['fpSelecteRowId'] = ttk.Tkinter.IntVar()
        self.infoDict['vars']['fpSelecteRowId'].trace('w', self._fpChange)

        self.infoDict['widgets']['fpSelectedName'].join(
            toNode=self._saveBtnEnabler)

    def _setupArea_UserWidgets(self, master):
        ttk.Label(master, text='Contribuzione dipendente (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=0, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'contribuzione.dipendente.valore',
            PercentageNotNegativeEntry(
                master,
                description='Contribuzione dipendente (%)'))
        self.infoDict['widgets']['contribuzione.dipendente.valore'].grid(
            row=0, column=1, sticky=stretchSticky)

        lFrame1 = ttk.LabelFrame(master, text='Rivalutazione')
        lFrame1.columnconfigure(0, weight=1)
        lFrame1.columnconfigure(1, weight=1)
        lFrame1.grid(row=1, column=0, sticky=stretchSticky, columnspan=2)

        lFrame2 = ttk.LabelFrame(master, text='Spese annue')
        lFrame2.columnconfigure(0, weight=1)
        lFrame2.columnconfigure(1, weight=1)
        lFrame2.grid(row=2, column=0, sticky=stretchSticky, columnspan=2)

        ttk.Label(lFrame1, text='Media (%)', justify=ttk.Tkinter.LEFT).grid(
            row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame1, text='Variazione (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=1, column=0, sticky=ttk.Tkinter.W)

        ttk.Label(lFrame2, text='Fisse (EUR)', justify=ttk.Tkinter.LEFT).grid(
            row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame2, text='Variabili (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=1, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame2, text='Imposta (%)', justify=ttk.Tkinter.LEFT).grid(
            row=2, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'rivalutazione.valore',
            PercentageNotNegativeEntry(
                lFrame1,
                description='Rivalutazione montante media (%)'))
        self.infoDict['widgets']['rivalutazione.valore'].grid(
            row=0, column=1, sticky=stretchSticky)

        self.addWidget(
            'rivalutazione.variazione',
            PercentageNotNegativeEntry(
                lFrame1,
                description='Variazione della rivalutazione montante (%)'))
        self.infoDict['widgets']['rivalutazione.variazione'].grid(
            row=1, column=1, sticky=stretchSticky)

        self.addWidget(
            'spese.fisse',
            FloatNotNegativeEntry(
                lFrame2,
                description='Spese fisse'))
        self.infoDict['widgets']['spese.fisse'].grid(
            row=0, column=1, sticky=stretchSticky)

        self.addWidget(
            'spese.variabili',
            PercentageNotNegativeEntry(
                lFrame2,
                description='Spese variabili'))
        self.infoDict['widgets']['spese.variabili'].grid(
            row=1, column=1, sticky=stretchSticky)

        self.addWidget(
            'spese.imposta',
            PercentageNotNegativeEntry(
                lFrame2,
                description='Spese per imposte'))
        self.infoDict['widgets']['spese.imposta'].grid(
            row=2, column=1, sticky=stretchSticky)

        andNode = signals.And()
        for w in ['contribuzione.dipendente.valore',
                  'rivalutazione.valore',
                  'rivalutazione.variazione',
                  'spese.fisse',
                  'spese.variabili',
                  'spese.imposta']:
            self.infoDict['widgets'][w].join(toNode=andNode)
        andNode.join(toNode=self._fieldsSetValidityStatusDispatcher)
