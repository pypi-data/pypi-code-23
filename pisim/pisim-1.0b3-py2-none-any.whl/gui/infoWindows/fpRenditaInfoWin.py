# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin


class FpRenditaInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per la configurazione delle caratteristiche della fase "
             "di rendita di un fondo pensione.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Descrizione Dei Campi\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Tassi di conversione\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tabella in cui inserire i tassi di conversione, distinti "
             "per sesso ed età di pensionamento. Il tasso di conversione "
             "è il rapporto percentuale fra la rendita pensionistica annuale "
             "erogata dal fondo e il montante accumulato alla fine "
             "del periodo di accumulo. (La rendita effettiva sarà "
             "questa decurtata dalle spese.) Almeno un tasso deve essere "
             "inserito per permettere il salvataggio del descrittore. "
             "I tassi di conversione si trovano nei documenti informativi "
             "dei fondi pensione.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Spese annue) Fisse\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Valore, in valuta, del costo di gestione annuo del montante "
             "ai fini di erogazione della rendita pensionistica.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Spese annue) Variabili\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Costo percentuale applicato alla rendita pensionistica annua.\n"
            "Formato: Percentuale 0-100.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Rivalutazione annua\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Rivalutazione annua lorda della rendita pensionistica. "
             "Questa informazione serve al simulatore per confrontare "
             "la rendita pensionistica complementare con quella alternativa "
             "ed ipotetica derivante dal solo TFR.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))
