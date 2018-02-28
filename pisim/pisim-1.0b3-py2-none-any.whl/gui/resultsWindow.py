# -*- coding: utf-8 -*-

import ttk
import tkMessageBox

from . import stretchSticky
from pisim.dataLoadStore.common import DescIo
from ..dataLoadStore.reports.reports import ReportsDescIo
from settingsWindow import SettingsWindow
from commonEntry import DescriptorNameEntry, RemotelyEnabledButton
from infoWindows.risultatiInfoWin import RisultatiInfoWin
from ..simulation.fpSim import FpSim
from resultsCommon import ShowMode
from ..settingsLoadStore.common import SettingsIo


class Headline(ttk.Label):
    def __init__(self, master, *args, **kwargs):
        ttk.Label.__init__(self, master, style='emph.TLabel', *args, **kwargs)

        self._containedWidgets = []
        self._isVisible = True

        numRows = master.grid_size()[1]
        self.grid(row=numRows, column=0, columnspan=3,
                  sticky=ttk.Tkinter.W+ttk.Tkinter.E)

    def addContainedWidget(self, w):
        self._containedWidgets.append(w)

    def updateVisibility(self, widget):
        if self._isVisible and widget.isRowVisible():
            return
        if (not self._isVisible) and (not widget.isRowVisible()):
            return
        if self._isVisible and (not widget.isRowVisible()):
            self._isVisible = False
            for w in self._containedWidgets:
                if w.isRowVisible():
                    self._isVisible = True
                    break
            self.grid() if self._isVisible else self.grid_remove()
        if (not self._isVisible) and widget.isRowVisible():
            self._isVisible = True
            self.grid()


class DataRow:
    def __init__(self, master, labelText, outF, headline):
        self._outF = outF if outF else lambda x: '{}'.format(x)

        self._showMode = ShowMode.MINMAX

        self._isVisible = ttk.Tkinter.IntVar()
        self._isVisible.set(1)
        self._isVisible.trace('w', self._traceIsVisible)
        self._headline = headline

        self._scenarioVisibility = {
            FpSim.Scenarios.WORST: True,
            FpSim.Scenarios.BEST: True,
            FpSim.Scenarios.NORMAL: True
        }

        self._values = {
            FpSim.Scenarios.BEST:
            {
                'average': None,
                'confInt': 0.0
            },
            FpSim.Scenarios.WORST:
            {
                'average': None,
                'confInt': 0.0
            },
            FpSim.Scenarios.NORMAL:
            {
                'average': None,
                'confInt': 0.0
            }
        }

        numRows = master.grid_size()[1]
        self._label = \
            ttk.Label(master, text=labelText, justify=ttk.Tkinter.LEFT)
        self._label.grid(row=numRows, column=0, sticky=ttk.Tkinter.W)

        self._widgets = {
            FpSim.Scenarios.WORST:
                ttk.Label(master, text='', justify=ttk.Tkinter.LEFT),
            FpSim.Scenarios.BEST:
                ttk.Label(master, text='', justify=ttk.Tkinter.LEFT),
            FpSim.Scenarios.NORMAL:
                ttk.Label(master, text='', justify=ttk.Tkinter.LEFT)
        }
        self._widgets[FpSim.Scenarios.BEST].grid(row=numRows, column=1)
        self._widgets[FpSim.Scenarios.NORMAL].grid(row=numRows, column=2)
        self._widgets[FpSim.Scenarios.WORST].grid(row=numRows, column=3)

        self.setValue(FpSim.Scenarios.BEST)
        self.setValue(FpSim.Scenarios.WORST)
        self.setValue(FpSim.Scenarios.NORMAL)

        headline.addContainedWidget(self)

    def _traceIsVisible(self, *args):
        self._headline.updateVisibility(self)

    def setShowMode(self, showMode):
        if self._showMode != showMode:
            self._showMode = showMode
            self._updateShownValue()

    def _updateShownValue(self):
        for scen in self._values:
            if self._values[scen]['average'] is None:
                labelText = ''
            else:
                if self._showMode == ShowMode.AVGONLY:
                    labelText = '{}'.format(
                        self._outF(self._values[scen]['average']))
                else:
                    if self._showMode == ShowMode.MINMAX:
                        labelText = '{}  -  {}'.format(
                            self._outF(self._values[scen]['average'] -
                                       self._values[scen]['confInt']),
                            self._outF(self._values[scen]['average'] +
                                       self._values[scen]['confInt']))
                    elif self._showMode == ShowMode.RELCONFINT:
                        try:
                            relRange = abs(self._values[scen]['confInt'] /
                                           self._values[scen]['average'])
                        except ZeroDivisionError:
                            relRange = 0
                        labelText = '{}    ({:.2f}%)'.format(
                            self._outF(self._values[scen]['average']),
                            relRange*100)

            self._widgets[scen].configure(text=labelText)

    def setValue(self, scenario, average=None, confInt=0.0):
        self._values[scenario] = {
            'average': average,
            'confInt': confInt
        }
        self._updateShownValue()

    def setRowVisibility(self, isVisible):
        if isVisible != (self._isVisible.get() == 1):
            if isVisible:
                self._label.grid()
                for k in self._widgets:
                    if self._scenarioVisibility[k]:
                        self._widgets[k].grid()
            else:
                self._label.grid_remove()
                for k in self._widgets:
                    self._widgets[k].grid_remove()
            self._isVisible.set(1 if isVisible else 0)

    def setScenarioVisibility(self, scenario, isVisible):
        if isVisible != self._scenarioVisibility[scenario]:
            self._scenarioVisibility[scenario] = isVisible
            if isVisible:
                if self._isVisible.get() == 1:
                    self._widgets[scenario].grid()
            else:
                self._widgets[scenario].grid_remove()

    def isRowVisible(self):
        return (self._isVisible.get() == 1)

    def isScenarioVisible(self, scenario):
        return (self._scenarioVisibility[scenario])


class ResultsWindow(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, ttk.Tkinter.Toplevel(master))

        self._ioModule = ReportsDescIo()
        self._mainWindow = master
        self._settingsWindow = None

        self.infoDict = {
            'vars': {},
            'widgets': {},
            'reportWidgets': {},
            'showMode': ShowMode.MINMAX,
            'scenarioVisibility': {
                FpSim.Scenarios.BEST: True,
                FpSim.Scenarios.WORST: True,
                FpSim.Scenarios.NORMAL: True,
            }
        }

        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(sticky=stretchSticky)

        top.title('Analisi Report')

        self.master.protocol("WM_DELETE_WINDOW", self.hide)
        top.bind('<KeyPress-Escape>', self._keyPressEsc)

        self.createWidgets()

        # Load and apply settings
        settings = SettingsIo().load('resSettings')
        if settings:
            self._applySettings(settings)

        # Moving the focus to this window
        top.focus_set()

    def _infoCmd(self):
        w = RisultatiInfoWin(self, 'Risultati')
        self.wait_window(w.master)

    def show(self):
        self.master.deiconify()
        self.master.lift()

    def hide(self):
        if self._settingsWindow:
            self._settingsWindow.master.destroy()
            self._settingsWindow = None
        self.master.withdraw()

    def _keyPressEsc(self, event):
        self.hide()

    def _deleteCommand(self):
        w = self.infoDict['widgets']['descList']
        fName = w.get(int(w.curselection()[0]))
        answer = tkMessageBox.askquestion(
            'Conferma',
            "Confermare l'eliminazione del report '{}'?".format(fName),
            default=tkMessageBox.NO,
            parent=self.winfo_toplevel())
        if answer == tkMessageBox.YES:
            self._ioModule.delete(
                self.infoDict['vars']['descListRowIds'][fName])
            self.loadDescriptorsList()
            self._clearUserWidgets()

    def _renameCommand(self):
        newName = self.infoDict['widgets']['nomeConfig'].var.read()
        w = self.infoDict['widgets']['descList']
        oldName = w.get(int(w.curselection()[0]))
        if newName in list(
                self.infoDict['widgets']['descList'].get(0, ttk.Tkinter.END)):
            tkMessageBox.showerror(
                'Errore',
                ("Impossibile rinominare, il nome di report specificato "
                 "è già in uso. Riprovare con un altro nome."),
                parent=self.winfo_toplevel())
            # Without specifying this as
            # parent, message box would brind
            # the root window above this one
        else:
            answer = tkMessageBox.askquestion(
                'Conferma',
                "Confermare la rinomina del report '{}' in '{}'?".format(
                    oldName, newName),
                default=tkMessageBox.NO,
                parent=self.winfo_toplevel())
            if answer == tkMessageBox.YES:
                reportId = self.infoDict['vars']['selectedDescRowId']
                self._ioModule.rename(reportId, newName)
                self.loadDescriptorsList()
                rId = list(self.infoDict['widgets']['descList'].get(
                    0, ttk.Tkinter.END)).index(newName)
                self.infoDict['widgets']['descList'].selection_set(rId)
                self._loadAndShowDescriptor()

    def _settingsCommand(self):
        settingsDict = {'showMode': self.infoDict['showMode']}
        for s in [FpSim.Scenarios.BEST, FpSim.Scenarios.WORST,
                  FpSim.Scenarios.NORMAL]:
            settingsDict['scenarioVisibility.{}'.format(s)] = \
                self.infoDict['scenarioVisibility'][s]
        for k in self.infoDict['reportWidgets']:
            settingsDict[k] = self.infoDict['reportWidgets'][k].isRowVisible()

        resVar = ttk.Tkinter.IntVar()
        self._settingsWindow = SettingsWindow(self, settingsDict, resVar)
        self.wait_window(self._settingsWindow.master)
        self._settingsWindow = None

        if resVar.get():
            self._applySettings(settingsDict)
            SettingsIo().save(settingsDict, 'resSettings')

    def _applySettings(self, settingsDict):
        self.infoDict['showMode'] = settingsDict['showMode']
        if self.infoDict['showMode'] == ShowMode.AVGONLY:
            labelText = 'medi'
        elif self.infoDict['showMode'] == ShowMode.MINMAX:
            labelText = 'min  -  max'
        elif self.infoDict['showMode'] == ShowMode.RELCONFINT:
            labelText = 'medi (err.%)'
        self.infoDict['widgets']['bestScenarioValuesHeader'].configure(
            text=labelText)
        self.infoDict['widgets']['worstScenarioValuesHeader'].configure(
            text=labelText)
        self.infoDict['widgets']['normScenarioValuesHeader'].configure(
            text=labelText)

        for s in [FpSim.Scenarios.BEST, FpSim.Scenarios.WORST,
                  FpSim.Scenarios.NORMAL]:
            self.infoDict['scenarioVisibility'][s] = \
                settingsDict['scenarioVisibility.{}'.format(s)]

        if self.infoDict['scenarioVisibility'][FpSim.Scenarios.WORST]:
            self.infoDict['widgets']['worstScenarioTitleHeader'].grid()
            self.infoDict['widgets']['worstScenarioValuesHeader'].grid()
        else:
            self.infoDict['widgets']['worstScenarioTitleHeader'].grid_remove()
            self.infoDict['widgets']['worstScenarioValuesHeader'].grid_remove()
        if self.infoDict['scenarioVisibility'][FpSim.Scenarios.NORMAL]:
            self.infoDict['widgets']['normScenarioTitleHeader'].grid()
            self.infoDict['widgets']['normScenarioValuesHeader'].grid()
        else:
            self.infoDict['widgets']['normScenarioTitleHeader'].grid_remove()
            self.infoDict['widgets']['normScenarioValuesHeader'].grid_remove()
        if self.infoDict['scenarioVisibility'][FpSim.Scenarios.BEST]:
            self.infoDict['widgets']['bestScenarioTitleHeader'].grid()
            self.infoDict['widgets']['bestScenarioValuesHeader'].grid()
        else:
            self.infoDict['widgets']['bestScenarioTitleHeader'].grid_remove()
            self.infoDict['widgets']['bestScenarioValuesHeader'].grid_remove()

        for k in self.infoDict['reportWidgets']:
            self.infoDict['reportWidgets'][k].setShowMode(
                self.infoDict['showMode'])
            self.infoDict['reportWidgets'][k].setRowVisibility(settingsDict[k])
            for s in [FpSim.Scenarios.WORST, FpSim.Scenarios.NORMAL,
                      FpSim.Scenarios.BEST]:
                self.infoDict['reportWidgets'][k].setScenarioVisibility(
                    s, self.infoDict['scenarioVisibility'][s])

        # Update canvas' scrolling region to the new vertical dimension of the
        # frame containing data widgets
        self.update_idletasks()
        self.infoDict['widgets']['canvas']['scrollregion'] = \
            self.infoDict['widgets']['canvas'].bbox('all')

    def _loadAndShowDescriptor(self, *args):
        w = self.infoDict['widgets']['descList']
        if w.curselection() != '':
            self.infoDict['widgets']['delete'].configure(
                state=ttk.Tkinter.NORMAL)

            confName = w.get(int(w.curselection()[0]))
            self.infoDict['widgets']['nomeConfig'].var.write(confName)
            self.infoDict['vars']['selectedDescRowId'] = \
                self.infoDict['vars']['descListRowIds'][confName]
            report = self._ioModule.load(
                self.infoDict['vars']['selectedDescRowId'])
            self._showDescriptor(report)

            self.infoDict['vars']['selectedDesc'].set(confName)

            report['fpBase'] = report['fp']['base']
            report['fpAccumulo'] = report['fp']['accumulo']
            report['fpRendita'] = report['fp']['rendita']
            for k in self._mainWindow.sections:
                self._mainWindow.sections[k].showDescriptor(report[k])
        else:
            self.infoDict['vars']['selectedDesc'].set('')
            self.infoDict['widgets']['delete'].configure(
                state=ttk.Tkinter.DISABLED)
            self._clearUserWidgets()

    def showRecentlyComputedReport(self, reportId, report):
        self.infoDict['widgets']['delete'].configure(state=ttk.Tkinter.NORMAL)

        self.loadDescriptorsList()

        self.infoDict['widgets']['nomeConfig'].var.write(report['name'])
        self.infoDict['vars']['selectedDescRowId'] = reportId
        self._showDescriptor(report)

        self.infoDict['vars']['selectedDesc'].set(report['name'])

    def loadDescriptorsList(self):
        self.infoDict['vars']['descList'].set('')

        filesList = self._ioModule.list()
        self.infoDict['vars']['descList'].set(
            ' '.join(sorted([e['name'] for e in filesList],
                     key=lambda x: x.lower())))
        self.infoDict['vars']['descListRowIds'] = \
            {e['name']: e['descId'] for e in filesList}
        self.infoDict['vars']['selectedDesc'].set('')
        self.infoDict['vars']['selectedDescRowId'] = None
        self.infoDict['widgets']['delete'].configure(
            state=ttk.Tkinter.DISABLED)

    def _clearUserWidgets(self):
        for k in self.infoDict['reportWidgets']:
            for s in [FpSim.Scenarios.BEST, FpSim.Scenarios.WORST,
                      FpSim.Scenarios.NORMAL]:
                self.infoDict['reportWidgets'][k].setValue(s)
        self.infoDict['widgets']['nomeConfig'].var.write('')

        self.infoDict['vars']['selectedDescRowId'] = None

    def _showDescriptor(self, desc):
        for k1 in ['best', 'worst', 'normal']:
            sDesc = DescIo.serializeDesc(desc['results'][k1])
            for k2 in self.infoDict['reportWidgets']:
                self.infoDict['reportWidgets'][k2].setValue(
                    FpSim.Scenarios.BEST
                    if k1 == 'best'
                    else (FpSim.Scenarios.WORST
                          if k1 == 'worst'
                          else FpSim.Scenarios.NORMAL),
                    sDesc['{}.average'.format(k2)],
                    sDesc['{}.confInt'.format(k2)])

    def _setupArea_DescList(self, master):
        master.rowconfigure(master.grid_size()[1], weight=1)

        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.grid(sticky=stretchSticky)

        # ----
        yScroll = ttk.Scrollbar(frame, orient=ttk.Tkinter.VERTICAL)
        yScroll.grid(row=0, column=2, sticky=ttk.Tkinter.N+ttk.Tkinter.S)

        # ----
        self.infoDict['vars']['descList'] = ttk.Tkinter.StringVar()
        self.infoDict['vars']['descListRowIds'] = None
        self.infoDict['vars']['selectedDesc'] = ttk.Tkinter.StringVar()
        self.infoDict['vars']['selectedDescRowId'] = None
        self.infoDict['widgets']['descList'] = ttk.Tkinter.Listbox(
            frame,
            listvariable=self.infoDict['vars']['descList'],
            activestyle='none', exportselection=0)
        self.infoDict['widgets']['descList'].bind(
            '<<ListboxSelect>>', self._loadAndShowDescriptor)
        self.infoDict['widgets']['descList'].grid(
            sticky=stretchSticky, row=0, column=0, columnspan=2)
        self.infoDict['widgets']['descList']['yscrollcommand'] = yScroll.set
        yScroll['command'] = self.infoDict['widgets']['descList'].yview

        # ----
        frame = ttk.Frame(frame)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.grid(sticky=stretchSticky, columnspan=3)

        # ----
        self.infoDict['widgets']['delete'] = RemotelyEnabledButton(
            frame, text='Elimina', state=ttk.Tkinter.DISABLED,
            command=self._deleteCommand)
        self.infoDict['widgets']['delete'].grid(
            row=0, column=0, sticky=stretchSticky)

        self.infoDict['widgets']['rename'] = RemotelyEnabledButton(
            frame, text='Rinomina', state=ttk.Tkinter.DISABLED,
            command=self._renameCommand)
        self.infoDict['widgets']['rename'].grid(
            row=0, column=1, sticky=stretchSticky)

        # ----
        self.loadDescriptorsList()

    def _setupArea_aboveUserWidgets(self, master):
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)
        frame.grid(sticky=ttk.Tkinter.W+ttk.Tkinter.E)

        ttk.Label(frame, text='Nome Report', justify=ttk.Tkinter.LEFT).grid(
            row=0, column=0, sticky=ttk.Tkinter.W)

        self.infoDict['widgets']['nomeConfig'] = \
            DescriptorNameEntry(master=frame, name='Nome Report')
        self.infoDict['widgets']['nomeConfig'].grid(
            row=0, column=1, sticky=stretchSticky)

        # Connecting report name entry widget to both
        # rename button and delete button
        self.infoDict['widgets']['nomeConfig'].join(
            toNode=self.infoDict['widgets']['rename'])

    def _setupArea_UserWidgets(self, master):
        self.infoDict['widgets']['bestScenarioTitleHeader'] = \
            ttk.Label(master, text='Scenario Migliore',
                      justify=ttk.Tkinter.CENTER,
                      style='emph.TLabel', padding=(10, 0, 10, 0))
        self.infoDict['widgets']['bestScenarioTitleHeader'].grid(
            row=0, column=1)
        self.infoDict['widgets']['normScenarioTitleHeader'] = \
            ttk.Label(master, text='Scenario Medio',
                      justify=ttk.Tkinter.CENTER,
                      style='emph.TLabel', padding=(10, 0, 10, 0))
        self.infoDict['widgets']['normScenarioTitleHeader'].grid(
            row=0, column=2)
        self.infoDict['widgets']['worstScenarioTitleHeader'] = \
            ttk.Label(master, text='Scenario Peggiore',
                      justify=ttk.Tkinter.CENTER,
                      style='emph.TLabel', padding=(10, 0, 10, 0))
        self.infoDict['widgets']['worstScenarioTitleHeader'].grid(
            row=0, column=3)
        self.infoDict['widgets']['bestScenarioValuesHeader'] = \
            ttk.Label(master, text='min  -  max', justify=ttk.Tkinter.CENTER,
                      style='emph.TLabel')
        self.infoDict['widgets']['bestScenarioValuesHeader'].grid(
            row=1, column=1)
        self.infoDict['widgets']['normScenarioValuesHeader'] = \
            ttk.Label(master, text='min  -  max', justify=ttk.Tkinter.CENTER,
                      style='emph.TLabel')
        self.infoDict['widgets']['normScenarioValuesHeader'].grid(
            row=1, column=2)
        self.infoDict['widgets']['worstScenarioValuesHeader'] = \
            ttk.Label(master, text='min  -  max', justify=ttk.Tkinter.CENTER,
                      style='emph.TLabel')
        self.infoDict['widgets']['worstScenarioValuesHeader'].grid(
            row=1, column=3)

        repW = self.infoDict['reportWidgets']
        hl = Headline(master, text='Primo anno', justify=ttk.Tkinter.LEFT)
        repW['fp.primoAnno.salario'] = \
            DataRow(master, 'Salario lordo',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.primoAnno.contribuzione.dipendente'] = \
            DataRow(master, 'Contrib. dipendente',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.primoAnno.contribuzione.datore'] = \
            DataRow(master, 'Contrib. datore',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.primoAnno.contribuzione.tfr'] = \
            DataRow(master, 'Contrib. TFR', lambda x: '{:.0f}'.format(x), hl)
        repW['fp.primoAnno.deduzioni'] = \
            DataRow(master, 'Totale deduzioni',
                    lambda x: '{:.0f}'.format(x), hl)

        hl = Headline(master, text='Prospetto Fondo Pensione, fase accumulo',
                      justify=ttk.Tkinter.LEFT)
        repW['fp.accumulo.contribuzione.dipendente'] = \
            DataRow(master, 'Contrib. dipendente',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.accumulo.contribuzione.datore'] = \
            DataRow(master, 'Contrib. datore',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.accumulo.contribuzione.tfr'] = \
            DataRow(master, 'Contrib. TFR',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.accumulo.contribuzione.deduzioni'] = \
            DataRow(master, 'Totale deduzioni',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.accumulo.montante.finale'] = \
            DataRow(master, 'Montante finale',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.accumulo.montante.erogato'] = \
            DataRow(master, 'Montante erogato',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['fp.accumulo.tir.globale'] = \
            DataRow(master, 'TIR, globale',
                    lambda x: '{:.2f}%'.format(x*100), hl)
        repW['fp.accumulo.tir.dipendente'] = \
            DataRow(master, 'TIR, dipendente',
                    lambda x: '{:.2f}%'.format(x*100), hl)
        repW['fp.accumulo.isc'] = \
            DataRow(master, 'ISC', lambda x: '{:.2f}%'.format(x*100), hl)

        hl = Headline(master, text='Prospetto Fondo Pensione, fase rendita',
                      justify=ttk.Tkinter.LEFT)
        repW['fp.rendita'] = \
            DataRow(master, 'Rendita annua', lambda x: '{:.0f}'.format(x), hl)

        hl = Headline(master, text='Ultimo salario', justify=ttk.Tkinter.LEFT)
        repW['ultimoSalario.lordo'] = \
            DataRow(master, 'Lordo', lambda x: '{:.0f}'.format(x), hl)
        repW['ultimoSalario.netto'] = \
            DataRow(master, 'Netto', lambda x: '{:.0f}'.format(x), hl)

        hl = Headline(master, text='Pensione INPS', justify=ttk.Tkinter.LEFT)
        repW['pensioneInps.lorda'] = \
            DataRow(master, 'Annua, lorda', lambda x: '{:.0f}'.format(x), hl)
        repW['pensioneInps.netta'] = \
            DataRow(master, 'Annua, netta', lambda x: '{:.0f}'.format(x), hl)

        hl = Headline(master, text='Prospetto accumulo TFR',
                      justify=ttk.Tkinter.LEFT)
        repW['tfr.accumulo.montante.finale'] = \
            DataRow(master, 'Montante finale',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['tfr.accumulo.montante.erogato'] = \
            DataRow(master, 'Montante erogato',
                    lambda x: '{:.0f}'.format(x), hl)
        repW['tfr.accumulo.tir.senzaContributi'] = \
            DataRow(master, 'TIR, senza contributi dip.',
                    lambda x: '{:.2f}%'.format(x*100), hl)
        repW['tfr.accumulo.tir.conContributiNoRiv'] = \
            DataRow(master, 'TIR, con contributi dip. (no riv.)',
                    lambda x: '{:.2f}%'.format(x*100), hl)
        repW['tfr.accumulo.isc'] = \
            DataRow(master, 'ISC', lambda x: '{:.2f}%'.format(x*100), hl)
        repW['tfr.rendita.durataAnni'] = \
            DataRow(master, 'Durata anni', lambda x: '{:.0f}'.format(x), hl)

    def _setupArea_BelowUserWidgets(self, master):
        master.columnconfigure(1, weight=1)

        self.infoDict['widgets']['fieldsInfo'] = \
            ttk.Button(master, text='Info', command=self._infoCmd)
        self.infoDict['widgets']['fieldsInfo'].grid(
            sticky=ttk.Tkinter.W, row=0, column=0)

        self.infoDict['widgets']['settings'] = \
            ttk.Button(master, text='Filtro', command=self._settingsCommand)
        self.infoDict['widgets']['settings'].grid(
            sticky=ttk.Tkinter.W, row=0, column=1)

        self.infoDict['widgets']['export'] = \
            ttk.Button(master, text='Esporta', state=ttk.Tkinter.DISABLED)
        self.infoDict['widgets']['export'].grid(
            sticky=ttk.Tkinter.E, row=0, column=2)

    def createWidgets(self):
        panedWin = ttk.PanedWindow(self, orient=ttk.Tkinter.HORIZONTAL)
        panedWin.grid(sticky=stretchSticky)

        # ----
        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        panedWin.add(frame)

        # ----
        self._setupArea_DescList(frame)

        # ----
        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        panedWin.add(frame)
        paneMasterFrame = frame

        frame = ttk.Frame(paneMasterFrame)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        yScroll = ttk.Scrollbar(frame, orient=ttk.Tkinter.VERTICAL)
        yScroll.grid(column=1, row=0, sticky=ttk.Tkinter.N+ttk.Tkinter.S)
        frame.grid(sticky=stretchSticky)

        # ----
        canv = ttk.Tkinter.Canvas(frame)
        canv.grid(column=0, row=0, sticky=stretchSticky)
        canvId = canv.create_window(0, 0, anchor=ttk.Tkinter.NW)
        frame = ttk.Frame(canv)
        frame.grid()
        canv.itemconfigure(canvId, window=frame)
        canv['yscrollcommand'] = yScroll.set
        yScroll['command'] = canv.yview
        self.infoDict['widgets']['canvas'] = canv

        masterFrame = frame

        # ----
        self._setupArea_aboveUserWidgets(masterFrame)

        # ----
        frame = ttk.LabelFrame(masterFrame, text='Risultati')
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.grid(sticky=ttk.Tkinter.W+ttk.Tkinter.E)

        self._setupArea_UserWidgets(frame)

        # ----
        footerFrame = ttk.Frame(paneMasterFrame)
        footerFrame.grid(sticky=ttk.Tkinter.W+ttk.Tkinter.E+ttk.Tkinter.S)

        self._setupArea_BelowUserWidgets(footerFrame)

        # ----
        # Needed to make the next call return correct dimensions
        self.update_idletasks()
        canv['scrollregion'] = canv.bbox('all')
        neededWidth = canv.bbox('all')[2]-canv.bbox('all')[0]
        if canv.winfo_reqwidth() < neededWidth:
            canv.configure(width=neededWidth*1.05)
        canv.configure(height=400)
