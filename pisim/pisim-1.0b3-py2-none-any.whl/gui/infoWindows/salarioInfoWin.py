# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin

class SalarioInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per la configurazione delle caratteristiche essenziali del "
             "salario del dipendente.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Descrizione Dei Campi\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Salario) Lordo Annuo\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ('Totale stipendio annuo percepito, comprensivo anche '
             "degli eventuali contributi INPS.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Salario) Minimo contrattuale, mese\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Mensilità minima mensile prevista dal CCNL.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Rivalutazione) Annua\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tasso annuo medio di rivalutazione del salario, "
             "in termini reali.\n"
             "'Termini reali' vuol dire che la rivalutazione effettiva "
             "applicata è pari a quella specificata aumentata del tasso "
             "di inflazione.\n"
             'Formato: Percentuale 0-100\n'),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            '(Rivalutazione) Periodicità\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Cadenza (in termini di anni) con la quale la rivalutazione "
             "salariale è applicata. Un valore di 1 comporta "
             "una rivalutazione pari a '(Rivalutazione) Annua' applicata "
             "annualmente. Valori superiori determinano valori "
             "di rivalutazione pari al tasso composto relativo "
             "alla cadenza specificata. Ad esempio, una rivalutazione "
             "media di 1%/anno è ottenuta in uno dei seguenti modi: "
             "1% applicato ogni anno; 2.01% (tasso composto su 2 anni) "
             "applicato ogni 2 anni; 3.0301% applicato ogni 3 anni; "
             "e così via. \n"
             'Formato: Numero intero maggiore o uguale a 0.\n'),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Altri dettagli\n',
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("La rivalutazione salariale, per la parte relativa al tasso "
             "di inflazione, viene applicata con un anno di ritardo. "
             "Vale a dire: ogni anno viene applicato l'aumento "
             "a compensazione del tasso di inflazione dell'anno "
             "precedente. Questo per simulare una dinamica di aumento "
             "salariale quanto più vicina possibile a quella reale "
             "(dove le compensazioni del potere di acquisto sono applicate "
             "sempre in modo differito).\n"
             "Coerentemente, non viene applicata alcuna rivalutazione "
             "salariale nel primo anno. Questo anche perchè si presume "
             "che il valore di salario lordo specificato già incorpori "
             "eventuali aumenti decisi negli anni precedenti.\n\n"
             "E' necessario specificare due tipologie differenti di salario "
             "(lordo annuo e minimo contrattuale mensile) in quanto "
             "da entrambe può dipendere il calcolo dei contributi "
             "del dipendente e del datore di lavoro al fondo pensione "
             "(dipende dalle regole istitutive del fondo stesso).\n\n"
             "Il calcolo del contributo a carico del dipendente può dipendere "
             "(sempre in base alle regole istitutive del fondo) "
             "dal lordo in busta o dal lordo ai fini del calcolo del TFR. "
             "Queste due voci potrebbero essere diverse. "
             "In questo simulatore si è scelto di semplificare, "
             "uguagliandole."),
            (BaseInfoWin.Tags.NORMAL,))
