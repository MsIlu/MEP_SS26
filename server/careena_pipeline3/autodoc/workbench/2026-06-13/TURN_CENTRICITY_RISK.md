# Careena3: Risiko einer zu turn-zentrierten Architektur

Stand: 2026-06-13
Status: Arbeitsnotiz
Bezug:

- `server/careena_pipeline3/autodoc/workbench/2026-06-13/CAREENA3_TARGET_SYSTEM.md`
- `server/careena_pipeline3/autodoc/workbench/2026-06-13/CAREENA3_ARCHITECTURE_ABSTRACTION.md`
- `server/careena3.py`
- `server/careena_pipeline3/application/managers/dialogue_manager.py`


## Warum diese Notiz existiert

Diese Einsicht ist wichtig genug, um sie nicht nur im Gespraech zu lassen.

Sie betrifft nicht einen einzelnen Bug, sondern eine moegliche strukturelle
Schwaeche des Systems:

- der Turn ist als Ausfuehrungseinheit richtig
- aber das System koennte zu stark turn-zentriert als Daten- und
  Zustandsmodell geworden sein

Das ist spaetestens fuer den naechsten groesseren Refactor relevant.


## Kernbeobachtung

Aktuell wirkt der Turn nicht nur wie:

- die Einheit, in der ein Dialogschritt ausgefuehrt wird

sondern zunehmend auch wie:

- der Transportbehaelter fuer fast den gesamten relevanten Zustand
- der Sammelpunkt fuer viele Wahrheitsarten
- der Ort, an dem andere Schichten ihre Sicht auf das System zwischenlagern

Das kann dazu fuehren, dass der Turn von einer sinnvollen
Ausfuehrungseinheit zu einem impliziten Sekundaersystem wird.


## Was daran nicht das Problem ist

Es ist nicht falsch, dass das System turn-basiert arbeitet.

Fuer einen Dialog ist das sogar richtig:

- der Nutzer spricht turnweise
- das System antwortet turnweise
- Orchestrierung, Logging und Response laufen sinnvoll pro Turn

Das Problem beginnt erst dort, wo turn-basiertes Ausfuehren in
turn-basiertes Wahrheitshalten kippt.


## Die eigentliche Gefahr

Wenn der Turn bei jeder Ausfuehrung grosse Teile des bestehenden Zustands
einfach mitsichtraegt, statt dass Schichten gezielt die fuer sie noetige
Wahrheit lesen, entstehen mehrere Risiken.

### 1. Der Turn wird zum universellen Transportbus

Dann wird fast jede Frage zuerst zu einer Frage an den Turn-Kontext,
obwohl sie eigentlich eine Frage an ein anderes Aggregat waere.

Zum Beispiel:

- medizinische Wahrheit gehoert an den Fall
- offene Prozesslage gehoert an den Dialogzustand
- Concern-Kontinuitaet gehoert an den Concern-Zustand

Wenn der Turn all das einfach mittransportiert, verlieren diese Grenzen an
Schaerfe.

### 2. Der Turn wird zum zweiten Wahrheitszentrum

Sobald im Turn-Arbeitsobjekt viel gespiegelt, gesammelt und weitergereicht
wird, droht ein schleichender Rollenwechsel:

- offiziell bleibt die Wahrheit in den persistierten Aggregaten
- praktisch wird aber der Turn zum Ort, an dem "das meiste Wichtige gerade
  liegt"

Das ist architektonisch gefaehrlich.

### 3. Jede neue Logik vergroessert den Turn weiter

Wenn der Standardweg ist, neue Information einfach in den Turn-Kontext zu
legen, dann wird fast jede neue fachliche Anforderung auf denselben grossen
Container aufgeschichtet.

Dann wird nicht nur die Logik groesser, sondern auch die Kopplung zwischen
den Schichten.

### 4. Schichten lesen nicht mehr gezielt, sondern bequem

Ein gesundes System laesst Schichten nur die Wahrheit lesen, die sie fuer ihre
Arbeit wirklich brauchen.

Ein zu turn-zentriertes System verlockt dagegen zu:

- "liegt ja schon im Turn"
- "haengen wir noch ein Feld dazu"
- "geben wir es einfach weiter"

Das ist kurzfristig bequem und langfristig teuer.


## Woran man das im aktuellen System erkennt

Im aktuellen HTTP-Einstieg wird pro Request bereits ein grosses Paket in den
Turn hineingegeben:

- `conversation_messages`
- `existing_case`
- `existing_dialogue_state`
- `existing_concern_state`

Danach wird daraus turn-intern erneut ein grosser Arbeitskontext aufgebaut,
der sowohl persistierte Wahrheit als auch abgeleitete und ausgabenahe
Informationen mitfuehrt.

Die Beobachtung ist daher nicht:

- "der Turn liest ueberhaupt Zustand"

sondern eher:

- "der Turn traegt sehr viel Zustand als Gesamtpaket mit sich herum"


## Architekturelle Lesart

Der Turn sollte im Zielsystem sein:

- Ausfuehrungseinheit
- Orchestrierungsrahmen
- kurzlebiger Arbeitskontext

Der Turn sollte nicht sein:

- primaerer Speicherort fuer Wahrheit
- Ersatz fuer gezielte Schichtzugriffe
- universelles Datenpaket fuer alle Problemarten


## Die eigentliche Design-Regel

Die richtige Zielregel lautet nicht:

- "moeglichst wenig Turn"

sondern:

- "so viel Turn wie fuer die Ausfuehrung noetig, aber so wenig Turn wie
  moeglich als Wahrheits- und Transportmodell"

Das ist der entscheidende Unterschied.


## Was das fuer den naechsten groesseren Refactor bedeutet

Der naechste groessere Refactor sollte diese Frage explizit stellen:

- Welche Informationen muessen wirklich in den Turn hinein?
- Welche Informationen koennen von einer Schicht gezielt aus einem
  kanonischen Aggregat gelesen werden?
- Welche Daten sind nur Zwischenbefund und duerfen den Turn wieder verlassen?
- Welche Felder im Turn-Kontext existieren nur deshalb, weil andere Vertraege
  noch nicht scharf genug sind?

Diese Fragen sind nicht nur Detailfragen.
Sie sind ein eigener Refactor-Treiber.


## Praktische Verdachtsregel

Immer wenn eine neue Logik am einfachsten dadurch eingebaut werden kann, dass:

- noch ein Feld an den Turn-Kontext gehaengt wird
- noch ein bestehender Zustand in den TurnInput kopiert wird
- noch eine weitere Sicht auf dieselbe Wahrheit im Turn gesammelt wird

sollte das als Warnsignal gelesen werden.

Die Rueckfrage muss dann sein:

- Ist das wirklich Turn-Arbeitszustand?
- Oder fehlt eigentlich ein schaerferer Vertrag an einer anderen Schicht?


## Vorlaeufiges Fazit

Ja, es ist sehr plausibel, dass das System in einer wichtigen Weise zu
eindimensional geworden ist:

- nicht weil es turn-basiert arbeitet
- sondern weil der Turn zu viel von der gesamten Systemrealitaet
  mittransportiert

Das ist keine kleine Stilfrage.
Es ist ein moeglicher Hauptgrund dafuer, dass spaetere Fachlogik schnell
wieder das halbe System beruehrt.

Fuer den naechsten groesseren Refactor sollte diese Einsicht daher als
explizite Architekturwarnung erhalten bleiben.
