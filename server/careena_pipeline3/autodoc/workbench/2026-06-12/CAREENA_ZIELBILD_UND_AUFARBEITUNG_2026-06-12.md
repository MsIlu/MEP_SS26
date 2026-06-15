# Careena: Zielbild und Aufarbeitung der letzten Tage

Stand: 2026-06-12
Status: Synthese / Arbeitsdokument


## Zweck

Dieses Dokument fuehrt die wichtigsten Linien aus:

- `CHAT_COMPRESSION.md`
- `CHANGE_LOG.md`
- `autodoc/2026-06-11/*`
- `autodoc/2026-06-12/*`
- `autodoc/workbench/2026-06-09/*`
- `autodoc/workbench/2026-06-08/*`

zusammen und versucht daraus ein belastbareres Gesamtbild zu machen:

1. worum es bei Careena eigentlich gehen soll
2. wie Careena funktionieren soll
3. was davon heute schon real angelegt ist
4. was aktuell noch fehlt oder semantisch schief sitzt
5. welche Loesungsansaetze bereits existieren

Das Dokument ist bewusst keine reine Nacherzaehlung der KI-Texte.
Es trennt moeglichst zwischen:

- stabilen, mehrfach bestaetigten Leitlinien
- plausiblen, aber noch offenen Architekturannahmen
- klar sichtbaren Restproblemen im aktuellen Lauf


## Leseregel und Belastbarkeit

Die Quelltexte sind groesstenteils KI-generierte Arbeitsdokumente.
Deshalb gilt fuer dieses Dokument folgende Gewichtung:

### Hohe Belastbarkeit

- wiederkehrende Aussagen ueber viele Dokumente und Tage hinweg
- Aussagen, die in Plan, Architekturtext und Change Log zusammenpassen
- Aussagen, die als reale Codeaenderung oder Logbefund dokumentiert wurden

### Mittlere Belastbarkeit

- konzeptionelle Vorschlaege, die mehrfach auftauchen, aber noch nicht sauber
  im Code oder Laufverhalten bestaetigt sind

### Niedrige Belastbarkeit

- zu glatte Erklaerungen einzelner Probleme ohne klare Rueckbindung an Code,
  Logs oder spaetere Korrekturen
- fruehere Aussagen, die spaeter sichtbar relativiert oder umpriorisiert wurden


## Executive Summary

Careena soll kein freier medizinischer Chatbot und auch kein starres
Formularsystem sein.

Das Zielbild ist ein begrenztes konversationelles Medizinsystem:

- vorne wirkt es wie ein natuerlicher Chat
- hinten arbeitet es mit klar getrennten Zustaenden und engen Vertraegen
- das LLM darf nicht frei "die Wahrheit entscheiden", sondern nur klar
  begrenzte Teilaufgaben uebernehmen

Der eigentliche Kern ist:

1. eine Nutzernachricht kurz einordnen
2. nur wenn noetig tiefer arbeiten
3. nur kontrolliert strukturierte Wahrheit fortschreiben
4. auf Basis dieser Wahrheit und des Dialogzustands den naechsten erlaubten
   Zug waehlen
5. die Antwort entlang einer begrenzten Strategie formulieren

Die Hauptbewegung der letzten Tage war:

- 08.06.: Fokus stark auf Case-Truth, Observation-Identitaet und zu breitem
  Call-2-Pfad
- 09./10.06.: V3 schneidet Orchestrierung, Bridge, Call 1, Call 2,
  Process-State und den Recommendation-Abschlussknoten sauberer
- 11.06.: V4 verlagert den Hauptfokus nach hinten auf Response,
  Recommendation-Transition, spaetere Antwortstrategie und dynamischen
  Werkzeugkasten
- 12.06.: die Architektur wird als allgemeines Careena-System neu gelesen;
  zusaetzlich erscheint das fortlaufende Nutzeranliegen als fehlende
  concern-nahe Schicht

Der wichtigste neue Befund ist nicht nur "es gibt noch Bugs", sondern:

- mehrere Restprobleme haengen an derselben fehlenden Ordnung zwischen
  Nutzeranliegen,
  medizinischer Wahrheit,
  Dialogprozess,
  Readiness/Freigabelogik
  und Antwortstrategie


## Rekonstruktion der letzten Tage

## 2026-06-08: Fundament und fruehe Priorisierung

Die aelteren 08.06.-Dokumente setzen sehr klar eine Grundhaltung:

- Rolle vor Datei
- Vertrag vor Verhalten
- Extraktion ist nicht Wahrheit
- Kontext ist Hilfe, nicht Faktenquelle
- Response-Policy ist nicht Text
- Recommendation ist ein eigener freizugebender Pfad

Die damals wichtigste Problemzone war die semantische Mitte:

- Observation-Identitaet
- Update vs. Neuanlage
- unsauberer Extraction-to-Truth-Uebergang
- zu breiter Call-2-Kontext
- zu schwerer zweiter LLM-Normalisierungsschritt

Das Zielbild aus dieser Phase:

- `DialogueManager` als zentrale Orchestrierung
- `MedicalCase` als kanonische medizinische Wahrheit
- `Call 2` als begrenzter Extraktionsschritt
- eine explizite Truth-Schicht zwischen Extraktion und Case
- Recommendation als mehrstufiger, freizugebender Pfad

Wichtig:

- diese Phase ist konzeptionell stark
- sie unterschlaegt aber noch teilweise die spaetere hintere Problemzone
  rund um Transition, Antwortstrategie und Nutzeranliegen


## 2026-06-09 bis 2026-06-10: V3 und echte Grenzschnitte

Mit V3 verschiebt sich die Arbeit von allgemeinem Architekturdenken auf reale
Laufgrenzen.

Die Reihenfolge wird neu festgezogen:

1. Orchestrierung
2. Bridge / Uebergangsvertrag
3. kleine Entry-Signale
4. engerer Call-2-Vertrag
5. Process-State / Requirement / Readiness
6. Response-Transition

Die wichtigsten Bewegungen:

- der `DialogueManager` wird als sichtbare Souveraenitaetsstelle gestaerkt
- das alte haessliche Bridge-Objekt wird nicht sofort idealisiert ersetzt,
  sondern bewusst begrenzt
- `Call 1` wird als kleiner Scout-/Signal-Lieferant gelesen
- `Call 2` wird als Werkzeugkasten statt als breiter Fall-Rekonstruktionscall
  neu gedacht
- der Mischfall "Rueckfrage beantwortet plus neue Information" wird als
  Doppelspur aus Prozess und Case verstanden
- `guide_next_step` wird nicht mehr nur als Textproblem gelesen, sondern als
  fehlender dialogischer Abschluss-/Freigabevertrag

Am Ende dieses Strangs ist die Lage klar:

- die vordere und mittlere Architektur wurde bereits deutlich stabiler
- die neue Hauptkante liegt hinten bei Response und Recommendation-Transition


## 2026-06-11: V4 und Verlagerung auf die hintere Reaktionsarchitektur

V4 ist keine neue Theorie von vorne.
V4 ist die Einsicht, dass die heutigen Restprobleme nicht mehr primaer in der
groben Extraction-Architektur sitzen, sondern in der hinteren Turn-Haelfte:

- Entry gegen aktive Abschlussknoten
- dialogische Transition
- Freigabelogik / Readiness
- Response-Policy
- spaetere Antwortstrategie

Neu oder geschaerft werden:

- ein kleiner expliziter hinterer Reaktionskern
- ein expliziter Zwei-Wege-Abschlussknoten fuer:
  - `request_recommendation`
  - `report_more_information`
- die Trennung zwischen:
  - medizinischer Rueckfrage
  - dialogischer Abschlussfrage
  - Recommendation-Freigabe
  - Recommendation-Inhalt

Zusaetzlich taucht ab 11.06. immer deutlicher ein weiterer Punkt auf:

- das fortlaufende Nutzeranliegen ist nicht dasselbe wie `primary_focus`
  oder `readiness`


## 2026-06-12: Concern, Mittelstreifen und allgemeines Careena-System

Am 12.06. wird die Perspektive nochmals hoeher:

- nicht nur `careena_pipeline3` als enger Turn-Kern
- sondern Careena als Gesamtsystem

Die wichtigste neue Architekturlesart lautet:

- zwischen `Entry peek`, optionaler tieferer Verarbeitung,
  moeglichem Truth-Write und spaeterem Response-Pfad liegt eine eigene
  mittlere Steuerzone

Genau dort entscheidet Careena:

- ob ueberhaupt tiefer gearbeitet wird
- ob aus dem Ergebnis Fallwahrheit wird
- welche Art Antwortbahn freigegeben ist

Parallel dazu wird das fehlende fortlaufende Nutzeranliegen jetzt als
`concern`-nahe Schicht sichtbar gemacht.

Wichtig dabei:

- dieser `ConcernState` ist noch kein bewiesenes drittes dauerhaftes Zentrum
- er ist vorerst eine vorsichtige Architekturhilfe
- seine Semantik ist noch offen und darf nicht vorschnell mit
  `DialogueState` oder `MedicalCase` verschmolzen werden


## Was Careena im Kern sein soll

Die konsistenteste Definition ueber alle Dokumente hinweg ist:

Careena ist ein zustandsorientiertes, begrenztes medizinisches
Konversationssystem, das freie Nutzernachrichten in eine kontrollierte
interne Architektur aus Anliegen, medizinischer Wahrheit, Dialogprozess,
Freigabelogik und Antwortstrategie ueberfuehrt.

Nicht gemeint ist:

- ein freier Chat mit grossem Master Prompt als Hauptlogik
- ein Slot-Filling-Formular mit etwas Text drumherum
- ein LLM, das selbst implizit Case-Wahrheit, Readiness und Empfehlung
  "miterfindet"

Gemeint ist:

- natuerliche Konversationsoberflaeche
- strengere innere Grenzen
- nachvollziehbare Zustandsfortschreibung
- gestufte Freigabe von Recommendation
- bewusst begrenzte LLM-Rollen


## Was Careena fachlich leisten soll

Aus den Dokumenten laesst sich als belastbarer fachlicher Auftrag ableiten:

1. Careena soll das fuer Careena relevante medizinische Anliegen des
   Patienten erfassen.
2. Careena soll den Dialog so fuehren, dass fuer dieses Anliegen genug
   belastbare Information entsteht.
3. Careena soll erst dann in einen Recommendation-Pfad gehen, wenn dieser
   dialogisch und fachlich freigegeben ist.

Wichtige Ableitungen daraus:

- nicht jede geaeusserte Information gehoert automatisch in den
  `MedicalCase`
- nicht jede symptomnahe Vollstaendigkeit bedeutet, dass das Anliegen
  verstanden ist
- `Readiness` darf nicht mit "wir haben ueberhaupt genug Text" verwechselt
  werden
- Recommendation ist kein Default-Ausgang nach jeder medizinisch relevanten
  Nachricht


## Zielbild: Wie Careena funktionieren soll

## 1. Chat vorne, Begrenzung hinten

Die sichtbare Nutzererfahrung darf chatartig bleiben.
Die Rueckseite soll aber nicht chatartig sein, sondern in kleine,
lesbare Schichten zerfallen.

Das bedeutet:

- freier Text kommt rein
- aber nicht jede Schicht darf frei mit diesem Text "denken"
- jede Stufe hat einen engeren Vertrag


## 2. Der elementare Turn

Der elementare Careena-Turn sieht im Zielbild so aus:

1. Nachricht empfangen
2. kurz reinspicken
3. kleine Signale und Routing bestimmen
4. optional tiefer arbeiten
5. optional Fallwahrheit fortschreiben
6. Dialogprozess und Freigabelage aktualisieren
7. begrenzte Reaktionsart waehlen
8. Antwort entlang dieser Reaktionsart formulieren

Das ist der Kern der "bounded conversational system"-Lesart.


## 3. Persistente Wahrheitszentren

Die stabilste spaete Lesart ist:

- `MedicalCase` fuer medizinische Wahrheit
- `DialogueState` fuer Gespraechsprozess
- `Turn` nur als Ausfuehrungseinheit

`ConcernState` ist vorerst eine offene Zusatzsicht.

Belastbare Regel:

- was nach dem Turn weiterleben muss, gehoert nicht in einen grossen
  Turn-Sammelcontainer
- es gehoert in persistente Wahrheits- oder Prozessobjekte


## 4. Die mittlere Steuerzone

Diese Zone ist zentral und in den neueren Dokumenten die vielleicht
wertvollste Einsicht.

Sie liegt zwischen:

- kurzem `Entry`-Peek
- optionalem `Call 2`
- moeglichem Truth-Write
- spaeterer Antwortbahn

Diese Zone entscheidet:

- ob `Call 2` ueberhaupt noetig ist
- welche Aufgaben `Call 2` bekommen soll
- ob ein Ergebnis in den `MedicalCase` geschrieben wird
- ob nur transient weitergearbeitet wird
- welche Antwortpfade anschliessend erlaubt sind

Das ist wichtig, weil Careena gerade nicht aus einem einzigen linearen
LLM-Rohr bestehen soll.


## 5. Call 1 und Call 2

Die spaeter stabilste Lesart ist:

- `Call 1` scoutet und liefert kleine Signale
- `Call 2` arbeitet nur dann tiefer, wenn es gebraucht wird

`Call 2` soll langfristig sein:

- ein technischer Werkzeugkasten
- mit kleinem Aufgabenpaket
- modussensitiv
- optional

Wichtig:

- `Call 2` ist nicht gleich "Extraktion als grosse Wahrheit"
- `Extraction` ist nur eine moegliche Aufgabe in diesem Werkzeugkasten


## 6. MedicalCase als kontrollierte Wahrheit

`MedicalCase` ist die kanonische medizinische Wahrheitsquelle.

Aber:

- Extraktion ist nicht automatisch Wahrheit
- der Write in den Case muss kontrolliert passieren
- neue Information darf nicht frei aus Summaries oder losem Kontext
  nachmaterialisiert werden

Das fruehe 08.06.-Thema bleibt in reduzierter Form weiter gueltig:

- Observation-Identitaet
- Update vs. Neuanlage
- Konflikt vs. Enrichment

sind weiter Kernfragen der Truth-Schicht, auch wenn sie in den juengsten
Dokumenten nicht mehr die alleinige Hauptbaustelle sind.


## 7. DialogueState als Prozessspur

`DialogueState` soll tragen:

- offene Follow-ups
- Pending-Transitions
- Recommendation-Wunsch
- Recommendation-Readiness
- weitere Prozessmarker

Nicht Aufgabe von `DialogueState` allein ist:

- das medizinische Anliegen selbst voll abzubilden
- die gesamte Antwortstrategie still mitzuschleppen


## 8. Concern / Nutzeranliegen

Das fortlaufende Nutzeranliegen ist inzwischen klar als fehlende Schicht
erkannt.

Die belastbare Aussage ist nicht:

- "ConcernState ist sicher das finale Modell"

sondern:

- das System braucht irgendeine concern-nahe Semantik, die nicht naiv mit
  `primary_focus`,
  lokaler Symptomvollstaendigkeit
  oder `Readiness`
  gleichgesetzt wird

Wofuer diese Schicht gebraucht wird:

- das eigentliche Anliegen ueber den Verlauf stabil halten
- Drift verhindern
- begruendete Anliegenwechsel zulassen
- spaeter adaptive Gespraechstiefe ermoeglichen


## 9. Readiness und Freigabelogik

`Readiness` bleibt im Zielbild wichtig, aber enger:

- Pflichtfelder
- Mindestvoraussetzungen
- Recommendation-Freigabe vorbereiten

Wichtig:

- `Readiness` ist fuer dieses Dokument kein Synonym fuer die ganze
  Freigabelogik
- `Readiness` beschreibt eher,
  ob Mindestvoraussetzungen oder Pflichtbedingungen erfuellt sind
- die Freigabelogik beschreibt anschliessend,
  welcher naechste Systemzug auf Basis von
  `MedicalCase`,
  `DialogueState`,
  concern-naher Lage
  und `Readiness`
  ueberhaupt erlaubt ist

Nicht allein Aufgabe von `Readiness` ist:

- zu entscheiden, ob das Anliegen inhaltlich schon wirklich verstanden ist
- zu entscheiden, ob der Dialog fuer den Nutzer natuerlich an einem Abschluss
  angekommen ist


## 10. Response-Policy und Antwortstrategie

Ein weiterer inzwischen sehr belastbarer Punkt:

- Response-Policy ist nicht Text
- Antwortstrategie ist nicht identisch mit `response_mode`

Das Zielbild braucht mindestens diese Trennung:

- Reaktionspfad / Policy
- Antwortstrategie
- finaler Text
- spaeter Recommendation-Inhalt

Statische Texte sind dabei nicht "falsch".
Sie haben im Zielbild aber eher diese Rolle:

- haeufige Muster
- absicherungskritische Pfade
- robuste Standardbahnen

Freier KI-Text soll spaeter nur dort andocken, wo die Policy ihn bereits
sauber freigibt.


## Konkrete Anforderungen an die Anwendung

## 1. Application Fit vor oder waehrend Case-Aufnahme

Nicht jede Nutzeraeusserung darf sofort zum medizinischen Fallkern werden.

Die Anwendung braucht eine kleine Passungspruefung:

- ist das Anliegen in Careenas Anwendungsrahmen?
- ist es medizinisch relevant genug?
- kann Careena dazu sinnvoll einen versorgungsbezogenen Dialog fuehren?


## 2. Natuerlicher, aber begrenzter Dialog

Der Dialog soll nicht wie ein starres Formular wirken.
Gleichzeitig darf die Freiheitsgrade des Systems intern nicht explodieren.

Das bedeutet:

- natuerliche Antworten nach aussen
- kleine explizite Vertragsknoten nach innen


## 3. Adaptives Nachfragen

Spaetere Rueckfragen sollen je nach Fall und Anliegen unterschiedlich tief
gehen koennen.

Dabei gilt laut spaeteren Dokumenten:

- statische Rueckfragen sind eher Performance- und Robustheitswerkzeug
- adaptive, LLM-gestuetzte Rueckfragen sollen dort moeglich sein, wo das
  Anliegen oder der Verlauf sie wirklich braucht


## 4. Recommendation nur als freigegebener Pfad

Sauber zu trennen sind:

- Nutzer will Empfehlung
- System ist fachlich bereit
- Recommendation ist dialogisch freigegeben
- Recommendation-Inhalt wird erzeugt
- finaler Text wird formuliert


## 5. Klares Verhalten am Recommendation-Abschlussknoten

Die spaet klarste Anforderung ist:

Wenn Careena an einem aktiven Abschlussknoten steht, soll dort semantisch
primaer nur zwischen zwei Ausgaengen unterschieden werden:

- `request_recommendation`
- `report_more_information`

Buttons und Freitext sind nur zwei Oberflaechen desselben Zustandsknotens.


## 6. Kein verdecktes Wiederanlaufen falscher Pfade

Das System darf nicht:

- freie Antworttexte am Abschlussknoten wieder blind in normalen
  medizinischen Call-2-Pfad kippen lassen
- wegen zu aggressiver `Readiness` sofort wieder dieselbe Abschlussfrage
  erzeugen
- Recommendation textlich andeuten, ohne dass der Zustand sie wirklich traegt


## Was heute schon real angelegt ist

## Starke vorhandene Bausteine

- `DialogueManager` als sichtbare Orchestrierungsmitte
- getrennte grobe Schichten fuer Entry, Extraction, Case, Dialogue,
  Freigabelogik und Response
- `MedicalCase` als echter Wahrheitsanker
- `DialogueState` als Prozessspur
- Logging und Simulation als reale Architekturwerkzeuge
- kleinere Entry-Signale statt grossem Fruehentscheider
- engerer Call-2-Vertrag als noch am 08.06.
- expliziter Recommendation-Abschlussknoten als Zwei-Wege-Idee
- erster kleiner Response-Kern
- erster kleiner `ResponseStrategy`-Vertrag
- erste concern-nahe Laufspur im Code


## Was sich in den letzten Tagen praktisch verbessert hat

- V3 hat vordere und mittlere Grenzen deutlich stabilisiert
- medizinische Rueckfrage und dialogische Abschlussfrage werden bewusster
  getrennt
- `Call 2` wurde kleiner und weniger summary-getrieben gedacht
- der zweite grosse Extraction-Re-Emission-Call wurde als Fehlrichtung
  erkannt und teilweise bereits zurueckgedraengt
- Response ist nicht mehr nur als fixer Textmodus gedacht
- der Recommendation-Abschluss wird nicht mehr nur textlich, sondern als
  Zustandsknoten gelesen


## Was aktuell noch fehlt oder schief sitzt

## 1. Das Anliegen ist noch nicht sauber modelliert

Das ist inzwischen die wichtigste uebergeordnete offene Architekturfrage.

Heute tragen ersatzweise Teile davon:

- `primary_focus`
- lokale Fokuspfade
- `recommendation_ready`
- Antwortpfad-Entscheidungen

Das ist zu viel Last fuer die falschen Stellen.


## 2. Readiness ist im Lauf teils zu aggressiv

Die aktuellen Befunde zeigen:

- das System kippt teilweise zu frueh auf
  `ready_for_transition` / `recommendation_ready`
- dadurch wird der Abschlussknoten zu frueh aktiv
- freie Antworten darauf werden leichter fehlgeroutet


## 3. Response und Transition sind noch nicht robust genug

Trotz Fortschritten bleibt die Kante fragil:

- freie knappe Antworten auf Abschlussfragen
- Mischung aus sozialer, medizinischer und dialogischer Bedeutung
- Wiederholung derselben Abschlussfrage
- falsche Rueckfaelle in Intent-/Call-2-Pfade


## 4. Die medizinische Wahrheit driftet in realen Laeufen noch

Der Bugreport-Strang zeigt:

- Alter, Geschlecht und sogar Symptomtyp koennen im echten Lauf falsch
  materialisiert werden

Das ist besonders kritisch, weil spaetere Entscheidungen darauf aufbauen.


## 5. Die Truth-write-Schwelle ist noch zu implizit

Neuere Architekturtexte benennen klar:

- real existiert bereits eine Schwelle
  "Truth write ja/nein"
- sie steckt aber noch implizit in Uebergangsobjekten und deren Vorhandensein

Das ist konzeptionell zu unscharf.


## 6. Recommendation-Inhalt ist noch Placeholder

Die Freigabelogik wird inzwischen ernster genommen.
Der eigentliche Recommendation-Inhalt ist aber noch kein reifer Pfad.


## 7. Safety ist architektonisch da, fachlich aber weiterhin schwach

Die 08.06.-Reviews lesen die Safety-Schicht sehr kritisch.
In den spaeteren Dokumenten ist sie nicht Hauptfokus, aber sie ist auch nicht
geloest.

Das ist wichtig:

- nicht Haupthebel fuer die aktuelle Refactor-Reihenfolge
- aber weiter ein reales Defizit des Gesamtsystems


## 8. `ConcernState` ist noch sichtbar, aber nicht validiert

Der Concern-Einbau am 12.06. ist bewusst klein.
Das ist gut.
Aber:

- noch ist nicht belegt, welche dauerhafte Rolle dieser State wirklich haben
  wird
- er ist heute eher Sichtbarkeits- und Entlastungsschritt als finale
  Semantik


## Bereits existierende Loesungsansaetze

## 1. Boundary-first statt heuristischer Schnellfixes

Das ist der wichtigste gemeinsame Ansatz ueber fast alle Tage:

- lieber den Vertrag schaerfen als lokale Sonderlogik bauen

Dieser Ansatz ist belastbar und sollte beibehalten werden.


## 2. Kleiner Response-Kern und spaetere ResponseStrategy

Fuer die hintere Problemzone existiert bereits eine erste tragfaehige Spur:

- expliziter hinterer Reaktionskern
- getrennte Antwortstrategie
- enger freier `continue`-Pfad
- statische Sonderpfade fuer robuste Kanten


## 3. Zwei-Wege-Resolver fuer den Recommendation-Abschluss

Statt lokaler Freitext-Heuristik gibt es jetzt die klarere Idee:

- aktiver Abschlussknoten
- genau zwei erlaubte semantische Ausgaenge
- enger Resolver fuer Freitext oder UI-Aktionen

Das ist ein guter Ansatz, auch wenn die Robustheit noch nicht reicht.


## 4. Concern als kleine parallele Sicht statt Sofortverschmelzung

Der aktuell vorsichtige Concern-Einbau ist architektonisch sinnvoll:

- Sichtbarkeit vor Macht
- keine vorschnelle Vermischung mit `DialogueState`, `MedicalCase` oder
  `Readiness`


## 5. Call 2 als Werkzeugkasten

Die stabilste Call-2-Richtung lautet inzwischen:

- kleine Aufgabenbereiche
- kleinere Kontexte
- kleinere Outputs
- optionaler Einsatz
- spaeter dynamische Komposition aus Modus plus Tasks


## 6. Strikte Trennung von Policy, Inhalt und Text

Diese Trennung existiert nicht nur als Idee, sondern inzwischen als
Arbeitsrichtung:

- Policy entscheidet Pfad
- Strategie entscheidet Antwortart
- Inhalt wird spaeter erzeugt
- Text formuliert nur freigegebene Bahnen


## 7. Simulation und Logs als Wahrheitsanker gegen Dokumentenrhetorik

Gerade weil viele Texte KI-generiert sind, ist ein guter vorhandener Schutz:

- Laufverhalten und Logbefunde werden mehrfach gegen die Konzepte gehalten

Das sollte unbedingt so bleiben.


## Was man aus den Dokumenten gerade nicht ueberziehen sollte

## 1. Nicht jede fruehe Priorisierung gilt noch unveraendert

Am 08.06. wirkt Observation-Identitaet wie das dominierende Kernproblem.
Das war fuer den damaligen Stand plausibel.

Heute gilt genauer:

- die Truth-Schicht bleibt zentral
- aber die aktuell wirksamste Restbaustelle sitzt hinten bei
  Transition / Response / Concern / Readiness


## 2. Concern ist noch kein bewiesenes finales Fachzentrum

Der Concern-Ansatz ist vielversprechend.
Aber die Dokumente selbst warnen davor, daraus vorschnell eine dogmatische
neue Kernwelt zu machen.


## 3. Nicht jedes "natuerlicher dialogisch" bedeutet mehr freie LLM-Macht

Die belastbare Richtung ist nicht:

- mehr Freiheit fuer das Modell

sondern:

- bessere innere Ordnung,
  damit freie Formulierung spaeter kontrollierter und natuerlicher moeglich
  wird


## 4. Recommendation-Content ist noch nicht das eigentliche Reifezeichen

Die Dokumente klingen stellenweise so, als waere spaeter nur noch
Recommendation-Inhalt offen.
Das ist zu optimistisch.

Real offen sind davor noch:

- concern-nahe Semantik
- robuste Freigabelage
- saubere Response-Transition
- stabiler freier Antwortfluss


## Verdichtetes neues Zielbild

Wenn man die letzten Tage streng zusammenzieht, ergibt sich dieses
wahrscheinlich beste Arbeitsbild:

Careena soll ein medizinisch vorsichtiges, intern stark begrenztes
Konversationssystem sein, das nicht einfach Symptome sammelt, sondern das
aktuelle fuer Careena relevante Anliegen des Nutzers aufnimmt, dazu
kontrolliert medizinische Wahrheit aufbaut, den Dialogprozess getrennt davon
fuehrt, Recommendation nur auf explizitem Wunsch und stabiler Basis freigibt
und seine Antworten entlang kleiner erlaubter Bahnen statt aus diffuser
LLM-Autonomie erzeugt.

Im Zielzustand gilt:

- `MedicalCase` traegt medizinische Wahrheit
- `DialogueState` traegt Gespraechsprozess
- eine concern-nahe Sicht traegt das fortlaufende Anliegen oder zeigt, dass
  diese Sicht am Ende doch woanders aufgehoben werden muss
- `Call 1` liefert kleine Signale
- `Call 2` ist optionaler Werkzeugkasten
- ein expliziter Truth-Write entscheidet ueber Fallfortschreibung
- `Readiness` bleibt Teilbefund fuer Mindestvoraussetzungen innerhalb der
  Freigabelogik
- Response-Policy, Antwortstrategie und Recommendation-Inhalt bleiben
  getrennte obere Schichten


## Priorisierte naechste Arbeit aus dieser Sicht

## 1. Concern-Semantik lesend gegen bestehende Pfade pruefen

Naechster sinnvoller Schritt ist nicht sofort mehr Concern-Logik,
sondern:

- welche heutigen Pfade lesen faktisch Anliegen-Semantik aus
  `primary_focus`,
  `readiness`
  oder lokalem Response-Verhalten


## 2. Hintere Transition weiter haerten

Besonders wichtig:

- Abschlussknoten
- nackte Wahl vs. echte neue medizinische Information
- freie knappe Antworten
- Schleifen durch zu aggressive Freigabe-Zustaende

## 3. Freigabelogik- / Readiness-Haerte gegen reales Anliegen korrigieren

Das System braucht eine engere Trennung zwischen:

- Pflichtfelder vorhanden
- Anliegen wirklich hinreichend verstanden


## 4. Freien `continue`-Pfad nur auf stabilerer Kante weiter ausbauen

Die neue Antwortstrategie ist sinnvoll.
Sie sollte aber nicht weiter vergroessert werden, solange der Abschlussknoten
noch zu weich ist.


## 5. Danach erst Call-2-Werkzeugkasten dynamischer ausbauen

Die spaetere Dynamisierung von `Call 2` bleibt sinnvoll,
aber erst auf stabilerer hinterer Reaktionsarchitektur.


## Schlussurteil

Die Dokumente der letzten Tage ergeben trotz viel KI-Rauschen ein relativ
klares Gesamtbild:

Die Richtung von Careena ist gut und inzwischen deutlich schaerfer als am
08.06.

Der groesste qualitative Fortschritt ist nicht ein einzelner Bugfix,
sondern die Verschiebung von:

- "mehr Extraktion, mehr Prompt, mehr Reparatur"

zu:

- "besser geschnittene Zustands- und Uebergangsschichten"

Die wichtigste offene Aufgabe ist deshalb nicht bloss,
ein paar Antworten schoener zu machen.

Die eigentliche Aufgabe ist,
das Zusammenspiel aus Anliegen, Case-Wahrheit, Dialogprozess, Freigabelogik und
Response so sauber zu machen, dass Careena gleichzeitig natuerlich wirkt und
intern streng kontrollierbar bleibt.
