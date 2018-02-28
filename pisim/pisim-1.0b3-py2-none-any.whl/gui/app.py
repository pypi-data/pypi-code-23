# -*- coding: utf-8 -*-

import ttk
import tkMessageBox
from datetime import datetime

from . import stretchSticky
from ..dataLoadStore import factoryDescs
from .. import pisimVer
import signals
from commonEntry import RemotelyEnabledButton
from mainWinPanes import dipendentePane, salarioPane, inflazionePane, \
                          pensionePane, fpBasePane, fpAccumuloPane, \
                          fpRenditaPane
from pisim.simulation import errors as simErrors
from pisim.simulation.fpSim import FpSim
from pisim.engine import errors as engineErrors
from pisim.dataLoadStore.reports.reports import ReportsDescIo
from resultsWindow import ResultsWindow
from infoWindows.mainWinInfoWin import MainWinInfoWin

import sys
import os.path
path_to_top = \
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path = [path_to_top] + sys.path


class PiSimApp(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)

        self.buttons = {}
        self.sections = {}

        self._reportsWin = None

        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.grid(sticky=stretchSticky)

        self._processBtnEnabler = signals.And()

        self.createWidgets()

    def _changePaneTitle(self, s):
        title = self.notebook.tab(int(s.userName), option='text')
        title = ' '.join(title.split(' ')[1:])
        if s.state:
            self.notebook.tab(int(s.userName), text='[O] '+title)
        else:
            self.notebook.tab(int(s.userName), text='[X] '+title)

    def _createPane(self, sectionName, paneTitle, className):
        pWin = className(self.notebook)
        self.notebook.add(pWin, text='[X] '+paneTitle, sticky=stretchSticky)
        pWin.createWidgets()

        dupNode = signals.Dup()
        pWin.join(toNode=dupNode, signalName='fieldsValidityStatus')
        dupNode.join(toNode=self._processBtnEnabler)
        dupNode.join(
            signals.Sink(signalRxCallback=self._changePaneTitle),
            signalName=str(self.notebook.index('end')-1))

        self.sections[sectionName] = pWin

    def _trackFpBaseConfFileSelection(self, *args):
        val = self.sections['fpBase'].infoDict['vars']['selectedDesc'].get()
        fpId = self.sections['fpBase'].infoDict['vars']['selectedDescRowId']
        for s in ['fpAccumulo', 'fpRendita']:
            self.sections[s].infoDict['widgets']['fpSelectedName'].var.write(
                val)
            self.sections[s].infoDict['vars']['fpSelecteRowId'].set(fpId)

    def _elaboraCommand(self):
        descs = {}
        for k in self.sections:
            descs[k] = self.sections[k].getDesc()
        descs['fp'] = {
            'base': dict(descs['fpBase']),
            'accumulo': dict(descs['fpAccumulo']),
            'rendita': dict(descs['fpRendita'])
        }
        del descs['fpBase']
        del descs['fpAccumulo']
        del descs['fpRendita']

        try:
            report = {
                'name': 'rep-' + datetime.now().strftime("%Y.%m.%d-%H.%M.%S"),
                'results': {
                    'worst': FpSim.run(descs, FpSim.Scenarios.WORST),
                    'best': FpSim.run(descs, FpSim.Scenarios.BEST),
                    'normal': FpSim.run(descs, FpSim.Scenarios.NORMAL)
                },
                'dipendente': descs['dipendente'],
                'inflazione': descs['inflazione'],
                'salario': descs['salario'],
                'pensione': descs['pensione'],
                'fp': {
                    'base': descs['fp']['base'],
                    'accumulo': descs['fp']['accumulo'],
                    'rendita': descs['fp']['rendita'],
                }
            }
            sct = self.sections
            for k in ['dipendente', 'inflazione', 'salario', 'pensione']:
                report[k]['name'] = \
                    sct[k].infoDict['widgets']['nomeConfig'].var.get()
            report['fp']['base']['name'] = \
                sct['fpBase'].infoDict['widgets']['nomeConfig'].var.get()
            report['fp']['accumulo']['name'] = \
                sct['fpAccumulo'].infoDict['widgets']['nomeConfig'].var.get()
            report['fp']['rendita']['name'] = \
                sct['fpRendita'].infoDict['widgets']['nomeConfig'].var.get()

            reportId = ReportsDescIo().save(report)

            self._risultatiCommand()
            self._reportsWin.showRecentlyComputedReport(reportId, report)
        except (
                simErrors.NotPositiveYearsError,
                simErrors.TooManyYearsError,
                engineErrors.EtaPensionamentoNotFoundError) as e:
            tkMessageBox.showerror(
                'Errore nel salvataggio dei risultati', e.__str__())

    def _aboutCmd(self):
        pass

    def _infoCmd(self):
        w = MainWinInfoWin(self, 'PiSim')
        self.wait_window(w.master)

    def _risultatiCommand(self):
        if self._reportsWin is None:
            self._reportsWin = ResultsWindow(self)
        else:
            self._reportsWin.show()

    def createWidgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(sticky=stretchSticky)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text='Azioni')
        frame.grid(sticky=stretchSticky)

        self.buttons['info'] = \
            ttk.Button(frame, text='About',
                       state=ttk.Tkinter.DISABLED, command=self._aboutCmd)
        # To be enabled lately
        # self.buttons['info'].grid(sticky=ttk.Tkinter.W, row=0, column=0)

        self.buttons['info'] = \
            ttk.Button(frame, text='Info', command=self._infoCmd)
        self.buttons['info'].grid(sticky=ttk.Tkinter.W, row=0, column=1)
        frame.columnconfigure(1, weight=1)

        self.buttons['elabora'] = \
            RemotelyEnabledButton(
                frame, text='Elabora',
                state=ttk.Tkinter.DISABLED, command=self._elaboraCommand)
        self.buttons['elabora'].grid(sticky=ttk.Tkinter.E, row=0, column=2)
        self._processBtnEnabler.join(toNode=self.buttons['elabora'])
        frame.columnconfigure(2, weight=1)

        self.buttons['risultati'] = \
            ttk.Button(frame, text='Risultati',
                       command=self._risultatiCommand)
        self.buttons['risultati'].grid(sticky=ttk.Tkinter.E, row=0, column=3)

        self._createPane('dipendente', 'Dipendente',
                         dipendentePane.DipendentePane)
        self._createPane('inflazione', 'Inflazione',
                         inflazionePane.InflazionePane)
        self._createPane('salario', 'Salario', salarioPane.SalarioPane)
        self._createPane('pensione', 'Pensione', pensionePane.PensionePane)
        self._createPane('fpBase', 'F.P. - Base', fpBasePane.FpBasePane)
        self._createPane('fpAccumulo', 'F.P. - Accumulo',
                         fpAccumuloPane.FpAccumuloPane)
        self._createPane('fpRendita', 'F.P. - Rendita',
                         fpRenditaPane.FpRenditaPane)

        self.sections['fpBase'].infoDict['vars']['selectedDesc'].trace(
            'w', self._trackFpBaseConfFileSelection)


def main():
    # Checking db -- installing factory descriptors if they're not found
    factoryDescs.run()

    app = PiSimApp()
    app.master.title('PiSim - Simulatore di pensione integrativa')
    app.mainloop()


if __name__ == "__main__":
    main()
