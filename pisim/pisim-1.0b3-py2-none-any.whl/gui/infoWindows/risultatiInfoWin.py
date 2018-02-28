# -*- coding: utf-8 -*-

import ttk
from baseInfoWin import BaseInfoWin


class RisultatiInfoWin(BaseInfoWin):
    def _dumpTxt(self):
        self.infoText.insert(
            ttk.Tkinter.END,
            "Generale\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tab per l'analisi dei risultati delle simulazioni "
             "di accumulo e rendita da fondo pensione. La struttura "
             "è identica alle tab della finestra principale:\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("-\tA sinistra c'è l'elenco dei report generati e memorizzati;\n"
             "-\tA destra c'è l'area dove vengono visualizzate "
             "tutte le informaioni generate da una simulazione.\n"),
            (BaseInfoWin.Tags.DOTLIST1,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("\nPer caricare un report é necessario selezionare "
             "l'elemento corrispondente dall'elenco a sinistra. "
             "A caricamento effettato, le informazioni sono mostrate "
             "nel modo seguente:\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("-\tQuesta finestra, area di destra: caratteristiche "
             "sintetiche e generali risultanti dalla simulazione;\n"
             "-\tFinestra principale, singole tab: tutte le impostazioni "
             "di simulazione. In altri termini, ogni report conserva, "
             "insieme ai risultati di simulazione, anche i descrittori di "
             "dipendente, inflazione, ecc. con i quali la simulazione é stata "
             "impostata. A report caricato, ogni tab viene aggiornata "
             "per mostrare i valori del descrittore relativo "
             "usato per la simulazione.\n"),
            (BaseInfoWin.Tags.DOTLIST1,))

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
            ("Eliminazione di un report. Il tasto si abilita "
             "solo se è selezionato un elemento nell'elenco superiore - "
             "é questo elemento che viene eliminato.\n"),
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Rinomina\n",
            (BaseInfoWin.Tags.ACTIONNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Rinomina di un report salvato. L'eventuale nuovo nome é quello "
             "specificato nel campo 'Nome Report' in alto nella zona "
             "di destra. Il tasto si abilita quando é selezionato "
             "un elemento nell'elenco superiore (elemento a cui si applica "
             "il cambio di nome) ed il nome specificato nel campo é valido "
             "(il testo non deve essere di colore rosso.) Nel caso in cui "
             "il nuovo nome sia identico a quello di un altro report "
             "già salvato, l'operazione é interrotta, generando un errore.\n"),
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Filtro\n",
            (BaseInfoWin.Tags.ACTIONNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Apre una sotto-finestra tramite la quale é possibile "
             "specificare: quali informazioni nell'area di destra "
             "visualizzare; se mostrare gli intervalli di variazione oppure "
             "i soli valori medi.\n"),
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Esporta\n",
            (BaseInfoWin.Tags.ACTIONNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Operazione attualmente non implementata.\n",
            (BaseInfoWin.Tags.ACTIONDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Descrizione Delle Colonne - Scenari\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Ogni simulazione calcola le prestazioni del fondo pensione "
             "in tre scenari differenti di seguito descritti. "
             "E' possibile attivare/disattivare la visualizzazione di ogni "
             "scenario tramite la finestra di filtro.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Scenario Migliore\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("A parità di parametri di simulazione, le prestazioni "
             "del fondo pensione dipendono da come i tassi di inflazione "
             "e le rivalutazioni annue del montante del fondo pensione "
             "si dispongono durante il periodo di accumulo. "
             "Lo scenario migliore - vale a dire quello in cui si ottiene "
             "la più alta rivalutazione del montate e, quindi, la più elevata "
             "rendita pensionistica - si ha quando l'inflazione "
             "é decrescente e la rivalutazione montante è crescente.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Scenario Peggiore\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Come sopra ma per il caso pessimo: inflazione crescente "
             "e rivalutazione montante decrescente.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Scenario Medio\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Come sopra ma per il caso generale: inflazione e "
             "rivalutazione sono simulate in modo del tutto casuale "
             "senza imporre un ordine. I risultati relativi possono essere "
             "considerati come le prestazioni medie del fondo pensione "
             "date le impostazioni.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Descrizione Delle Colonne - Valori\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Dato che in una simulazione sono coinvolti (a meno di "
             "impostazioni da parte dell'utente) valori determinati, "
             "anno per anno, in modo casuale, i risultati finali "
             "sono affetti da un margine di imprecisione. Per questo motivo "
             "sono previste diverse modalità di visualizzazione, "
             "di seguito descritte. E' possibile selezionare la modalità "
             "di visualizzazione tramite la finestra di filtro.\n"),
            (BaseInfoWin.Tags.NORMAL,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Min - Max\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Sono visualizzati il valore minimo ed il valore massimo. "
             "Il presunto valore reale per una data combinazione "
             "di misurazione e scenario é compreso, "
             "al 95% di probabilità, in questo intervallo.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Medi\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Per agevolare l'analisi dei dati a video, é possibile "
             "attivare questa modalità che mostra solo il valore medio, "
             "per misurazione e scenario. Tale valore é il centro "
             "dell'intervallo mostrato con la modalità 'min - max'.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Medi (% err.)\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("E' una modalità di visualizzazione simile a quella 'min - max'. "
             "Qui il raggio dell'intervallo é espresso in termini percentuali "
             "rispetto al valore centrale. Questo permette "
             "di apprezzare meglio il grado di precisione "
             "della misurazione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Descrizione Delle Righe\n",
            (BaseInfoWin.Tags.HEADLINE,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Primo Anno) Salario lordo\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Salario lordo (attualizzato) percepito nel primo anno "
             "di contribuzione. Da tenere presente che questo valore "
             "non rapresenta un'annualità piena nel caso in cui "
             "la data inizio piano non é nel mese di Gennaio "
             "ma la quota parte.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Primo Anno) Contrib. dipendente\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) della contribuzione volontaria "
             "dipendente nel primo anno di contribuzione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Primo Anno) Contrib. datore\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) dei contributi versati dal datore "
             "di lavoro durante il primo anno di contribuzione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Primo Anno) Contrib. TFR\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) del TFR maturato dal dipendente "
             "nel primo anno di contribuzione totalmente versato al fondo.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Primo Anno) Totale deduzioni\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) delle deduzioni IRPEF "
             "spettanti al dipendente.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) Contrib. dipendente\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) dei contributi dipendente versati durante "
             "tutto il periodo di accumulo fondo pensione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) Contrib. datore\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) dei contributi del datore di lavoro "
             "versati durante tutto il periodo di accumulo fondo pensione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) Contrib. TFR\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) del TFR maturato dal dipendente "
             "durante il periodo di accumulo e versato interamente "
             "nel fondo pensione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) Totale deduzioni\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Totale (attualizzato) delle deduzioni spettanti "
             "al dipendente durante il periodo di accumulo fondo pensione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) Montante finale\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Montante finale (attualizzato) risultante "
             "dalla gestione del fondo.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) Montante erogato\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Montante finale (attualizzato) al netto delle imposte "
             "spettanti prima della sua conversione in "
             "rendita pensionistica.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) TIR, globale\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tasso Interno di Rendimento dell'investimento nel fondo, "
             "cosiderando come versamenti solo la parte di contribuzione "
             "volontaria del dipendente. Per una descrizione di cosa é "
             "il TIR e come é calcolato vedere: "),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "https://it.wikipedia.org/wiki/Tasso_interno_di_rendimento",
            (BaseInfoWin.Tags.FIELDDESCR, BaseInfoWin.Tags.HYPERLINK,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ".\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) TIR, dipendente\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Tasso Interno di Rendimento, considerando come versamenti "
             "la contribuzione volontaria del dipendente ed il suo TFR, "
             "e decurtando delle deduzioni godute. Rispetto al TIR standard "
             "fornisce una valutazione più accurata dell'effetttiva "
             "prestazione del fondo rispetto a tutte le somme movimentate "
             "dal punto di vista del dipendente.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Accumulo) ISC\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Indice Sintetico di Costo. Vedere ",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "https://it.wikipedia.org/wiki/Indice_sintetico_di_costo",
            (BaseInfoWin.Tags.FIELDDESCR, BaseInfoWin.Tags.HYPERLINK,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ".\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto F.P. Rendita) Rendita annua\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Rendita (attualizzata) di pensione integrativa annuale erogata "
             "dal fondo il primo anno di pensionamento.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Ultimo salario) Lordo\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Ultimo salario annuale lordo (attualizzato) percepito.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Ultimo salario) Netto\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Ultimo salario annuale netto (attualizzato) percepito.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Pensione INPS) Annua, lorda\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Pensione INPS annuale lorda (attualizzata) percepita "
             "il primo anno di pensionamento.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Pensione INPS) Annua, netta\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Pensione INPS annuale netta (attualizzata) percepita "
             "il primo anno di pensionamento.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto accumulo TFR) Montante finale\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("TFR lordo (attualizzato) accumulato nel caso in cui "
             "il dipendente non aderisse a nessun fondo pensione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto accumulo TFR) Montante erogato\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "TFR erogato (attualizzato), quindi al netto delle imposte.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto accumulo TFR) TIR, senza contributi dip.\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Tasso Interno di Rendimento del TFR.\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto accumulo TFR) TIR, con contributi dip. (no riv.)\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Come sopra ma aggingendo i contributi che il dipendente "
             "riconoscerebbe al fondo pensione come contribuzione volontaria, "
             "senza però riconoscergli alcuna rivalutazione.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto accumulo TFR) ISC\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "Indice Sintetico di Costo del TFR (tipicamente 0.00%).\n",
            (BaseInfoWin.Tags.FIELDDESCR,))

        self.infoText.insert(
            ttk.Tkinter.END,
            "(Prospetto accumulo TFR) Durata anni\n",
            (BaseInfoWin.Tags.FIELDNAME,))

        self.infoText.insert(
            ttk.Tkinter.END,
            ("Durata (in anni) del montante TFR "
             "- aumentato della contribuzione dipendente (non rivalutata "
             "negli anni) e diminuito delle deduzioni di cui il dipendente "
             "ha eventualmente goduto partecipando al fondo pensione - "
             "nel caso in cui venisse usato per generare una rendita "
             "pensionistica analoga a quella prodotta dal fondo pensione "
             "(nel calcolo é inclusa anche la rivalutazione "
             "della rendita pensionistica specificata nell'apposita tab.) "
             "Il calcolo non prevede nessuna rivalutazione del TFR "
             "negli anni di erogazione della rendita.\n"),
            (BaseInfoWin.Tags.FIELDDESCR,))
