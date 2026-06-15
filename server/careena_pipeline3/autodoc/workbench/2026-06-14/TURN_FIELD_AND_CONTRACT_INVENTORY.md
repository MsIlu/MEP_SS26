# Turn Field And Contract Inventory

Stand: 2026-06-14
Status: explizite Feld- und Vertragsinventur gegen den aktuellen
`careena_pipeline3`-Code


## Zweck

Diese Datei zieht die aktuell nur implizit im Code verteilte Vertragslage
kompakt zusammen.

Sie soll sichtbar machen:

- welche Felder zu welcher Wahrheitsart gehoeren
- welche Stage-Vertraege der aktive Laufpfad wirklich benutzt
- wo noch Mischrollen oder Zweitwahrheiten sitzen
- und welche naechsten Schrumpfstellen sich mit kleinem Radius anbieten


## Feldklassen

Fuer diese Inventur gelten fuenf Feldklassen:

- `persisted_truth`
  - langlebige Runtime-Wahrheit,
    die ueber Session-Grenzen erhalten bleibt
- `turn_work`
  - turn-lokale Arbeits-,
    Routing-
    oder Orchestrierungssignale
- `derived_assessment`
  - abgeleitete Bewertungen oder Policy-Entscheidungen
- `output`
  - Boundary-Ausgabe oder spaete Antwortprodukte
- `observability`
  - Trace,
    Debug-
    und Sichtbarkeitssignale ohne primaere fachliche Wahrheit


## Feldinventur

### `TurnInput`

Rolle:
- Boundary-Eingabevertrag fuer genau einen Turn

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `message` | `turn_work` | neueste Nutzernachricht | passend |
| `session_id` | `turn_work` | Boundary-/Session-Referenz | passend |
| `persisted_case` | `persisted_truth` | kanonische Case-Wahrheit beim Turn-Eintritt | passend |
| `persisted_dialogue_state` | `persisted_truth` | kanonische Dialogprozess-Wahrheit beim Turn-Eintritt | passend |
| `persisted_concern_state` | `persisted_truth` | persistierte concern-nahe Kontinuitaetssicht | passend, aber spaeter auf Heimat pruefen |
| `entry_history_messages` | `turn_work` | kleiner Historienausschnitt fuer Call 1 / Entry | sinnvoll, aber noch Listenvertrag |
| `extraction_history_messages` | `turn_work` | kleiner Historienausschnitt fuer Extraction | sinnvoll, aber noch Listenvertrag |
| `transition_history_messages` | `turn_work` | kleiner Historienausschnitt fuer Choice-Resolver | sinnvoll, aber noch Listenvertrag |
| `response_history_messages` | `turn_work` | kleiner Historienausschnitt fuer freie spaete Antwort | sinnvoll, aber noch Listenvertrag |

Beobachtung:
- `TurnInput` ist heute deutlich sauberer als frueher,
  aber die History-Slices sind weiterhin breite Nachrichtenlisten
  statt kleinerer spezialisierter Signale.


### `TurnContext`

Rolle:
- interner turn-lokaler Orchestrierungsarbeitsraum

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `medical_case` | `persisted_truth` | gespiegelt eingezogene Case-Wahrheit | legitim, aber Teil der Turn-Schattenwelt |
| `dialogue_state` | `persisted_truth` | gespiegelt eingezogene Dialogprozess-Wahrheit | legitim, aber Teil der Turn-Schattenwelt |
| `concern_state` | `persisted_truth` | gespiegelt eingezogene concern-nahe Sicht | legitim, Heimat spaeter weiter pruefen |
| `active_modules` | `turn_work` | aktive Routing-/Modulsignale | passend |
| `process_state_signals` | `turn_work` | kleine Folge-Signale nach Case-Fortschreibung | passend |
| `case_update_dialogue_consequences` | `turn_work` | kleine turn-lokale Prozessfolgen aus dem Write-Pfad | passend |
| `person_reference_present` | `turn_work` | Call-1-Signal zur Personenlage | passend |
| `multi_person_context` | `turn_work` | Call-1-Signal fuer Mehrpersonenlage | passend |
| `subject_relation_unclear` | `turn_work` | Call-1-Signal fuer unklare Subjektlage | passend |
| `concern_relation` | `turn_work` | turn-lokale Einordnung des neuesten Beitrags zum Anliegen | passend |
| `latest_turn_role` | `turn_work` | turn-lokale Rollenmarkierung des letzten Beitrags | passend |
| `assessment_readiness` | `derived_assessment` | Readiness-Bewertung nach Prozessfortschreibung | passend |
| `gate_decision` | `derived_assessment` | aktive post-processing-Handlungsfreigabe | passend |
| `raw_safety` | `observability` | fruehes Safety-Ergebnis fuer den Turn | passend |
| `extraction_safety` | `observability` | Safety-Ergebnis nach Extraction | passend |
| `case_safety` | `observability` | Safety-Ergebnis nach Case-Fortschreibung | passend |
| `trace_notes` | `observability` | laufende technische Sichtbarkeit | passend |

Beobachtung:
- `TurnContext` ist schon stark geschrumpft,
  aber weiterhin ein Mischtraeger aus
  `persisted_truth`,
  `turn_work`,
  `derived_assessment`
  und
  `observability`.
- Das ist heute bewusst kontrollierter als frueher,
  bleibt aber die zentrale Reststelle fuer spaetere weitere Verkleinerung.


### `TurnResult`

Rolle:
- Boundary-Ausgabevertrag fuer einen abgeschlossenen Turn

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `medical_case` | `persisted_truth` | zurueckzuschreibende Case-Wahrheit | passend |
| `dialogue_state` | `persisted_truth` | zurueckzuschreibende Dialogprozess-Wahrheit | passend |
| `concern_state` | `persisted_truth` | zurueckzuschreibende concern-nahe Sicht | passend |
| `response_mode` | `output` | sichtbare spaete Antwortbahn | passend |
| `response_text` | `output` | finaler Antworttext | passend |
| `recommendation_result` | `output` | optionaler spaeter Recommendation-Output | passend |
| `trace_notes` | `observability` | Boundary-Trace | passend |

Beobachtung:
- `TurnResult` ist aktuell die ruhigste der drei Turn-Hauptstrukturen.


### `DialogueState`

Rolle:
- persistierter Dialogprozessvertrag,
  nicht medizinische Primärwahrheit

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `conversation_id` | `persisted_truth` | Identitaet des laufenden Dialogprozesses | passend |
| `active_case_id` | `persisted_truth` | Prozessanker zum aktiven Fall | passend |
| `current_topic_status` | `persisted_truth` | grobe Prozesssicht auf Themenlage | passend |
| `active_modules` | `persisted_truth` | persistierte Prozess-/Modulsicht | plausibel, aber auf Doppelverantwortung pruefen |
| `open_requirements` | `persisted_truth` | noch offene Pflicht-/Rueckfrageanforderungen | passend |
| `resolved_requirements` | `persisted_truth` | bereits geklaerte Anforderungen | passend |
| `pending_followup` | `persisted_truth` | aktuelle kanonische Rueckfragewahrheit | passend |
| `pending_choice_prompt` | `persisted_truth` | offener spaeter System-Choice-Prompt | passend |
| `recommendation_requested` | `persisted_truth` | Nutzerintention zur Recommendation | passend als Prozesswahrheit |
| `recommended_modules` | `persisted_truth` | spaeterer Recommendation-/Planner-Rest | aktuell schwach begruendet |
| `focus_observation_id` | `persisted_truth` | observation-spezifischer Prozessfokus | plausibel, weiter Heimat pruefen |
| `focus_label` | `persisted_truth` | sichtbarer Label-Spiegel zum Fokus | potentieller Spiegelkandidat |

Beobachtung:
- `DialogueState` ist nach dem Legacy-Closing-Schnitt deutlich ruhiger.
- Die groessten offenen Fragen sitzen hier nicht mehr bei Recommendation,
  sondern eher bei
  `recommended_modules`,
  `active_modules`
  und
  `focus_label`
  als moeglichen Sicht-/Spiegelresten.


### `ResponsePlan`

Rolle:
- kleiner spaeter Policy-/Output-Vertrag aus `ResponseManager`

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `response_mode` | `derived_assessment` | gewaehlte sichtbare Antwortbahn | passend |
| `response_state` | `derived_assessment` | kleiner spaeter Reaktionskern | passend |
| `response_strategy` | `derived_assessment` | Formulierungs-/Antwortstrategie | passend |
| `response_text` | `output` | finaler Antworttext | passend |
| `recommendation_result` | `output` | optionales spaetes Recommendation-Payload | passend |
| `trace_notes` | `observability` | spaete technische Sichtbarkeit | passend |

Beobachtung:
- `ResponsePlan` ist nach Entfernung des alten Transition-Payloads kleiner,
  bleibt aber noch ein Mischvertrag aus Policy und Output.
- Das ist aktuell akzeptabel,
  aber spaeter weiter pruefbar.


### `ProcessStateUpdate`

Rolle:
- kleiner Stage-Vertrag fuer Dialogprozess-Fortschreibung nach Case-Update

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `dialogue_state` | `persisted_truth` | fortgeschriebener Dialogprozess | passend |
| `pending_followup` | `persisted_truth` | Kompatibilitaets-/Explizitheitsfeld fuer aktuelle Rueckfrage | tendenziell redundant zu `dialogue_state.pending_followup` |
| `process_state_signals` | `turn_work` | kleine turn-lokale Folge-Signale | passend |

Beobachtung:
- `pending_followup` ist hier wahrscheinlich der naechste offensichtliche
  Spiegelkandidat,
  weil die kanonische Wahrheit schon im `dialogue_state` lebt.


### `ReadinessStateUpdate`

Rolle:
- kleiner Stage-Vertrag fuer Readiness und aktive Next-Step-Policy

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `dialogue_state` | `persisted_truth` | evtl. leicht fortgeschriebener Dialogprozess | passend |
| `assessment_readiness` | `derived_assessment` | explizite Readiness-Bewertung | passend |
| `pending_followup` | `persisted_truth` | Kompatibilitaetsfeld | tendenziell redundant |
| `gate_decision` | `derived_assessment` | aktive post-processing-Handlungsfreigabe | passend |

Beobachtung:
- Auch hier ist `pending_followup` eher Migrations-/Kompatibilitaetsrest
  als eigene notwendige Wahrheitsflaeche.


### `RecommendationGateDecision`

Rolle:
- kleine aktive post-processing-Handlungsfreigabe

Feldmatrix:

| Feld | Klasse | Aktuelle Rolle | Urteil |
| --- | --- | --- | --- |
| `allowed_next_step` | `derived_assessment` | eine aktive naechste erlaubte Handlung | zentral und passend |
| `gate_status` | `observability` | benannte Einordnungs-/Erklaerungsschicht | noetzlich, aber keine aktive Wahrheit |
| `active_prompt_kind` | `observability` | sichtbarer Hinweis auf offenen Prompt-Knoten | noetzlich, aber nur Sichtbarkeit |
| `reason_tags` | `observability` | technische/fachliche Begruendungshinweise | passend |

Beobachtung:
- Hier sitzt die heute klare aktive Policy-Wahrheit.
- `gate_status` ist nicht falsch,
  aber eher Erklaerung als zweite Handlungsachse.


## Stage-Vertragsinventur fuer `DialogueManager.run_turn()`

### Stage 0: Boundary-In

Input:
- `TurnInput`

Aktive Wahrheiten:
- `persisted_case`
- `persisted_dialogue_state`
- `persisted_concern_state`

In den Turn gespiegelt:
- `medical_case`
- `dialogue_state`
- `concern_state`

Urteil:
- sauberer Boundary-Eintritt,
  aber ab hier beginnt die Turn-Schattenwelt


### Stage 1: Raw Safety

Input:
- `TurnInput.message`

Output:
- `raw_safety`
- `trace_notes`

Urteil:
- reine Observability-/Safety-Stufe,
  lokal sauber


### Stage 2: Entry

Input:
- `TurnInput.message`
- `entry_history_messages`
- kleiner Kontext aus
  `dialogue_state`,
  `medical_case`
  und
  `pending_choice_prompt`

Output:
- `EntryDecision`
- kleine turn-lokale Signale im `TurnContext`
- moegliches Clear von `dialogue_state.pending_choice_prompt`
- moegliches Setzen von `dialogue_state.recommendation_requested`

Urteil:
- heute deutlich expliziter als frueher
- weiterhin ein guter Kandidat fuer spaetere Historienverkleinerung


### Stage 3: Extraction

Input:
- `extraction_history_messages`
- `EntryDecision`
- kanonische Case-/Dialogue-Wahrheit plus kleine Signalsicht

Output:
- `ExtractionPayload`
- `extraction_safety`

Urteil:
- operativ brauchbar,
  aber die Write-Relevanz wird spaeter noch expliziter gebraucht


### Stage 4: Truth Write

Input:
- `ExtractionPayload`
- `medical_case`

Output:
- fortgeschriebener `medical_case`
- `case_update_dialogue_consequences`
- Trace

Urteil:
- klare Stage,
  aber noch zu stark an
  `case_update_bridge`
  als operative Schwelle gekoppelt


### Stage 5: Dialogue Process Update

Input:
- `dialogue_state`
- `medical_case`
- kleine turn-lokale Signalsicht

Output:
- `ProcessStateUpdate`

Urteil:
- guter kleiner Zwischenvertrag,
  aber mit
  `pending_followup`
  noch Restspiegel


### Stage 6: Readiness / Next Step

Input:
- `dialogue_state`
- `medical_case`
- `concern_state`
- Entry-Signale

Output:
- `ReadinessStateUpdate`
- aktive `gate_decision`

Urteil:
- heute die ruhigste Policy-Kante
- wichtigste aktive Wahrheit:
  `gate_decision.allowed_next_step`


### Stage 7: Response

Input:
- `gate_decision`
- `assessment_readiness`
- `dialogue_state`
- `response_history_messages`
- Safety-Signale

Output:
- `ResponsePlan`
- moegliches Setzen von `dialogue_state.pending_choice_prompt`

Urteil:
- nach dem Choice-Prompt-Schnitt deutlich sauberer
- `ResponsePlan` bleibt kleiner Mischvertrag,
  aber kontrolliert


### Stage 8: Boundary-Out

Input:
- `medical_case`
- `dialogue_state`
- `concern_state`
- `response_mode`
- `response_text`

Output:
- `TurnResult`

Urteil:
- aktuell sauberste Boundary des Laufpfads


## Historieninventur

### Aktuelle Slices

- `entry_history_messages`
  - gelesen von:
    Call 1 / Intent Gateway
- `extraction_history_messages`
  - gelesen von:
    Extraction-/Call-2-Pfad
- `transition_history_messages`
  - gelesen von:
    Recommendation-Choice-Resolver
- `response_history_messages`
  - gelesen von:
    spaete freie Antwortgenerierung

### Urteil

- die Historie ist nicht mehr global blind durchgeschoben
- aber jede Slice ist weiterhin eine Nachrichtenliste,
  keine kleinere semantische Vorstruktur
- der naechste sinnvolle Schrumpfschritt liegt hier nicht in neuer Logik,
  sondern in der Frage:
  welche Schicht braucht wirklich
  Verlauf,
  letzte Assistenzfrage,
  letzten User-Turn
  oder nur einen kleinen Label-/Prompt-Hinweis


## Aktuelle Spiegel- und Restkandidaten

Die derzeit sichtbarsten Schrumpf- oder Klaerungskandidaten sind:

- `ProcessStateUpdate.pending_followup`
  - wirkt wie Kompatibilitaets-/Spiegelrest neben
    `dialogue_state.pending_followup`
- `ReadinessStateUpdate.pending_followup`
  - gleicher Restcharakter
- `RecommendationGateDecision.gate_status`
  - noetzliche Erklaerung,
    aber keine aktive Wahrheit
- `RecommendationGateDecision.active_prompt_kind`
  - reine Sichtbarkeit
- `DialogueState.focus_label`
  - moeglicher Sicht-/Textspiegel zu
    `focus_observation_id`
    bzw.
    Case-/Observation-Daten
- `DialogueState.recommended_modules`
  - aktuell fachlich noch schwach geerdet


## Haupturteil

Die Feldinventur bestaetigt den aktuellen Zwischenstand:

- die groessten aktiven Doppelwahrheiten sind bereits entfernt
- `TurnResult` und der spaete Recommendation-Abschluss sind deutlich
  beruhigt
- die groessten offenen Strukturreste sitzen jetzt nicht mehr an einem
  einzelnen kaputten Legacy-Hook,
  sondern in drei kleineren Restfeldern:
  Turn-Mischtraeger,
  Historienlisten
  und
  Write-Edge-Vertrag

Wenn wir von hier aus den naechsten kleinen sauberen Schritt schneiden wollen,
hat diese Reihenfolge das beste Chancenprofil:

1. `pending_followup`-Restspiegel in
   `ProcessStateUpdate` /
   `ReadinessStateUpdate`
   explizit pruefen und wenn moeglich entfernen
2. History-Slices pro Schicht auf den kleinsten echten Bedarf reduzieren
3. Write-Edge zwischen Extraction und Merge als eigenen kleinen
   Schreibintention-Vertrag expliziter machen
