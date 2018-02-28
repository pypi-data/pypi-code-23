# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin


class PensioneInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per la configurazione delle caratteristiche essenziali "
             "relative a alla pensione INPS.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Descrizione Dei Campi\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Età pensionamento\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Età (anni) in cui il lavoratore prevede di andare in pensione.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Tasso di sostituzione\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Rapporto percentuale fra ultimo salario (lordo) annuo "
             "percepito e prima annualità (lorda) della pensione INPS.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Altri Dettagli\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("La 'età di pensionamento' viene confrontata, in fase di "
             "generazione del piano pensione, con la 'data di nascita' "
             "e la 'data di inizio' piano entrambi specificati nella tab "
             "'Dipendente'. Se i valori non sono coerenti, "
             "la simulazione viene interrotta generando un errore. "
             "Vedere le 'info' della tab 'Dipendente' per altri dettagli.\n\n"
             "Il 'tasso di sostituzione' è un valore che dipende "
             "da una molteplicità di fattori, come, ad esempio, "
             "la previsione di crescita salariale, gli anni di contribuzione, "
             "l'età di pensionamento, ed altri. E' possibile "
             "averne una stima usando il motore di simulazione "
             "messo a disposizione nel sito dell'INPS "
             "(registrazione necessaria)."),
            (BaseInfoWin.Tags.NORMAL,))
