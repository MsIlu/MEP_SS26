# Refactor Plan Data

Stand: 2026-06-14
Status: Arbeitsplan fuer den naechsten schrittweisen Architekturumbau


## Zweck

Dieses Papier uebersetzt die Richtung aus
`2026-06-13/NEXT_REFACTOR_GROUNDING_2026-06-13.md`
in einen vorsichtigen Umsetzungsplan gegen den echten Codezustand.

Es ist bewusst kein Voll-Zielbild und keine starre Reihenfolge fuer alle
spaeteren Schritte.

Es soll vor allem helfen,

- die heute reale Hauptspannung sauber zu benennen
- den minimalen wirksamen Refactor-Radius zu finden
- die richtigen Leitfragen pro Phase festzuhalten
- und zu verhindern,
  dass wieder nur lokale Spiegel verschoben werden


## Arbeitsurteil

Die vorhandene Struktur ist bereits deutlich weiter,
als es das Systemgefuehl zuerst vermuten laesst.

Der groesste Hebel ist sehr wahrscheinlich nicht:

- ein neuer grosser Concern-Ausbau
- ein neuer groesserer Call-2-Ausbau
- oder ein weiterer lokaler Response-Feinschnitt

Der groesste Hebel ist:

- Runtime-Wahrheit wieder staerker an ihren Heimataggregaten lesen
- Turn-Objekte auf Ausfuehrung, Assessment und Ausgabe zurueckschneiden
- und im spaeten Steuerbereich genau eine aktive Handlungswahrheit erzwingen


## Statusupdate 2026-06-14 nach Umsetzung

### Bereits umgesetzt

- `TurnInput` traegt persistierte Runtime-Wahrheit jetzt explizit ueber
  `persisted_case`,
  `persisted_dialogue_state`
  und
  `persisted_concern_state`
- `TurnInput` schiebt nicht mehr eine einzige globale Turn-Historie aktiv
  durch alle Stufen,
  sondern getrennte purpose-spezifische History-Slices fuer
  Entry,
  Extraction,
  Transition
  und
  Response
- `TurnContext.allowed_next_step` und
  `TurnContext.active_allowed_next_step`
  sind aus dem aktiven Laufpfad entfernt;
  aktive spaete Steuerung liest jetzt direkt
  `gate_decision.allowed_next_step`
- `TurnContext.pending_followup` ist als aktiver Spiegel entfernt;
  aktuelle Follow-up-Wahrheit sitzt jetzt nur noch in
  `dialogue_state.pending_followup`
- response-nahe Spiegel im aktiven
  `TurnContext`
  sind weitgehend entfernt:
  `response_mode`,
  `response_state`,
  `response_strategy`,
  `response_text`
  und
  `recommendation_result`
  treiben das Laufverhalten nicht mehr ueber den Context
- `TurnResult` ist zum echten Boundary-Vertrag geworden und traegt jetzt
  direkt:
  `medical_case`,
  `dialogue_state`,
  `concern_state`,
  `response_mode`,
  `response_text`,
  `recommendation_result`
  und
  `trace_notes`
- `careena3.py` und der Simulations-Adapter lesen und schreiben Persistenz
  jetzt ueber
  `TurnResult`
  statt ueber
  `result.context`
- der Boundary-Fallback fuer
  `response_text`
  in
  `careena3.py`
  ist entfernt;
  die Response-Schicht muss jetzt selbst echten Antworttext liefern


### Teilweise umgesetzt, aber noch nicht voll beruhigt

- die Feldinventur ist jetzt implizit im Code und in den Doc-Kommentaren
  sichtbar,
  aber noch nicht als eigene knappe Feldmatrix zusammengezogen
- die Historie ist kleiner und zweckgebundener,
  aber noch nicht auf die kleinstmoeglichen Signale reduziert;
  es werden weiterhin Listen von Nachrichten herumgereicht,
  nur eben schmaler und gezielter
- `RecommendationGateDecision` ist als aktive Next-Step-Wahrheit gestarkt,
  aber die Legacy-Hooks
  `recommendation_ready`
  und
  `pending_dialogue_transition`
  leben noch im
  `DialogueState`
  weiter
- `ResponsePlan`
  bleibt noch eine kleine Mischkante aus
  Policy,
  Output
  und
  Legacy-Transition-Observability
- die Write-Kante bleibt weiterhin bridge-zentriert:
  `case_extension_status`
  hilft schon,
  aber operativ schreibt weiterhin die Existenz von
  `case_update_bridge`
  den Hauptpfad vor


### Neue Lage nach dem Refactor

Der urspruengliche Plan traegt weiterhin,
aber seine Reihenfolge hat sich praktisch verschoben.

Die fruehen Wellen sind nicht mehr offen,
sondern zu grossen Teilen bereits erledigt:

- Phase 1:
  weitgehend praktisch eingeloest
- Phase 2:
  im aktiven Pfad umgesetzt
- Phase 3:
  grossenteils umgesetzt
- Phase 4:
  begonnen und sinnvoll vorgezogen

Damit ist der sinnvollste naechste Schritt nicht mehr,
noch einmal an
`TurnResult`
oder an der reinen
`allowed_next_step`
-Singularisierung zu arbeiten.

Der sinnvollste naechste Schritt liegt jetzt an den verbliebenen
Uebergangsresten:

1. Legacy-Hooks im spaeten Steuerbereich
2. letzte Response-/Policy-Mischkanten
3. expliziterer Truth-Write-Vertrag


## Statusupdate 2026-06-14 nach Legacy-Closing-Schnitt

### Zusaetzlich umgesetzt

- `DialogueState.pending_dialogue_transition` ist aus dem aktiven
  Runtime-Pfad entfernt und durch den kleineren Prozessvertrag
  `pending_choice_prompt`
  mit
  `kind="recommendation_choice"`
  ersetzt
- `DialogueState.recommendation_ready` ist als persistente bzw. turn-aktive
  Wahrheit entfernt;
  die HTTP-Boundary gibt es nur noch als abgeleiteten
  Kompatibilitaetswert aus
- `EntryManager`,
  Recommendation-Choice-Resolver,
  `RecommendationStateService`,
  `ConcernStateService`
  und der Call-1-/LLM-Kontext lesen jetzt den offenen spaeten
  Abschlussknoten ueber
  `pending_choice_prompt`
  statt ueber den alten Transition-Hook
- `guide_next_step` setzt diesen neuen Prompt-Vertrag jetzt sichtbar im
  spaeten Response-Schritt;
  der naechste Turn kann ihn explizit aufloesen oder beenden
- `ResponsePlan` traegt kein altes Transition-Payload mehr und ist dadurch
  etwas sauberer auf Policy,
  Output
  und Trace zurueckgeschnitten


### Dadurch beruhigt

- die zuvor staerkste Legacy-Doppelwahrheit im spaeten
  Recommendation-Abschluss ist praktisch entfernt
- die aktive post-processing-Handlungswahrheit liegt jetzt noch klarer bei
  `RecommendationGateDecision.allowed_next_step`
- die alte Planannahme
  "erst Legacy-Hooks im spaeten Steuerbereich abbauen"
  ist damit nicht mehr nur offen,
  sondern in ihrem wichtigsten lokalen Teil praktisch eingeloest


### Weiter offen

- die Feldinventur ist weiterhin nur implizit ueber Modelle,
  Docstrings
  und den aktuellen Code verteilt,
  aber noch nicht als eigene knappe Matrix zusammengezogen
- `TurnContext` bleibt trotz Schrumpfung weiter ein Mischtraeger fuer
  persistierte Wahrheit,
  turn-lokale Signale,
  Assessments
  und Observability
- die Historie ist zwar zweckgebunden gesplittet,
  aber weiterhin relativ breit;
  mehrere Schichten lesen noch Listen von Nachrichten statt kleinerer
  spezialisierter Signale
- `gate_status` und Teile von
  `response_state`
  bleiben weiterhin eher beobachtungsnahe Sekundaerachsen neben der
  eigentlichen Handlungsfreigabe
- die Write-Kante bleibt der naechste klar sichtbare strukturelle Rest:
  `case_extension_status`
  hilft,
  aber die operative Schwelle bleibt noch
  `case_update_bridge is not None`


### Neue Lage nach dem zweiten Schnitt

Der Plan traegt weiterhin,
aber der Schwerpunkt verschiebt sich jetzt noch deutlicher.

Die fruehen und mittleren Policy-/Boundary-Wellen sind inzwischen
praktisch weitgehend eingeloest:

- Phase 1:
  fachlich noch als Dokumentationsaufgabe offen,
  aber implizit im Code schon stark vorbereitet
- Phase 2:
  im aktiven Laufpfad weitgehend umgesetzt
- Phase 3:
  in wichtigen Teilen umgesetzt,
  aber noch nicht als saubere Feldmatrix expliziert
- der fruehere Legacy-Closing-Block ist jetzt als lokaler Refactor
  praktisch erledigt

Damit liegt der naechste sinnvollste Schritt nicht mehr primaer bei
spaeten Recommendation-Hooks,
sondern bei:

1. expliziter Feld-/Vertragsinventur als kleine Architektursicherung
2. weiterer Verkleinerung der turnweiten Historien- und Mischvertraege
3. der expliziteren Truth-Write-Kante zwischen Extraction und Merge


## Beobachteter Ist-Zustand im Code

### 1. Die Persistenz ist da, aber sie wird im Turn zu breit neu verteilt

`careena3.py` laedt bereits genau die drei persistierten Aggregate:

- `session.case`
- `session.dialogue_state`
- `session.concern_state`

und schreibt sie nach dem Turn wieder zurueck.

Das eigentliche Problem sitzt danach:

- `TurnInput` transportiert Persistenz plus Nachrichtenhistorie
- `DialogueManager` seedet daraus `TurnContext`
- fast alle mittleren und spaeten Schichten lesen danach primaer den
  `TurnContext`

Damit existiert eine echte Persistenzkante,
aber die Laufarbeit operiert danach zu stark auf einer turnweiten
Zwischenwelt.


### 2. `TurnContext` ist heute Mischobjekt statt klarer Arbeitskontext

Im aktuellen `TurnContext` liegen gleichzeitig:

- persistierte Wahrheit:
  `medical_case`,
  `dialogue_state`,
  `concern_state`
- turn-lokale Signale:
  `process_state_signals`,
  `person_reference_present`,
  `concern_relation`,
  `latest_turn_role`
- spaete Assessments:
  `assessment_readiness`,
  `gate_decision`,
  `response_state`,
  `response_strategy`
- Ausgabe:
  `response_mode`,
  `response_text`,
  `recommendation_result`
- Observability:
  `trace_notes`,
  Safety-Stufen

Das ist die eigentliche Driftquelle.
Nicht weil ein Context generell falsch waere,
sondern weil zu viele Wahrheitsarten denselben Traeger teilen.


### 3. Die Orchestrierung ist bereits sichtbar und sollte erhalten bleiben

`DialogueManager.run_turn()` ist aktuell eine der staerksten Stellen im
System:

- Entry
- optional Extraction
- Truth-Write
- Dialogue-Fortschreibung
- Readiness / Next Step
- Response
- Confirmation

Der Refactor sollte deshalb nicht die Orchestrierung verstecken,
sondern die Vertraege der einzelnen Stufen verkleinern.


### 4. Die spaete Steuerung ist verbessert, aber noch nicht singulaer

Die eigentliche Handlungsfreigabe steckt heute fachlich in:

- `RecommendationGateDecision.allowed_next_step`

Parallel dazu laufen aber weiter mit:

- `TurnContext.allowed_next_step`
- `TurnContext.active_allowed_next_step`
- `gate_status`
- Teile von `response_state`
- Legacy-Hooks in `DialogueState`
  wie `recommendation_ready` und `pending_dialogue_transition`

Die Lage ist also besser als frueher,
aber noch nicht ruhig genug,
um spaetere Response- oder Concern-Schnitte wirklich lokal zu halten.


### 5. `ConcernState` ist derzeit eher Sichtobjekt als primaeres Zentrum

Der aktuelle Service zeigt sehr klar:

- `active_concern_id` wird aus `medical_case.primary_problem_id` gespiegelt
- `summary` wird aus `medical_case.current_case_frame_label()` gelesen
- `phase` wird aus Follow-up-, Closing- und Next-Step-Lage gesetzt
- `information_sufficiency` wird aus `Readiness` abgeleitet

Das spricht nicht gegen `ConcernState`,
aber gegen einen vorschnellen Ausbau.

Vor jedem groesseren Concern-Schritt muss erst beantwortet werden:
Welche Concern-Daten waeren heute ueberhaupt primaer genug,
um eine eigene persistente Heimat zu rechtfertigen?


### 6. Die Write-Kante ist verbessert, aber noch immer bridge-zentriert

Positiv:

- `case_extension_status` existiert
- `CaseMerger` liest ihn bereits als kleinen Write-Guard

Aber operativ bleibt die Schwelle weiter:

- `ExtractionPayload.case_update_bridge is not None`

Das heisst:
die Schreibentscheidung ist expliziter als frueher,
aber noch nicht als eigener kleiner Vertrag sichtbar genug.


### 7. Historie wird sehr breit durchgereicht

`conversation_messages` laeuft heute mindestens in:

- `EntryManager`
- `ExtractionManager`
- `RecommendationTransitionService`
- `ResponseGenerationService`
- `LLMResponseGenerationService`

Das kann sinnvoll sein,
ist aber aktuell ein Warnsignal:
die Historie wird als universeller Hilfskontext benutzt,
anstatt pro Schicht scharf zu definieren,
welcher Ausschnitt wirklich gebraucht wird.


## Strukturelles Hauptproblem

Die Schwaeche des Systems ist nicht primaer,
dass gar nichts persistent waere.

Die eigentliche Schwaeche ist:

- persistente Wahrheit ist vorhanden,
  wird aber pro Turn breit neu in ein zentrales Mischobjekt gezogen
- nachgelagerte Schichten lesen danach lieber die Turn-Welt
  als gezielt ihre Heimataggregate
- dadurch entstehen Spiegel,
  Legacy-Hooks,
  breite Kontexte
  und groessere Refactor-Radien

Kurz:

- Persistenz existiert
- aber ihre Nutzung ist noch zu turn-zentriert


## Ziel fuer den naechsten Refactor

Nicht:

- alles neu schneiden
- Concern neu erfinden
- oder gleich neue Antwortintelligenz aufbauen

Sondern:

1. Runtime-Wahrheit wieder klarer an ihren Heimatorten lesen
2. Turn-Vertraege auf Arbeitsdaten, Assessments und Ausgabe begrenzen
3. spaete Handlungsfreigabe singularisieren
4. erst danach Concern und Truth-Write weiter schaerfen


## Leitfragen vor jedem Codeschnitt

### Wahrheitsfrage

- Ist dieses Feld persistente Wahrheit,
  turn-lokaler Arbeitszustand,
  abgeleitetes Assessment
  oder reine Ausgabe?

### Heimatfrage

- Wo waere die fachlich richtige Heimat fuer diese Information,
  wenn es keinen `TurnContext` gaebe?

### Lesefrage

- Liest die betroffene Schicht heute den kleinsten noetigen Vertrag,
  oder liest sie nur bequem den grossen Turn-Schatten?

### Spiegel-Frage

- Ist dieses Feld aktive Wahrheit,
  nur Sichtbarkeit,
  Legacy-Kompatibilitaet
  oder verdeckte Zweitwahrheit?

### Refactor-Frage

- Reduziert der Schnitt wirklich Verantwortung,
  oder verschiebt er nur dieselbe Verantwortung hinter einen neuen Wrapper?


## Empfohlene Refactor-Reihenfolge

### Phase 1: Vertragsinventur statt Umbau

Ziel:

- vor dem ersten tieferen Codeeingriff alle Turn-Daten nach Wahrheitsarten
  markieren

Konkrete Arbeit:

- `TurnInput`, `TurnContext`, `TurnResult` komplett klassifizieren in:
  `persisted_truth`,
  `turn_work`,
  `derived_assessment`,
  `output`,
  `observability`
- fuer `DialogueManager.run_turn()` pro Stufe notieren:
  was kommt hinein,
  was darf hinaus,
  was wird nur aus Bequemlichkeit im Context abgelegt
- fuer `conversation_messages` dieselbe Inventur machen:
  wer braucht wirklich Historie,
  wer nur den letzten User-Turn,
  wer nur kleine extrahierte Historien-Signale

Warum zuerst:

- ohne diese Karte wird fast jeder Folgeschritt wieder zu mechanischem
  Feldverschieben

Erfolgskriterium:

- eine explizite Feldliste,
  aus der sichtbar wird,
  welche Teile des Turn-Kontexts zuerst schrumpfbar sind


### Phase 2: Aktive Next-Step-Wahrheit singularisieren

Ziel:

- genau eine aktive Handlungsfreigabe nach der Verarbeitungsphase

Konkrete Arbeit:

- `RecommendationGateDecision.allowed_next_step` als einzige aktive Wahrheit
  festziehen
- `TurnContext.allowed_next_step` explizit als reine Altlast markieren
  und schrittweise aus aktiven Lesepfaden entfernen
- pruefen,
  ob `active_allowed_next_step` nur temporaere Migrationshilfe bleibt
  oder direkt wieder verschwinden kann
- `gate_status` auf reine Erklaerung / Trace zurueckschneiden,
  falls keine eigene fachliche Rolle uebrig bleibt
- `ResponseManager`,
  `LLMResponseGenerationService`
  und sichtbare Response-Texte nur noch ueber diese eine Handlungswahrheit
  lesen lassen

Warum dieser Schnitt frueh:

- er ist relativ lokal
- er entlastet spaetere Response- und Concern-Schnitte
- und er verhindert,
  dass wieder weitere Policy auf Mehrfachspuren aufbaut

Erfolgskriterium:

- Antwortpfad und Prompt lesen denselben einen erlaubten naechsten Zug


### Phase 3: Turn-Kontext in kleine Stage-Ergebnisse zerlegen

Ziel:

- `TurnContext` bleibt Orchestrierungsarbeitsraum,
  aber nicht mehr Sammelbehaelter fuer alles

Konkrete Arbeit:

- kleine Stufenergebnisse staerken oder einfuehren,
  wo heute breit in `context` geschrieben wird
- besonders trennen:
  `case truth`,
  `process update`,
  `readiness/next-step`,
  `response output`
- pruefen,
  welche Felder direkt in `TurnResult` oder in reine Trace-Ausgabe gehoeren
  statt dauerhaft im Arbeitskontext zu liegen
- `pending_followup` nicht parallel in
  `DialogueState`
  und als turnweites Spiegel-Feld weitertragen,
  ausser wo es als explizite Migrationshilfe kurzfristig noetig ist

Wichtige Vorsicht:

- nicht einen noch groesseren Meta-Vertrag bauen
- lieber vorhandene kleine Update-Typen
  wie `ProcessStateUpdate`,
  `ReadinessStateUpdate`,
  `ResponsePlan`
  konsequent ernst nehmen

Erfolgskriterium:

- mehrere heutige `TurnContext`-Felder werden nur noch in ihrer Heimat oder
  in einem klaren Stage-Result gefuehrt


### Phase 4: Historienzugriffe verkleinern

Ziel:

- weniger globale `conversation_messages`-Durchreichung

Konkrete Arbeit:

- pro Schicht explizit entscheiden:
  kompletter Verlauf,
  letzte N Nachrichten,
  nur letzter User-Turn,
  oder gar keine Historie
- wenn moeglich kleine vorbereitete Historien-Signale statt voller Liste an
  Entry,
  Extraction
  oder Response weiterreichen
- `TurnInput` mittelfristig von
  `conversation_messages`
  auf kleinere spezialisierte Inputs umstellen,
  ohne die Boundary zu brechen

Warum nicht zuerst:

- die groessten fachlichen Doppelwahrheiten sitzen nicht in der Historie
  selbst,
  sondern in Turn- und Next-Step-Vertraegen

Erfolgskriterium:

- weniger Stufen haengen von derselben globalen Nachrichtenliste ab


### Phase 5: Concern nur nach Heimat pruefen

Ziel:

- entscheiden,
  ob `ConcernState` schrumpft,
  bleibt
  oder spaeter echte primaere Semantik bekommt

Konkrete Arbeit:

- alle Concern-Felder auflisten und markieren:
  gespiegelt,
  abgeleitet,
  primaer,
  unklar
- nur dann neue Concern-Verantwortung anfassen,
  wenn nach Phase 2 und 3 noch ein echter semantischer Rest bleibt,
  der weder in
  `MedicalCase`
  noch in
  `DialogueState`
  noch in der Next-Step-Policy sauber aufhebbar ist

Vermutung heute:

- `ConcernState` sollte eher kleiner und klarer werden,
  nicht groesser

Erfolgskriterium:

- klare Antwort,
  ob Concern eigene persistente Wahrheit traegt
  oder vorerst bewusst nur abgeleitete Kontinuitaetssicht bleibt


### Phase 6: Truth-Write-Vertrag expliziter machen

Ziel:

- Schreiben in den Case nicht mehr primaer ueber
  `bridge vorhanden / nicht vorhanden`
  verstehen

Konkrete Arbeit:

- zwischen Extraction und Merge einen kleinen expliziteren Write-Vertrag
  sichtbar machen:
  nicht nur Payload,
  sondern auch Schreibintention und Relevanz
- `case_update_bridge` nicht sofort entfernen,
  aber weiter auf operative Minimalrolle zurueckschneiden
- pruefen,
  ob `CaseStateManager.apply_extraction()` spaeter ein noch schmaleres
  Update-Objekt statt des breiteren Extraction-Payloads lesen sollte

Warum spaeter:

- vorher sollten Turn- und Policy-Wahrheiten schon ruhiger sein,
  sonst wird die Write-Kante wieder mit fremder Verantwortung belastet

Erfolgskriterium:

- die Frage
  "wird Case-Wahrheit fortgeschrieben?"
  ist expliziter als
  "war irgendwo noch eine Bridge vorhanden?"


## Kleinste Schnitte mit dem besten Verhaeltnis aus Effekt zu Risiko

Wenn wir sehr konservativ vorgehen wollen,
haben diese Schnitte aktuell das beste Chancenprofil:

1. `allowed_next_step` als einzige aktive spaete Handlungswahrheit wirklich
   durchziehen
2. `gate_status` und weitere spaete Spiegel als Observability markieren oder
   abbauen
3. `TurnContext` nur inventarisieren und dann zuerst offensichtliche
   Output-/Mirror-Felder herausziehen
4. `conversation_messages` pro Schicht verkleinern,
   aber erst nach der Vertragsinventur
5. `ConcernState` erst nach Entspannung der Turn-Mitte wieder anfassen


## Betroffene Hauptstellen im aktuellen Code

Die staerksten Refactor-Hotspots sind nach heutigem Stand:

- `server/careena3.py`
  als Boundary mit Session-Lade-/Schreibkante und Fallback-Text
- `application/managers/dialogue_manager.py`
  als zentrale Orchestrierung und aktueller Verdichtungsort des Turn-Kontexts
- `models/turn/input.py`
  wegen breitem Persistenz- und Historientransport
- `models/turn/context.py`
  wegen Mischverantwortung
- `models/turn/result.py`
  wegen noch duennem, aber potenziell sinnvollerem Ausgabeziel
- `application/services/recommendation_state_service.py`
  wegen aktiver Next-Step-Policy plus Legacy-Hooks
- `application/managers/response_manager.py`
  wegen spaeter Policy-Ableitung auf mehreren Schichten
- `application/services/llm_response_generation_service.py`
  wegen breitem Lesen des Turn-Schattenmodells
- `application/services/concern_state_service.py`
  wegen sichtbar stark gespiegelt-abgeleiteter Concern-Lage
- `application/managers/case_state_manager.py`
  als spaetere Write-Kante


## Was wir ausdruecklich vermeiden sollten

- keinen neuen Super-Context bauen
- keine neue Wrapper-Schicht,
  die dieselbe Doppelwahrheit nur besser tarnt
- `ConcernState` nicht aufblasen,
  nur weil andere Heimatvertraege noch unscharf sind
- Response nicht weiter verfeinern,
  solange die aktive Handlungswahrheit noch mehrfach laeuft
- Historie nicht pauschal ueberall durchreichen,
  wenn eigentlich nur kleine Signale gebraucht werden
- den sichtbaren `DialogueManager` nicht wieder in unsichtbare Magie
  zerlegen


## Empfehlung fuer den ersten echten Umsetzungsschritt

Der erste echte Umsetzungsschritt sollte noch kein grosser Umbau sein,
sondern ein sehr kleiner Vertrags-Refactor in zwei Zuegen:

1. vollstaendige Feldinventur fuer
   `TurnInput`,
   `TurnContext`,
   `TurnResult`
   und die spaete Policy-/Response-Felder
2. direkt danach der kleine Code-Schnitt,
   der aktive Next-Step-Wahrheit wirklich singularisiert

Warum genau so:

- das liefert sofort mehr Architekturwahrheit
- reduziert das Risiko planloser Spiegelverschiebung
- und schafft die sauberste Basis fuer alle spaeteren lokalen Schnitte


## Abschlussurteil

Das System muss sehr wahrscheinlich nicht neu erfunden werden.

Die meiste brauchbare Struktur ist schon da:

- persistierte Aggregate
- sichtbare Orchestrierung
- kleine Stage-Vertraege
- klarere Case-Wahrheit
- explizitere Next-Step- und Response-Fragen

Der naechste Gewinn liegt deshalb nicht im grossen Neuaufbau,
sondern in einer disziplinierten Migration:

- weniger Turn-Schattenwelt
- weniger Zweitwahrheit
- klarere Heimataggregate
- kleinere spaete Vertraege

Wenn dieser Schritt sauber gelingt,
werden Concern,
Truth-Write
und spaetere Antwortarbeit danach deutlich lokaler und mit kleinerem
Code-Radius weiterbearbeitbar.
