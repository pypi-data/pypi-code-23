# -*- coding: utf-8 -*-

import ttk
from . import stretchSticky
from functools import partial
from ..simulation.fpSim import FpSim
from resultsCommon import ShowMode


class SettingsWindow(ttk.Frame):
    def __init__(self, master, settingsDict, resVar, *args, **kwargs):
        ttk.Frame.__init__(self, ttk.Tkinter.Toplevel(master))

        self._settingsDict = settingsDict
        self._resVar = resVar

        self.infoDict = {}
        self.ctrlVarsGroups = []

        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        top.resizable(False, False)
        top.transient()

        self.columnconfigure(0, weight=1)
        self.grid(sticky=stretchSticky)

        top.title('Filtro')
        top.protocol("WM_DELETE_WINDOW", self._cancelCommand)
        top.bind('<KeyPress-Escape>', self._keyPressEsc)
        top.bind('<KeyPress-Return>', self._keyPressReturn)

        self.grab_set()

        self.createWidgets()

        # Moving the focus to this window
        top.focus_set()

    def _cancelCommand(self):
        self._resVar.set(0)
        self.winfo_toplevel().destroy()

    def _okCommand(self):
        self._resVar.set(1)

        for k in self._settingsDict:
            if k == 'showMode':
                self._settingsDict[k] = self.infoDict[k].get()
            else:
                self._settingsDict[k] = (self.infoDict[k].get() == 1)

        self.winfo_toplevel().destroy()

    def _keyPressEsc(self, event):
        self._cancelCommand()

    def _keyPressReturn(self, event):
        self._okCommand()

    def _toggleSettingsGroup(self, groupId):
        val = 1 -\
            sum([v.get() for v in self.ctrlVarsGroups[groupId]]) / \
            len(self.ctrlVarsGroups[groupId])
        for v in self.ctrlVarsGroups[groupId]:
            v.set(val)

    def createWidgets(self):
        settingsFrm = ttk.Frame(self)
        settingsFrm.columnconfigure(0, weight=1)
        settingsFrm.columnconfigure(1, weight=1)
        settingsFrm.grid(sticky=stretchSticky)

        def _addCheckbutton(key, text, row, col, addToGroup=True):
            self.infoDict[key] = ttk.Tkinter.IntVar()
            w = ttk.Checkbutton(settingsFrm, text=text,
                                variable=self.infoDict[key])
            w.grid(row=row, column=col, sticky=ttk.Tkinter.W)
            self.infoDict[key].set(self._settingsDict[key])
            if addToGroup:
                self.ctrlVarsGroups[-1].append(self.infoDict[key])

        def _addGroupHeadline(text):
            frame = ttk.Frame(settingsFrm)
            frame.columnconfigure(0, weight=1)
            frame.grid(sticky=stretchSticky, columnspan=2)
            ttk.Label(frame, text=text, justify=ttk.Tkinter.LEFT,
                      style='emph.TLabel').grid(sticky=ttk.Tkinter.W)
            self.ctrlVarsGroups += [[]]
            btn = ttk.Button(
                frame, text='Sel. tutti/nessuno',
                command=partial(self._toggleSettingsGroup,
                                len(self.ctrlVarsGroups)-1))
            btn.grid(row=0, column=1)

        _addGroupHeadline('Primo anno')
        _addCheckbutton('fp.primoAnno.salario', 'Salario', 1, 0)
        _addCheckbutton('fp.primoAnno.contribuzione.dipendente',
                        'Contribuzione dipendente', 2, 0)
        _addCheckbutton('fp.primoAnno.contribuzione.datore',
                        'Contribuzione datore', 3, 0)
        _addCheckbutton('fp.primoAnno.contribuzione.tfr',
                        'Contribuzione TFR', 1, 1)
        _addCheckbutton('fp.primoAnno.deduzioni', 'Totale deduzioni', 2, 1)

        _addGroupHeadline('Fondo pensione, accumulo')
        _addCheckbutton('fp.accumulo.contribuzione.dipendente',
                        'Contribuzione dipendente', 5, 0)
        _addCheckbutton('fp.accumulo.contribuzione.datore',
                        'Contribuzione datore', 6, 0)
        _addCheckbutton('fp.accumulo.contribuzione.tfr',
                        'Contribuzione TFR', 7, 0)
        _addCheckbutton('fp.accumulo.contribuzione.deduzioni',
                        'Totale deduzioni', 8, 0)
        _addCheckbutton('fp.accumulo.montante.finale', 'Montante finale', 9, 0)
        _addCheckbutton('fp.accumulo.montante.erogato',
                        'Montante erogato', 5, 1)
        _addCheckbutton('fp.accumulo.tir.globale', 'TIR, globale', 6, 1)
        _addCheckbutton('fp.accumulo.tir.dipendente', 'TIR, dipendente', 7, 1)
        _addCheckbutton('fp.accumulo.isc', 'ISC', 8, 1)

        ttk.Label(settingsFrm, text='Fondo pensione, rendita',
                  justify=ttk.Tkinter.LEFT,
                  style='emph.TLabel').grid(
                    sticky=ttk.Tkinter.W, row=10, column=0, columnspan=2)
        _addCheckbutton('fp.rendita', 'Rendita annua', 11, 0, False)

        _addGroupHeadline('Ultimo salario')
        _addCheckbutton('ultimoSalario.lordo', 'Lordo', 13, 0)
        _addCheckbutton('ultimoSalario.netto', 'Netto', 13, 1)

        _addGroupHeadline('Pensione INPS')
        _addCheckbutton('pensioneInps.lorda', 'Lorda', 15, 0)
        _addCheckbutton('pensioneInps.netta', 'Netta', 15, 1)

        _addGroupHeadline('TFR')
        _addCheckbutton('tfr.accumulo.montante.finale',
                        'Montante finale', 17, 0)
        _addCheckbutton('tfr.accumulo.montante.erogato',
                        'Montante erogato', 18, 0)
        _addCheckbutton('tfr.accumulo.tir.senzaContributi',
                        'TIR, senza contributi dip.', 19, 0)
        _addCheckbutton('tfr.accumulo.tir.conContributiNoRiv',
                        'TIR, con contributi dip.', 17, 1)
        _addCheckbutton('tfr.accumulo.isc', 'ISC', 18, 1)
        _addCheckbutton('tfr.rendita.durataAnni', 'Durata anni', 19, 1)

        _addGroupHeadline('Scenari')
        _addCheckbutton('scenarioVisibility.{}'.format(FpSim.Scenarios.BEST),
                        'Migliore', 21, 0)
        _addCheckbutton('scenarioVisibility.{}'.format(FpSim.Scenarios.WORST),
                        'Peggiore', 22, 0)
        _addCheckbutton('scenarioVisibility.{}'.format(FpSim.Scenarios.NORMAL),
                        'Medio', 21, 1)

        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        ttk.Label(settingsFrm, text='Valori visualizzati',
                  justify=ttk.Tkinter.LEFT, style='emph.TLabel').grid(
                    sticky=ttk.Tkinter.W, column=0, columnspan=2)
        frame.grid(column=0, sticky=stretchSticky, columnspan=2)
        self.infoDict['showMode'] = ttk.Tkinter.IntVar()
        self.infoDict['showMode'].set(self._settingsDict['showMode'])
        ttk.Radiobutton(
            frame,
            text='Media',
            value=ShowMode.AVGONLY,
            variable=self.infoDict['showMode']).grid(row=0, column=0)
        ttk.Radiobutton(
            frame,
            text='Min & Max',
            value=ShowMode.MINMAX,
            variable=self.infoDict['showMode']).grid(row=0, column=1)
        ttk.Radiobutton(
            frame,
            text='% Errore',
            value=ShowMode.RELCONFINT,
            variable=self.infoDict['showMode']).grid(row=0, column=2)

        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.grid(column=0, sticky=stretchSticky, columnspan=2)
        ttk.Button(frame, text='Annulla', command=self._cancelCommand).grid(
            sticky=ttk.Tkinter.E)
        ttk.Button(frame, text='Ok', command=self._okCommand).grid(
            row=0, column=1, sticky=ttk.Tkinter.W)

        # Placing the window
        top = self.winfo_toplevel()
        top.update_idletasks()
        w = top.winfo_screenwidth()
        h = top.winfo_screenheight()
        winSize = [int(_) for _ in top.geometry().split('+')[0].split('x')]
        x = w/4 - winSize[0]/4
        y = h/4 - winSize[1]/4
        top.geometry("{:d}x{:d}+{:d}+{:d}".format(*(winSize+[x, y])))
