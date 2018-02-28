# -*- coding: utf-8 -*-

import ttk
import tkMessageBox
from .. import stretchSticky
from .. import signals
from pisim.dataLoadStore.common import DescIo
from ..commonEntry import RemotelyEnabledButton, DescriptorNameEntry


class BasePane(ttk.PanedWindow, signals.Node):
    def __init__(self, master, ioModule, *args, **kwargs):
        signals.Node.__init__(self)

        ttk.PanedWindow.__init__(
            self, master, *args, orient=ttk.Tkinter.HORIZONTAL, **kwargs)

        self._ioModule = ioModule

        self.infoDict = {'vars': {}, 'widgets': {}}
        self._userWidgets = {}

        self._saveBtnEnabler = signals.And()

        self._fieldsSetValidityStatusDispatcher = signals.Dup()
        self._fieldsSetValidityStatusDispatcher.join(
            toNode=self,
            signalName='fieldsSetValidityStatus_toExtern')

    def _procRxSignals(self, s):
        if s.fromNode == self._fieldsSetValidityStatusDispatcher:
            try:
                self._userDefinedOutSignals['fieldsValidityStatus'].state = \
                    s.state
            except KeyError:
                pass

    def _checkInSignal(self, signal):
        return True

    def _checkOutSignal(self, signal):
        return True

    def _saveCommand(self):
        newFName = self.infoDict['widgets']['nomeConfig'].var.get()

        # Checking the existence of a config file with newFName
        if newFName in self.infoDict['vars']['descListRowIds']:
            answer = tkMessageBox.askquestion(
                'Conferma',
                'File di configurazione esistente, sovrascrivere?',
                default=tkMessageBox.NO)
            if answer == tkMessageBox.NO:
                return

        try:
            desc = self.getDesc(False)
            desc['name'] = newFName
            desc['descId'] = self.infoDict['vars']['descListRowIds'].get(
                newFName, None)
            self._ioModule.save(desc, True)
            self.loadDescriptorsList()
        except IOError:
            tkMessageBox.showerror('Errore', 'Impossibile salvare il file')

    def _deleteCommand(self):
        w = self.infoDict['widgets']['descList']
        fName = w.get(int(w.curselection()[0]))
        answer = tkMessageBox.askquestion(
            'Conferma',
            ("Confermare l'eliminazione del file "
             "di configurazione '{}'?").format(fName),
            default=tkMessageBox.NO)
        if answer == tkMessageBox.YES:
            self._ioModule.delete(
                self.infoDict['vars']['descListRowIds'][fName])
            self.loadDescriptorsList()
            self._clearUserWidgets()

    def _infoCmd(self):
        raise NotImplementedError

    def _loadAndShowDescriptor(self, *args):
        self.infoDict['widgets']['delete']['state'] = ttk.Tkinter.NORMAL

        w = self.infoDict['widgets']['descList']
        confName = w.get(int(w.curselection()[0]))
        self.infoDict['widgets']['nomeConfig'].var.set(confName)
        self.infoDict['vars']['selectedDescRowId'] = \
            self.infoDict['vars']['descListRowIds'][confName]
        self._showDescriptor(self._ioModule.load(
            self.infoDict['vars']['selectedDescRowId'], False))

        self.infoDict['vars']['selectedDesc'].set(confName)

    def loadDescriptorsList(self):
        self.infoDict['vars']['descList'].set('')

        if self._ioModule:
            filesList = self._ioModule.list()
            self.infoDict['vars']['descList'].set(' '.join(sorted(
                [e['name'] for e in filesList],
                key=lambda x: x.lower())))
            self.infoDict['vars']['descListRowIds'] = \
                {e['name']: e['descId'] for e in filesList}
        try:
            self.infoDict['widgets']['delete']['state'] = ttk.Tkinter.DISABLED
        except KeyError:
            # Needed to properly manage first call, when delete button
            # has not been already created
            pass
        self.infoDict['vars']['selectedDesc'].set('')
        self.infoDict['vars']['selectedDescRowId'] = None

    def _clearUserWidgets(self):
        for k in self._userWidgets:
            self._userWidgets[k].var.write('')
        self.infoDict['widgets']['nomeConfig'].var.write('')

        self.infoDict['vars']['selectedDescRowId'] = None

    def _showDescriptor(self, desc):
        for k in self._userWidgets:
            self._userWidgets[k].var.write(desc[k])

    def showDescriptor(self, desc):
        # Similar to _showDescriptor(), but with following differences:
        # - Meant to be a class' API
        # - Check the presence of 'name' key and if it's so
        #   it's put in the 'configName' widget

        try:
            self.infoDict['widgets']['nomeConfig'].var.write(desc['name'])
        except KeyError:
            pass
        self._showDescriptor(DescIo.serializeDesc(desc))

    def getDesc(self, deserialized=True):
        desc = {k: self._userWidgets[k].var.read() for k in self._userWidgets}
        return DescIo.deserializeDesc(desc) if deserialized else desc

    def addWidget(self, name, instance):
        self.infoDict['widgets'][name] = instance
        self._userWidgets[name] = self.infoDict['widgets'][name]

    def _setupArea_AboveDescList(self, master):
        raise NotImplementedError

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
        self.loadDescriptorsList()
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
        self.infoDict['widgets']['delete'] = ttk.Button(
            frame, text='Elimina',
            state=ttk.Tkinter.DISABLED, command=self._deleteCommand)
        self.infoDict['widgets']['delete'].grid(
            row=0, column=0, sticky=stretchSticky)

        # ----
        self.infoDict['widgets']['save'] = RemotelyEnabledButton(
            frame, text='Salva',
            state=ttk.Tkinter.DISABLED, command=self._saveCommand)
        self.infoDict['widgets']['save'].grid(
            row=0, column=1, sticky=stretchSticky)

    def _setupArea_aboveUserWidgets(self, master):
        frame = ttk.LabelFrame(master, text='Configurazione')
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.grid(sticky=ttk.Tkinter.W+ttk.Tkinter.E)

        ttk.Label(frame, text='Nome', justify=ttk.Tkinter.LEFT).grid(
            row=0, column=0, sticky=ttk.Tkinter.W)

        self.infoDict['widgets']['nomeConfig'] = DescriptorNameEntry(
            master=frame,
            name='nomeConfig')
        self.infoDict['widgets']['nomeConfig'].grid(
            row=0, column=1, sticky=stretchSticky)

    def _setupArea_UserWidgets(self, master):
        raise NotImplementedError

    def _setupArea_BelowUserWidgets(self, master):
        frame = ttk.LabelFrame(master, text='Azioni')
        frame.columnconfigure(0, weight=1)
        frame.grid(sticky=ttk.Tkinter.W+ttk.Tkinter.E)

        self.infoDict['widgets']['fieldsInfo'] = ttk.Button(
            frame, text='Info', command=self._infoCmd)
        self.infoDict['widgets']['fieldsInfo'].grid(
            sticky=ttk.Tkinter.E, row=0, column=0)

        self.infoDict['widgets']['clearFields'] = ttk.Button(
            frame, text='Cancella', command=self._clearUserWidgets)
        self.infoDict['widgets']['clearFields'].grid(
            sticky=ttk.Tkinter.E, row=0, column=1)

    def createWidgets(self):
        # ----
        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        self.add(frame)

        # ----
        self._setupArea_AboveDescList(frame)

        # ----
        self._setupArea_DescList(frame)

        self._fieldsSetValidityStatusDispatcher.join(
            toNode=self._saveBtnEnabler)
        self._saveBtnEnabler.join(toNode=self.infoDict['widgets']['save'])

        # ----
        frame = ttk.Frame(self)
        self.add(frame)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        yScroll = ttk.Scrollbar(frame, orient=ttk.Tkinter.VERTICAL)
        yScroll.grid(column=1, row=0, sticky=ttk.Tkinter.N+ttk.Tkinter.S)

        # ----
        canv = ttk.Tkinter.Canvas(frame)
        canv.grid(column=0, row=0, sticky=stretchSticky)
        canvId = canv.create_window(0, 0, anchor=ttk.Tkinter.NW)
        frame = ttk.Frame(canv)
        frame.grid()
        canv.itemconfigure(canvId, window=frame)
        canv['yscrollcommand'] = yScroll.set
        yScroll['command'] = canv.yview

        masterFrame = frame

        # ----
        self._setupArea_aboveUserWidgets(masterFrame)

        self.infoDict['widgets']['nomeConfig'].join(
            toNode=self._saveBtnEnabler)

        # ----
        frame = ttk.LabelFrame(masterFrame, text='Generali')
        frame.grid(sticky=stretchSticky)

        self._setupArea_UserWidgets(frame)

        # ----
        self._setupArea_BelowUserWidgets(masterFrame)

        # ----
        # Needed to make the next call return correct dimensions
        self.update_idletasks()
        canv['scrollregion'] = canv.bbox('all')
        neededWidth = canv.bbox('all')[2]-canv.bbox('all')[0]
        if canv.winfo_reqwidth() < neededWidth:
            canv['width'] = neededWidth
