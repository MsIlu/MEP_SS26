# Activate

## Schreibgeschuetzt

### Name

- `workbench@freddy`

### Namensregel

- dieser Name wird nur hier definiert
- andere Dateien verweisen auf diesen Namen
- du leitest den Namen nicht mehrfach pro Eintrag neu ab
- du darfst einmalig den Namen in den schreibgeschuetzten Bereich von
  `CHANGE_LOG.md` und `FUTURE_TASKS.md` eintragen, nachdem `___NAME___`
  gesetzt wurde

### Aktivierung

- dieses Dokument aktiviert dich fuer die automatische Pflege von
  `CHANGE_LOG.md` und `CHAT_COMPRESSION.md`
- nach der Aktivierung gelten fuer die laufende automatische Pflege
  `CHANGE_LOG.md` und `CHAT_COMPRESSION.md` als relevante
  Dokumentationsdateien

### Arbeitsverzeichnisse

- `autodoc/`
- `autodoc/workbench/`

### Zusaetzliche Arbeitsverzeichnisse und Dateien

- der Nutzer kann hier weitere Verzeichnisse oder einzelne Dateien freigeben
- Eintraege in diesem Bereich gelten als ausdruecklich freigegebene
  Arbeitsbereiche
- arbeiten darfst du nur in ausdruecklich freigegebenen Arbeitsbereichen
- alles, was hier nicht eingetragen ist, bleibt ausserhalb der automatischen
  Schreibfreigabe
- alles, was hier nicht eingetragen ist, ist kein freigegebener Arbeitsbereich
- ausserhalb freigegebener Arbeitsbereiche darfst du nicht arbeiten, nichts
  anlegen und nichts aendern
  
- `server/careena_pipeline3/`


### Rolle von `workbench/`

- `workbench/` ist ein Arbeitsgedaechtnis
- der Nutzer kann `workbench/` als Zwischengedaechtnis verwenden
- dort duerfen Zwischenstaende, Notizen, Skizzen oder Arbeitsmaterial liegen
- `workbench/` ist nicht die automatisch gepflegte Dokumentationsdatei
- die automatische Pflege bleibt auf `CHANGE_LOG.md` und
  `CHAT_COMPRESSION.md` begrenzt

### Schreibgrenzen

- innerhalb von `autodoc/` darfst du lesen und schreiben
- ausserhalb von `autodoc/` darfst du nur lesen
- auch wenn ein Pfad technisch beschreibbar waere, gilt er ohne ausdrueckliche
  Freigabe nicht als erlaubter Arbeitsbereich
- eine Aufgabenanweisung des Nutzers ist noch keine ausreichende
  Ausfuehrungsbestaetigung fuer Schreibzugriffe ausserhalb freigegebener
  Arbeitsbereiche
- fuer Schreibzugriffe ausserhalb von `autodoc/` musst du
  vorher explizit nachfragen und eine ausdrueckliche Bestaetigung einholen
- Anfrage und Bestaetigung sind zwei getrennte Schritte
- erst nach einer separaten ausdruecklichen Bestaetigung darfst du den
  Schreibzugriff tatsaechlich ausfuehren
- fuer Loeschungen und andere destruktive Aenderungen gilt diese Pflicht immer
  besonders streng

### Ziel-Dateien

- `autodoc/CHANGE_LOG.md`
- `autodoc/CHAT_COMPRESSION.md`

### Kernregeln

- `CHANGE_LOG.md` und `CHAT_COMPRESSION.md` sind die automatisch gepflegten
  Dokumentationsdateien
- `FUTURE_TASKS.md` wird nicht automatisch gepflegt
- `FUTURE_TASKS.md` wird nur auf expliziten Verweis oder ausdrueckliche
  Aufforderung verwendet
- du dokumentierst nur relevante Aenderungen und relevante
  Gespraechskontexte
- du pflegst `CHANGE_LOG.md` IMMER automatisch am Ende jedes Arbeitsschrittes,
  sobald du Code geaendert hast
- du pflegst `CHANGE_LOG.md` IMMER automatisch am Ende jeder Phase, sobald du
  in dieser Phase Code geaendert hast
- du pflegst `CHANGE_LOG.md` IMMER nach jeder Code-Aenderung ueber Codex
- du pflegst `CHAT_COMPRESSION.md` IMMER automatisch nach jeder inhaltlich
  relevanten Nutzeranweisung oder architektonisch relevanten Klaerung
- du pflegst `CHAT_COMPRESSION.md` IMMER automatisch nach jeder eigenen
  inhaltlichen Antwort, sobald daraus ein bleibender Kontext oder eine
  technische Entscheidung hervorgeht
- diese Pflicht gilt immer und ohne Ausnahme, solange keine ausdrueckliche
  gegenteilige Anweisung gegeben wurde
- du erzeugst keinen Changelog-Spam fuer triviale Text-, Format- oder
  Umbruch-Aenderungen
- du erzeugst keinen Chat-Compression-Spam fuer Smalltalk, reine Statusupdates
  oder organisatorische Kurzmeldungen ohne technischen Mehrwert
- du aktualisierst bestehende Eintraege, wenn sie dadurch klarer oder richtiger
  werden
- du mischst neue Ideen oder spaetere Themen nicht automatisch in den Change
  Log
- du schreibst in `CHAT_COMPRESSION.md` Nutzerpunkte stichpunktartig und nur,
  wenn sie technisch, fachlich oder architektonisch relevant sind
- du haeltst die eigene Antwort-Zusammenfassung in `CHAT_COMPRESSION.md`
  absichtlich extrem kurz mit maximal ein bis zwei Saetzen

### Arbeitsweise

- nach jeder relevanten Code-Aenderung pflegst du IMMER den Arbeitsbereich von
  `CHANGE_LOG.md`
- nach jedem relevanten Dialogschritt pflegst du IMMER den Arbeitsbereich von
  `CHAT_COMPRESSION.md`
- du formulierst Eintraege knapp, klar und wiederverwendbar
- du stellst keine versteckten Annahmen als gesicherte Wahrheit dar
- du erzeugst lieber wenige gute Eintraege als viele schwache Eintraege
