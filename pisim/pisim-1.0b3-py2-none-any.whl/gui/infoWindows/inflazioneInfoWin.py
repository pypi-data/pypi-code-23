# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin

class InflazioneInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per la configurazione dei parametri per la simulazione "
             "del tasso di inflazione per il periodo di accumulo "
             "su fondo pensione.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Descrizione Dei Campi\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Tasso medio\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ('Tasso di inflazione medio per tutta la fase di accumulo '
             'del fondo pensione.\n'
             'Formato: Percentuale 0-100.\n'),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Variazione\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Massimo scostamento, in positivo o in negativo, del tasso "
             "di inflazione simulato per un anno rispetto al tasso medio "
             "di inflazione.\n"
             "Un valore di 0 determina un valore fisso di inflazione, "
             "per tutti gli anni di accumulo, pari a quello specificato "
             "nel campo 'Tasso medio'.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Altri Dettagli\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("L'impostazione del campo 'Variazione' ad un valore diverso "
             "da zero determina che i tassi di inflazione per gli anni "
             "di accumulo del fondo pensione siano calcolati in modo casuale, "
             "tutti all'interno dell'intervallo 'valore medio'-'variazione' - "
             "'valore medio'+'variazione'.\n"
             "Il motore di simulazione fa sì che il tasso d'inflazione "
             "nominale annuo medio, corrispondente alla serie di tassi "
             "di inflazione calcolati per gli anni di accumulo, "
             "sia il più vicino possibile al tasso medio specificato.\n"),
            (BaseInfoWin.Tags.NORMAL,))
