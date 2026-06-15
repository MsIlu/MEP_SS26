# Block-6-Konzept: Response-Transition, Abschluss-Follow-up und Recommendation-Uebergang

Stand: 2026-06-10
Status: Entwurf
Bezug:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `application/managers/response_manager.py`
- `application/services/response_text_builder.py`
- `application/services/recommendation_state_service.py`
- `application/services/recommendation_result_builder.py`
- `application/managers/entry_manager.py`
- `llm/prompts/intent_gateway.py`
- `models/common/types.py`


## Zweck

Dieses Konzept bereitet Block 6 vor.

Es setzt bewusst die "obere Brille" aus V3 auf:

- boundary first
- behavior over names
- erst Vertrag, dann Verhalten
- keine vorschnelle Festlegung von `Call 3` vs. neuem `Call-2`-Modus
- keine textliche Scheinfertigstellung an Stellen, wo der Zustand noch nicht
  sauber modelliert ist

Block 6 soll den hinteren Teil des Turn-Flusses sauberer verkabeln, nachdem
die vorderen Grenzen inzwischen deutlich stabiler geworden sind.


## Ausgangslage

Die juengeren Refactor-Schritte haben vor allem den vorderen und mittleren
Teil des Systems klarer gezogen:

- `DialogueManager` als sichtbare Orchestrierung
- kleinere Entry-Signale
- kleinere Call-2-Vertraege
- klarere Truth-Kante
- explizitere Process-State- und Readiness-Stufen

Dadurch wird der hintere Bereich jetzt deutlicher sichtbar als eigentliche
Restbaustelle:

- `ResponseManager`
- `ResponseTextBuilder`
- Recommendation-Uebergang
- spaetere Inhaltsableitung fuer Recommendation

Der aktuelle Logrest zeigt genau diese Zone:

- `guide_next_step` behauptet einen Abschluss-/Freigabe-Uebergang
- aber die Antwort `Nein.` darauf wird noch als medizinischer
  Extraktions-Turn behandelt
- damit ersetzt Text weiterhin ein fehlendes explizites
  Transition-Modell


## Kernbeobachtung

Im aktuellen Verhalten werden mehrere Ebenen noch nicht sauber auseinander
gehalten:

1. medizinische Rueckfrage
2. dialogische Abschlussfrage
3. Recommendation-Freigabe
4. Recommendation-Inhaltsgenerierung
5. finale Textausgabe

Genau diese Ebenen muessen fuer Block 6 getrennt lesbar werden.


## Wichtige Trennung der Ebenen

### Ebene A: Policy-/Zustandsebene

Hier wird entschieden:

- fehlt noch medizinisch notwendige Information?
- ist der Fall intern schon recommendation-bereit?
- braucht es noch eine dialogische Abschlussklaerung?
- ist der Recommendation-Pfad wirklich freigegeben?

Das ist nicht dieselbe Ebene wie Text oder LLM-Inhalt.


### Ebene B: Dialogische Uebergangsebene

Hier geht es um Antworten wie:

- `Gibt es noch weitere Beschwerden?`
- `Sind Sie soweit fertig mit der Schilderung?`
- `Soll ich aus dem bisherigen Fall jetzt die Empfehlung ableiten?`

Diese Ebene ist prozessual und dialogisch.
Sie ist nicht identisch mit medizinischem Requirement-Follow-up.


### Ebene C: Inhaltsgenerierungsebene

Hier entsteht spaeter entweder:

- eine medizinisch bessere freie Rueckfrage,
- oder Recommendation-Content,
- oder eine freiere zusammenfassende Antwort.

Diese Ebene kann spaeter ueber einen neuen Call laufen,
oder ueber einen anderen Modus eines vorhandenen Werkzeugkastens.

Diese Frage soll Block 6 noch nicht final entscheiden.


### Ebene D: Textausgabe

Der `ResponseTextBuilder` soll nur noch formulieren,
was auf den oberen Ebenen bereits freigegeben wurde.

Er soll keine fehlende Zustandslogik ersetzen.


## Zentrale Block-6-Lesart

`guide_next_step` ist fachlich keine normale medizinische Rueckfrage.

Es ist eher ein Abschluss-/Freigabe-Follow-up:

- medizinisch koennte das System intern bereits recommendation-bereit sein
- aber dialogisch soll noch nicht vorschnell direkt eine Empfehlung
  herausgegeben werden
- deshalb wird vor der Recommendation noch die Gespraechsfreigabe eingeholt

Die richtige Lesart ist daher:

- `ask_followup` = medizinisches Requirement-Follow-up
- `guide_next_step` = dialogischer Abschluss-/Freigabe-Uebergang
- `recommend` = Recommendation-Pfad ist wirklich freigegeben


## Praezisierung des Abschluss-/Freigabepfads

Der bisherige `guide_next_step`-Text ist inhaltlich noch zu unscharf.

Die staerkere Block-6-Lesart lautet:

- das System ist intern recommendation-bereit
- aber der Nutzer soll noch explizit zwischen zwei dialogischen Wegen waehlen

Diese zwei semantischen Ausgaenge sind:

1. `request_recommendation`
2. `report_more_information`

Das ist wichtiger als die genaue Formulierung der Oberflaechenfrage.

Eine brauchbare Richtung waere zum Beispiel:

- `Moechten Sie jetzt eine Versorgungsempfehlung erhalten oder haben Sie noch weitere Beschwerden?`

Noch klarer als Zwei-Wege-Semantik:

- `Moechten Sie jetzt eine Versorgungsempfehlung erhalten?`
- `Oder moechten Sie noch weitere Beschwerden ergaenzen?`

Wichtig ist:

- der Zustand muss diese zwei moeglichen Antworten tragen
- der Text ist nur eine Darstellung davon


## Erlaubte Antworten am Abschlussknoten

Wenn `pending_dialogue_transition` auf dem Recommendation-Abschlusspfad steht,
dann soll der Knoten nicht beliebige Bedeutungen tragen, sondern primaer genau
diese zwei semantischen Ausgaenge unterscheiden:

- Recommendation jetzt ausloesen
- weitere medizinische Information nachreichen

Moegliche Oberflaechenformen fuer
`request_recommendation`:

- `Nein.`
- `Das war alles.`
- `Ja, bitte Empfehlung.`
- Klick auf einen Antwortvorschlag wie `Empfehlung erhalten`

Moegliche Oberflaechenformen fuer
`report_more_information`:

- freie neue Beschwerdeschilderung
- `Ja, ich habe noch ...`
- Klick auf einen Antwortvorschlag wie `Weitere Beschwerden angeben`

Die eigentliche Architekturfrage ist daher nicht:

- Buttons oder Freitext?

sondern:

- welche semantischen Ausgaenge sind in diesem Zustand ueberhaupt erlaubt?


## Was `guide_next_step` nicht sein sollte

`guide_next_step` sollte nicht:

- nur ein zufaelliger Textmodus sein
- eine versteckte Ersatzlogik fuer fehlende Zustandssemantik sein
- wieder in medizinische Extraktion zurueckfallen, wenn der Nutzer schlicht
  mit `Nein.` oder `Das war alles.` antwortet


## Arbeitsannahme fuer Block 6

Der Response-Knoten braucht mindestens zwei verschiedene Arten von
"Rueckfrage":

1. medizinische Rueckfrage
2. dialogische Abschluss-/Freigaberueckfrage

Diese beiden Rollen duerfen im Zustandssystem nicht mehr nur als Text
ineinanderfallen.

Fuer die dialogische Abschluss-/Freigaberueckfrage gilt zusaetzlich:

- sie ist kein offener Wunsch nach beliebiger Interpretation
- sie ist ein kleiner Knoten mit zwei primaeren erlaubten Ausgaengen
- Recommendation jetzt
- oder weitere Informationen


## Gewuenschter Response-Knoten

Der Response-Knoten soll sichtbar zwischen mehreren Pfaden unterscheiden:

1. `emergency`
2. `out_of_scope`
3. `cannot_assess`
4. `ask_followup`
5. `guide_next_step` oder spaeter klarer benannter Abschluss-/Freigabepfad
6. `recommend`
7. spaeter moegliche weitere Pfade wie `confirm_information`

Entscheidend ist:

- jeder Pfad braucht einen kleinen expliziten Bedeutungsvertrag
- Text ist nur die Oberflaeche dieses Pfads


## Vorschlag fuer die kleine neue Vertragsmitte

Block 6 braucht wahrscheinlich ein kleines explizites
Transition-/Response-Policy-Objekt oder eine kleine neue Ergebnisstruktur.

Arbeitsnamen:

- `ResponseTransitionState`
- `DialogueCompletionState`
- `ResponseGateState`

Noch kein finales Naming erzwingen.

Wichtige minimale Fragen, die dieses Objekt lesbar machen sollte:

- braucht der Turn noch medizinische Information?
- ist Recommendation intern bereit?
- wartet das System noch auf dialogische Abschlussfreigabe?
- ist Recommendation jetzt wirklich freigegeben?
- soll als naechstes ein medizinischer, ein dialogischer oder ein
  recommendation-inhaltlicher Pfad laufen?


## Empfohlene Minimalfelder

Noch ohne Anspruch auf Endnamen:

- `medical_followup_required: bool`
- `dialogue_completion_check_required: bool`
- `recommendation_can_be_offered: bool`
- `recommendation_committed: bool`
- `allowed_completion_actions: list[str]`
- `next_response_gate: str`
- `trace_notes`

Wichtig:

- das ist kein Content-Objekt
- das ist kein Recommendation-Ergebnis
- das ist keine neue medizinische Wahrheit
- es beschreibt nur die Freigabelage des hinteren Turn-Teils

Ein sinnvoller frueher Inhalt fuer `allowed_completion_actions` waere:

- `request_recommendation`
- `report_more_information`


## Wie `Nein.` darauf gelesen werden sollte

Wenn das System gerade im dialogischen Abschluss-/Freigabepfad ist,
dann ist `Nein.` nicht primaer:

- `new_information`
- medizinisches `answer_to_followup`
- oder normaler Call-2-Extraktionsinput

sondern eher:

- Antwort auf einen dialogischen Abschluss-Check
- und in vielen Faellen konkret:
  `request_recommendation`

Umgekehrt gilt:

- wenn der Nutzer auf denselben Knoten hin neue medizinische Information
  liefert,
  dann ist die Antwort kein Recommendation-Commit,
  sondern `report_more_information`
  und darf wieder in den medizinischen Entry-/Call-1-/Call-2-Pfad
  zurueckfliessen

Das bedeutet nicht automatisch,
dass dafuer nie ein LLM gebraucht werden darf.

Es bedeutet nur:

- die Policy-Ebene muss zuerst explizit wissen,
  dass dies eine Antwort auf einen dialogischen Transition-Knoten ist


## Abgrenzung zu Block 5

Block 5 trennt:

- Requirement
- Process-State
- Readiness

Block 6 trennt:

- Response-Freigabe
- dialogischen Abschluss-Uebergang
- Recommendation-Commit
- und finalen Text

Die beiden Bloecke greifen ineinander,
aber Block 6 sollte Block 5 nicht wieder unsichtbar machen.

Deshalb:

- medizinische Requirement-Follow-ups bleiben bei Block 5 / Process-State
- dialogische Abschluss-Follow-ups gehoeren in Block 6 / Response-Transition


## Abgrenzung zur spaeteren Inhaltsfrage

Eine medizinisch bessere freie Rueckfrage oder Recommendation-Inhalt kann
spaeter sehr wohl wieder ein LLM-Thema sein.

Aber diese Frage sitzt unterhalb der Policy-Entscheidung:

1. erst Pfad und Freigabe
2. dann Inhalt

Das bedeutet:

- Block 6 muss noch nicht final entscheiden,
  ob Recommendation-Inhalt ein eigener `Call 3` wird
  oder ein anderer Modus des vorhandenen Call-2-Werkzeugkastens
- Block 6 muss nur die Stelle schaffen,
  an der diese spaetere Inhaltsarbeit sauber andocken kann


## UI-Vorschlaege und freie Eingabe

Die Architektur soll sowohl streng gefuehrte UI
als auch freie Eingabe tragen koennen.

### Variante A: gefuehrte UI

- das Frontend zeigt Antwortvorschlaege fuer den aktiven Abschlussknoten
- optional wird das freie Eingabefeld kurz gesperrt
- der Nutzer waehlt z. B.:
  `Empfehlung erhalten`
  oder
  `Weitere Beschwerden angeben`

Vorteil:

- sehr robuste Dialogfuehrung
- wenig Interpretationslast im Backend


### Variante B: freie Eingabe

- das Textfeld bleibt offen
- die Antwort wird gegen den aktiven Abschlussknoten gelesen
- semantisch wird wieder nur unterschieden:
  `request_recommendation`
  oder
  `report_more_information`

Vorteil:

- flexibler fuer natuerliche Antworten
- keine harte UI-Sperre noetig


### Empfohlene Zwischenhaltung

Backend-seitig sollte Block 6 beide Varianten tragen.

Das bedeutet:

- Vorschlaege im Frontend sind eine UI-Oberflaeche auf denselben
  kleinen Zustandsknoten
- freie Eingabe bleibt moeglich
- aber freie Eingabe wird zuerst gegen den aktiven
  Recommendation-Abschlussknoten gelesen
  und nicht sofort wie ein gewoehnlicher medizinischer Extraktions-Turn
  behandelt

Damit bleibt die Architektur zustandsbasiert,
waehrend die UI spaeter frei entscheiden kann,
wie stark sie fuehrt


## Bewertung: `Call 3` vs. neuer Werkzeugkasten-Modus

Diese Frage ist real und wichtig,
aber fuer Block 6 noch bewusst offen.

### Was fuer einen spaeteren eigenen `Call 3` spricht

- Recommendation-Inhalt ist fachlich und funktional etwas anderes als
  medizinische Fakt-Extraktion
- dialogische freie Rueckfragen oder Recommendation-Formulierung sind naeher
  an Ausgabe-/Inhaltsgenerierung als an Case-Update
- ein eigener Call trennt Eingangsarbeit und Ausgangsarbeit deutlicher


### Was fuer einen spaeteren anderen Modus desselben Werkzeugkastens spricht

- ein konfigurierbarer Werkzeugkasten kann in einem gemeinsamen
  LLM-Runtime-Rahmen bleiben
- fuer spaetere Runtime-/Prompt-Komposition kann ein einheitlicherer
  Mechanismus praktisch sein


### V3-konforme Zwischenentscheidung

Noch nicht festlegen.

Fuer Block 6 reicht:

- Recommendation-Inhalt und freie dialogische Inhaltsantworten sind eine
  eigene spaetere Inhaltskante
- sie duerfen nicht implizit schon in der Response-Policy oder in
  `guide_next_step` versteckt sein


## Konkrete Zielbewegung fuer den naechsten Refactor-Schritt

### Schritt 1

`guide_next_step` als sichtbaren Transition-Pfad lesen,
nicht nur als Text.

### Schritt 2

Einen kleinen expliziten Response-/Transition-Vertrag einfuehren oder
vorbereiten.

### Schritt 3

`Nein.` / `das war alles` / aehnliche Antworten auf diesen Transition-Pfad
nicht mehr als normalen medizinischen Extraktions-Turn behandeln.

Parallel dazu den Gegenpfad explizit mitdenken:

- wenn der Nutzer auf denselben Knoten weitere Beschwerden liefert,
  muss dies als `report_more_information`
  sauber wieder in den medizinischen Pfad zurueckgehen

### Schritt 4

`ResponseManager` staerker als Policy-Schicht lesen.

### Schritt 5

`ResponseTextBuilder` auf freigegebene Pfade reduzieren.

### Schritt 6

Erst danach spaeter entscheiden,
ob Recommendation-Inhalt oder freie medizinische Rueckfragen ueber
einen eigenen `Call 3`
oder ueber einen neuen Werkzeugkasten-Modus laufen.


## Was dieser Block bewusst noch nicht loest

- die finale Recommendation-Engine
- den finalen Zuschnitt eines spaeteren `Call 3`
- die komplette freie medizinische Rueckfragegenerierung
- Confirmation-Ausbau
- Safety-Ausbau

Das ist Absicht.
Block 6 soll zuerst den hinteren Knoten vertraglich sauber machen,
nicht sofort alle spaeteren Inhalte ausbauen.


## Definition von Erfolg fuer Block 6

Block 6 ist bereits gut getroffen, wenn danach klarer ist:

- wann ein medizinisches Follow-up offen ist
- wann nur noch ein dialogischer Abschluss-/Freigabe-Check offen ist
- wann Recommendation nur intern bereit ist
- wann Recommendation wirklich freigegeben ist
- welche kleinen erlaubten Ausgaenge der Abschlussknoten ueberhaupt hat
- dass Text diese Unterschiede nicht mehr ueberdecken muss

Wenn das erreicht ist, ist der hintere Bereich deutlich sauberer verkabelt,
auch wenn die spaetere Inhaltskante
`Call 3` vs. Werkzeugkasten-Modus
noch offen bleibt.
