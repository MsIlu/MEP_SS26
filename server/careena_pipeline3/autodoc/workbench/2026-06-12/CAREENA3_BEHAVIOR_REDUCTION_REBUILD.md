# Careena3 Behavior Reduction Rebuild

## Zweck

Diese Notiz versucht nicht,
den aktuellen Code zu verteidigen
oder ihn Block fuer Block nachzuerzaehlen.

Stattdessen wird das beobachtbare Verhalten von Careena 3
gedanklich immer weiter auseinandergebaut,
bis nur noch das groebste tragende Geruest uebrig bleibt.

Danach wird dieses Geruest von unten wieder aufgebaut:
nicht entlang der heutigen Codegrenzen,
sondern entlang der Frage,
welche Schichten logisch wirklich noetig waeren,
damit ein begrenztes medizinisches Dialogsystem stabil funktioniert.

Der Wechsel zu `recommend`
wird hier bewusst ausgeblendet.
Es geht nur um den allgemeinen Turn-Fluss davor.

---

## 1. Ausgangsbeobachtung

Wenn man den heutigen Careena-3-Code
nicht nach seinen Namen,
sondern nach seinem tatsaechlichen Bewegungsmuster liest,
dann tut das System in einem Turn im Kern ungefaehr Folgendes:

1. Eine neue Nutzernachricht kommt herein.
2. Ein frueher LLM-Schritt versucht grob zu deuten,
   was das fuer eine Nachricht ist.
3. Danach wird entschieden,
   ob ueberhaupt tiefer extrahiert werden soll.
4. Falls ja,
   wird ein weiterer LLM-Schritt fuer medizinische Extraktion aufgerufen.
5. Das Extraktionsergebnis wird nachtraeglich eingegrenzt,
   repariert,
   umgedeutet
   und an die Fallwahrheit angeschlossen.
6. Aus der aktualisierten Fallwahrheit
   werden Follow-up-,
   Prozess-
   und Freigabesignale abgeleitet.
7. Daraus wird ein naechster Antwortpfad gewaehlt.
8. Fuer manche Antwortpfade wird noch einmal ein eigener Antwort-LLM-Call benutzt.
9. Das Ergebnis wird als Systemantwort zurueckgegeben
   und in der Session mitgefuehrt.

Diese Form ist schon die erste brauchbare Verdichtung:
Careena 3 ist aktuell nicht einfach ein einzelner Prompt,
aber auch noch nicht voll eine kleine saubere Maschinenlogik.
Es ist ein kontrollierter Mehrschrittfluss,
der versucht,
zwischen Chat,
Extraktion,
strukturierter Wahrheit
und Antwortwahl zu vermitteln.

---

## 2. Weitere Reduktion

Wenn man aus diesem Ablauf
alles entfernt,
was eher Detail,
Sonderfall
oder aktuelle Zwischenarchitektur ist,
dann bleibt:

1. Nachricht lesen
2. frueh einordnen
3. bei Bedarf tiefer auswerten
4. bekannte Wahrheit fortschreiben
5. naechsten erlaubten Zug bestimmen
6. Antwort erzeugen

Schon hier sieht man eine wichtige Sache:
Der eigentliche Kern von Careena 3
ist nicht
`Extraktion`
und auch nicht
`Antwortgenerierung`,
sondern die Mitte:

- Was bedeutet diese Nachricht fuer den laufenden Fall?
- Veraendert sie die bekannte Wahrheit?
- Und welcher naechste Zug ist danach ueberhaupt erlaubt?

Fast alle heutigen Probleme entstehen dort,
wo diese Mitte unklar ist.

---

## 3. Minimalgeruest

Wenn man noch haerter reduziert
und wirklich nur das nackte Geruest stehenlaesst,
dann bleibt:

`Nachricht -> Call 1 -> evtl. Call 2 -> State-Update -> naechster Zug -> evtl. Call 3 -> Antwort`

Das ist das groebste sinnvolle Ablaufgeruest,
das aus dem heutigen System noch uebrig bleibt.

Dabei bedeuten die Knoten nicht den heutigen Code,
sondern nur ihre logisch kleinste Rolle:

- `Nachricht`
  roher neuer Nutzereingang

- `Call 1`
  fruehe Deutung:
  Worum geht es grob
  und lohnt sich tiefere Arbeit?

- `evtl. Call 2`
  tiefere inhaltliche Arbeit:
  Was steckt medizinisch oder dialogisch wirklich in der Nachricht?

- `State-Update`
  bekannte Wahrheit
  und laufender Bearbeitungszustand
  werden fortgeschrieben

- `naechster Zug`
  aus dem neuen Zustand wird bestimmt,
  was das System jetzt sinnvollerweise tun darf

- `evtl. Call 3`
  freiere Formulierung oder spaetere Antwortintelligenz

- `Antwort`
  sichtbarer Systemzug nach aussen

Mehr braucht man auf dieser Ebene nicht.
Alles andere ist Unterbau,
Spezialisierung
oder Sicherheitskante.

---

## 4. Was in diesem Geruest logisch getrennt sein muss

Damit dieses Minimalgeruest tragfaehig ist,
muessen darin einige Dinge hart getrennt bleiben.

### 4.1 Deutung ist nicht Wahrheit

`Call 1`
und Teile von `Call 2`
duerfen eine Nachricht deuten,
klassifizieren
oder vermuten,
was gemeint ist.

Aber diese Deutung ist noch nicht dieselbe Sache wie:

- kanonische Fallwahrheit
- offener Klaerungsbedarf
- erlaubter naechster Zug

Sobald diese Ebenen ineinanderlaufen,
wirkt das System logisch,
ohne es wirklich zu sein.

### 4.2 Extraktion ist nicht Schreiben

Dass etwas aus der Nachricht erkannt wurde,
heisst noch nicht,
dass es direkt in den Fall geschrieben werden sollte.

Zwischen
`Call 2`
und
`State-Update`
gibt es logisch immer eine eigene Schwelle:

- neue relevante Information
- Update bestehender Information
- Korrektur
- unklar
- fuer den Fall praktisch irrelevant

Wenn diese Schwelle unsauber ist,
wirkt der ganze Mittelstreifen unzuverlaessig.

### 4.3 Zustand ist nicht Antwort

Der Zustand soll sagen,
wo das System fachlich und dialogisch steht.

Die Antwort soll nur den daraus erlaubten Zug formulieren.

Wenn die Antwortschicht fehlende Zustandssemantik ersetzt,
wirkt das System im guenstigen Fall fluessiger,
im unguenstigen Fall aber zufaellig.

### 4.4 Natuersprache ist nicht Steuervertrag

Freier Text,
Buttons,
kurze Antworten,
Ja/Nein,
soziale Antworten
und gemischte Nachrichten
muessen intern auf kleine semantische Vertrage abgebildet werden.

Nicht die Oberflaechenform darf ueber die Logik entscheiden,
sondern die erkannte Funktion im laufenden Turn.

---

## 5. Das Geruest noch abstrakter gelesen

Wenn man das Geruest nicht technisch,
sondern funktional liest,
dann ist Careena 3 im Kern:

`Eingang -> Deutung -> Vertiefung -> Uebernahmeentscheidung -> Fortschrittsentscheidung -> Formulierung`

Diese Lesart ist fast hilfreicher als
`Call 1 / Call 2 / Call 3`,
weil sie weniger an bestehende Implementationsnamen gebunden ist.

Sie zeigt:

- das System braucht einen fruehen Deuter
- einen optionalen Vertiefer
- eine Wahrheitskante
- eine Fortschritts- oder Next-Step-Kante
- und erst danach eine Formulierung

Wenn man Careena 3 sauber machen will,
dann muss man genau diese fuenf Rollen sauber schneiden.

---

## 6. Logischer Wiederaufbau vom Minimalgeruest aus

Jetzt wird das Geruest wieder ausgebaut,
aber nur mit Schichten,
die logisch wirklich notwendig sind.

### Stufe A: Nachricht und fruehe Deutung

Minimal noetig ist eine erste Stufe,
die auf eine neue Nachricht schaut
und nur wenige Fragen beantwortet:

- ist die Nachricht fuer den medizinischen Fall relevant?
- ist sie primaer inhaltlich,
  dialogisch,
  korrigierend,
  bestaetigend
  oder nur sozial?
- braucht es tieferes Verstehen,
  oder reicht der aktuelle Zustand schon?
- ist offensichtlich,
  dass der Fall nicht erweitert werden soll?

Diese Stufe sollte moeglichst klein bleiben.
Sie darf nicht anfangen,
heimlich schon die spaetere Fachlogik zu tragen.

Ihre Aufgabe ist nur:
den Turn in eine brauchbare Arbeitsrichtung zu stellen.

### Stufe B: optionale Vertiefung

Wenn die erste Stufe sagt,
dass mehr Verstehen noetig ist,
dann braucht es eine zweite Stufe.

Diese sollte nicht als
"groesserer Call fuer alles"
gelesen werden,
sondern als begrenzte Aufgabenmaschine.

Sie darf je nach Lage nur genau die Arbeit bekommen,
die gerade wirklich noetig ist,
zum Beispiel:

- medizinische Information extrahieren
- bestehende Information praezisieren
- Korrekturen deuten
- unklare Zuordnung sichtbar machen
- markieren,
  ob ueberhaupt neuer fallrelevanter Inhalt entstanden ist

Diese Stufe sollte nicht selbst entscheiden:

- was der offizielle neue Systemzustand ist
- welche Follow-up-Frage als naechstes kommt
- ob das System jetzt schon ausreichend verstanden hat

Sie ist Zuarbeit,
nicht Souveraenitaet.

### Stufe C: Uebernahme in Wahrheit

Jetzt braucht das System eine explizite Wahrheitskante.

Hier wird aus Vertiefungsergebnissen
und vorhandenem Fallkontext entschieden:

- was wird neu uebernommen?
- was aktualisiert Bestehendes?
- was ist nur Bestaetigung?
- was ist Widerspruch?
- was ist unklar
  und erzeugt eher Klaerungsbedarf als direkte Uebernahme?

Diese Kante ist logisch zentral.

Hier sollte moeglichst wenig Prompt-Magie sitzen.
Denn wenn diese Kante unsauber ist,
werden spaetere Readiness-,
Follow-up-
und Antwortentscheidungen auf Sand gebaut.

### Stufe D: Fortschritt und naechster Zug

Erst nach der Wahrheitskante
kommt die eigentliche Prozessfrage:

- ist fuer den aktuellen Problemstrang genug klar?
- fehlt noch gezielte Klaerung?
- wurde gerade nur auf eine Rueckfrage geantwortet?
- wurde zugleich neuer Inhalt eingebracht?
- ist eher medizinische Exploration noetig
  oder eher ein dialogischer Abschlusszug?

Das ist die eigentliche Schicht,
die im heutigen System oft zwischen
`DialogueState`,
`Readiness`,
`Gate`,
`primary_focus`
und concern-nahen Begriffen verteilt wirkt.

Logisch sollte sie aber eine einzige Rolle haben:

`Welcher naechste Zug ist auf Basis des jetzt bekannten Zustands erlaubt?`

Nicht mehr
und nicht weniger.

### Stufe E: Formulierung

Erst jetzt ist die Antwortschicht dran.

Sie sollte nur noch wissen:

- welche Antwortfamilie erlaubt ist
- welche bekannte Wahrheit genannt werden darf
- ob eine Rueckfrage,
  kurze Weiterfuehrung
  oder begrenzte dialogische Antwort gefragt ist

Wenn dafuer ein LLM genutzt wird,
dann als Formulierungswerkzeug
innerhalb eines schon entschiedenen Zuges.

Nicht als versteckter Ersatz
fuer fehlende Fortschrittslogik.

---

## 7. Daraus folgt ein logisch saubereres Zielgeruest

Wenn man Careena 3 auf diese Weise neu zusammensetzt,
dann waere ein sinnvoller Zielablauf eher:

`Nachricht`
-> `fruehe Turn-Deutung`
-> `optional gezielte Vertiefung`
-> `explizite Truth-Write-Entscheidung`
-> `fortschrittsbasierte Next-Step-Entscheidung`
-> `optional freie Formulierung innerhalb enger Antwortfamilie`
-> `Antwort`

Oder noch kuerzer:

`Nachricht -> Deuten -> Verstehen -> Uebernehmen -> Entscheiden -> Formulieren`

Das ist das eigentliche nackte Funktionsskelett,
auf das der heutige Code hinauslaeuft,
auch wenn er das noch nicht ueberall offen ausspricht.

---

## 8. Welche Teile man beim Wiederaufbau zuerst einbauen sollte

Wenn man von diesem Grundgeruest aus neu priorisiert,
dann waere die sinnvolle Reihenfolge:

### 1. Wahrheitskante stabilisieren

Zuerst muss klar sein,
was aus einer Nachricht ueberhaupt als Fallwahrheit uebernommen wird
und was nicht.

Solange diese Kante unsauber ist,
sind spaetere Follow-up-,
Gate-
und Antwortschichten immer nur halb belastbar.

### 2. Next-Step-Schicht als echte Souveraenitaet bauen

Danach braucht es genau eine Schicht,
die den erlaubten naechsten Zug bestimmt.

Diese Schicht sollte nicht an Promptlaune haengen
und nicht dieselbe Frage gleichzeitig als
Readiness,
Concern-Phase,
Follow-up-Rest
und Antwortmodus verstreuen.

### 3. Fruehe Deutung klein halten

Erst wenn Wahrheit
und Next-Step stabiler sind,
sollte man die fruehe Deutung weiter verfeinern.

Sonst landet zu viel Verantwortung wieder zu frueh im Scout.

### 4. Vertiefungs-Call als Werkzeugkasten,
nicht als Weltmodell

Die tiefere LLM-Arbeit sollte dann
auf wenige klar benannte Arbeitsarten begrenzt werden.

Nicht:
"Verstehe alles und liefere schon die halbe Architektur."

Sondern:
"Bearbeite genau diese Art von inhaltlicher Vertiefung."

### 5. Freie Antwort wieder staerker machen,
aber spaet

Erst wenn die Semantik unterhalb davon sauberer ist,
sollte man die freie Antwortlane wieder offensiver ausbauen.

Sonst wirkt das System vorn intelligenter,
wird aber hinten semantisch nicht wirklich stabiler.

---

## 9. Was dabei bewusst nicht wieder eingebaut werden sollte

Aus diesem Reduktionspfad folgt auch,
was man gerade eher vermeiden sollte:

- keine neuen lokalen Heuristikinseln,
  die nur einen sichtbaren Spezialfall retten
- keine zusaetzlichen Begriffe,
  die nach Architektur klingen,
  aber keine echte eigene Entscheidung tragen
- keine Antwortschicht,
  die fehlende Zustandslogik durch guten Stil kaschiert
- kein groesserer Vertiefungs-Call,
  der still Merge-,
  Gate-
  und Antwortpolitik mit erledigen soll
- keine Gleichsetzung von
  "lokal genug Daten"
  mit
  "Anliegen ausreichend verstanden"

---

## 10. Verdichtetes Fazit

Wenn man den heutigen Careena-3-Code
bis auf sein nacktes Geruest abbaut,
dann bleibt nicht
`Prompt + etwas State`,
sondern:

`Nachricht -> fruehe Deutung -> optionale Vertiefung -> Wahrheitsupdate -> Next-Step-Entscheidung -> Formulierung`

Das ist die kleinste sinnvolle Struktur,
die im System heute schon angelegt ist.

Der logisch richtige Wiederaufbau waere dann:

1. zuerst die Wahrheitskante sauber machen
2. dann die Next-Step-Souveraenitaet daraus ableiten
3. danach fruehe Deutung und Vertiefung eng darauf ausrichten
4. und erst spaeter die freie Gespraechsintelligenz wieder staerker machen

Wenn Careena 3 einmal wirklich stabil werden soll,
dann ist wahrscheinlich genau diese Reihenfolge die entscheidende:

nicht zuerst besser reden,
sondern zuerst sauber wissen,
was die Nachricht bedeutet,
was davon wahr wird
und welcher naechste Zug daraus logisch folgt.
