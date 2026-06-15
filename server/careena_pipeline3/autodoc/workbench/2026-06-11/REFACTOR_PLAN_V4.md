# Careena3 Refactor Plan V4

Stand: 2026-06-11
Status: aktiv

Baut auf:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
- `autodoc/workbench/2026-06-09/BLOCK5_PROCESS_STATE_CONCEPT.md`
- `autodoc/workbench/2026-06-09/BLOCK6_RESPONSE_TRANSITION_CONCEPT.md`
- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `autodoc/2026-06-11/BUG_REPORTS_V4.md`


## Zweck

V4 setzt nicht noch einmal ganz vorne an.

Die vorderen V3-Grenzen sind im aktiven Code heute bereits weit genug
stabilisiert:

- sichtbare Turn-Orchestrierung
- kleinere Entry-Signale
- kleinere Call-2-Vertraege
- klarere Truth-Kante
- sichtbarere Process-/Readiness-Trennung

Der neue Fokus von V4 liegt deshalb auf dem hinteren und erneut ausbaurelevanten
Teil des Systems:

1. Response-/Transition-Bereich sauber fertigstellen
2. den Antwortfluss wieder robust herstellen
3. danach das modulare Werkzeugkasten-Prinzip von `Call 2` wirklich dynamisch
   machen

V4 ist damit keine Abkehr von V3.
V4 ist eine Fortsetzung auf spaeterer Baustelle mit engerem Fokus.


## Was aus V3 bewusst unveraendert uebernommen wird

Die Haltungsregeln aus V3 bleiben gueltig und sind fuer V4 weiterhin
verbindlich.

Insbesondere:

- boundary first, not feature first
- behavior over names
- lieber eine kleine ehrliche Schicht als eine fachlich scheinbar clevere,
  aber architektonisch gemischte Loesung
- Uebergangsobjekte duerfen sichtbar bleiben, wenn sie Grenzen schuetzen
- der `DialogueManager` bleibt Orchestrierungsmitte und soll nicht wieder
  mit versteckter Policy oder Fachmagie aufgeladen werden
- Text darf fehlende Zustandssemantik nicht kaschieren
- spaetere Ausbaupfade sind erlaubt, aber nicht auf Kosten sauberer
  Verantwortungsgrenzen


## Dokumentationsregel in V4

Wenn ein Modul in V4 semantisch enger geschnitten,
als Placeholder abgesichert
oder als neue Ausbaukante vorbereitet wird,
soll eine kleine strukturierte Code-Dokumentation mitlaufen oder aktualisiert
werden.

Bevorzugte Minimalinhalte:

- Rolle
- Eingangsvertrag
- Ausgangsvertrag
- was das Modul explizit nicht entscheidet
- ob es noch transitional,
  placeholderhaft
  oder bewusst vorbereitete Ausbaukante ist

Wenn ein Name oder ein aktueller Vertrag historisch schief liegt,
ohne dass schon umbenannt wird,
darf die Doku das explizit sagen.

Wichtig:

- die Doku soll keine Prosawand werden
- sie soll reale Grenzentscheidungen im Code schneller lesbar machen
- sie ist Teil des Refactors und kein spaeterer Luxus


## Platzhalter-Regel in V4

V4 uebernimmt ausdruecklich die V3-Haltung,
dass funktionale Placeholder erlaubt
und unsauberen Mischloesungen vorzuziehen sind.

Das gilt besonders dann,
wenn eine fachlich bessere medizinische Logik spaeter von anderen Personen
ausgebaut werden soll,
ohne die Architektur wieder aufzureissen.

Ein guter Placeholder in V4:

- schuetzt eine Schichtgrenze
- ist im Code und in der Doku als Placeholder oder Ausbaukante markiert
- liefert einen kleinen ehrlichen Vertrag
- taeuscht keine fachliche Reife vor

Nicht gut ist:

- fachlich halbkluge Zwischenlogik,
  die medizinische,
  dialogische
  und response-nahe Entscheidungen unsichtbar vermischt

Der Massstab lautet:

- lieber architektonisch sauber andockbare Ausbaufläche
  als heute schon "intelligenter" wirkende,
  aber spaeter schwer erweiterbare Mischlogik


## Fortschreibungsregel fuer V4

V4 soll waehrend des laufenden Refactors nicht nur Zielbild,
sondern auch Arbeitsstand dokumentieren.

Deshalb gilt wie in V3:

- unter jedem Block darf und soll spaeter ein verdichteter Stand-Abschnitt
  mitlaufen
- dort soll sichtbar werden:
  was erreicht ist,
  was bewusst offen bleibt,
  und wohin sich der Fokus verschiebt

Bevorzugte Form:

- `### Stand [Datum] [Statushinweis]`
- kurze Punkte zu:
  erreichte Struktur,
  bewusst stehen gelassene Reste,
  naechster sinnvoller Hebel

Die Fortschreibung soll:

- den realen Codezustand abbilden
- keine Erfolgsrhetorik erzeugen
- keine Kleinstaenderungen aufblasen

Ziel:

- der Plan bleibt waehrend der Arbeit lebendiger Arbeitsanker
  statt nur Startdokument


## V4-Arbeitsannahme aus dem aktuellen Code

Der aktuelle Code zeigt:

- `DialogueManager` ist als Turn-Sequenz sauber sichtbar
- `EntryManager` traegt schon einen kleinen ersten Umgang mit
  `pending_dialogue_transition`
- `ResponseManager` waehlt heute Antwortpfade, haelt aber den hinteren
  Zustandsvertrag noch zu grob in `response_mode`
- die aktuelle Restkante sitzt dadurch nicht nur im `ResponseManager`,
  sondern in der gemeinsamen Strecke aus `Entry`,
  `Transition`
  und `Readiness`
- `ResponseTextBuilder` formuliert bereits getrennt, ist aber noch an eine
  zu kleine Policy-Semantik gebunden
- `PendingDialogueTransition` ist als Idee da, aber noch kein vollwertiger
  kleiner hinterer Steuervertrag
- der Recommendation-Abschlussknoten ist strukturell bereits als kleiner
  Zwei-Wege-Knoten sichtbar,
  aber freie Antworten darauf sind noch nicht robust genug
- die Gate-/Readiness-Lage wirkt in den juengeren Logbefunden teils noch zu
  aggressiv und kann den hinteren Knoten dadurch in Schleifen oder zu fruehe
  Recommendation-Uebergaenge druecken
- `Call 2` ist schon deutlich kleiner, aber seine Werkzeugkasten-Idee ist
  noch eher promptseitig vorbereitet als wirklich dynamisch komponiert

Die wichtigste Lesart fuer V4 lautet deshalb:

- das Hauptproblem ist nicht mehr primaer medizinische Extraktion
- das Hauptproblem ist die hintere Reaktions- und Uebergangslogik ueber
  mehrere Schichten hinweg
- der offene Fehlerraum sitzt heute vor allem an der Kombination aus
  `Entry`,
  dialogischer Transition,
  Readiness/Gate
  und erst danach am finalen Antworttext
- danach folgt als naechster Ausbauhebel die echte Dynamisierung des
  `Call-2`-Werkzeugkastens


## Aktuelle Codebasis fuer V4

Die folgenden Stellen sind fuer V4 der reale Ausgangspunkt:

- `application/managers/dialogue_manager.py`
- `application/managers/entry_manager.py`
- `application/managers/response_manager.py`
- `application/services/response_text_builder.py`
- `application/services/dialogue_state_service.py`
- `application/services/recommendation_state_service.py`
- `application/services/readiness_evaluator.py`
- `models/domain/dialogue.py`
- `models/turn/response_plan.py`
- `models/common/types.py`
- `llm/context.py`
- `llm/prompts/case_extraction.py`
- `application/services/call2_operation_mode_service.py`

V4 urteilt bewusst vom Verhalten dieser aktiven Kanten aus und nicht aus
ihren historischen Namen.


## Neue Hauptfrage von V4

Wie wird der hintere Teil des Turns so geschnitten, dass das System je nach
Zustand sauber zwischen verschiedenen Reaktionsarten unterscheiden kann:

- statische Rueckfrage
- KI-gestuetzte Rueckfrage
- Recommendation-Uebergang
- Recommendation-Inhalt
- einfache bestaetigende Weiterfuehrung

Und wie wird dabei verhindert, dass:

- ein Abschlussknoten zu frueh als recommendation-ready gelesen wird
- freie Antworten wie `ja`,
  `weitere Beschwerden`
  oder `Empfehlung jetzt`
  in unpassende Extraktions- oder Fallback-Pfade fallen
- der hintere Knoten durch zu aggressive Gate-/Readiness-Signale erneut
  dieselbe Abschlussfrage produziert

Dabei ist zentral:

- medizinische Steuersignale sind nicht dasselbe wie dialogische
  Steuersignale
- beide koennen gleichzeitig relevant sein
- dieselbe Nutzernachricht darf nicht zwangsweise nur einer einzigen
  Bedeutungsart zugeordnet werden, wenn der Turn architektonisch mehrere
  kleine Folgerungen braucht


## Verantwortungsklaerung fuer V4

Die Frage

- `soll das der ResponseManager machen oder der DialogueManager?`

wird in V4 vorlaeufig so beantwortet:

- der `DialogueManager` soll weiterhin orchestrieren und explizite Ergebnisse
  anwenden
- die hintere Reaktions- und Uebergangspolitik soll nicht in den
  `DialogueManager` zurueckwandern
- V4 sucht daher eher eine kleinere explizite Response-/Transition-Schicht
  ueber die gemeinsame Kante von
  `EntryManager`,
  `ResponseManager`,
  `RecommendationStateService`
  und angrenzenden kleinen Vertragsobjekten

Nicht sinnvoll waere:

- den `DialogueManager` wieder mit Sonderfaellen fuer
  `nein`, `doch noch etwas`, `freie Rueckfrage`, `Recommendation jetzt`
  oder spaetere Contentpfade zu beladen

Sinnvoll waere:

- der `DialogueManager` bleibt Leser und Anwender kleiner klarer Ergebnisse
- die hintere Policy liefert diese Ergebnisse sichtbar


## Zielbild von V4

Careena3 soll nach V4 im hinteren Bereich klarer in diese Ebenen lesbar sein:

1. medizinische Prozess- und Requirement-Lage
2. Entry-seitige Deutung des aktuellen Turns gegen aktive
   Uebergangs-/Abschlussknoten
3. dialogische Uebergangs- und Abschlusslage
4. fortlaufende Concern-Lage des aktuellen Nutzeranliegens
5. Readiness- und Gate-Lage
6. Response-Policy
7. Antwortstrategie
8. finaler Text oder spaeterer KI-Inhalt
9. Recommendation-Inhaltskante
10. spaeter dynamische Werkzeugkasten-Komposition von `Call 2`

Wichtige Schutzregel:

- keine einzelne Klasse soll zugleich medizinische Wahrheit,
  Uebergangspolitik,
  Antwortwahl
  und Textreparatur still zusammenziehen


## V4-Leitprinzipien

## 1. Hinten ebenso boundary-first wie vorne

Der Response-Bereich wird nicht als "letzter Rest" behandelt,
sondern als eigene Architekturgrenze.

## 2. Zustand vor Text

Der Text darf nur formulieren, was der Zustand und die Policy bereits tragen.

## 3. Medizinische und dialogische Steuerung getrennt halten

Medizinische Pflichtinformation,
dialogischer Abschluss,
Recommendation-Freigabe
und spaetere Recommendation-Inhaltserzeugung
sind verschiedene Rollen.

Das gilt auch dann,
wenn dieselbe Nutzernachricht Anteile aus mehreren dieser Rollen traegt.

## 4. Adaptive Reaktion statt Einheitsantwort

Das Ziel ist nicht eine einzige universelle Rueckfrageform,
sondern eine kleine saubere Reaktionsarchitektur,
die je nach Zustand den richtigen Pfad waehlt.

Diese Architektur muss auch freie knappe Antworten auf aktive
Abschlussknoten robust tragen koennen.

## 5. Erst Reaktionsarchitektur, dann inhaltlicher Ausbau

Bevor spaetere freie KI-Rueckfragen oder Recommendation-Inhalte ausgebaut
werden, muss der Schaltpunkt sauber sein.

## 6. Dynamischer Werkzeugkasten erst auf stabileren hinteren Grenzen

Die echte Dynamisierung von `Call 2` soll auf einem stabileren hinteren
Reaktionssystem aufbauen, nicht parallel wieder neue Grenzunschärfe erzeugen.

## 7. Dokumentierte Ausbaufaehigkeit vor lokaler Cleverness

Die Architektur soll so geglaettet werden,
dass medizinisch fachliche Bereiche spaeter von anderen Personen erweitert
werden koennen,
ohne die Grenzlogik des Systems wieder zu zerstoeren.

Darum gilt:

- lieber kleine dokumentierte Andockstellen
- lieber sichtbare Placeholder
- lieber explizite Nicht-Zustaendigkeiten

als lokale Speziallogik,
die heute "praktisch" wirkt,
spaeter aber Architektur und Fachausbau verklebt

## 8. Nutzeranliegen spaeter explizit stabilisieren

Fuer V4 ist bereits auf dem Schirm,
dass das System spaeter nicht nur Symptome und Requirements,
sondern auch das aktuelle Anliegen des Nutzers sauber mitfuehren muss.

Wichtig ist dabei:

- das Anliegen kann sich im Verlauf aendern
- es darf aber nicht zu leicht durch lokale Symptomvollstaendigkeit
  oder Gespraechsdrift ersetzt werden
- spaetere Readiness- und Recommendation-Entscheidungen duerfen nicht bloss
  daran haengen,
  dass ein einzelner Symptomfokus formal vollstaendig wirkt

Diese Kante gehoert noch nicht zu den ersten V4-Hauptbloecken,
soll aber als spaeterer Architekturpunkt sichtbar bleiben:

- Nutzeranliegen erkennen
- ueber den Verlauf stabil halten
- begruendete Verschiebungen zulassen
- Drift gegen spaetere freie LLM-Interpretation begrenzen
- medizinische Fokusarbeit und dialogisches Anliegen nicht naiv gleichsetzen

Neue Lesart ab 12-06-26:

- dieses Nutzeranliegen soll im Code vorerst lieber als eigener kleiner
  `concern`-Layer gedacht werden
  als sofort mit `DialogueState` identisch gemacht zu werden
- wenn die Grenze im aktiven Code noch nicht klar genug ist,
  ist eine untergeordnete oder benachbarte concern-nahe Schicht
  ausdruecklich vorzuziehen
  gegenueber einer vorschnellen Verschmelzung mit `DialogueState`
- wenn sich spaeter zeigt,
  dass diese concern-nahe Schicht faktisch voll in `DialogueState`
  aufgeht,
  kann sie immer noch sauber dorthin gezogen werden;
  die erste Aufgabe ist aber,
  ihre Semantik ueberhaupt erst einmal explizit zu machen
- wichtig ist dabei:
  `Readiness` bleibt davon begrifflich getrennt
  und soll spaeter weiter die zentrale Lage fuer Pflichtfelder,
  Gate
  und Mindestvoraussetzungen tragen
- eine andere Frage ist jedoch,
  ob fuer das aktuelle Nutzeranliegen bereits genug Fallverstaendnis
  oder genug materialisierte Information vorliegt;
  dafuer fehlt heute noch eine uebergeordnete concern-nahe Instanz
- daraus folgt fuer den spaeteren Umbau:
  bereits angelegte,
  aber heute noch falsch verkabelte Pfade,
  die faktisch auf
  `primary_focus`
  oder einzelne Symptomvollstaendigkeit lesen,
  sollen schrittweise auf diese concern-nahe Lage umgelegt werden
  statt das Anliegen weiter implizit mit einem lokalen medizinischen Fokus
  gleichzusetzen

Eng damit verbunden bleibt fuer spaeter:

- Careena soll dem eigentlichen Anliegen des Nutzers wieder aktiver folgen
- der Dialog soll je nach Situation mehr oder weniger in die Tiefe gehen
- relevante Details sollen gezielt fuer den Fall erfragt werden,
  statt bloss lokale Pflichtfelder schematisch abzuarbeiten
- der Gespraechsfluss soll dabei natuerlicher wirken
  und nicht wie ein starres Formular

Die spaetere Zielrichtung lautet daher:

- statische Rueckfragen sind primaer ein Performance- und Robustheitswerkzeug
  fuer haeufige oder absicherungskritische Muster
- freie oder LLM-gestuetzte Rueckfragen sollen dort moeglich bleiben,
  wo das Anliegen,
  der Verlauf
  oder der Fallkontext mehr adaptive Gespraechsfuehrung verlangen
- die Architektur soll diese spaetere adaptive Gespraechssteuerung vorbereiten,
  ohne sie schon frueh als unsichtbare Mischlogik in Readiness,
  Response
  oder `Call 2` einzubauen


## Was V4 bewusst nach hinten stellt

Weiter bewusst spaeter:

- `Safety`
- `Confirmation`
- grosser `(Re-)Naming`-Nachschnitt

Begruendung:

- diese Themen sind real, aber nicht die aktuelle Hauptkante
- der aktuelle Produkt- und Architekturwert liegt zuerst in einem wieder
  robusten Antwortfluss
- ein sauberer hinterer Reaktionsknoten hilft spaeter auch diesen Bloecken


## Block 0: V4-Arbeitsvertrag [aktiv]

## Ziel

Die V3-Haltung explizit weitertragen und den Refactor auf die hinteren
Systemgrenzen fokussieren.

## Kernfragen

1. wird eine Grenze klarer oder nur umetikettiert
2. wird eine Entscheidung sichtbarer oder nur verschoben
3. wird Text von Zustand entlastet oder kaschiert er ihn weiter
4. wird `DialogueManager` geschuetzt oder wieder mit Sonderpolitik beladen

## Done

- ein Schritt ist gut, wenn er die hintere Reaktionsarchitektur lesbarer macht
- eine unfertige, aber ehrliche Zwischenstufe ist erlaubt
- eine fachlich "nette" Abkuerzung ist nicht gut, wenn sie
  Response-/Transition-/Content-Verantwortung wieder vermischt

### Stand 11-06-26 [aktiv]

- V4 ist als Folgeplan zu V3 angelegt und uebernimmt dessen Haltungsanker
  bewusst weiter
- der neue Fokus ist festgezogen:
  zuerst hintere Response-/Transition-Grenzen,
  danach Antwortstrategie,
  danach Recommendation-Inhaltskante
  und erst anschliessend der echte dynamische `Call-2`-Werkzeugkasten
- zusaetzlich ist fuer V4 jetzt explizit festgehalten,
  dass Code-Dokumentation,
  funktionale Placeholder
  und laufende Standfortschreibung Teil des Refactor-Vertrags selbst sind


## Block 1: Hinteren Response-Vertrag zentralisieren [hoechste Prioritaet]

## Ziel

Den hinteren Reaktionsvertrag expliziter machen, statt Antwortpfade weiter
hauptsaechlich ueber `response_mode` plus lose Restsignale zu steuern.

## Warum jetzt zuerst

Der Code hat schon:

- `ResponsePlan`
- `PendingDialogueTransition`
- `recommendation_ready`
- `recommendation_requested`

Aber diese Teile bilden noch nicht gemeinsam einen kleinen gut lesbaren
hinteren Zustandsvertrag.

Zusaetzlich zeigen die juengeren Logbefunde:

- die eigentliche Restkante sitzt nicht nur im Response-Text
- sie sitzt in der gemeinsamen Auswertung von
  Turn-Eingang,
  aktivem Abschlussknoten,
  Gate-/Readiness-Lage
  und Pfadwahl

Genau deshalb ist die Schicht funktional schon da,
aber semantisch noch nicht klein und stabil genug.

## Sollzustand

- der hintere Turn-Teil hat einen kleineren sichtbaren Vertragskern
- `ResponseManager` entscheidet auf Basis expliziter Reaktionslage,
  nicht nur aus indirekter Bool-/Mode-Kombinatorik
- diese Reaktionslage ist klein genug,
  dass auch ihre vorgelagerten Entry-/Gate-Anteile sichtbar andocken koennen
- diese Reaktionslage bleibt bewusst offen dafuer,
  spaeter concern-nahe Signale zu lesen,
  ohne sie mit `Readiness`
  oder lokalem `primary_focus`
  zu verwechseln
- `DialogueManager` wendet das Ergebnis an,
  ohne selbst neue Antwortpolitik zu berechnen
- jede Schicht soll dabei nicht mehr Information tragen oder lesen,
  als fuer ihre eigene Rolle notwendig ist;
  nach oben und unten sollen moeglichst nur die jeweils relevanten kleinen
  Informationspakete weitergegeben werden

## Wichtige Fragen

1. welche minimalen Zustandsfragen braucht die hintere Policy wirklich
2. welche davon sind medizinisch,
   welche dialogisch,
   welche recommendation-bezogen
3. welche davon muessen schon vor der eigentlichen Response-Planung an der
   Entry-/Transition-Kante sauber geklaert sein
4. was ist ein Response-Pfad,
   was ist eine Response-Strategie,
   was ist schon Content
5. welche vorhandenen Felder koennen Teil des kleinen Vertrags bleiben,
   ohne neue Mischobjekte zu bauen
6. welche heutigen Lesepfade benutzen faktisch
   `primary_focus`
   oder lokale Symptomvollstaendigkeit,
   obwohl sie spaeter concern-nahe Semantik lesen sollten

## Leitplanken

- die gemeinsame Kante aus `Entry`,
  `Transition`
  und `Readiness`
  soll klarer werden,
  ohne wieder eine neue Sammelklasse zu erzeugen

- kein grosser "Super-ResponseState", der alles einsammelt
- lieber wenige klare Achsen
- `PendingDialogueTransition` darf bleiben,
  wenn es enger und ehrlicher wird
- `ResponsePlan` darf wachsen,
  wenn dies den Vertrag klaerer macht und nicht nur mehr Felder anhäuft

## Done

- der hintere Bereich ist kleiner vertraglich lesbar als heute
- `ResponseManager` wirkt zentraler,
  aber nicht groesser oder diffuser
- `DialogueManager` bleibt Orchestrator statt Antwort-Policy-Sammelstelle

### Stand 11-06-26 [noch offen]

- zusaetzlich ist jetzt klarer:
  der erste reale Rest sitzt nicht nur im `ResponseManager`,
  sondern an der gemeinsamen Kante aus
  `EntryManager`,
  aktivem Abschlussknoten
  und Readiness-/Gate-Lage

- der Block ist noch nicht praktisch begonnen
- aktueller Codeanker bleibt:
  `ResponsePlan`,
  `PendingDialogueTransition`,
  `response_mode`,
  `recommendation_requested`
  und `recommendation_ready` tragen gemeinsam schon einen Teil der Logik,
  aber noch keinen kleinen sauber zentralen hinteren Vertrag
- der erste reale Hebel bleibt daher:
  diese bestehende Vertragslage explizit lesen und enger schneiden,
  statt sofort neue Antwortpfade zu bauen

### Stand 12-06-26 [begonnen]

- ein erster kleiner hinterer Reaktionskern ist jetzt explizit im Code
  eingefuehrt:
  `ResponseState` traegt als spaete Policy-Achsen getrennt
  `safety_override`,
  `entry_response_hint`,
  `medical_state`,
  `transition_state`
  und
  `recommendation_state`
- `ResponseManager` waehlt den sichtbaren `response_mode` damit nicht mehr
  direkt aus loser Bool-/Mode-Kombinatorik,
  sondern aus diesem kleineren expliziten Kern;
  `ResponsePlan` und `TurnContext` tragen ihn jetzt sichtbar mit
- bewusst offen bleibt:
  dieser erste Kern ist noch keine fertige eigene
  Response-/Transition-Schicht,
  sondern ein kleinerer vertraglicher Zwischenstand unter bestehendem
  `response_mode`
- naechster sinnvoller Hebel:
  den Abschlussknoten aus
  `PendingDialogueTransition`,
  `EntryDecision.dialogue_transition_action`
  und Readiness-Lage auf diesem Kern weiter robust schneiden


## Block 2: Medizinische Rueckfrage, dialogische Transition und Recommendation-Freigabe sauber trennen [hoechste Prioritaet]

## Ziel

Den Antwortfluss wieder robust herstellen,
indem medizinische Rueckfragen und dialogische Abschluss-/Freigabeknoten
nicht mehr ineinanderfallen.

## Warum jetzt

Hier sitzt der reale Produktfehlerraum:

- Abschlussantworten duerfen nicht wieder wie normale medizinische
  Extraktionsturns zerfallen
- neue medizinische Information auf demselben Knoten darf aber auch nicht
  verschluckt werden
- freie knappe Antworten auf dem Abschlussknoten muessen robust lesbar werden
- eine zu aggressive Gate-/Readiness-Lage darf den Abschlussknoten nicht
  vorzeitig oder wiederholt ausloesen

## Sollzustand

Das System kann sauber unterscheiden zwischen:

1. medizinische Rueckfrage bleibt offen
2. medizinisch ist genug da,
   aber dialogisch ist noch ein Abschluss-/Freigabeschritt offen
3. Recommendation ist intern moeglich,
   aber noch nicht committed
4. Recommendation ist wirklich freigegeben
5. auf demselben Abschlussknoten wird doch noch weitere medizinische
   Information geliefert
6. eine freie kurze Antwort auf denselben Knoten ist sozial,
   unklar
   oder aufschiebend
   und haelt den Knoten offen,
   statt blind in einen anderen Pfad zu kippen
7. concern-nahe Signale zum aktuellen Nutzeranliegen koennen diese
   Unterscheidung spaeter mit stabilisieren,
   ohne dass der Abschlussknoten selbst zur concern-Engine werden muss

## Wichtige Fragen

1. welche Antworten auf einem aktiven Abschlussknoten sind echte
   `request_recommendation`-Signale
2. welche Antworten sind `report_more_information`
3. welche Antworten sind sozial,
   aufschiebend
   oder semantisch noch unklar
4. wie bleibt der Gegenpfad zur medizinischen Schiene klein lesbar,
   wenn aus einem Abschlussknoten wieder neue Informationen in den Case-Pfad
   zuruecklaufen
5. wie verhindert die Architektur,
   dass `recommendation_ready`
   oder vergleichbare Gates zu frueh gesetzt bleiben
   und dadurch denselben Abschlussknoten erneut triggern
6. wie werden Fehlerbilder wie
   leere `focus_update`-Objekte
   oder ungueltige Call-1-Kategorien
   als Signal fuer die Schnittstelle gelesen,
   statt nur als lokaler Promptfehler

## Leitplanken

- keine Sonderfallliste nur fuer Oberflaechentexte
- nicht alles ueber Call 1 loesen
- nicht alles ueber den finalen Text loesen
- medizinische Process-State-Signale und dialogische Abschluss-Signale
  duerfen koexistieren
- der Zwei-Wege-Knoten
  `request_recommendation`
  / `report_more_information`
  bleibt die bevorzugte Lesart des Recommendation-Abschlusses
- Frontend-Vorschlaege und freie Eingabe bleiben zwei Oberflaechen
  desselben kleinen Zustandsknotens

## Done

- der Fluss `medizinische Rueckfrage -> Abschlussknoten -> recommend`
  ist architektonisch lesbar und robust
- der Gegenfluss `Abschlussknoten -> weitere medizinische Information`
  ist ebenfalls sauber
- der Fehlerraum wird kleiner,
  ohne neue versteckte Heuristik-Sammler zu bauen
- freie Antworten auf dem Abschlussknoten sind robuster gegen Fehlrouting
  und gegen zu aggressive Gate-Zustaende

### Stand 11-06-26 [teilweise vorbereitet]

- der Code hat diesen Block bereits vorbereitet,
  aber noch nicht sauber zu Ende gezogen:
  `PendingDialogueTransition` existiert,
  der Abschlussknoten hat erlaubte Aktionen,
  und `EntryManager` behandelt schon einen Teil von
  `request_recommendation` bzw. `report_more_information`
- offen bleibt:
  der vertragliche Kern ist noch zu schmal
  und die robuste Trennung zwischen medizinischer Rueckfrage,
  dialogischer Transition
  und Recommendation-Freigabe ist noch nicht als kleine eigene Reaktionslage
  ausmodelliert
- die juengeren Logbefunde schaerfen diesen Rest weiter:
  freie Antworten wie
  `ja`,
  `weitere Beschwerden`
  oder `Empfehlung jetzt`
  sind noch nicht robust genug,
  und die Gate-/Readiness-Lage kann den Abschlussknoten noch zu frueh oder
  erneut aktiv halten
- der Fokus dieses Blocks bleibt deshalb nah am aktuellen Runtime-Pfad
  und nicht bei spaeteren freien KI-Antworten

### Stand 12-06-26 [begonnen]

- der Recommendation-Abschlussknoten wird jetzt nicht mehr ueber lokale
  Freitext-Heuristiken weitergeschnitten,
  sondern ueber einen kleinen expliziten Zwei-Wege-Normalizer-Vertrag:
  `request_recommendation` /
  `report_more_information`
- fuer aktive `recommendation_ready_check`-Knoten gibt es jetzt eine kleine
  eigene Service-/LLM-Kante,
  die freien Text auf genau diese zwei erlaubten Aktionen mappt;
  kanonische Aktionswerte koennen denselben Vertrag direkt ohne Zusatzcall
  bedienen
- dadurch bleibt der Spezialknoten semantisch klein:
  Button- bzw. Aktionspfad und freier Text enden im selben Vertrag,
  statt dass lokale Textlisten in `EntryManager` versteckt neue
  Oberflaechenlogik aufbauen
- zusaetzlich liest der Call-1-Scout jetzt den aktiven
  `recommendation_ready_check`
  expliziter mit:
  fuer die nackte Wahl
  `da ist noch mehr`
  ohne bereits genannte neue medizinische Fakten gibt es nun einen kleinen
  expliziten Scout-Hinweis
  `dialogue_hint:transition_continue_without_medical_content`,
  damit dieser Rueckweg den Abschlussknoten verlassen kann,
  ohne sofort unnoetig in `Call 2` zu fallen
- bewusst offen bleibt:
  wie breit der spaetere Normalizer-Prompt fuer freie knappe Antworten,
  knappe Ablehnungen
  oder gemischte Freitext-Antworten genau sein soll,
  ohne wieder in eine grosse implizite Spezialgrammatik zu kippen
- ebenfalls offen bleibt:
  die generelle Gate-/Readiness-Haerte,
  wegen der das System nach fruehen Minimalinformationen teils weiterhin sehr
  schnell wieder auf
  `ready_for_transition`
  kippt
- zusaetzlich wird jetzt klarer:
  ein Teil dieser Haerte ist nicht bloss lokales Gate-Verhalten,
  sondern haengt daran,
  dass das System das aktuelle Nutzeranliegen noch nicht als eigene
  concern-nahe Lage fuehrt
- naechster sinnvoller Hebel:
  die freie Antwortbreite dieses kleinen Zwei-Wege-Normalizers weiter
  absichern
  und die Kante
  `freier Text mit echter Zusatzinformation` vs.
  `blosse Wahl des medizinischen Rueckwegs`
  bewusst klein halten,
  ohne daraus eine breite Sonderfallgrammatik zu machen
  - siehe dazu aktuell besonders:
    `BR-V4-001`
    und
    `BR-V4-003`


## Block 3: Antwortstrategie explizit machen: statisch, KI-Rueckfrage, Recommendation [hoch]

## Ziel

Nicht jede Antwortart in denselben textlichen Pfad zwingen,
sondern eine kleine Architektur fuer verschiedene Reaktionsstrategien schaffen.

## Warum hier

Sobald Block 1 und 2 den hinteren Vertrag geklaert haben,
stellt sich die naechste echte Frage:

- welche Art von Antwort soll aus dem aktuellen Zustand ueberhaupt entstehen

Das ist mehr als nur `response_mode`.

## Sollzustand

Das System kann strukturell unterscheiden zwischen:

- statischer Rueckfrage
- spaeter KI-gestuetzter Rueckfrage
- Recommendation-Uebergang
- Recommendation-Inhalt
- einfacher kurzer Weiterfuehrung

Spaeter soll diese Antwortstrategie nicht nur technisch verschiedene
Ausgabearten tragen,
sondern auch unterschiedliche Gespraechstiefen:

- knappe Standard-Rueckfrage bei haeufigen oder absicherungskritischen Mustern
- freiere adaptive Rueckfrage,
  wenn das Anliegen oder der Verlauf mehr gezielte Exploration verlangt

Wichtig:

- dies ist zunaechst eine Strategiefrage,
  nicht sofort eine Implementierungsfrage

## Wichtige Fragen

1. welche Pfade brauchen nur Templates
2. welche Pfade brauchen spaeter freien KI-Inhalt
3. wo sitzt diese Entscheidung:
   in der Policy,
   in einem kleinen Strategy-Vertrag,
   oder in einer spaeteren Inhaltskante
4. wie laesst sich das vorbereiten,
   ohne jetzt schon `Call 3` festzunageln
5. wie kann die Architektur spaeter unterschiedliche Gespraechstiefen tragen,
   ohne wieder formularartige Pflichtfeldlogik als Hauptmodus zu verankern

## Leitplanken

- `ResponseTextBuilder` soll nicht zur verkappten Policy werden
- freie KI-Antwort darf nicht denselben Vertrag ersetzen,
  den sie eigentlich nur ausformulieren soll
- statisch und KI-gestuetzt sind Varianten derselben uebergeordneten
  Reaktionsarchitektur,
  nicht zwei getrennte Systeme
- statische Fragen bleiben bevorzugt dort,
  wo sie haeufig,
  schnell
  oder absicherungstechnisch besonders wertvoll sind
- adaptive Rueckfragen sollen spaeter dort andocken koennen,
  wo natuerlichere und fallbezogen tiefere Gespraechsfuehrung gebraucht wird
- der Verteiler soll langfristig nicht nur Hardcode-Antworten bevorzugen,
  sondern im Regelfall auch KI-gestuetzte Reaktion zulassen,
  wenn die Signale nicht bewusst einen statischen Pfad verlangen

## Done

- Antwortstrategie ist als eigene Frage sichtbar
- spaetere KI-Rueckfragen koennen sauber andocken
- Recommendation-Inhalt wird nicht implizit mit Uebergangspolitik vermischt

### Stand 11-06-26 [bewusst nach Block 1-2]

- im aktuellen Code ist Antwortstrategie noch weitgehend an
  `response_mode` plus `ResponseTextBuilder` gebunden
- das ist fuer heute okay,
  solange Block 1 und 2 zuerst die hintere Reaktionslage sauberer schneiden
- dieser Block soll daher nicht voreilig freie KI-Rueckfragen einfuehren,
  sondern zuerst die spaetere Andockfaehigkeit vorbereiten
- zugleich ist bereits vorgemerkt,
  dass statische Fragen langfristig eher Performance-/Sicherheitswerkzeug
  sein sollen
  und nicht das eigentliche Zielbild einer natuerlichen
  anliegengefuehrten Gespraechssteuerung

### Stand 12-06-26 [als naechster Hebel schaerfer geworden]

- die juengsten Logbefunde machen sichtbarer,
  dass Block 3 nicht nur spaeterer Komfort,
  sondern ein relevanter Stabilitaetshebel fuer den laufenden
  Antwortfluss ist:
  aktuell wirkt Careena im aktiven Pfad noch zu sehr wie eine feste
  Kategorien-/Template-Maschine
- wichtig:
  das ersetzt Block 2 nicht,
  sondern sitzt quer dazu
  und erklaert mit,
  warum freie Antworten trotz besserer Struktur noch leicht in unpassende
  Pfade kippen
- fuer den naechsten realen Arbeitsfokus ist deshalb plausibel:
  einen kleinen vorgezogenen Block-3-Schnitt zu machen,
  sobald die aktuelle Block-2-Transition-Kante nicht weiter im Weg steht
- besonders relevant dazu:
  `BR-V4-002`

### Stand 12-06-26 [begonnen]

- ein erster kleiner Strategy-Vertrag ist jetzt explizit im Code:
  `ResponseStrategy`
  trennt die Antwortformulierung erstmals sichtbar von der reinen
  `response_mode`-Pfadwahl
- die bestehende statische Reaktionsflaeche bleibt bewusst fuer
  Sonderpfade erhalten:
  `emergency`,
  `out_of_scope`,
  `ask_followup`,
  Recommendation-Uebergang,
  Recommendation-Placeholder
  und der kleine Rueckweg
  `return_to_medical`
- neu geoeffnet ist nur ein enger freier Antwortpfad fuer den normalen
  medizinischen
  `continue`-Verlauf:
  ein kleiner
  `LLMResponseGenerationService`
  formuliert dort auf Basis des
  `MASTER_PROMPT`
  plus expliziter Turn-Fakten eine kurze naechste Antwort
- bewusst wichtig:
  diese freie Antwortkante ersetzt keine Policy
  und keine Sonderpfade;
  wenn der LLM-Call ausfaellt oder leer bleibt,
  faellt der Lauf weiter ehrlich auf die bestehende statische
  `continue`-Formulierung zurueck
- Block 3 ist damit noch nicht fertig,
  aber nicht mehr nur vorgemerkt:
  die Antwortstrategie beginnt jetzt als eigene kleine Vertragskante
  sichtbar zu werden
- naechster sinnvoller Hebel:
  den Recommendation-Abschluss um
  `awaiting_reply`
  vs.
  `request_recommendation`
  vs.
  `report_more_information`
  weiter schaerfen,
  damit der neue freie
  `continue`-Pfad nicht gegen einen noch zu unsauberen Abschlussknoten
  arbeiten muss


## Block 4: Recommendation-Inhaltskante vorbereiten, ohne sie zu frueh festzunageln [mittel]

## Ziel

Den spaeteren Recommendation-Inhalt als eigene Kante vorbereiten,
ohne schon endgueltig zu entscheiden,
ob dies ein eigener `Call 3` oder ein anderer Werkzeugkasten-Modus wird.

## Warum jetzt nicht frueher

Bevor der Recommendation-Inhalt sauber ausgebaut wird,
muss klar sein,
wann das System ueberhaupt dort ankommt.

## Sollzustand

- Recommendation-Freigabe ist sauber von Recommendation-Inhalt getrennt
- die vorhandene `RecommendationResult`-Strecke bleibt als sichtbarer
  Placeholder erlaubt
- die spaetere Inhaltskante kann explizit andocken

## Wichtige Fragen

1. welche Daten braucht Recommendation-Inhalt spaeter wirklich
2. welche davon sind kanonische Case-Wahrheit,
   welche davon sind dialogische oder policy-nahe Ableitungen
3. was waere fuer Recommendation-Inhalt ein kleiner ehrlicher Vertrag
4. welche Teile der jetzigen Placeholder-Strecke sind nuetzlich,
   welche nur Uebergang
5. wie soll spaeter das fortlaufende Nutzeranliegen in Recommendation- und
   Readiness-Entscheidungen eingehen,
   ohne auf ein einzelnes vollstaendiges Symptom reduziert zu werden
6. wie bleibt dabei klar getrennt:
   `Readiness` fuer Pflichtfelder und Gate
   versus concern-nahe Einschaetzung,
   ob fuer das aktuelle Nutzeranliegen schon genug Fallverstaendnis vorliegt

## Leitplanken

- keine implizite Recommendation-Engine im `ResponseManager`
- keine versteckte Inhaltslogik im `ResponseTextBuilder`
- Recommendation-Content bleibt eine spaetere eigene Arbeitskante

## Done

- der Recommendation-Pfad ist in Freigabe und Inhalt sauber auseinandergezogen
- spaetere Ausbauentscheidungen werden vorbereitet statt verdeckt vorweggenommen

### Stand 11-06-26 [strukturell vorbereitet]

- eine kleine sichtbare Placeholder-Strecke existiert bereits ueber
  `RecommendationResultBuilder` und `RecommendationResult`
- genau das ist fuer V4 kein Makel,
  sondern aktuell eine erlaubte funktionale Ausbaufläche,
  solange sie weiter klar als nicht finale fachliche Recommendation-Logik
  markiert bleibt
- zusaetzlich ist schon vorgemerkt,
  dass spaetere Recommendation- und Readiness-Logik nicht einfach aus der
  Vollstaendigkeit eines einzelnen Symptomfokus abgeleitet werden darf,
  sondern das fortlaufende Nutzeranliegen mitlesen muss
- neue Zwischenlesart:
  dieses fortlaufende Nutzeranliegen soll vorerst eher als eigener kleiner
  `concern`-Layer andocken
  als direkt in `DialogueState` aufzugehen;
  bestehende
  `primary_focus`-gekoppelte Ableitungen sollen spaeter gezielt auf diese
  concern-nahe Lage umgelegt werden
- der spaetere Fokus liegt daher nicht auf mehr Fachinhalt an dieser Stelle,
  sondern auf einer sauberen Inhaltskante nach stabilerer Freigabelogik


## Block 5: `Call 2` vom vorbereiteten Werkzeugkasten zu echter dynamischer Komposition weiterziehen [hoch, nach Block 1-3]

## Ziel

Das in V3 und im Block-4-Konzept angelegte Werkzeugkasten-Prinzip
wirklich dynamisch machen.

## Warum erst nach dem hinteren Response-Schnitt

`Call 2` ist heute schon kleiner und deutlich besser als frueher.
Der naechste Mehrwert liegt deshalb nicht darin,
denselben Vertrag nur noch etwas schoener zu formulieren,
sondern die Komposition tatsaechlich dynamischer und zustandssensitiver
zu machen.

Damit das nicht wieder in Flusschaos kippt,
soll der hintere Antwortbereich vorher stabiler sein.

## Sollzustand

- `Call 2` ist nicht nur konzeptionell,
  sondern praktisch als zusammensetzbarer Werkzeugkasten lesbar
- Aufgabenbereiche koennen sichtbarer nach Zustand und Signalen aktiviert
  werden
- Kontext wird gezielt mitgegeben statt pauschal
- spaetere neue Werkzeugbereiche koennen andocken,
  ohne den ganzen Call wieder breiter zu machen

## Wichtige Fragen

1. was ist an `call2_tasks` heute schon tragfaehig
2. wo ist die aktuelle Komposition noch nur Prompt-Rhetorik
3. `operation_mode` eher als gewaehlter Kasten bzw. Arbeitsmodus lesen,
   `tasks` eher als aktivierte Werkzeuge innerhalb dieses Modus:
   wie tragfaehig ist diese Lesart fuer den realen Ausbau
4. welche Teile gehoeren in kleine Python-Komposition,
   welche ins Prompt,
   welche in den Zustand davor
5. wie werden aus `tasks` spaeter Prompt-Bloecke und Kontextpakete gezielt
   zusammengesetzt,
   ohne den Call wieder breit und implizit zu machen
6. wie stark soll Dynamik ueber medizinische Signale,
   dialogische Signale
   oder gemeinsame Meta-Signale gesteuert werden
7. wie bleibt `Call 2` optional,
   wenn der Turn gar keine medizinische Extraktion braucht

## Leitplanken

- Dynamik ja,
  aber nicht als verdeckte Spezialfallgrammatik
- kein breiter dirty context als Abkuerzung
- keine Rueckwanderung von Process- oder Response-Politik in den
  medizinischen Werkzeugkasten
- lieber sichtbar komponierte kleine Rollen als ein immer kluegerer
  Einheits-Prompt

## Done

- die Werkzeugkasten-Idee ist im aktiven Pfad realer als heute
- neue Module lassen sich eher andocken als einschmuggeln
- `Call 2` bleibt klein genug,
  obwohl seine Komposition dynamischer wird

### Stand 11-06-26 [vorbereitet, aber bewusst spaeter]

- `Call 2` ist im aktuellen Code bereits kleiner und vertraglich deutlich
  ehrlicher als im frueheren Zustand
- die echte Dynamik ist aber noch nur teilweise real:
  `call2_tasks`,
  `operation_mode`
  und die Prompt-/Kontextstruktur bereiten sie vor,
  ohne schon eine wirklich flexible Kompositionsarchitektur zu bilden
- fuer den spaeteren Ausbau ist jetzt als Leitlesart vorgemerkt:
  `operation_mode` beschreibt eher den gewaehlten Kasten,
  `tasks` die aktivierten Werkzeuge,
  aus denen spaeter Prompt-Bloecke und Kontextpakete zusammengesetzt werden
- dieser Block bleibt deshalb klar relevant,
  soll aber erst nach einem stabileren hinteren Antwortfluss der naechste
  Haupthebel werden


## Block 6: Safety, Confirmation und spaetere Korrekturschichten vorbereitet halten [spaeter]

## Ziel

Diese Schichten weiter bewusst hinten halten,
ohne sie zu vergessen.

## V4-Entscheidung

- kein Vorziehen ohne neuen konkreten Produktdruck
- Placeholder bleibt erlaubt,
  solange die Schichtgrenze sichtbar bleibt

### Stand 11-06-26 [bewusst spaeter]

- an dieser Priorisierung wird in V4 vorerst bewusst festgehalten
- ein sauberer Response-/Transition-Schnitt und danach der dynamische
  Werkzeugkasten haben aktuell den hoeheren Architekturwert


## Block 7: Naming-/Rename-Nachschnitt weiter nachrangig [spaeter querliegend]

## Ziel

Namen erst dann nachziehen,
wenn die Rollen durch V4 stabiler geworden sind.

## V4-Entscheidung

- keine fruehen Cosmetic-Renames
- Missnamer weiter beobachten
- echter Rename erst nach stabilerem Response- und Werkzeugkasten-Schnitt

### Stand 11-06-26 [bewusst spaeter]

- diese Nachrangigkeit bleibt explizite V4-Entscheidung
- wichtige Klarheit soll vorerst ueber Rollen-Doku und Vertragskommentare
  entstehen,
  nicht ueber teure fruehe Umbenennungen


## Praktische Reihenfolge fuer V4

1. Block 1:
   hinteren Response-Vertrag zentralisieren
2. Block 2:
   medizinische Rueckfrage,
   dialogische Transition
   und Recommendation-Freigabe sauber trennen
3. Block 3:
   Antwortstrategie explizit machen
4. Block 4:
   Recommendation-Inhaltskante vorbereiten
5. Block 5:
   dynamischen `Call-2`-Werkzeugkasten wirklich ausbauen
6. Block 6 und 7 spaeter nur bei Bedarf


## Konkrete Startempfehlung fuer V4

Der erste praktische Schritt fuer V4 ist nicht:

- sofort ein neuer KI-Antwortpfad
- sofort `Call 3`
- sofort tiefere Recommendation-Inhalte
- sofort dynamische Vollkomposition von `Call 2`

Sondern:

1. die aktuelle hintere Vertragslage im Code explizit sezieren:
   `ResponsePlan`,
   `PendingDialogueTransition`,
   `response_mode`,
   `recommendation_requested`,
   `recommendation_ready`
2. daraus einen kleineren lesbaren Response-/Transition-Kern ableiten
3. dann den Abschlussknoten
   `weitere Beschwerden?` / `Empfehlung jetzt`
   robust auf diesen Kern setzen
4. erst danach die Antwortstrategie
   `statisch vs spaeter KI`
   sauber aufspannen
5. anschliessend den dynamischen `Call-2`-Werkzeugkasten auf diesen
   stabileren Fluss aufbauen


## Schlussbewertung

V4 beginnt nicht mit einer neuen Theorie,
sondern mit einer anderen Lage im echten Code.

Die vorderen Grenzen aus V3 haben genug getragen,
um jetzt den hinteren Reaktionsknoten als eigene Architekturaufgabe
ehrlich anzugehen.

Der wichtigste Merksatz fuer V4 lautet:

- erst den hinteren Antwort- und Uebergangsfluss sauber schalten,
  dann den medizinischen Werkzeugkasten wirklich dynamisch ausbauen

Oder anders:

- lieber zuerst eine kleine robuste Reaktionsarchitektur,
  als gleichzeitig halbfertige Recommendation-Inhalte,
  freie KI-Rueckfragen
  und dynamische Werkzeugkastenlogik auf noch zu weichen Hinterkanten
  aufzutuermen
