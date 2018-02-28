# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin

class DipendenteInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per la configurazione della anagrafica dipendente "
             "essenziale per la simulazione di un "
             "piano pensione complementare.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Descrizione Dei Campi\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Data di nascita\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ('Data di nascita del lavoratore di cui si va a calcolare '
             'il piano pensionistico.\n'
             'Formato: mm/gg/aaaa.\n'),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Sesso\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ('Sesso del lavoratore. Serve per determinare '
             'i corretti coefficienti di conversione '
             'montante fondo pensione -> rendita pensionistica.\n'),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Data inizio piano\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ('Data da cui far partire la simulazione del fondo pensione '
             '(fase di accumulo).\n'
             'Formato: mm/gg/aaaa.\n'),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Limiti\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("L'elaborazione della simulazione fondo pensione "
             "oppure il salvataggio delle informazioni dipendente "
             "non sono eseguiti, generando un errore, "
             "nel caso in cui i valori dei campi 'Data di nascita', "
             "'Data partenza piano' e 'Età pensionamento' "
             "(tab 'Pensione') non siano coerenti. Ad esempio se:\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("-\tLa data di inizio piano è anticipata"
             "rispetto a quella di nascita;\n"
             "-\tLa durata della fase di accumulo (in anni)"
             "è superiore ai 35 anni."
             "\n"),
            (BaseInfoWin.Tags.DOTLIST1,))
