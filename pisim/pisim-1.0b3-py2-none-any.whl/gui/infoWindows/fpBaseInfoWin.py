# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin

class FpBaseInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per la configurazione delle caratteristiche generali "
             "di un fondo pensione, "
             "comuni a tutte le linee di investimento.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Descrizione Dei Campi\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Tipo\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tipologia del fondo pensione. "
             "I possibili valori sono: 'chiuso' per i fondi pensione "
             "chiusi (altrimenti detti negoziali); 'aperto' per gli altri.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Contribuzione dipendente) Minima per contrib. datore\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Valore minimo della contribuzione dipendente volontaria "
             "al fondo per avere riconosciuta anche la contribuzione "
             "a carico del datore di lavoro. "
             "Valore significativo solo nel caso di fondo pensione chiuso.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Contribuzione dipendente) Base calcolo < minimo\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tipologia di retribuzione dipendente che il simulatore "
             "deve considerare per il calcolo effettivo della contribuzione "
             "dipendente al fondo nel caso in cui la percentuale "
             "di contribuzione dipendente sia inferiore a "
             "'(Contribuzione dipendente) Minima per contrib. datore'. "
             "Valore significativo solo nel caso di fondo pensione chiuso.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Contribuzione dipendente) Base calcolo >= minimo\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Come sopra, ma relativamente alla contribuzione dipendente "
             "superiore al minimo. "
             "Valore significativo solo nel caso di fondo pensione chiuso."
             "Nel caso di fondo pensione aperto, la tipologia di retribuzione"
             "dipendente considerata è sempre 'lordo'.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Contribuzione datore) Base\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tipologia di retribuzione dipendente che il simulatore "
             "deve considerare per il calcolo della contribuzione al fondo "
             "a carico del datore di lavoro. "
             "Valore significativo solo nel caso di fondo pensione chiuso.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Contribuzione datore) Valore\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Percentuale della '(Contribuzione datore) Base' che determina "
             "la contribuzione del datore di lavoro al fondo - questo "
             "ovviamente nel caso in cui la percentuale "
             "di contribuzione del dipendente sia superiore a "
             "('(Contribuzione dipendente) Minima per contrib. datore'). "
             "Valore significativo solo nel caso di fondo pensione chiuso.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))
