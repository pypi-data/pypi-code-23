# -*- coding: utf-8 -*-

import ttk
from .. import signals
from basePane import BasePane
from pisim.dataLoadStore import dipendente
from ..commonEntry import EnhOptionMenu, DateEntry
from .. import stretchSticky
from ..infoWindows.dipendenteInfoWin import DipendenteInfoWin


class DipendentePane(BasePane):
    def __init__(self, master, *args, **kwargs):
        BasePane.__init__(self, master, dipendente.DipendenteDescIo(),
                          *args, **kwargs)

    def _infoCmd(self):
        w = DipendenteInfoWin(self, 'Dipendente')
        self.wait_window(w.master)

    def _setupArea_AboveDescList(self, master):
        pass

    def _setupArea_UserWidgets(self, master):
        ttk.Label(master, text='Data di nascita',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=0, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(master, text='Sesso', justify=ttk.Tkinter.LEFT).grid(
            row=1, column=0, sticky=ttk.Tkinter.W)
        ttk.Label(master, text='Data di inizio piano',
                  justify=ttk.Tkinter.LEFT).grid(
                    row=2, column=0, sticky=ttk.Tkinter.W)

        self.addWidget(
            'nascita',
            DateEntry(master, description='Data di nascita'))
        self.infoDict['widgets']['nascita'].grid(
            row=0, column=1, sticky=stretchSticky)

        self.addWidget(
            'sesso',
            EnhOptionMenu(
                master,
                values=['Uomo', 'Donna'],
                defaultId=0,
                description='Sesso',
                setConvF=lambda x: 'Uomo'
                                   if x == 'm' else
                                   ('Donna' if x == 'f' else 'Uomo'),
                getConvF=lambda x: 'm' if x == 'Uomo' else 'f'))
        self.infoDict['widgets']['sesso'].grid(
            row=1, column=1, sticky=stretchSticky)

        self.addWidget(
            'inizioPiano',
            DateEntry(master, description='Data di inizio piano'))
        self.infoDict['widgets']['inizioPiano'].grid(
            row=2, column=1, sticky=stretchSticky)

        andNode = signals.And()
        for w in ['nascita', 'inizioPiano']:
            self.infoDict['widgets'][w].join(toNode=andNode)
        andNode.join(toNode=self._fieldsSetValidityStatusDispatcher)
