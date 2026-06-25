# Careena3: Architektur durch Abstraktion lesbar machen

Stand: 2026-06-13
Status: Entwurf
Bezug:

- `server/careena3.py`
- `server/careena_pipeline3/runtime.py`
- `server/careena_pipeline3/application/managers/dialogue_manager.py`
- `server/careena_pipeline3/application/managers/entry_manager.py`
- `server/careena_pipeline3/application/managers/extraction_manager.py`
- `server/careena_pipeline3/application/managers/case_state_manager.py`
- `server/careena_pipeline3/application/services/dialogue_state_service.py`
- `server/careena_pipeline3/application/services/recommendation_state_service.py`
- `server/careena_pipeline3/application/managers/response_manager.py`
- `server/careena_pipeline3/models/turn/context.py`


## Auftrag und Leseregel

Diese Notiz versucht nicht, den aktuellen Python-Code nachzuerzaehlen.

Sie versucht etwas anderes:

- das System zuerst nur ueber sein beobachtbares Verhalten zu lesen
- dieses Verhalten als Repraesentation ernst zu nehmen
- dann stufenweise zu abstrahieren
- und erst danach wieder in die Implementierung zurueckzugehen

Die Arbeitsregel lautet daher:

- nicht vom Code zur Architektur
- sondern vom Verhalten zur Rolle
- von der Rolle zum Vertrag
- vom Vertrag zur Schicht

Vorhandener Code ist dafuer Evidenz, aber kein Wahrheitsbeweis.


## Erste Abstraktion: Was tut das System ueberhaupt?

In grobster Form ist das System kein einzelner Chatbot und auch nicht einfach
eine Folge von LLM-Calls.

Es ist ein zustandsbehafteter Turn-Prozessor.

Pro Turn passiert abstrahiert nur dies:

1. Das System nimmt eine neue Nutzernachricht entgegen.
2. Es liest dazu einen bereits vorhandenen Fall- und Dialogzustand.
3. Es gewinnt aus der neuen Nachricht kleine Steuersignale.
4. Es entscheidet, ob medizinische Fallwahrheit fortgeschrieben werden muss.
5. Es aktualisiert danach den internen Prozesszustand.
6. Es leitet daraus ab, was als naechster Systemschritt erlaubt ist.
7. Es formuliert erst ganz am Ende eine passende Antwort.

Das ist die erste wichtige Beobachtung:

- der Kern ist nicht Textproduktion
- der Kern ist Zustandsfortschreibung unter einer sichtbaren Turn-Orchestrierung


## Zweite Abstraktion: Welche Rollen existieren?

Wenn man nicht auf Klassen, sondern auf Verhalten schaut, treten einige
stabile Rollen hervor.

### 1. Boundary

Eine aeussere Huelle nimmt HTTP-Requests an, verwaltet Sessions und uebersetzt
zwischen API-Eingabe und Turn-Verarbeitung.

Ihre Rolle ist nicht medizinische Logik, sondern:

- Nachricht annehmen
- Sessionzustand laden
- Turn ausfuehren
- Ergebnis nach aussen zurueckgeben

### 2. Turn-Orchestrierung

Eine zentrale Instanz fuehrt den Turn in einer festen Reihenfolge aus.

Ihre Rolle ist:

- die sichtbare Ausfuehrungsordnung zu halten
- Teilschritte zu sequenzieren
- kleine Signale zwischen Schichten weiterzureichen

Sie sollte nicht selbst die Detailpolitik jeder Unterschicht tragen.

### 3. Fruehe Signalverdichtung

Vor der eigentlichen Fallfortschreibung wird aus der Nutzernachricht gelesen,
welche Art von Turn ueberhaupt vorliegt.

Die Rolle dieser Zone ist:

- nicht schon Wahrheit zu erzeugen
- sondern kleine Einstiegssignale zu liefern

Zum Beispiel:

- braucht es Extraktion?
- ist das medizinisch oder dialogisch?
- gibt es Anzeichen fuer Themenwechsel?
- wird eine Empfehlung angefragt?

### 4. Truth-Kante

Irgendwo muss die neue Nachricht in kanonische Fallwahrheit uebersetzt werden.

Diese Rolle ist die eigentliche innere Kernkante des Systems:

- nur hier darf neue medizinische Wahrheit sauber in den Fall eingehen
- nur hier duerfen extrahierte Signale in persistente Fachstruktur umschlagen

### 5. Prozess- und Requirement-Schicht

Nachdem Fallwahrheit fortgeschrieben wurde, muss das System lesen:

- welche Anforderungen noch offen sind
- welche Rueckfrage jetzt fachlich ansteht
- ob der Turn eine offene Rueckfrage beantwortet hat
- wie weit der Fall fuer die naechste Stufe ueberhaupt ist

Diese Schicht ist keine Textschicht.
Sie ist die innere Prozesslogik oberhalb der Fallwahrheit.

### 6. Gate- und Response-Policy

Aus der stabilisierten Lage wird entschieden, welcher Antwortpfad ueberhaupt
freigegeben ist.

Das ist die Schicht der Antwortart, nicht der Antwortformulierung.

Sie entscheidet Dinge wie:

- Notfallpfad
- Rueckfragepfad
- Weitermachen
- Abschluss-/Recommendation-Pfad
- ausserhalb des Scopes

### 7. Textschicht

Erst ganz am Ende wird aus einem freigegebenen Pfad ein Text gebaut.

Diese Rolle sollte nur formulieren, was die oberen Schichten bereits
entschieden haben.


## Dritte Abstraktion: Welche Wahrheiten gibt es?

Ein grosser Teil der Lesbarkeit haengt daran, welche Wahrheitsarten das System
fuehrt.

### Persistierte Wahrheit

Das System fuehrt ueber Turns hinweg mindestens drei persistierte Wahrheiten:

- medizinische Fallwahrheit
- Dialogprozesszustand
- Concern-/Fokuszustand

Diese drei Dinge sind nicht identisch.

Schon auf dieser Ebene wird sichtbar:

- medizinische Wahrheit
- Dialogprozess
- Concern-Kontinuitaet

sind voneinander getrennte Problemarten.

### Turn-Arbeitszustand

Fuer einen einzelnen Turn existiert ein grosser Arbeitskontext, der die
aktuellen Zwischenbefunde einsammelt.

Das ist keine persistierte Wahrheit im strengen Sinn, sondern ein
Ausfuehrungsbehaelter fuer diesen Turn.

### Abgeleitete Teilbefunde

Daneben entstehen pro Turn weitere Signale, die nicht primaere Wahrheit sind,
sondern abgeleitete Lesarten:

- Safety-Befunde
- Readiness-Befunde
- Gate-Entscheidungen
- Response-Zustaende
- Response-Strategien

Diese sind wichtig, aber sie sind nicht dasselbe wie der medizinische Fall.

### Ausgabe

Am Ende entsteht nur noch:

- ein Antwortmodus
- ein Antworttext
- optional ein Recommendation-Ergebnis

Das ist Ausgabe, nicht Wahrheit.


## Vierte Abstraktion: Das System als Schichtenkette

In maximal verdichteter Form laesst sich die Kernbewegung des Systems so
darstellen:

`Boundary -> Entry-Signale -> Extraction -> Case Truth -> Process State -> Gate Decision -> Response Policy -> Text`

Diese Kette wirkt nach dem jetzigen Codebild wie die eigentliche gedachte
Architektur.

Wichtig daran:

- die Kette ist stark turn-orientiert
- die Orchestrierung ist bewusst sichtbar
- die Fallwahrheit sitzt vor Process/Gate/Response
- die Textschicht sitzt am Ende und nicht in der Mitte

Das ist die staerkste plausible Grundidee des Systems.


## Rueckaufbau: Wo sitzen diese Rollen im aktuellen System?

Erst an dieser Stelle lohnt sich der Rueckweg in den konkreten Code.

### Boundary

`server/careena3.py` ist im Wesentlichen die API-Huelle.

Dort sitzen:

- Sessionzugriff
- HTTP-Endpoints
- Uebersetzung zwischen Request und TurnInput
- Rueckgabe einfacher JSON-Antworten

Diese Datei wirkt architektonisch nicht wie der Denkort der Fachlogik.

### Turn-Orchestrierung

`DialogueManager.run_turn()` ist die zentrale sichtbare Turn-Sequenz.

Hier wird der Ablauf in klar lesbaren Stufen gefahren:

- roher Safety-Blick
- Case-Kontext sichern
- Entry-Signale lesen
- Extraktion ausfuehren
- Case fortschreiben
- Prozesszustand synchronisieren
- Readiness und Gate lesen
- finalen Safety-Blick setzen
- Response planen
- Confirmation spaet anhaengen

Das ist sehr wahrscheinlich die eigentliche Steuer-Mitte des Systems.

### Fruehe Signalverdichtung

`EntryManager` ist die Schicht, die aus der Nachricht kleine
orchestrierungsfaehige Signale macht.

Seine Rolle ist klarer als die konkrete Implementierung:

- Entscheidung, ob Extraktion noetig ist
- fruehe Einordnung der Turn-Art
- Steuerhinweise fuer den weiteren Pfad

### Truth-Kante

Die Kombination aus `ExtractionManager` und `CaseStateManager` bildet die
Wahrheitskante.

Dabei wirkt das Muster so:

- `ExtractionManager` beschafft und normalisiert einen verarbeitbaren Befund
- `CaseStateManager` schlaegt diesen Befund in kanonische Fallwahrheit um

Genau hier liegt die sensible Grenze:

- vor dieser Kante: Signale und Vorstufen
- nach dieser Kante: persistierte Fachwahrheit

### Prozess- und Requirement-Schicht

`DialogueStateService` und `RequirementPolicy` lesen die Fallwahrheit danach
prozessual weiter.

Dort wird aus Fallwahrheit abgeleitet:

- welche Anforderungen offen sind
- welche Rueckfrage ansteht
- welche Requirements als erledigt gelten
- welche Prozesssignale der Turn erzeugt hat

### Gate-Schicht

`RecommendationStateService` ist die aktive Naechstschritt-Schicht.

Sie beantwortet nicht primaer:

- was medizinisch wahr ist

sondern:

- welcher weitere Pfad jetzt erlaubt ist

### Response-Policy und Text

`ResponseManager` entscheidet den Antwortpfad.
`ResponseGenerationService` und `ResponseTextBuilder` formulieren ihn.

Das ist eine sinnvolle Schichtung:

- erst Pfad
- dann Text


## Was wirkt architektonisch sauber?

Trotz der KI-generierten Herkunft sind einige Grundgedanken erkennbar und
nicht nur zufaellig plausibel.

### Sichtbare Orchestrierung statt versteckter Magie

Der Turn-Ablauf ist zentral lesbar und nicht auf viele unsichtbare Seiteneffekte
verteilt.

Das ist ein echter Architekturgewinn.

### Truth vor Response

Der Code versucht ueberwiegend, erst die Fallseite und dann die Antwortseite
zu entscheiden.

Das ist fachlich die richtige Richtung.

### Kleine Zwischenvertraege

Mit Dingen wie:

- `EntryDecision`
- `ExtractionPayload`
- `ProcessStateUpdate`
- `ReadinessStateUpdate`
- `ResponsePlan`

existiert eine erkennbare Absicht, Schichten ueber kleine Vertraege zu koppeln
statt ueber globale Magie.

### Response als spaete Policy

Die spaete Antwortauswahl wirkt nicht als primaerer Wahrheitserzeuger, sondern
als Ableitung aus dem davor stabilisierten Zustand.


## Wo truebt die Implementierung das Bild?

Hier wird das System wieder absichtlich gegen seine unsaubere konkrete
Auspraegung gelesen.

### 1. Der `TurnContext` ist zu gross und traegt zu viele Wahrheitsarten

`TurnContext` sammelt gleichzeitig:

- persistierte Wahrheit
- turn-lokale Arbeitsdaten
- abgeleitete Gate-Befunde
- Response-Zustand
- Response-Text
- Trace-Observability

Dadurch wird er teils Arbeitsbehaelter, teils Zustandsspiegel, teils
Ausgabecontainer.

Das ist kein lokales Stilproblem, sondern eine strukturelle Verdichtung von
zu vielen Rollen an einem Ort.

### 2. Es existieren sichtbare Zweitwahrheiten fuer denselben Steuerpunkt

Besonders deutlich ist das bei der Naechstschritt-Steuerung:

- `gate_decision.allowed_next_step`
- `allowed_next_step` als Legacy-Mirror im `TurnContext`

Die aktive Wahrheit soll laut Code bei `gate_decision` liegen.
Dass der Spiegel trotzdem mitgetragen wird, zeigt eine Uebergangsarchitektur
mit doppelter Lesbarkeit.

Dasselbe Muster erscheint bei:

- `recommendation_requested`
- `recommendation_ready`
- `response_mode`
- `response_state.selected_response_mode`

Nicht alles davon ist fachlich gleichwertig.
Aber vieles davon beschreibt denselben hinteren Antwortzustand aus mehreren
Richtungen.

### 3. Concern, Dialogue und Recommendation/Gate liegen nah beieinander, aber ohne ganz scharfen Gesamtvertrag

Es ist sichtbar, dass das System drei verschiedene Dinge modellieren will:

- worum es im Fall gerade geht
- was im Dialogprozess als naechstes offen ist
- welcher Antwortpfad jetzt freigegeben ist

Diese Trennung ist richtig.

Aber der Gesamtvertrag dazwischen ist noch nicht voll stabil.
Man sieht das daran, dass `ConcernStateService`, `DialogueStateService` und
`RecommendationStateService` teilweise dieselbe Lage aus verschiedenen
Blickwinkeln nachzeichnen.

### 4. Text-Fallbacks verdecken teils den unfertigen Zustand

In `careena3.py` und in der Response-Erzeugung existieren sichtbare
Fallback-Texte.

Als Uebergangsbruecke ist das sinnvoll.
Architektonisch bedeutet es aber auch:

- die API kann nach aussen eine scheinbar vollstaendige Antwort zeigen
- obwohl die eigentliche semantische Schicht darunter noch Platzhalterstatus hat

Das ist nicht falsch, aber es macht Unfertigkeit weniger sichtbar.

### 5. Safety ist praesent im Ablauf, aber noch nicht als echte Fachschicht ausmodelliert

Safety wird sauber sichtbar in den Turn eingebaut:

- roh
- nach Extraktion
- nach Case

Das ist als Orchestrierungsentscheidung gut.

Die aktuelle konkrete Safety-Logik ist aber weitgehend Scaffold.
Das ist hier kein Hauptvorwurf, aber es zeigt:

- der Ablauf ist angelegt
- der Fachvertrag ist dort noch nicht wirklich eingeloest


## Wo koennte wirklich etwas fehlen?

Hier sind nur echte Luecken gemeint, nicht offensichtliche Platzhalter wie
Confirmation oder die noch duenne Safety-Ausgestaltung.

### 1. Es fehlt ein wirklich scharfer Gesamtvertrag fuer Wahrheitsarten

Der Code macht zwar praktisch einen Unterschied zwischen:

- persistiert
- turn-lokal
- abgeleitet
- ausgabeseitig

Aber dieser Unterschied ist nicht als eigene erste Architekturregel
ausmodelliert.

Die Folge:

- dieselbe Information taucht in mehreren Aggregaten und Rollen wieder auf
- Uebergangsobjekte koennen unklar werden, ob sie Wahrheit oder nur Lesart sind

### 2. Es fehlt eine klar zentrale Definition von Concern-Wechsel versus Turn-Fortsetzung

Der Code hat Signale fuer:

- `same_concern`
- `possible_shift`
- `dialogue_only`

und er fuehrt einen `ConcernState`.

Was aber nicht als durchgehend harter Vertrag sichtbar ist:

- wann genau ein neuer Concern entsteht
- wann ein Turn nur Dialog ist
- wann der gleiche Concern mit neuer medizinischer Wahrheit fortgesetzt wird

Das ist eine echte strukturelle Luecke, weil daran Fallkontinuitaet,
Rueckfragen und Recommendation-Pfad haengen.

### 3. Es fehlt ein expliziter Vertrag fuer Konflikt zwischen Fachwahrheit und Antwortpfad

Das System trennt zwar Wahrheit und Response-Policy.
Aber nicht voll sichtbar modelliert ist die Frage:

- was passiert, wenn Fallwahrheit stabil ist, der Dialogprozess aber noch nicht
- oder wenn ein Recommendation-Pfad offen scheint, waehrend die Concern-Lage
  noch unscharf ist

Vieles davon wird momentan implizit ueber Kombinationen aus
`pending_followup`, `gate_decision`, `concern_state.phase` und
`response_mode` getragen.

Das kann funktionieren, bleibt aber als Gesamtvertrag noch unscharf.

### 4. Es fehlt eine ganz klare Grenze zwischen Gate-Erlaubnis und dialogischer Fuehrung

Der Code unterscheidet schon sinnvoll:

- welcher Pfad erlaubt ist
- welcher Text gezeigt wird

Aber nicht immer ist voll scharf getrennt:

- ob ein Zustand nur eine interne Freigabelage beschreibt
- oder schon einen konkreten dialogischen Knoten mit erlaubten Nutzerantworten

Gerade im Recommendation-/Closing-Bereich wirkt das System noch teilweise wie
eine Mischung aus:

- interner Freigabelogik
- dialogischem Uebergangsknoten
- Textoberflaeche


## Was wirkt doppelt oder gemischt?

Einige Probleme sind weniger "fehlt ganz" und mehr "existiert doppelt oder in
unsauber gemischter Form".

### Doppelte oder parallele Lesarten

- `allowed_next_step` als aktiv und zugleich gespiegelt
- Recommendation-Zustand ueber mehrere Felder statt ueber eine einzige
  primaere Wahrheit
- Response-Pfad teils als Mode, teils als State, teils als Strategy

### Gemischte Verantwortungen

- `TurnContext` als Zustand, Diagnosebehaelter und Ausgabecontainer
- `ConcernStateService` als Kontinuitaetsschicht, die zugleich Phasenlage
  sichtbar mitschreibt
- `ResponseManager` als saubere Policy-Schicht, aber mit legacy-naher
  Uebergangsbeobachtbarkeit im selben Objektfeldraum


## Was scheint die eigentliche Kernarchitektur zu sein?

Wenn man die Unsauberkeiten abzieht, bleibt ein relativ klares Zielbild uebrig.

Die eigentliche Architekturidee scheint zu sein:

- eine sichtbare Turn-Orchestrierung fuehrt den Ablauf
- fruehe Schichten liefern kleine Signale statt Gesamtentscheidungen
- nur eine begrenzte Truth-Kante schreibt medizinische Fallwahrheit fort
- Prozess, Requirement und Gate lesen diese Wahrheit weiter
- Response entscheidet spaet nur noch den erlaubten Antwortpfad
- Text formuliert nur noch freigegebene Bahnen

Das ist ein vernuenftiges und tragfaehiges Grundmodell.


## Was ist eher Uebergangs- oder Reparaturlogik?

Als Uebergangslogik wirken vor allem:

- Legacy-Mirror-Felder
- Fallback-Texte an API- und Response-Kante
- Recommendation-Hooks, die sichtbar mitlaufen, aber nicht immer die
  primaere Steuerwahrheit sind
- Confirmation als spaet sichtbarer, aber noch duenn eingeloester Randknoten

Diese Teile sind nicht nutzlos.
Aber sie sind eher Bruecken als Kernarchitektur.


## Schlussbild

Die staerkste Lesart des Systems ist nicht:

- "hier gibt es viele Manager und Services"

sondern:

- "hier wird versucht, einen medizinischen Turn als geschichtete
  Zustandsfortschreibung zu behandeln"

Das ist der wichtige architektonische Gedanke.

Die groessten Risiken liegen derzeit nicht primaer in einzelnen fehlerhaften
If-Abzweigungen, sondern in drei strukturellen Punkten:

1. zu viele Wahrheitsarten und Ableitungen treffen sich im `TurnContext`
2. mehrere Steuerwahrheiten fuer denselben hinteren Antwort-/Gate-Bereich
3. Concern-, Prozess- und Gate-Vertrag sind schon getrennt gedacht, aber
   noch nicht voll scharf gegeneinander abgeschlossen

Wenn man das System weiter verbessern will, ist daher die sinnvollste
Arbeitsrichtung:

- nicht mehr Heuristiken in bestehende Klassen zu kippen
- sondern die primaeren Wahrheiten, die Uebergangsvertraege und die aktiven
  Steuerknoten noch klarer voneinander zu trennen

Dann kann die unsaubere Implementierung nach und nach verschwinden, ohne dass
die eigentliche Architekturidee verloren geht.
