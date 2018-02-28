# -*- coding: utf-8 -*-

import ttk
from .. import stretchSticky
from basePane import BasePane
from .. import signals
from pisim.dataLoadStore.fondoPensione import base
from ..commonEntry import EnhOptionMenu, PercentageNotNegativeEntry
from ..infoWindows.fpBaseInfoWin import FpBaseInfoWin


class FpBasePane(BasePane):
    def __init__(self, master, *args, **kwargs):
        BasePane.__init__(self, master, base.FpBaseDescIo(), *args, **kwargs)

    def _infoCmd(self):
        w = FpBaseInfoWin(self, 'F.P. Base')
        self.wait_window(w.master)

    def _setupArea_AboveDescList(self, master):
        pass

    def _setupArea_UserWidgets(self, master):
        def _addBaseContribOptionButton(master, widgetName, description, row):
            def setConvF(x):
                if x == 'minContratto':
                    return 'Minimo contrattuale'
                elif x == 'lordo':
                    return 'Lordo'
                else:
                    return 'Minimo contrattuale'

            def getConvF(x):
                if x == 'Minimo contrattuale':
                    return 'minContratto'
                elif x == 'Lordo':
                    return 'lordo'
                else:
                    return 'minContratto'
            self.addWidget(
                widgetName,
                EnhOptionMenu(
                    master,
                    values=['Minimo contrattuale', 'Lordo'],
                    defaultId=0,
                    description=description,
                    setConvF=setConvF,
                    getConvF=getConvF))
            self.infoDict['widgets'][widgetName].grid(
                row=row, column=1, sticky=stretchSticky)

        ttk.Label(master, text='Tipo', justify=ttk.Tkinter.LEFT).grid(
            row=0, column=0, sticky=ttk.Tkinter.W)
        self.addWidget(
            'tipo',
            EnhOptionMenu(
                master,
                values=['Chiuso', 'Aperto'],
                defaultId=0,
                description='Tipo fondo pensione',
                setConvF=lambda x: x.capitalize(),
                getConvF=lambda x: x.lower()))
        self.infoDict['widgets']['tipo'].grid(
            row=0, column=1, sticky=stretchSticky)

        lFrame1 = ttk.LabelFrame(master, text='Contribuzione dipendente')
        lFrame1.columnconfigure(0, weight=1)
        lFrame1.columnconfigure(1, weight=1)
        lFrame1.grid(row=1, column=0, sticky=stretchSticky, columnspan=2)

        lFrame2 = ttk.LabelFrame(master, text='Contribuzione datore')
        lFrame2.columnconfigure(0, weight=1)
        lFrame2.columnconfigure(1, weight=1)
        lFrame2.grid(row=2, column=0, sticky=stretchSticky, columnspan=2)

        ttk.Label(lFrame1, text='Minima per contrib.datore (%)',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame1, text='Base calcolo, <minimo',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=1, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame1, text='Base calcolo, >minimo',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=2, column=0, sticky=ttk.Tkinter.W)

        ttk.Label(lFrame2, text='Base', justify=ttk.Tkinter.LEFT).grid(
            row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame2, text='Valore (%)', justify=ttk.Tkinter.LEFT).grid(
            row=1, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'accumulo.contribuzione.dipendente.minimaPerContributoDatore',
            PercentageNotNegativeEntry(
                lFrame1,
                description=('Contribuzione minima dipendent e'
                             'per contrib.datore (%)')))
        tmp = self.infoDict['widgets']
        tmp = \
            tmp['accumulo.contribuzione.dipendente.minimaPerContributoDatore']
        tmp.grid(row=0, column=1, sticky=stretchSticky)

        _addBaseContribOptionButton(
            master=lFrame1,
            widgetName='accumulo.contribuzione.dipendente.base.sottoMinima',
            description=('Base per calcolo contribuzione dipendente, '
                         'contribuzione<minimo'),
            row=1)

        _addBaseContribOptionButton(
            master=lFrame1,
            widgetName='accumulo.contribuzione.dipendente.base.sopraMinima',
            description=('Base per calcolo contribuzione dipendente, '
                         'contribuzione>minimo'),
            row=2)

        _addBaseContribOptionButton(
            master=lFrame2,
            widgetName='accumulo.contribuzione.datore.base',
            description='Base per calcolo contribuzione datore',
            row=0)

        self.addWidget(
            'accumulo.contribuzione.datore.valore',
            PercentageNotNegativeEntry(
                lFrame2,
                description='Valore contribuzione datoriale (%)'))
        self.infoDict['widgets']['accumulo.contribuzione.datore.valore'].grid(
            row=1, column=1, sticky=stretchSticky)

        andNode = signals.And()
        for w in \
            ['tipo',
             'accumulo.contribuzione.dipendente.minimaPerContributoDatore',
             'accumulo.contribuzione.dipendente.base.sottoMinima',
             'accumulo.contribuzione.dipendente.base.sopraMinima',
             'accumulo.contribuzione.datore.base',
             'accumulo.contribuzione.datore.valore']:
            self.infoDict['widgets'][w].join(toNode=andNode)
        andNode.join(toNode=self._fieldsSetValidityStatusDispatcher)
