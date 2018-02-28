# -*- coding: utf-8 -*-

import ttk
from .. import stretchSticky
from basePane import BasePane
from .. import signals
from pisim.dataLoadStore.fondoPensione import rendita
from ..commonEntry import FloatNotNegativeEntry, PercentageNotNegativeEntry
from fpAccumuloPane import NotEmptyEntry
from ..infoWindows.fpRenditaInfoWin import FpRenditaInfoWin


class FpRenditaPane(BasePane):
    class ModPercentageEntry(PercentageNotNegativeEntry):
        def __init__(self, master, *args, **kwargs):
            PercentageNotNegativeEntry.__init__(
                self,
                master,
                *args, **kwargs)

        def _setConvF(self, x):
            try:
                return round(float(x)*100.0, 5)
            except (ValueError, TypeError):
                return ''

        def _getConvF(self, x):
            try:
                return round(float(x)/100.0, 7)
            except (ValueError, TypeError):
                return None

        def _checkValue(self, *args):
            if self.var.get() == '':
                return True
            else:
                return PercentageNotNegativeEntry._checkValue(self, *args)

    class TrackEmptyField(signals.Node):
        def __init__(self, refVar):
            signals.Node.__init__(self)
            self._refVar = refVar

        def callback(self, *args):
            state = (self._refVar.get() != '')
            for s in self._outSignals:
                s.state = state

        def _procRxSignals(self, *args):
            pass

        def _checkInSignal(self, signal):
            return False

        def _checkOutSignal(self, signal):
            return len(self._outSignals) == 0

    def __init__(self, master, *args, **kwargs):
        BasePane.__init__(self, master, None, *args, **kwargs)

    def _infoCmd(self):
        w = FpRenditaInfoWin(self, 'F.P. Rendita')
        self.wait_window(w.master)

    def _trackNumEmptyFields(self, *args):
        pass

    def _fpChange(self, *args):
        if self.infoDict['widgets']['fpSelectedName'].var.read():
            self._ioModule = rendita.FpRenditaDescIo(
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
        self._notEmptyFieldsCounter = 0

        lFrame1 = ttk.LabelFrame(master, text='Tassi di conversione (%)')
        lFrame1.columnconfigure(0, weight=1)
        lFrame1.columnconfigure(1, weight=1)
        lFrame1.columnconfigure(2, weight=1)
        lFrame1.grid(row=0, column=0, sticky=stretchSticky)

        lFrame2 = ttk.LabelFrame(master, text='Spese annue')
        lFrame2.columnconfigure(0, weight=1)
        lFrame2.columnconfigure(1, weight=1)
        lFrame2.grid(row=1, column=0, sticky=stretchSticky)

        lFrame3 = ttk.LabelFrame(master, text='Altri dati')
        lFrame3.columnconfigure(0, weight=1)
        lFrame3.columnconfigure(1, weight=1)
        lFrame3.grid(row=2, column=0, sticky=stretchSticky)

        ttk.Label(lFrame1, text='Uomini').grid(
            row=0, column=1, sticky=ttk.Tkinter.S+ttk.Tkinter.N)
        ttk.Label(lFrame1, text='Donne').grid(
            row=0, column=2, sticky=ttk.Tkinter.S+ttk.Tkinter.N)

        fieldsNotEmptyNode = signals.Or()
        for y in range(50, 71):
            ttk.Label(lFrame1, text='{:d} anni'.format(y),
                      justify=ttk.Tkinter.LEFT).grid(
                        row=y-50+1, column=0, sticky=ttk.Tkinter.W)

            widgetName = 'tabellaTassiConversione.m.{:d}'.format(y)
            self.addWidget(
                widgetName,
                FpRenditaPane.ModPercentageEntry(
                    lFrame1,
                    description=('Tasso di conversione, uomini, '
                                 '{:d} anni').format(y)))
            self.infoDict['widgets'][widgetName].grid(
                row=y-50+1, column=1, sticky=stretchSticky)

            obj = FpRenditaPane.TrackEmptyField(
                self.infoDict['widgets'][widgetName].var)
            self.infoDict['widgets'][widgetName].traceVarChange(obj.callback)
            obj.join(toNode=fieldsNotEmptyNode)

            widgetName = 'tabellaTassiConversione.f.{:d}'.format(y)
            self.addWidget(
                widgetName,
                FpRenditaPane.ModPercentageEntry(
                    lFrame1,
                    description=('Tasso di conversione, donne, '
                                 '{:d} anni').format(y)))
            self.infoDict['widgets'][widgetName].grid(
                row=y-50+1, column=2, sticky=stretchSticky)

            obj = FpRenditaPane.TrackEmptyField(
                self.infoDict['widgets'][widgetName].var)
            self.infoDict['widgets'][widgetName].traceVarChange(obj.callback)
            obj.join(toNode=fieldsNotEmptyNode)

        ttk.Label(lFrame2, text='Fisse (EUR)').grid(
            row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(lFrame2, text='Variabili (%)').grid(
            row=1, column=0, sticky=ttk.Tkinter.W)

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

        ttk.Label(lFrame3, text='Rivalutazione annua (%)').grid(
            row=0, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'rivalutazione',
            PercentageNotNegativeEntry(
                lFrame3,
                description='Rivalutazione rendita annua'))
        self.infoDict['widgets']['rivalutazione'].grid(
            row=0, column=1, sticky=stretchSticky)

        andNode = signals.And()
        for w in \
                ['tabellaTassiConversione.m.{:d}'.format(y)
                    for y in range(50, 71)] + \
                ['tabellaTassiConversione.f.{:d}'.format(y)
                    for y in range(50, 71)] + \
                ['spese.fisse', 'spese.variabili', 'rivalutazione']:
            self.infoDict['widgets'][w].join(toNode=andNode)
        fieldsNotEmptyNode.join(toNode=andNode)
        andNode.join(toNode=self._fieldsSetValidityStatusDispatcher)
