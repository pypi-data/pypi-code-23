# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin
from ... import pisimVer


class MainWinInfoWin(BaseInfoWin):
    def _dumpTxt(self):

        self.infoText.insert(
            ttk.Tkinter.END,
            "PiSim - Simulatore di Pensione Integrativa\n",
            (BaseInfoWin.Tags.TITLE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Autore: Luca Casone (csnluca@gmail.com)\n",
            (BaseInfoWin.Tags.SUBTITLE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Versione:  {}\n".format(pisimVer),
            (BaseInfoWin.Tags.SUBTITLE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "URL: ",
            (BaseInfoWin.Tags.SUBTITLE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "https://pypi.org/project/pisim/",
            (BaseInfoWin.Tags.HYPERLINK,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "\n",
            (BaseInfoWin.Tags.SUBTITLE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Finestra principale dell'applicazione PiSim, per la simulazione "
             "della prestazione pensionistica complementare. "
             "Prevede due sezioni:\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("-\tArea principale, suddivisa in sotto-sezioni, "
             "per configurare i diversi parametri previsti "
             "dalla simulazione;\n"
             "-\tArea in basso con tasti per richiamare "
             "le azioni principali.\n"),
            (BaseInfoWin.Tags.DOTLIST1,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "\nTutte le sotto-sezioni hanno la stessa organizzazione:\n",
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("-\tA sinistra: l'elenco dei descrittori già configurati e"
             " memorizzati;\n"
             "-\tA destra, in alto, nome del descrittore visualizzato.\n"
             "-\tA destra, area centrale, tutte le informazioni "
             "che compongono il descrittore. In questa area è possibile "
             "definire un nuovo descrittore, visualizzare o modificare "
             "uno precedentemente memorizzato.\n"
             "-\tA destra, in basso, due tasti azioni: 'Info' apre "
             "una finestra come questa che descrive le informazioni "
             "del descrittore; 'Cancella' per cancellare "
             "tutti i campi.\n"),
            (BaseInfoWin.Tags.DOTLIST1,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("\nPer caricare un descrittore è necessario selezionare "
             "l'elemento corrispondente dall'elenco a sinistra. "
             "Le informazioni sono caricate nei campi corrispondenti "
             "ed il nome del descrittore è inserito nel campo in alto.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("\nQualsiasi tab permane in uno stato invalido fintanto che "
             "tutti i suoi campi contengono valori non validi. "
             "Una tab non valida:\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("-\tHa il simbolo '[X]' all'inizio del nome.\n"
             "-\tNon permette il salvataggio del relativo descrittore.\n"
             "-\tNon permette l'avvio della simulazione del piano "
             "di fondo pensione.\n"),
            (BaseInfoWin.Tags.DOTLIST1,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("\nUna tab quando diventa valida ha il simbolo '[O]' "
             "all'inizio del nome, e permette il salvataggio "
             "del descrittore.\n\n"
             "Per avviare la simulazione tutte le tab devono essere valide. "
             "Non è necessario aver memorizzato i descrittori delle tab per "
             "avviare una simulazione.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Azioni\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Elimina\n",
            (BaseInfoWin.Tags.ACTIONNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Una volta selezionato un descrittore dall'elenco superiore, "
             "si abilita il tasto relativo a quest'azione. Se premuto, "
             "dopo una richiesta di conferma, il descrittore selezionato "
             "viene eliminato. I campi della tab "
             "però non vengono cancellati: questo permette di salvarli "
             "con un altro nome.\n\n"
             "Se il descrittore selezionato è di tipo 'F.P. Base', "
             "anche i descrittori ad esso collegati di tipo 'F.P. Accumulo' e "
             "'F.P. Rendita' sono eliminati.\n"),
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Salva\n",
            (BaseInfoWin.Tags.ACTIONNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Permette la memorizzazione del descrittore. "
             "Il tasto relativo si abilita "
             "quando sono verificate entrambe le seguenti condizioni: "
             "il nome contenuto nel campo 'Nome' (Configurazione) è valido; "
             "tutti i campi del descrittore contegono valori validi. "
             "Se il nome specificato è già usato da un descrittore esistente, "
             "quest'ultimo viene sovrascritto con il nuovo solo se l'utente "
             "risponde positivamente al messaggio di richiesta conferma.\n"),
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Elabora\n",
            (BaseInfoWin.Tags.ACTIONNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Una volta che tutte le tab diventano valide, questo tasto "
             "si abilita. Premendolo si avvia la simulazione di accumulo e "
             "rendita del fondo pensione. "
             "Se la simulazione termina con successo, il report "
             "generato viene salvato con un nome di default (data ed "
             "ora corrente), "
             "la finestra 'Risultati' è aperta ed il report stesso caricato "
             "e mostrato.\n"),
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Risultati\n",
            (BaseInfoWin.Tags.ACTIONNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Permette l'apertura della finestra di analisi dei dati "
             "delle simulazioni memorizzate.\n"),
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Descrizione Delle Tab\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Dipendente\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Raggruppa le informazioni anagrafiche del dipendente.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Inflazione\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Permette di configurare i valori di inflazione per gli anni di "
             "accumulo su fondo pensione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            'Salario\n',
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Permette di personalizzare il livello salariale iniziale del "
             "dipendente e la sua evoluzione nel periodo di accumulo "
             "su fondo pensione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Pensione\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Contiene i parametri per la determinazione "
             "della pensione INPS.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "F.P. Base, F.P. Accumulo e F.P. Rendita\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tre tab in cui è suddivisa la configurazione di tutti "
             "gli aspetti del fondo pensione (F.P.). La prima contiene "
             "le caratteristiche generali, la seconda quelle che descrivono "
             "una singola linea di investimento e la contribuzione "
             "volontaria da parte del dipendente, la terza i fattori che "
             "determinano il calcolo della rendita pensionistica "
             "complementare. Ad un descrittore memorizzato nella prima tab "
             "possono essere associati uno o più descrittori nella seconda "
             "ed uno o più descrittori nella terza.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))
