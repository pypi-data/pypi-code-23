# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin

class FpAccumuloInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per la configurazione della fase di accumulo "
             "di una specifica linea "
             "di investimento di un fondo pensione.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Descrizione Dei Campi\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Contribuzione dipendente\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Percentuale di contribuzione dipendente volontaria "
             "al fondo pensione. Fare riferimento alla tab precedente "
             "'F.P. Base' per la definizione della base contributiva su cui "
             "questa percentuale è applicata.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Rivalutazione) Media\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Rivalutazione media annua applicata al montante accumulato, "
             "in termini reali. Fare riferimento alle informazioni contenute "
             "nella tab 'Salario' per maggiori dettagli "
             "circa la definizione di rivalutazione in termini reali.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Rivalutazione) Variazione\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Massimo scostamento, in positivo o in negativo, "
             "della rivalutazione simulata per un anno rispetto al valore "
             "di rivalutazione media. Un valore pari a 0 determina "
             "una rivalutazione del montante costante "
             "per ogni anno simulato pari a '(Rivalutazione) Media'.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Spese annue) Fisse\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Valore, in valuta, del costo di adesione "
             "al fondo applicato ogni anno.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Spese annue) Variabili\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Costo di adesione al fondo applicato annualmente in percentuale "
             "sul montante accumulato al termine dell'anno stesso.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Spese annue) Imposta\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tasse pagate annualmente e calcolate percentualmente "
             "sul montante accumulato al termine dell'anno stesso. "
             "E' un valore che va ricavato dal bilancio di ogni linea "
             "di investimento di ogni fondo pensione, dato che le imposte "
             "dipendono dal tipo di strumento finanziario (20% su azioni "
             "ed obbligazioni, 12.5% su titoli di Stato) e dal loro mix.\n"
             "Formato: Percentuale 0-100.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Altri Dettagli\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Il funzionamento di questa tab è parzialmente collegato "
             "alla tab precedente 'F.P. Base'. L'elenco dei descrittori "
             "salvati per la fase di accumulo viene caricato solo se "
             "nella tab 'F.P. Base' è selezionato un fondo pensione. "
             "Altrimenti l'elenco rimane vuoto: non è "
             "possibile caricare alcun descrittore ma è possibile "
             "l'inserimento dei dati per il descrittore della fase di "
             "accumulo di un generico fondo pensione. I quali possono "
             "essere usati per la generazione di un report ma "
             "non possono essere salvati. Questo perchè un descrittore "
             "per essere salvato deve "
             "necessariamente essere associato ad un fondo pensione noto."),
            (BaseInfoWin.Tags.NORMAL,))
