# Careena3: Grounding fuer den naechsten groesseren Refactor

Stand: 2026-06-13
Status: Arbeitsgrundlage / Planungsbasis


## Zweck

Dieses Dokument ist bewusst nicht einfach ein neuer glatter `V6`-Plan.

Dafuer driftet die vorhandene Arbeitsdoku zu stark zwischen:

- historischer Beschreibung
- realen Codeaenderungen
- plausiblen Architekturideen
- und bereits wieder ueberholten Zwischenannahmen

Der Zweck hier ist daher enger und nuetzlicher:

1. die belastbaren Linien aus `CHANGE_LOG.md`, `CHAT_COMPRESSION.md` und
   `workbench/` seit `2026-06-09` zusammenziehen
2. sie gegen den aktuellen Codezustand vom `2026-06-13` lesen
3. trennen, was heute wirklich Kernarchitektur ist, was Uebergangslogik ist
   und was nur alte Planrhetorik war
4. daraus eine brauchbare Grundlage fuer den naechsten groesseren Refactor
   ableiten


## Quellengewichtung

Hoechste Gewichtung:

- reale spaete Codeaenderungen in `CHANGE_LOG.md` ab `2026-06-12`
- `CHAT_COMPRESSION.md` ab `2026-06-12`, wenn dort eine spaetere Korrektur
  fruehere Annahmen einschraenkt
- aktueller Code in:
  - `server/careena3.py`
  - `server/careena_pipeline3/application/managers/dialogue_manager.py`
  - `server/careena_pipeline3/application/managers/entry_manager.py`
  - `server/careena_pipeline3/application/managers/extraction_manager.py`
  - `server/careena_pipeline3/application/managers/response_manager.py`
  - `server/careena_pipeline3/application/services/concern_state_service.py`
  - `server/careena_pipeline3/application/services/dialogue_state_service.py`
  - `server/careena_pipeline3/application/services/recommendation_state_service.py`
  - `server/careena_pipeline3/domain/requirement_policy.py`
  - `server/careena_pipeline3/domain/dialogue_focus_sync.py`
  - `server/careena_pipeline3/models/turn/context.py`

Mittlere Gewichtung:

- `REFACTOR_PLAN_V5.md`
- `CAREENA_ZIELBILD_UND_AUFARBEITUNG_2026-06-12.md`
- `TARGET_ARCHITECTURE_OBJECT_MODEL.md`
- `CAREENA3_BEHAVIOR_REDUCTION_REBUILD.md`
- `CALL2_RUNTIME_STABILISIERUNGSKONZEPT.md`
- die 13.06.-Papiere zu
  `CAREENA3_ARCHITECTURE_ABSTRACTION`,
  `CAREENA3_TARGET_SYSTEM`,
  `TURN_CENTRICITY_RISK`,
  `RUNTIME_WORLD_VS_TURN_WORLD`

Niedrigere,
aber weiterhin wichtige Gewichtung:

- aeltere V3-, Block-5-, Block-6- und Call-2-Konzepte vom `09./10.06.`,
  sofern spaetere Dokumente sie nicht sichtbar relativieren


## Rekonstruierter roter Faden

Seit `2026-06-09` laeuft dieselbe Grundbewegung durch fast alle starken
Dokumente:

1. weg von "mehr Prompt, mehr Reparatur, mehr Glue"
2. hin zu sichtbarer Turn-Orchestrierung
3. hin zu klarerer Truth-Kante fuer `MedicalCase`
4. hin zu einer expliziten Next-Step-/Gate-/Response-Schicht
5. spaeter hin zur Einsicht, dass auch diese Verbesserung noch auf einer zu
   turn-zentrierten Zwischenwelt aufsitzt

Die Dokumente widersprechen sich nicht komplett.
Sie verschieben nur ihren Brennpunkt:

- `09./10.06.`:
  zuerst Orchestrierung, Bridge, Entry, Call 2, Process-State, Response
- `11./12.06.`:
  Hauptspannung sitzt hinten bei Readiness, Freigabelogik, Abschlussknoten,
  Response und dem fehlenden Anliegen-/Fortschrittsmodell
- `13.06.`:
  die noch groessere Frage wird sichtbar:
  ob `TurnInput` und `TurnContext` inzwischen eine Schattenwelt gebaut haben,
  die Runtime-Wahrheit in Turn-Welt herueberzieht und dort erneut verteilt


## Was heute mit hoher Sicherheit als Kernarchitektur gilt

### 1. `careena3.py` ist nicht das eigentliche Architekturproblem

Der aktuelle HTTP-Einstieg ist relativ duenn:

- Session laden
- `TurnInput` bauen
- `DialogueManager.run_turn()` aufrufen
- Ergebnis in Session zurueckschreiben
- Antwort nach aussen exponieren

Die aeussere Schale ist nicht schoen,
aber sie ist auch nicht der Ort,
an dem die groesseren inneren Schichtprobleme sitzen.


### 2. `DialogueManager` ist die reale Orchestrierungsmitte

Der aktuelle Turn laeuft sichtbar in dieser Reihenfolge:

1. Persistenz in den Turn ziehen
2. rohe Safety
3. Case-Kontext sichern
4. Entry lesen
5. Concern nach Entry spiegeln
6. Extraktion optional ausfuehren
7. Case fortschreiben
8. Concern nach Case spiegeln
9. Process-State ableiten
10. Readiness und Gate ableiten
11. Concern nach Gate spiegeln
12. finale Safety
13. Response waehlen und formulieren
14. Confirmation spaet anhaengen

Diese zentrale Sichtbarkeit ist eine der staerksten realen Errungenschaften
des bisherigen Refactors und sollte nicht wieder versteckt werden.


### 3. `MedicalCase` ist weiter der kanonische medizinische Wahrheitsanker

Das ist trotz aller Drift in den Dokumenten klar stabil geblieben.

Neu seit `12./13.06.`:

- das Fallthema bzw. der Fallrahmen ist nicht mehr nur implizit ueber
  `primary_focus` gedacht
- es gibt mit `case_frame_label` und `current_case_frame_label()` einen
  expliziteren Lesepfad fuer den medizinischen Fallrahmen

Wichtig:

- `primary_problem_id` bleibt nuetzlich
- aber eher als Observation-Cursor als als globale Anliegenwahrheit


### 4. `DialogueState` ist als Prozessspur gedacht und weitgehend auch so nutzbar

`DialogueState` traegt heute sinnvoll:

- `pending_followup`
- `pending_dialogue_transition`
- `recommendation_requested`
- `recommendation_ready`
- `focus_observation_id`
- `focus_label`
- Requirement-Spuren

Das Problem ist nicht,
dass `DialogueState` existiert.
Das Problem ist,
dass angrenzende Schichten teils noch dieselbe Lage ein zweites Mal im
Turn-Kontext oder in abgeleiteten Policy-Objekten spiegeln.


### 5. Die spaete Trennung
### `Next-Step/Gate -> Response Policy -> Text`
### ist als Idee inzwischen sehr belastbar

Sowohl die Doku als auch der aktuelle Code zeigen:

- die Frage "welcher naechste Zug ist erlaubt?" soll vor dem Text beantwortet
  werden
- `ResponseManager` soll den Pfad waehlen
- die Textschicht soll nur freigegebene Bahnen formulieren

Die Richtung ist also richtig.
Offen ist nicht die Grundidee,
sondern die saubere Eigentuemerschaft dieser Stufen.


## Was der aktuelle Code am 2026-06-13 ueber die Restprobleme zeigt

### 1. `TurnInput` und `TurnContext` tragen zu viel Runtime-Wirklichkeit

`TurnInput` bekommt heute:

- `conversation_messages`
- `existing_case`
- `existing_dialogue_state`
- `existing_concern_state`

`TurnContext` sammelt danach gleichzeitig:

- persistierte Wahrheit
  - `medical_case`
  - `dialogue_state`
  - `concern_state`
- turn-lokale Signale
  - `process_state_signals`
  - `person_reference_present`
  - `concern_relation`
  - `latest_turn_role`
- abgeleitete Policy-/Response-Schicht
  - `assessment_readiness`
  - `gate_decision`
  - `response_state`
  - `response_strategy`
- Ausgabe
  - `response_mode`
  - `response_text`
  - `recommendation_result`
- Observability
  - `trace_notes`
  - Safety-Stufen

Das ist nicht nur ein "etwas grosser Context".
Das ist der staerkste aktuelle Hinweis darauf,
dass Turn World und Runtime World zu stark ineinandergeschoben sind.


### 2. Die Next-Step-Wahrheit ist noch nicht wirklich singulaer

Offiziell soll die aktive Steuerwahrheit heute sein:

- `gate_decision.allowed_next_step`

Praktisch existieren aber gleichzeitig:

- `TurnContext.gate_decision`
- `TurnContext.allowed_next_step`
- `TurnContext.active_allowed_next_step`

Der Code benennt `allowed_next_step` selbst bereits als
"Legacy mirror for older tests / observability".

Damit ist das Problem nicht hypothetisch,
sondern im Code selbst dokumentiert:

- die aktive Steuerwahrheit ist noch nicht voll entdoppelt


### 3. Auch die spaete Response-Lage ist noch doppelt und geschichtet

Heute existieren parallel:

- `response_mode`
- `response_state.selected_response_mode`
- `response_strategy`

Das ist besser als frueher,
weil die spaete Schicht ueberhaupt sichtbar getrennt wurde.
Aber es bleibt eine Uebergangslage:

- Pfad,
- Reaction-State
- und Strategie

leben noch eng beieinander und werden im Turn-Kontext mitgetragen.


### 4. `ConcernState` ist aktuell eher Spiegel- und Sichtbarkeitsobjekt
### als klar bestaetigtes drittes Fachzentrum

Der aktuelle Code stuetzt genau die vorsichtige Lesart der spaeten Dokumente:

- `ConcernStateService.sync_after_case_update()` spiegelt
  `active_concern_id` heute direkt aus
  `medical_case.primary_problem_id`
- `summary` wird aus `medical_case.current_case_frame_label()` gezogen
- `phase` wird aus
  Closing Node,
  `pending_followup`
  und spaeter `gate_decision.allowed_next_step` gesetzt
- `information_sufficiency` wird aus `Readiness` abgeleitet

Das heisst:

- `ConcernState` traegt aktuell kaum eigenstaendige primaere Wahrheit
- er spiegelt vor allem aus
  `MedicalCase`,
  `DialogueState`
  und Gate-/Readiness-Befunden

Genau deshalb ist die 13.06.-Warnung wichtig:

- `ConcernState` jetzt nicht dogmatisch vergroessern
- zuerst klaeren,
  ob er wirklich eine eigene persistente Heimat braucht


### 5. Die Focus-/Follow-up-Schicht ist noch nicht ruhig genug von der
### Fallrahmen-Schicht getrennt

Aktuell gilt:

- `DialogueFocusSync` synchronisiert `focus_observation_id` und
  `focus_label` eng gegen `MedicalCase.primary_problem_id`
- `RequirementPolicy.focused_observation()` liest zuerst
  `dialogue_state.focus_observation_id`,
  dann `medical_case.primary_problem_id`
- `pending_followup` bekommt eine gezielte `focus_observation_id`
  fuer observation-nahe Rueckfragen

Das ist lokal sinnvoll.

Die Restspannung sitzt woanders:

- `RequirementPolicy.has_blocking_requirements()` liest den Fall breiter
- `pending_followup` bleibt aber observation-spezifisch
- damit ist die Trennung
  `fallweiter Rahmen`
  vs.
  `lokaler Follow-up-Cursor`
  zwar besser als frueher,
  aber noch nicht voll stabilisiert

Genau hier tauchte am `13.06.` auch der Testkonflikt auf:

- nach beantwortetem Husten-Follow-up ist `Fieber` als fallweit offene
  Anforderung sofort wieder relevant
- aeltere Testerwartungen haengen aber noch an der alten
  Einzelfokus-Lesart


### 6. Die Truth-Write-Schwelle ist expliziter geworden, aber noch nicht ruhig

Positiv:

- `case_extension_status` ist inzwischen eingefuehrt
- `CaseMerger` nutzt ihn schon fuer kleine Write-Guards
- die alte starke Kopplung
  `confirm_observation -> user_confirmed`
  wurde reduziert

Aber:

- die operative Write-Schwelle haengt weiter an
  `ExtractionPayload.case_update_bridge is not None`
- `ExtractionManager` baut weiterhin
  `extraction_result` plus `case_update_bridge`
- `CaseStateManager` schreibt nur,
  wenn diese Bruecke vorhanden ist

Die Doku hatte hier also recht:

- die Kante ist besser,
  aber weiterhin transitional


### 7. `careena3.py` kaschiert Unfertigkeit noch ueber Fallback-Text

`_chat_response()` nutzt:

- `result.response_text or _fallback_response_text(result.response_mode)`

Das ist als Boundary-Schutz okay,
aber architektonisch wichtig:

- nach aussen kann eine vollstaendige Antwort erscheinen,
  obwohl die innere Text- oder Policy-Schicht gerade nur einen
  Platzhalterzustand erreicht hat

Auch das bestaetigt die 13.06.-Warnung:

- Sichtbarkeit vor Macht
- Unfertigkeit nicht zu stark wegpolstern


## Zentrale Leitprobleme, die ueber viele Dokumente hinweg wirklich bleiben

### 1. Runtime World und Turn World sind zu eng verkoppelt

Das ist aus heutiger Sicht wahrscheinlich das groesste strukturelle Problem.

Die frueheren Plaene sahen einzelne Schichtenprobleme:

- Concern
- Readiness
- Response
- Call 2

Die 13.06.-Lesart zeigt die tiefere gemeinsame Ursache:

- zu viel langlebige Runtime-Wirklichkeit wird in Turn-Arbeitsobjekte
  hineingezogen
- zu viele Schichten lesen danach lieber den Turn-Kontext als gezielt ihre
  Heimataggregate

Das erzeugt:

- breite Kontexte
- Spiegelzustand
- Glue-Code
- und groessere Refactor-Radien als noetig


### 2. Es gibt noch zu viele Zweitwahrheiten fuer denselben Steuerbereich

Betroffen sind vor allem:

- `gate_decision.allowed_next_step`
  vs.
  `allowed_next_step`
- `response_mode`
  vs.
  `response_state.selected_response_mode`
- Recommendation-Lage ueber:
  `recommendation_requested`,
  `recommendation_ready`,
  `pending_dialogue_transition`,
  `gate_status`,
  `response_state.recommendation_state`

Nicht jede dieser Spuren ist gleich problematisch.
Aber zusammen zeigen sie:

- dieselbe spaete Systemlage wird noch aus mehreren Perspektiven parallel
  gehalten


### 3. Der Vertrag zwischen
### `MedicalCase`,
### `DialogueState`,
### `ConcernState`
### und Next-Step-Policy
### ist noch nicht scharf genug

`MedicalCase`,
`DialogueState`
und die spaete Policy-Welt sind grundsaetzlich gut getrennt gedacht.

Offen bleibt:

- was `ConcernState` darueber hinaus wirklich eigenstaendig traegt
- ob Concern-Phase echte persistente Wahrheit,
  nur abgeleitete Verlaufslesart
  oder eigentlich Process-/Policy-Hilfssicht ist
- wo der verbindliche Vertrag fuer
  Concern-Wechsel,
  Turn-Fortsetzung
  und fallweiten Rahmen
  wirklich liegt


### 4. Call 2 ist verkleinert worden, aber die Mitte ist noch nicht final ruhig

Die juengeren Dokus hatten recht:

- `Call 2` ist nicht mehr das groesste Einzelproblem
- aber die mittlere Zone
  `Entry -> optional Call 2 -> Truth write -> Process/Gate`
  bleibt eine aktive Uebergangskante

Besonders offen:

- wie klein `Call 2` langfristig wirklich bleiben soll
- ob er spaeter auch gezielte Rueckfragen liefern darf
- wie explizit
  `kein Call 2`,
  `Call 2 ohne Truth Write`,
  `Call 2 mit Truth Write`
  im Runtime-Modell werden


### 5. Fallbacks und Observability-Reste schuetzen den Lauf,
### aber halten zugleich Parallelwirklichkeiten am Leben

Das ist kein Vorwurf,
sondern eine Strukturbeobachtung.

Beispiele:

- `allowed_next_step`-Mirror
- `pending_dialogue_transition` als Legacy-Hook
- `recommendation_ready` als sichtbarer Legacy/Future-Hook
- Fallback-Texte in `careena3.py`
- Response-Observability in `ResponseState`

Diese Dinge sind oft sinnvoll.
Aber sie markieren genau die Orte,
an denen ein groesserer Refactor entweder echte Entkopplung schafft
oder nur neue Glue-Schichten baut.


## Was aus der historischen Doku weiterhin essenziell bleibt

### Essenziell geblieben

- Boundary first, not feature first
- erst Vertrag, dann Verhalten
- sichtbare Orchestrierung zentral halten
- persistente Wahrheit nur an wenigen klaren Orten
- Text darf fehlende Semantik nicht ersetzen
- `Call 2` nicht wieder zum breiten Einheitscall aufblasen
- `Readiness` nicht mit "Anliegen wirklich genug verstanden" verwechseln


### Teilweise ueberholt oder neu eingeordnet

- fruehere starke Hoffnung,
  dass ein kleiner Concern-Einbau schon die grosse Mittelspannung loest
- Annahmen,
  dass der Hauptrestfehler primaer nur hinten in Response/Transition sitzt
- Annahmen,
  dass `primary_focus` oder spaeter `primary_problem_id`
  laenger die Doppelfunktion aus
  Fallrahmen und lokalem Follow-up-Fokus tragen koennen


### Weiter offen und deshalb nicht dogmatisch vorwegzunehmen

- ob `ConcernState` bleibt,
  schrumpft
  oder spaeter ganz verschwindet
- ob Next-Step als eigener langlebiger Vertragstyp verbleibt
  oder nur als abgeleitete Stage-Entscheidung existiert
- wie weit spaeter freie bounded Antwortarbeit
  oder Rueckfragen-Erzeugung wieder nach vorne geholt werden


## Offene Baustellen aus laufenden Refactors

### 1. Entkopplung von Runtime World und Turn World

Das ist die groesste offene strukturelle Baustelle.

Noch offen:

- welche persistierten Aggregate direkt gelesen werden sollen
- welche Informationen im Turn nur Delta/Assessment sein duerfen
- wie stark `TurnInput` und `TurnContext` verkleinert werden koennen,
  ohne die sichtbare Orchestrierung zu verlieren


### 2. Vereinheitlichung der aktiven Next-Step-Wahrheit

Noch offen:

- `allowed_next_step`-Mirror entfernen
- `gate_decision` ruhiger schneiden
- klaeren,
  was im spaeten Pfad primaere Steuerwahrheit,
  was reine Trace-Sicht
  und was nur Response-Ableitung ist


### 3. Saubere Heimat fuer Concern-Semantik

Noch offen:

- ist Concern eine eigene persistente Welt
- oder nur eine abgeleitete Verlaufs- und Kontinuitaetslesart
- welche Concern-Daten sind primaer,
  welche nur aus Case/Dialogue/Gate gespiegelt


### 4. Fallrahmen vs. Observation-Cursor weiter beruhigen

Noch offen:

- `case_frame_label` konsequent als fallweiter Rahmen etablieren
- `primary_problem_id` und `focus_observation_id`
  nur noch fuer Cursor-/Follow-up-Arbeit lesen
- Requirement- und Follow-up-Verhalten gegen den fallweiten Rahmen haerten,
  ohne den lokalen Cursor zu verlieren


### 5. Truth-Write-Kante von der Bridge-Logik loesen

Noch offen:

- `case_update_bridge` weiter abbauen
- Case-Delta bzw. `ClinicalUpdate`-artige Zwischenvertraege scharfziehen
- Truth-Write expliziter machen als
  "Bridge vorhanden oder nicht"


### 6. Response-Policy weiter entmischen

Noch offen:

- wie viel von `response_state` nur Observability ist
- wie `response_mode`,
  `response_state`
  und `response_strategy`
  langfristig sauber zueinanderstehen
- wie weit Fallback-Texte an der Boundary ueberhaupt noch gebraucht werden


## Wahrscheinlich sinnvollster naechster groesserer Refactor

Nicht:

- direkt ein neuer grosser `Call 2`-Ausbau
- direkt ein Concern-Superstate
- direkt nur bessere freie Antworten

Sondern:

## Refactor-Achse A: Runtime- / Turn-Entkabelung

Ziel:

- `Turn` wieder klar als Ausfuehrungseinheit
- Runtime-Wahrheit wieder klar in persistierten Aggregaten
- kleinere Stage-Ergebnisse statt grossem turnweiten Zustandsschatten

Praktische Unterfragen:

1. Welche Felder in `TurnContext` sind eigentlich nur Spiegel persistierter
   Wahrheit?
2. Welche Felder sind echte turn-lokale Arbeitsdaten?
3. Welche Felder sind nur spaete abgeleitete Assessments?
4. Welche Felder gehoeren eigentlich in `TurnResult` oder reine Trace-Ausgabe
   statt in den Arbeitskontext?


## Refactor-Achse B: Eine primaere Next-Step-Wahrheit erzwingen

Ziel:

- genau eine aktive spaete Handlungsfreigabe

Nicht als blosses Rename,
sondern als Verantwortungsbereinigung:

- Gate/Next-Step entscheidet
- Response leitet davon Antwortpfad und Strategie ab
- Text formuliert nur noch


## Refactor-Achse C: Concern nicht vergroessern,
## sondern auf Heimat pruefen

Ziel:

- nicht "mehr Concern bauen"
- sondern pruefen,
  was davon wirklich persistente eigene Wahrheit ist

Praktische Leitfrage:

- Wenn `ConcernStateService` fast nur aus
  Case,
  Dialogue
  und Gate spiegelt,
  welche Concern-Daten waeren dann ueberhaupt noch primaer genug,
  um eine eigene persistente Heimat zu rechtfertigen?


## Konkrete Startreihenfolge fuer die Planung

1. `TurnInput`, `TurnContext`, `TurnResult` und Session-Daten strikt nach
   Wahrheitsarten markieren:
   persisted truth / turn work / derived assessment / output
2. fuer den spaeten Steuerbereich eine Tabelle bauen:
   primaere Wahrheit,
   aktuelle Spiegel,
   Observability-Reste,
   Fallback-Reste
3. erst danach entscheiden,
   ob der erste Code-Schnitt bei
   `TurnContext`,
   `RecommendationStateService`
   oder `ResponseManager`
   beginnt
4. Concern erst nach diesem Mapping wieder anfassen,
   nicht davor


## Was beim naechsten Refactor explizit nicht passieren sollte

- keinen neuen grossen Sammelvertrag nur sauberer benennen
- keine weitere Zwischenwelt zwischen Runtime und Turn bauen
- kein "wir lassen alles wie es ist und lesen es nur ueber neue Wrapper"
- kein Aufblasen von `ConcernState`, nur damit eine fehlende Heimat kaschiert
  wird
- keine weitere Response- oder Entry-Heuristik,
  solange die primaere Steuerwahrheit noch doppelt ist
- keinen neuen Glue-Code,
  der Bridge, Spiegel und Fallback lediglich besser tarnt


## Arbeitsurteil

Der bisherige Refactor hat echte Fortschritte gemacht:

- Orchestrierung sichtbar
- Truth-Kante klarer
- Next-Step- und Response-Fragen expliziter
- Fallrahmen staerker im Case verankert

Der naechste groessere Gewinn liegt aber sehr wahrscheinlich nicht mehr in
einem weiteren lokalen Policy- oder Call-2-Schnitt allein.

Der naechste groessere Gewinn liegt darin,
die noch immer zu breite Turn-Zwischenwelt gegen die eigentliche Runtime-Welt
zu entkabeln und dabei die primaeren Wahrheiten im spaeten Steuerbereich
wirklich zu singularisieren.

Wenn das gelingt,
werden die spaeteren Fragen zu Concern,
Follow-up,
Recommendation
und bounded Response deutlich lokaler und ruhiger bearbeitbar.
