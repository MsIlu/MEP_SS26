# Careena3: Runtime World vs Turn World

Stand: 2026-06-13
Status: Arbeitsgrundlage
Bezug:

- `server/careena_pipeline3/autodoc/workbench/2026-06-13/TURN_CENTRICITY_RISK.md`
- `server/careena_pipeline3/autodoc/workbench/2026-06-13/CAREENA3_TARGET_SYSTEM.md`


## Die eigentliche Frage

Die naechste wichtige Architekturfrage ist nicht:

- was kommt in `TurnInput`
- was kommt in `TurnContext`
- welchen Vertrag schneiden wir als naechstes um

Sondern:

- Welche zwei Welten sind hier ungesund miteinander verkoppelt?


## Die zwei Welten

### 1. Runtime World

Das ist die laufende Arbeitsgrundlage des Systems.

Hier lebt alles, was nicht an einen einzelnen Turn gebunden ist, sondern fuer
mehrere Turns als Ausgangslage, Referenz oder Arbeitskontext gebraucht wird.

Beispiele:

- Fallwahrheit
- Dialogprozess
- laufender Concern-Bezug, falls er als eigene Sicht bestehen bleibt
- relevante Langzeit-Historie
- aktive offene Knoten, die nicht nur fuer genau diesen Turn gelten

### 2. Turn World

Das ist die Ausfuehrungswelt einer einzelnen Nachricht.

Hier lebt alles, was nur fuer die Verarbeitung dieses einen Turns gebraucht
wird.

Beispiele:

- aktuelle Nutzernachricht
- Entry-Interpretation
- turn-lokale Assessments
- konkrete Ausfuehrungsentscheidungen
- Response-Auswahl
- Textgenerierung


## Der eigentliche Architekturfehler

Der Turn ist als Ausfuehrungseinheit richtig.

Der Fehler beginnt dort, wo Runtime World nicht nur gelesen wird, sondern bei
jedem Turn als Gesamtpaket in Turn World hineingezogen wird.

Dann passiert schleichend Folgendes:

- Turn World wird zum Transportbus fuer Runtime-Zustand
- Turn World wird zum Schatten der eigentlichen Wahrheitszentren
- neue Logik wird bevorzugt am Turn angedockt statt an der eigentlichen
  Heimatstruktur


## Die saubere Trennfrage

Fuer jede Information muss kuenftig zuerst gefragt werden:

- Gehoert das zur laufenden Arbeitsgrundlage?
- Oder entsteht das nur fuer die Verarbeitung dieser einen Nachricht?

Wenn es zur laufenden Arbeitsgrundlage gehoert, dann gehoert es in Runtime
World.

Wenn es nur fuer die Ausfuehrung eines Turns gebraucht wird, dann gehoert es
in Turn World.


## Die Leitregel

Runtime World wird nicht pro Turn mitgeschleppt.

Turn World arbeitet gegen Runtime World.

Das heisst:

- der Turn bekommt nicht moeglichst viel Zustand eingepackt
- der Turn liest gezielt, was er braucht
- der Turn erzeugt Deltas, Assessments und Entscheidungen
- danach wird Runtime World fortgeschrieben


## Woran man im aktuellen System die Verkopplung erkennt

Das aktuelle System ist naeher an:

- `Runtime World -> in Turn hineinladen -> im Turn weiterreichen -> aus dem Turn wieder zurueckschreiben`

als an:

- `Turn arbeitet gegen Runtime World und liefert gezielte Fortschreibung`

Das ist der Kern des Problems.


## Warum dieser Shift wichtig ist

Solange diese beiden Welten nicht sauber entkabelt sind, wirken viele lokale
Refactors groesser als sie sein sollten.

Dann fuehlt sich fast jede Aenderung so an, als muesse man:

- Turn
- Zustand
- Response
- und Prozesslogik

gleichzeitig anfassen.

Wenn die Welten sauber getrennt sind, wird klarer:

- was Runtime-Problem ist
- was Turn-Problem ist
- was nur eine lokale Stage-Logik ist


## Die richtige Folgefrage fuer den Refactor

Die naechste gute Arbeitsfrage lautet daher:

- Welche Teile des aktuellen Systems sind eigentlich Runtime World, welche sind
  Turn World, und wo wird Runtime World heute nur deshalb durch Turn World
  geschleppt, weil eine eigene Runtime-Struktur oder ein sauberer Zugriff fehlt?


## Unmittelbare Refactor-Bedeutung

Wenn wir diesen Shift ernst nehmen, ist der naechste groessere Umbau nicht
primaer:

- ein Vertrags-Umsortieren innerhalb des Turns

sondern:

- eine Entkabelung von Runtime World und Turn World

Erst danach lohnt sich die feinere Frage, welche Turn-Vertraege noch bleiben
oder kleiner werden sollen.


## Kurzfassung

Der zentrale Architektur-Shift lautet:

- nicht mehr alles vom Turn aus denken
- sondern zwei Welten sauber trennen:
  Runtime World und Turn World

Die wichtigste Regel daraus ist:

- Der Turn ist Ausfuehrung.
- Die Runtime ist Arbeitsgrundlage.
- Die Runtime wird nicht zum Turn-Schatten.
