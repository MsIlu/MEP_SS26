# Change Log

## Schreibgeschuetzt

- Name:
  - `workbench@freddy`

- Zweck:
  - Kurz halten
  - relevante Aenderungen fortlaufend festhalten
  - den Anlass und die beabsichtigte Wirkung sichtbar machen
  - keine vollstaendige Git-Historie ersetzen
  - zentrale laufende Pflegedatei fuer Codex sein

- Kategorien:
  - `bugfix`
  - `refactor`
  - `rework`
  - `feature`
  - `doc`
  - `cleanup`
  - `config`
  - `test`
  - `chore`

- Bereichslabel:
  - `frontend`
    - verwenden bei `Dart`
  - `backend`
    - verwenden bei `Python`

Number muss jedes mal um eins erhoeht werden und datum und uhrzeit falls das einfach geht waere schoen, sonst auslassen.


- Format:
=== CHANGE NUMBER: [number] Datum: [DD-MM-YY] [Uhrzeit] ===
  - Kategorie:
    - genau eine Kategorie aus der Liste oben
  - Bereich:
    - `frontend` bei `Dart`
    - `backend` bei `Python`
  - Aenderung:
    - was wurde konkret geaendert
  - Warum:
    - warum wurde diese Aenderung gemacht
  - Wirkung:
    - was aendert sich dadurch praktisch
  - Betroffene Dateien/Bereiche:
    - welche Dateien, Ordner oder Module waren direkt betroffen
  - Naechster Punkt:
    - leer lassen oder den naechsten sinnvollen Schritt knapp benennen
- DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 96 Datum: 12-06-26 01:33 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - fuer V4 Block 1 einen kleinen expliziten hinteren Reaktionskern
      `ResponseState` eingefuehrt und ihn in
      `ResponsePlan`,
      `TurnContext`,
      `ResponseManager`
      und die Response-Anwendung im `DialogueManager` verdrahtet
    - `ResponseManager` so umgeschnitten,
      dass er die spaete Policy jetzt zuerst auf getrennten Achsen fuer
      Safety-Override,
      Entry-Hint,
      medizinische Lage,
      dialogische Transition
      und Recommendation-Lage liest
      und daraus erst anschliessend den sichtbaren `response_mode` ableitet
    - die bestehende Block-6-/Orchestrierungs-Testkante auf den neuen
      Vertragskern erweitert
      und den V4-Plan unter Block 1 um einen ersten Stand zum begonnenen
      Vertragsschnitt fortgeschrieben
  - Warum:
    - V4 soll den hinteren Response-/Transition-Bereich nicht weiter
      hauptsaechlich ueber `response_mode` plus verstreute Boolsignale tragen
    - der erste praktische Hebel in Block 1 ist deshalb ein kleinerer
      expliziter spaeter Reaktionsvertrag,
      auf dem spaetere Transition- und Abschlussknoten robuster aufbauen
      koennen
  - Wirkung:
    - der hintere Policy-Bereich ist jetzt expliziter lesbar,
      ohne den `DialogueManager` wieder mit mehr Sonderpolitik zu beladen
    - `response_mode` bleibt als sichtbarer Pfad erhalten,
      ist aber nicht mehr die einzige semantische Traegerflaeche dieser
      spaeten Turn-Entscheidung
    - Verifikation:
      die relevanten Tests
      `server/tests/test_block6_response_transition.py`
      und
      `server/tests/test_dialogue_manager.py`
      laufen ueber die gebuendelte Runtime mit `unittest` erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/response_state.py`
    - `server/careena_pipeline3/models/turn/response_plan.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/tests/test_block6_response_transition.py`
    - `server/tests/test_dialogue_manager.py`
    - `server/careena_pipeline3/autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den Abschlussknoten um `recommendation_ready_check` auf dem neuen
      Reaktionskern weiter schaerfen,
      besonders an der Kante
      `awaiting_reply`
      vs.
      `request_recommendation`
      vs.
      `report_more_information`
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 118 Datum: 14-06-26 09:52 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Turn-Vertrag an der Runtime-Mitte und an den Boundaries sichtbar
      neu geschnitten:
      `TurnInput` traegt jetzt persistierte Aggregate explizit als
      `persisted_*`
      sowie getrennte purpose-spezifische History-Slices fuer
      Entry,
      Extraction,
      Transition
      und Response
    - `TurnContext` auf internen Arbeitszustand zurueckgeschnitten:
      die aktiven Spiegel
      `allowed_next_step`,
      `pending_followup`,
      `response_mode`,
      `response_state`,
      `response_strategy`,
      `response_text`
      und
      `recommendation_result`
      wurden aus dem aktiven Turn-Pfad entfernt
    - die aktive spaete Handlungswahrheit auf
      `gate_decision.allowed_next_step`
      singularisiert und alle aktiven Leser in
      `ResponseManager`
      und der freien Response-Generierung darauf umgezogen
    - `TurnResult` zum echten Boundary-Vertrag ausgebaut:
      er traegt jetzt direkt
      `medical_case`,
      `dialogue_state`,
      `concern_state`,
      `response_text`,
      `recommendation_result`
      und
      `trace_notes`
    - HTTP- und Simulations-Boundary auf diesen neuen
      `TurnResult`-Vertrag umgestellt und den alten
      Response-Fallback in
      `careena3.py`
      entfernt
    - die kleineren History-Vertraege bis in
      Intent-Gateway-,
      Transition-,
      Extraction-
      und freie Response-Pfade nachgezogen,
      sodass keine globale
      `conversation_messages`
      -Liste mehr durch den aktiven Turn-Lauf geschoben werden muss
  - Warum:
    - die bisherige Hauptspannung lag nicht in fehlender Persistenz,
      sondern darin,
      dass persistierte Wahrheit pro Turn zu breit in eine
      Schattenwelt gezogen und dort mehrfach gespiegelt wurde
    - der Refactor sollte deshalb zuerst aktive Doppelwahrheit abbauen,
      Boundaries von
      `result.context`
      entkoppeln
      und den Turn wieder staerker als Ausfuehrungseinheit statt als
      Zweit-Wahrheitscontainer lesbar machen
  - Wirkung:
    - die aktive Steuerung nach der Verarbeitung laeuft jetzt nur noch ueber
      die eine Next-Step-Wahrheit im Gate-Decision-Vertrag
    - Persistenz- und Ausgabe-Boundaries lesen nicht mehr den internen
      `TurnContext`,
      sondern den expliziten `TurnResult`
    - die freie Response-Schicht liest ihren Antwortpfad und ihre
      Observationsdaten jetzt ohne response-nahe Spiegel im
      `TurnContext`
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m compileall C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\careena_pipeline3 C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\careena3.py`
      lief erfolgreich durch
    - Verifikation:
      ein manueller Smoke-Run ueber
      `DialogueManager()`
      plus
      `TurnInput.from_persisted_state(...)`
      lieferte erfolgreich einen vollstaendigen
      `TurnResult`
      mit
      `response_mode`,
      `response_text`
      und den drei Persistenzobjekten
    - Verifikation:
      ein manueller Smoke-Run ueber den
      `CareenaPipeline3Adapter`
      bestaetigte den neuen Boundary-Pfad mit
      `state={case, concern_state, dialogue_state}`
      und einer aus
      `TurnResult`
      gebauten Simulation-Response
  - Betroffene Dateien/Bereiche:
    - `server/careena3.py`
    - `server/careena_pipeline3/models/turn/`
    - `server/careena_pipeline3/application/managers/`
    - `server/careena_pipeline3/application/services/`
    - `server/careena_pipeline3/llm/`
    - `server/careena_pipeline3/simulation_runtime/adapters/careena_pipeline3.py`
  - Naechster Punkt:
    - als naechstes die neue kleinere History-Schnittstelle noch weiter
      gegen wirklich benoetigte Informationen haerten
      und danach entscheiden,
      ob
      `recommendation_ready`
      und
      `pending_dialogue_transition`
      bereits weiter auf reine Legacy-/Trace-Rolle zurueckgeschnitten werden
      koennen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 116 Datum: 13-06-26 17:35 ===
  - Kategorie:
    - `docs`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter
      `server/careena_pipeline3/autodoc/workbench/2026-06-13/`
      die neue Arbeitsgrundlage
      `NEXT_REFACTOR_GROUNDING_2026-06-13.md`
      angelegt
    - darin die Doku ab `2026-06-09`,
      die juengeren Architekturpapiere
      und den aktuellen Codezustand gegeneinander gelesen
      und auf einen belastbareren Planungsstand verdichtet
    - den naechsten groesseren Refactor dort bewusst nicht als glatten
      `V6`-Plan festgeschrieben,
      sondern erst die heute wahrscheinlicheren Kernprobleme
      markiert:
      Runtime-World-vs-Turn-World-Verkopplung,
      doppelte spaete Steuerwahrheiten,
      ungeklaerte Heimat von
      `ConcernState`,
      noch transitorische Truth-Write-Kante
      und die Restspannung zwischen Fallrahmen und Observation-Cursor
  - Warum:
    - die bestehende Arbeitsdoku ist historisch wertvoll,
      aber nicht mehr durchgehend aktuell oder gleich gewichtet;
      fuer den naechsten groesseren Refactor brauchte es deshalb zuerst eine
      saubere Rekonstruktion der belastbaren Linien gegen den echten
      Codezustand
    - damit wird verhindert,
      dass der naechste Plan wieder zu stark aus lokalen Restproblemen
      oder aus zu glatter Alt-Dokumentation abgeleitet wird
  - Wirkung:
    - es gibt jetzt eine explizite Planungsbasis,
      die zwischen stabilen Architekturwahrheiten,
      Uebergangslogik
      und ueberholter Planrhetorik trennt
    - der wahrscheinlich sinnvollste naechste groessere Schnitt ist dort als
      Entkabelung von Runtime- und Turn-Welt plus Singularisierung der
      aktiven Next-Step-Wahrheit festgehalten,
      statt vorschnell einen weiteren lokalen Policy- oder Call-2-Ausbau zu
      erzwingen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-13/NEXT_REFACTOR_GROUNDING_2026-06-13.md`
  - Naechster Punkt:
    - als naechstes diese neue Grundlage bei Bedarf in einen konkreten
      Refactor-Plan oder in einen ersten expliziten Entkopplungsschnitt
      uebersetzen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 116 Datum: 13-06-26 13:49 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den bisherigen kleinen Themenanker semantisch vom symptomnahen
      `case_topic_label`
      auf einen expliziteren Fallrahmen
      `case_frame_label`
      umgezogen
      und den priorisierten Lesepfad im
      `MedicalCase`
      auf
      `current_case_frame_label()`
      umgestellt
    - den Requirement-/Readiness-Schnitt im
      `RequirementPolicy`
      und im
      `AssessmentReadinessEvaluator`
      von einer still fokussierten Einzel-Observation auf eine fallweite
      Blocking-Lesart umgebaut:
      offene Pflichtfelder koennen jetzt aus mehreren relevanten
      Observations desselben Falls sichtbar werden
    - gleichzeitig die observation-gezielte Rueckfragefuehrung erhalten und
      expliziter gemacht:
      `pending_followup`
      waehlt jetzt gezielt die Observation,
      bei der das konkrete Feld noch offen ist,
      statt blind am bisherigen Cursor zu haengen
    - die Text- und Prompt-Pfade getrennt nachgezogen:
      freier Response-Kontext traegt jetzt Fallrahmen und
      Follow-up-Fokus getrennt,
      statische Follow-up-Texte koennen observation-spezifisch auf das
      Zielobjekt zeigen
    - die lokale Testsuite auf den neuen Vertrag umgestellt und erweitert:
      Fallrahmen,
      globale Readiness,
      observation-spezifische Follow-up-Zielwahl
      und unmittelbarer Wechsel vom beantworteten Follow-up zur naechsten
      offenen Observation sind jetzt explizit abgesichert
  - Warum:
    - `primary_problem_id`
      und daran haengende Fokuspfade trugen bislang zu viel Last:
      Observation-Cursor,
      Fallsemantik
      und teils faktische Readiness-Lesart liefen ineinander
    - der Umbau sollte den Fall als Ganzes lesbar machen,
      ohne die gezielte Ansteuerbarkeit einzelner Observation-Felder zu
      verlieren
  - Wirkung:
    - der Fallrahmen ist jetzt begrifflich klarer von der Einzel-Observation
      getrennt
    - globale Readiness kann blockiert bleiben,
      auch wenn die aktuell fokussierte Observation bereits beantwortet ist,
      solange im selben Fall noch andere relevante Beobachtungen offene
      Pflichtfelder haben
    - observation-spezifische Rueckfragen bleiben moeglich und sind sogar
      praeziser ansteuerbar,
      weil das Zielobjekt expliziter mitgetragen wird
    - ein alter Testanker in
      `server/tests/test_dialogue_manager.py`
      ist jetzt bewusst ueberholt:
      nach beantwortetem
      `Husten`-
      Follow-up bleibt bei neuem offenem
      `Fieber`-
      Feld nicht mehr
      `pending_followup=None`,
      sondern es wird sofort auf die naechste offene Observation
      weitergezielt
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\careena_pipeline3\\tests\\test_case_frame_contract.py`
      lief erfolgreich durch
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\tests\\test_block6_response_transition.py`
      lief erfolgreich durch
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\tests\\test_dialogue_manager.py`
      zeigt jetzt genau einen erwartbaren alten Fail gegen die bisherige
      Einzelfokus-Annahme
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/case.py`
    - `server/careena_pipeline3/models/extraction/result.py`
    - `server/careena_pipeline3/models/turn/case_update_bridge.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
    - `server/careena_pipeline3/domain/case_update_applier.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/domain/requirement_policy.py`
    - `server/careena_pipeline3/application/services/readiness_evaluator.py`
    - `server/careena_pipeline3/application/services/concern_state_service.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena_pipeline3/application/services/llm_response_generation_service.py`
    - `server/careena_pipeline3/application/services/recommendation_result_builder.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/careena_pipeline3/simulation_runtime/adapters/careena_pipeline3.py`
    - `server/careena_pipeline3/tests/test_case_frame_contract.py`
  - Naechster Punkt:
    - als naechstes im realen Lauf pruefen,
      ob der neue Fallrahmen und die fallweite Readiness jetzt auch die
      Response-Kante stabiler machen,
      oder ob danach vor allem noch Prompt-/Response-Entscheidungen auf den
      getrennten Signalen haerter gezogen werden muessen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 117 Datum: 13-06-26 12:35 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die aktive `allowed_next_step`-Policy fachlich erweitert und den
      Recommendation-Abschlussknoten in diese Policy gezogen:
      zusaetzliche explizite Zuege fuer
      `stay_on_closing_check`,
      `allow_recommendation`
      und
      `return_to_medical`
    - `EntryManager` so nachgeschaerft,
      dass Recommendation-Transitionen jetzt sichtbar als
      `dialogue_transition_action`
      in den Turn-Vertrag laufen,
      inklusive frueher Kurzschluss fuer echte
      `request_recommendation`
      -Aufloesung
      und expliziter Rueckkehrkante bei
      `report_more_information`
    - `RecommendationStateService` faktisch zur
      Next-Step-Policy-Schicht nachgeschaerft:
      aus Readiness,
      Follow-up-Lage,
      aktivem Abschlussknoten
      und Entry-Transition-Signalen wird jetzt der kanonische naechste
      erlaubte Zug abgeleitet
    - `DialogueManager` zieht diese Policy wieder sichtbar in den Turn und
      cleared alte Pending-Transitionen,
      sobald der Entry-Vertrag sie explizit aufgeloest hat
    - `ResponseManager` und `ResponseTextBuilder` so umgestellt,
      dass
      `guide_next_step`,
      Recommendation
      und Rueckkehr in den medizinischen Pfad jetzt primaer aus
      `allowed_next_step`
      entstehen
      statt aus verstreuten Legacy-Hooks oder impliziten Mischungen
    - den LLM-Antwortprompt an dieser Stelle etwas gestrafft,
      damit die freie Antwortschicht nicht weiter das alte
      `recommendation_ready`
      als zweite Policy-Wahrheit mitliest
    - die bestehenden Orchestrierungs- und Block-6-Tests auf den neuen
      Vertragskern gezogen
  - Warum:
    - `allowed_next_step` soll die eigentliche post-processing-Policy sein
      und nicht nur ein schmales Nebenfeld neben einem unscharfen
      `gate`-Begriff
    - besonders der Recommendation-Abschlussknoten war bisher halb in
      Pending-Transition,
      halb in Response-Resten
      und halb in spaeten Hilfssignalen verteilt
  - Wirkung:
    - der naechste erlaubte Systemzug ist jetzt expliziter modelliert:
      Abschlussknoten halten,
      Recommendation freigeben
      oder bewusst in den medizinischen Pfad zurueckkehren
      laufen ueber denselben Policy-Vertrag
    - die spaete Antwortwahl ist klarer nachgelagert
      und zieht ihre sichtbare Bahn jetzt enger aus der Next-Step-Policy
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/concern.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/services/recommendation_state_service.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena_pipeline3/application/services/llm_response_generation_service.py`
    - `server/careena_pipeline3/application/services/concern_state_service.py`
    - `server/tests/test_dialogue_manager.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - als naechstes pruefen,
      ob
      `gate_status`
      nach diesem Schnitt noch mehr ist als reine Beobachtbarkeit
      oder nun konsequent weiter hinter
      `allowed_next_step`
      zurueckgebaut werden sollte
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 116 Datum: 13-06-26 12:04 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - im aktiven Turn-Vertrag eine kleine explizite Lesekante
      `TurnContext.active_allowed_next_step`
      eingefuehrt,
      damit Response- und Prompt-Schicht den tatsaechlich aktiven
      naechsten Zug primaer aus
      `gate_decision`
      lesen
    - den automatischen Spiegel
      `gate_decision.allowed_next_step -> context.allowed_next_step`
      im `DialogueManager` beendet;
      `allowed_next_step`
      bleibt nur noch als Legacy-/Observability-Feld fuer aeltere Pfade
      erhalten
    - `ResponseManager` und
      `LLMResponseGenerationService`
      auf die neue aktive Lesekante umgestellt
      und die direkt betroffenen Tests auf dieselbe Wahrheitsquelle gezogen
  - Warum:
    - zwischen Gate-Stufe und spaeter Antwortwahl lief dieselbe
      Steuerentscheidung doppelt sichtbar durch die Runtime:
      einmal als
      `gate_decision`
      und noch einmal als gespiegelt gesetztes
      `allowed_next_step`
    - der kleine Schnitt reduziert diese Zweitwahrheit,
      ohne die bestehende Observability oder alte Test-/Kompatibilitaetshaken
      sofort hart zu brechen
  - Wirkung:
    - aktive Routing- und Prompt-Lesart ist jetzt klarer:
      die spaete Policy liest primaer die Gate-Entscheidung
      statt einen parallel mitgefuehrten Spiegelwert
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager`
      lief erfolgreich durch
    - Zusatzbefund:
      der breitere Lauf
      `server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      zeigt weiterhin mehrere aeltere Block-6-Test-/Vertragsabweichungen,
      die nicht aus diesem kleinen Gate-Read-Schnitt stammen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/llm_response_generation_service.py`
    - `server/tests/test_dialogue_manager.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - als naechstes denselben Bereich weiter schaerfen
      und pruefen,
      ob
      `response_mode`
      auf aehnliche Weise noch zu stark als zweiter policy-naher
      Spiegelwert verwendet wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 115 Datum: 13-06-26 00:00 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den aktiven Extraction-Runtime-Schnitt von
      `ExtractionResult`
      auf den kleineren
      `Call2ExtractionResult`
      umgestellt:
      Extractor,
      Fallback
      und resilienter Postprocess arbeiten jetzt direkt auf diesem Vertrag
    - den Bridge-Bau in
      `ExtractionResultMapper`
      auf den direkten Pfad
      `Call2ExtractionResult -> CaseUpdateBridge`
      gezogen;
      `ExtractionResult`
      bleibt nur noch als Kompatibilitaets-/Diagnosehuelle verfuegbar
    - den Python-Normalizer so umgeschnitten,
      dass er
      `focus_update`,
      `new_items`,
      `open_questions`
      und
      `case_extension_status`
      direkt auf dem kleinen Call-2-Vertrag normalisiert,
      statt ueber
      `ExtractionResult.case_payload.observations`
      und versteckte
      `call2_contract_role`
      -Hilfssignale zu gehen
    - `ExtractionManager`,
      `ExtractionPayload`
      und `SafetyManager`
      auf den expliziten Bridge-zentrierten Runtime-Pfad nachgezogen;
      der diagnostische
      `extraction_result`
      bleibt sichtbar,
      ist aber nicht mehr operative Wahrheitsstufe
    - die relevanten Server-Tests vom alten Doppelvertrag auf den direkten
      Bridge-Pfad und den kleineren Normalizer-Vertrag umgestellt
  - Warum:
    - die doppelte Vertragskette
      `Call2ExtractionResult -> ExtractionResult -> CaseUpdateBridge`
      hielt Legacy-Semantik und versteckte Zweitwahrheiten im aktiven
      Runtime-Pfad fest
    - der Truth-Write-Rand sollte direkt aus einem kleinen expliziten
      Call-2-Vertrag gespeist werden,
      waehrend breitere Observability-Formen nur noch Nebenrolle spielen
  - Wirkung:
    - der aktive Extraction-zu-Truth-Pfad ist jetzt schmaler und klarer:
      Call 2 normalisiert seinen kleinen Vertrag
      und baut daraus direkt die Truth-Edge-Bridge
    - der Python-Normalizer haengt nicht mehr an impliziten
      Rollenmarkierungen in einem breiteren Zwischenobjekt
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_python_extraction_result_normalizer`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/extraction_service.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/models/extraction/result.py`
    - `server/tests/test_dialogue_manager.py`
    - `server/tests/test_python_extraction_result_normalizer.py`
  - Naechster Punkt:
    - als naechstes pruefen,
      ob
      `ExtractionResultMapper`
      als Name und Export noch zur neuen reinen Bridge-Builder-Rolle passt
      oder sichtbar umbenannt werden sollte,
      damit der verbliebene Kompatibilitaetspfad nicht wieder zur
      Hauptsemantik wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 97 Datum: 12-06-26 01:49 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den aktiven Recommendation-Abschlussknoten in
      `EntryManager` um eine kleine direkte Wahlkante erweitert:
      Antworten wie `Ja.` oder `weitere Beschwerden` auf
      `recommendation_ready_check` werden jetzt vor Call 1 als
      `report_more_information`-Wahl gelesen
    - `ResponseManager` priorisiert diesen Rueckweg jetzt sichtbar als
      `transition_state:return_to_medical`,
      statt bei weiter gesetztem `recommendation_ready` sofort wieder in
      `guide_next_step` zu kippen
    - `ResponseTextBuilder` formuliert fuer diesen kleinen Rueckweg eine
      kurze Aufforderung,
      die weiteren Beschwerden erst zu beschreiben,
      statt eine leere Extraktion oder eine Wiederholung des Abschlussknotens
      zu provozieren
    - den neuen Rueckweg mit gezielten Tests fuer
      `Ja.` im `EntryManager` und im echten
      `DialogueManager`-Pfad abgesichert
      und den V4-Plan in Block 2 um einen ersten begonnenen Stand erweitert
  - Warum:
    - Block 2 soll medizinische Rueckfrage,
      dialogische Transition
      und Recommendation-Freigabe sauberer trennen
    - ein sichtbarer Rest war,
      dass knappe Wahlantworten auf dem Abschlussknoten noch leicht wieder in
      denselben Recommendation-Loop oder in leere medizinische Arbeit kippen
  - Wirkung:
    - der Abschlussknoten hat jetzt eine explizitere Rueckkante:
      `Ja.` kann den Knoten verlassen,
      ohne schon neue medizinische Fakten zu behaupten
      und ohne sofort wieder dieselbe Abschlussfrage zu erzeugen
    - die Runtime bleibt damit naeher an der Zwei-Wege-Lesart
      `request_recommendation` / `report_more_information`,
      auch wenn die freie Sprachbreite dieser Kante spaeter noch ausgebaut
      werden muss
    - Verifikation:
      die relevanten Tests
      `server/tests/test_block6_response_transition.py`
      und
      `server/tests/test_dialogue_manager.py`
      laufen ueber die gebuendelte Runtime mit `unittest` erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/tests/test_block6_response_transition.py`
    - `server/careena_pipeline3/autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - die noch unklaren oder freien Kurzantworten auf dem Abschlussknoten
      weiter gegen Fehlrouting und erneute Schleifen absichern
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 98 Datum: 12-06-26 01:49 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den heuristischen Freitext-Sonderpfad am aktiven
      Recommendation-Abschlussknoten wieder entfernt
      und stattdessen einen kleinen expliziten Zwei-Wege-Vertrag
      `RecommendationTransitionResolution`
      mit genau den Aktionen
      `request_recommendation`
      und
      `report_more_information`
      eingefuehrt
    - dafuer eine kleine eigene LLM-/Support-Call-Kante aus
      `LLMRecommendationTransitionExtractor`,
      Prompt,
      Kontextbuilder
      und
      `RecommendationTransitionService`
      aufgebaut
      und diese in die Runtime sowie in den `EntryManager` verdrahtet
    - `EntryManager` loest aktive
      `recommendation_ready_check`-Knoten jetzt zuerst ueber diesen
      expliziten Resolver:
      `request_recommendation` wird direkt committed,
      ein kanonischer
      `report_more_information`-Aktionswert fuehrt kurz zurueck in den
      medizinischen Pfad,
      und freier Text mit derselben Resolution kann danach weiter normal ueber
      Call 1 / Extraktion bewertet werden
    - die Block-6-/Transition-Tests auf injizierte Transition-Resolver
      umgestellt,
      damit die Knotenlogik nicht mehr ueber lokale Textlisten abgesichert
      wird
  - Warum:
    - laut V4 soll dieser Spezialknoten nicht ueber lokale Oberflaechen-
      Heuristik,
      sondern ueber einen kleinen sauberen Zustands- und Vertragsknoten
      getragen werden
    - Buttons und freier Text sollen denselben Zwei-Wege-Vertrag bedienen,
      statt in `EntryManager` implizit aus Textlisten heraus neu modelliert zu
      werden
  - Wirkung:
    - der Recommendation-Abschlussknoten ist jetzt naeher an der beabsichtigten
      V4-Arbeitsweise:
      kleiner expliziter Zwei-Wege-Vertrag statt versteckter
      Freitext-Sonderlogik
    - die Runtime hat dafuer nun eine sichtbare kleine Ausbaukante,
      an der spaeter Prompt und freie Antwortbreite verbessert werden koennen,
      ohne den `DialogueManager` oder `EntryManager` wieder mit Textheuristiken
      aufzuladen
    - Verifikation:
      die relevanten Tests
      `server/tests/test_block6_response_transition.py`
      und
      `server/tests/test_dialogue_manager.py`
      laufen ueber die gebuendelte Runtime mit `unittest` erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/recommendation_transition.py`
    - `server/careena_pipeline3/llm/prompts/recommendation_transition.py`
    - `server/careena_pipeline3/llm/recommendation_transition_extractor.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/__init__.py`
    - `server/careena_pipeline3/application/services/recommendation_transition_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/runtime.py`
    - `server/tests/test_block6_response_transition.py`
    - `server/careena_pipeline3/autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den neuen Zwei-Wege-Normalizer im echten Lauf gegen freie knappe
      Abschlussantworten pruefen
      und seine Promptbreite dann gezielt statt heuristisch nachschaerfen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 99 Datum: 12-06-26 02:33 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - im V4-Verzeichnis eine neue strukturierte Sammeldatei
      `BUG_REPORTS_V4.md`
      angelegt,
      die kuenftig fortlaufend reale Lauf- und Architekturbugs zum V4-Refactor
      aufnehmen soll
    - dort drei aktuelle Kernbefunde aus den juengsten Logs und dem aktiven
      Codezustand festgehalten:
      der Recommendation-Transition-Resolver kontrolliert den weiteren
      Turn-Pfad noch nicht sauber genug,
      die Antwortstrategie fehlt als eigene Schicht noch deutlich,
      und der medizinische Pfad driftet im aktuellen Lauf fachlich stark
    - den V4-Plan so nachgeschaerft,
      dass diese Bugdatei als aktive Quellenbasis mitlaeuft
      und Block 3 nach den juengsten Befunden als naechster wichtiger Hebel
      schaerfer eingeordnet ist,
      ohne Block 2 dadurch zu ersetzen
  - Warum:
    - die aktuellen Probleme sollten nicht nur im Chat verstreut bleiben,
      sondern an einer zukunftig erweiterbaren Stelle strukturiert gesammelt
      werden
    - zusaetzlich war nach den juengsten Logbefunden eine ehrlichere
      Einordnung noetig,
      dass Careenas aktuelles Antwortverhalten selbst noch ein zentraler
      offener Architekturrest ist
  - Wirkung:
    - es gibt jetzt einen dauerhaften Bug-/Befundanker direkt neben dem
      V4-Plan
    - die naechsten Schnitte koennen sich gezielter auf reale Laufprobleme
      beziehen statt sie jedes Mal neu aus Logs herauszuziehen
    - der Plan spiegelt jetzt klarer,
      dass ein enger vorgezogener Block-3-Schnitt wahrscheinlich der
      naechste sinnvolle Arbeitshebel ist,
      auch wenn Block 2 weiter offen bleibt
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/2026-06-11/BUG_REPORTS_V4.md`
    - `server/careena_pipeline3/autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den naechsten praktischen Schnitt zwischen offener Block-2-
      Transition-Kante und einem kleinen vorgezogenen Block-3-Strategy-
      Vertrag festziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 100 Datum: 12-06-26 02:48 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - fuer den begonnenen V4-Block-3-Schnitt einen kleinen expliziten
      Antwortstrategie-Vertrag
      `ResponseStrategy`
      eingefuehrt und ihn in
      `ResponsePlan`,
      `TurnContext`,
      `ResponseManager`
      und die spaete Response-Anwendung im
      `DialogueManager`
      verdrahtet
    - einen neuen
      `ResponseGenerationService`
      als schmale Trennkante zwischen Policy und Formulierung eingebaut:
      statische Sonderpfade bleiben ueber
      `ResponseTextBuilder`
      aktiv,
      waehrend der normale medizinische
      `continue`-Pfad jetzt gezielt ueber einen kleinen
      `LLMResponseGenerationService`
      laufen kann
    - den neuen LLM-Antwortpfad bewusst eng gehalten:
      `MASTER_PROMPT` aus
      `server/config.py`
      wird nur lesend als Basis genutzt,
      der Prompt erhaelt ausschliesslich explizite Turn-Fakten,
      und bei Request-/Leerfehlern faellt der Lauf ehrlich auf den
      bestehenden statischen Builder zurueck
    - die Runtime-Verdrahtung bereinigt,
      so dass der neue Antwortdienst sauber ueber einen echten
      `ResponseManager`
      injiziert wird statt ueber eine kaputte spaete Umverdrahtung
    - den V4-Plan unter Block 3 um einen ersten begonnenen Stand zum neuen
      Antwortstrategie-Schnitt fortgeschrieben
  - Warum:
    - laut aktuellem V4-Befund fehlt Careena nicht nur noch eine robustere
      Transition-Kante,
      sondern auch eine ehrliche kleine Antwortstrategie-Schicht zwischen
      Policy und Text
    - ohne diesen Schnitt blieb der normale medizinische Antwortpfad zu stark
      auf feste Kategoriereaktionen reduziert,
      waehrend Sonderpfade und freie Weiterfuehrung noch nicht sauber
      getrennt waren
  - Wirkung:
    - Sonderpfade bleiben deterministisch und klein,
      waehrend der normale medizinische Verlauf erstmals eine eng begrenzte
      freie Antwortformulierung andocken kann
    - die Antwortseite ist damit nicht mehr nur
      `response_mode -> fixer Text`,
      sondern beginnt als eigene kleine Strategieebene lesbar zu werden
    - Verifikation:
      `server/careena_pipeline3`
      wurde ueber die gebuendelte Python-Runtime erfolgreich mit
      `compileall`
      statisch kompiliert;
      zusaetzlich laufen zwei Smoke-Checks gruen:
      saubere Runtime-Verdrahtung
      sowie
      `ResponseManager`
      mit
      `llm_continue`
      gegen
      `static_return_to_medical`
    - offener Rest:
      die echten
      `unittest`-Module konnten in der verfuegbaren Runtime hier nicht
      ausgefuehrt werden,
      weil dort die Projektdeps
      `dotenv`
      und
      `openai`
      fehlen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/response_strategy.py`
    - `server/careena_pipeline3/models/turn/response_plan.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/application/services/llm_response_generation_service.py`
    - `server/careena_pipeline3/application/services/response_generation_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/runtime.py`
    - `server/careena_pipeline3/autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den Recommendation-Abschlussknoten gegen
      `awaiting_reply`
      vs.
      `request_recommendation`
      vs.
      `report_more_information`
      weiter schaerfen,
      damit der neue freie
      `continue`-Pfad auf einer robusteren Transition-Kante sitzt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 101 Datum: 12-06-26 02:58 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den aktiven Recommendation-Abschlussrueckweg auf Scout-Ebene
      nachgeschaerft:
      `IntentGatewayContext`
      traegt jetzt den aktiven
      `recommendation_ready_check`
      explizit mit,
      und der Call-1-Prompt beschreibt den Unterschied zwischen
      blosser Wahl
      `da ist noch mehr`
      und bereits enthaeltener konkreter medizinischer Zusatzinformation
    - dafuer im Scout-Vertrag einen kleinen expliziten Dialoghinweis
      `dialogue_hint:transition_continue_without_medical_content`
      vorbereitet
      und in
      `IntentGateway`
      als eigene kleine Eigenschaft verankert
    - `EntryManager`
      nutzt diesen Hinweis jetzt als saubere Guardrail:
      wenn auf dem aktiven Abschlussknoten nur der medizinische Rueckweg
      gewaehlt wurde,
      aber noch keine konkreten neuen Fakten vorliegen,
      wird der Turn nicht mehr in `Call 2` gezwungen
  - Warum:
    - die neuesten Logs zeigten klar,
      dass
      `ich habe noch weitere beschwerden`
      zwar semantisch korrekt als
      `report_more_information`
      gelesen wurde,
      danach aber trotzdem in den normalen
      Intent-/Call-2-Pfad fiel
      und dort sogar einen kaputten leeren Extraktionslauf ausloeste
    - das Problem sass damit primaer nicht im finalen Antworttext,
      sondern an der unsauberen Rueckweg-Orchestrierung vor der Extraktion
  - Wirkung:
    - der Rueckweg
      `recommendation_ready_check -> report_more_information`
      hat jetzt eine explizitere kleine Scout-Grenze:
      blosse Wahl des medizinischen Weitergehens kann den Abschlussknoten
      verlassen,
      ohne schon als extrahierbarer medizinischer Fakt behandelt zu werden
    - dadurch sollte der fehlerhafte Pfad
      `Transition erkannt -> trotzdem leere Call-2-Extraktion -> falsche
      Bestaetigungsantwort`
      kleiner werden
    - bewusst offen bleibt:
      die generelle Gate-/Readiness-Haerte,
      durch die das System nach fruehen Minimalinformationen teils weiterhin
      schnell wieder auf
      `ready_for_transition`
      kippt
    - Verifikation:
      `server/careena_pipeline3`
      wurde ueber die gebuendelte Python-Runtime erfolgreich mit
      `compileall`
      statisch kompiliert;
      zusaetzlich bestaetigt ein gezielter Smoke-Check,
      dass
      `EntryManager`
      bei
      `report_more_information`
      plus
      `transition_continue_without_medical_content`
      sauber auf
      `extraction_required=False`
      faellt
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/context.py`
    - `server/careena_pipeline3/models/workflow/intent_gateway.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/prompts/intent_gateway.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
    - `server/careena_pipeline3/autodoc/2026-06-11/BUG_REPORTS_V4.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - im echten Lauf pruefen,
      ob der aktive Scout jetzt
      `blosse Rueckweg-Wahl`
      gegen
      `Rueckweg plus echte neue Fakten`
      robust genug trennt
      und danach die verbleibende Gate-/Readiness-Haerte gesondert angehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 102 Datum: 12-06-26 03:42 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - den V4-Plan um eine neue hoehere Zwischenlesart zum fortlaufenden
      Nutzeranliegen erweitert:
      statt dieses Anliegen weiter implizit ueber
      `primary_focus`
      oder lokale Symptomvollstaendigkeit mitzuschleppen,
      wird jetzt explizit ein concern-naher Layer als spaetere
      Architekturaufgabe beschrieben
    - dabei bewusst festgehalten,
      dass diese concern-nahe Schicht vorerst eher untergeordnet oder
      benachbart zu
      `DialogueState`
      gedacht werden soll
      und nicht vorschnell direkt darin aufgehen muss
    - ausserdem im Plan verschaerft:
      `Readiness`
      bleibt begrifflich die spaetere zentrale Schicht fuer Pflichtfelder und
      Gate,
      ist aber nicht identisch mit der Frage,
      ob fuer das aktuelle Nutzeranliegen schon genug Fallverstaendnis
      vorliegt
    - zusaetzlich an den relevanten Blockstellen sichtbar gemacht,
      dass bestehende heute schon angelegte,
      aber falsch verkabelte
      `primary_focus`-Lesepfade spaeter gezielt auf concern-nahe Semantik
      umgelegt werden sollen
  - Warum:
    - die juengsten Laufbefunde zeigen nicht nur lokale Knotenfehler,
      sondern machen klarer,
      dass dem System noch eine uebergeordnete Anliegensebene fehlt,
      zwischen strukturierten medizinischen Fakten,
      Dialogzustand,
      Readiness
      und spaeterer Recommendation
    - fuer die weitere Refactor-Arbeit sollte dieser Sprung zuerst
      architektonisch sauber formuliert sein,
      bevor einzelne lokale Reparaturen wieder nur Symptome behandeln
  - Wirkung:
    - V4 beschreibt das Nutzeranliegen jetzt nicht mehr nur als spaeteren
      losen Merksatz,
      sondern als klarere concern-nahe Ausbaukante mit Trennung zu
      `DialogueState`
      und
      `Readiness`
    - dadurch ist fuer die naechsten Schritte klarer,
      dass nicht jede Frage nach
      `genug Information`
      automatisch eine
      `Readiness`-
      oder eine
      `primary_focus`-
      Frage ist
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - aus dieser neuen concern-nahen Lesart einen kleinen expliziten
      Architekturvertrag ableiten
      und danach die heute falsch verkabelten
      `primary_focus`-
      Pfade gezielt dagegen halten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 95 Datum: 10-06-26 15:07 ===
  - Kategorie:
    - `cleanup`
  - Bereich:
    - `backend`
  - Aenderung:
    - die nach Block 4 nicht mehr aktiven Restartefakte des alten
      zweiten LLM-Normalizer-Pfads entfernt:
      `server/careena_pipeline3/llm/extraction_result_normalizer.py`,
      `server/careena_pipeline3/llm/prompts/extraction_normalization.py`
      sowie die dazugehoerigen Exporte und die tote
      `case_normalization`-Verdrahtung in
      `server/careena_pipeline3/llm/call_control.py`
    - ausserdem die veraltete Normalizer-Input-Kante und ihre alten Summary-
      Hilfsfunktionen aus `server/careena_pipeline3/llm/context.py`
      entfernt
    - den Block-4-Stand in `REFACTOR_PLAN_V3.md` um einen expliziten
      Abschnitt der bewusst stehen gelassenen Uebergangspunkte erweitert
  - Warum:
    - nach dem Wechsel auf den kleinen Python-Normalizer war der alte zweite
      breite LLM-Pfad nur noch irrefuehrender Altballast
    - fuer einen sauberen Uebergabepunkt vor Block 5 sollten tote
      Verdrahtungen und halbveraltete Hilfskanten nicht mehr im aktiven
      Umfeld liegen
  - Wirkung:
    - der aktive Call-2-Pfad hat jetzt keine tote Altverdrahtung zum frueheren
      zweiten LLM-Normalizer mehr
    - im Block-4-Stand ist jetzt direkt dokumentiert, welche Uebergangspunkte
      bewusst stehen gelassen werden und warum
    - die bereinigten Python-Dateien wurden ueber die gebuendelte Runtime mit
      `py_compile` erfolgreich statisch kompiliert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/llm/__init__.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/call_control.py`
    - `server/careena_pipeline3/llm/extraction_result_normalizer.py`
    - `server/careena_pipeline3/llm/prompts/extraction_normalization.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - mit dem gesaeuberten Uebergabepunkt in Block 5 gehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 96 Datum: 10-06-26 15:21 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - im `REFACTOR_PLAN_V3.md` unter Block 5 einen kurzen Bugreport aus dem
      aktuellen Runtime-Log eingetragen:
      Mischfall aus beantwortetem Follow-up und zusaetzlicher neuer
      medizinischer Information wird noch nicht sauber als kombinierter
      Prozess-/Case-Pfad behandelt
    - die Doku damit um einen direkten Anschluss vom Block-4-Abschluss zum
      naechsten funktionalen Schnitt ergaenzt
  - Warum:
    - nach dem Architekturumbau aus Block 3 und 4 ist der naechste sichtbare
      Restfehler kein breiter Kontextfehler mehr, sondern ein konkreter
      Folgefehler an der Grenze zwischen Follow-up-Aufloesung,
      Requirement-Erfuellung und neuem Faktmaterial
  - Wirkung:
    - der Uebergabepunkt in Richtung Block 5 ist jetzt nicht nur strukturell,
      sondern auch mit einem konkreten reproduzierbaren Restfall dokumentiert
    - spaetere Arbeit kann direkt an einem echten Laufverhalten ansetzen statt
      den naechsten Schnitt erst wieder aus Logs herausdestillieren zu muessen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/server_log/logs/debug_log_pipeline3.txt`
  - Naechster Punkt:
    - bei Block 5 die kombinierbaren Spuren fuer Follow-up-Erfuellung und neue
      Fakten systematisch schneiden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 94 Datum: 10-06-26 14:29 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den zweiten breiten LLM-Normalizer aus dem aktiven Runtime-Pfad
      herausgenommen und durch eine kleine Python-Normalisierung in
      `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
      ersetzt
    - zusaetzlich einen kleinen
      `ExtractionFailureFallbackBuilder` eingefuehrt und
      `ResilientExtractionService` so umgeschnitten, dass er jetzt vor allem
      Extraktion, Failure-Fallback und schmale Post-Processing-Orchestrierung
      traegt
    - die Runtime-Verdrahtung in `server/careena_pipeline3/runtime.py`
      auf den neuen Python-Normalizer umgestellt
    - den Block-4-Stand in `REFACTOR_PLAN_V3.md` nachgeschaerft und dort
      festgehalten, dass der fruehere zweite breite Re-Emissions-Call nicht
      mehr Teil des aktiven Pfads ist
  - Warum:
    - nach dem vorherigen Block-4-Schnitt war die groesste Restlast weiter
      der zweite LLM-Normalizer und die Sammelrolle von
      `ResilientExtractionService`
    - fuer einen ehrlichen Block-4-Abschluss sollte die aktive Call-2-Kette
      nicht mehr von einem zweiten grossen Extraction-aehnlichen LLM-Pass
      abhaengen
  - Wirkung:
    - der aktive Call-2-Pfad ist jetzt kleiner und nachvollziehbarer:
      primaerer kleiner LLM-Call plus enge Python-Nachbearbeitung
    - `ResilientExtractionService` ist nicht mehr der Ort eines zweiten
      breiten LLM-Passes, sondern deutlich naeher an einem kleinen
      Runtime-Orchestrator fuer die verbleibenden Restaufgaben
    - die geaenderten Python-Dateien wurden ueber die gebuendelte Runtime mit
      `py_compile` erfolgreich statisch kompiliert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/extraction_failure_fallback_builder.py`
    - `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/runtime.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den naechsten Haupthebel in Block 5 gegen Requirement-, Follow-up- und
      Readiness-Schicht waehlen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 93 Datum: 10-06-26 14:22 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Block-4-Schnitt fuer den primaeren Call-2-Pfad umgesetzt:
      `llm/context.py` gibt fuer den ersten Extraction-Call jetzt nur noch
      einen harten Minimalkontext mit
      `latest_user_message`, `profile`, `call2_tasks`, `operation_mode`,
      `pending_slot`, `last_assistant_question`, optional
      `focus_observation` und optional kleinen
      `relevant_existing_observations`
    - gleichzeitig in
      `models/extraction/result.py` einen kleineren internen Call-2-Vertrag
      `Call2ExtractionResult` eingefuehrt, der
      `subject_update`, `focus_update`, `new_items` und `open_questions`
      trennt
    - `LLMCaseExtractionExtractor` und der Call-2-Prompt wurden auf diesen
      kleineren Vertrag umgestellt; der Extractor adaptiert das Ergebnis
      bewusst noch zurueck in das bestehende `ExtractionResult`, damit der
      restliche aktive Codepfad weiterlaeuft
    - den neuen kleinen `profile`-Anker bis in den aktiven Call-2-Pfad
      weitergetragen und die betreffenden Service-/Manager-Signaturen
      entsprechend erweitert
  - Warum:
    - nach dem Block-3-Schnitt sollte `Call 2` nicht weiter auf breiten
      Summary-Paketen und einem zu grossen primaeren Output beruhen
    - fuer einen echten Block-4-Fortschritt war wichtig, den primaeren
      LLM-Call kleiner und ehrlicher zu schneiden, ohne die restliche
      Pipeline sofort vollstaendig neu zu bauen
  - Wirkung:
    - der primaere Call-2-Layer ist jetzt naeher am Werkzeugkasten-Zielbild
      aus dem Konzept:
      weniger breiter Kontext, klarere Aufgabenbereiche und ein kleinerer
      interner Outputvertrag
    - die verbleibende Restlast sitzt jetzt sichtbarer im zweiten
      Normalizer-Call und in `ResilientExtractionService`, statt weiter im
      primaeren Call-2-Vertrag zu kleben
    - die geaenderten Python-Dateien wurden zusaetzlich ueber die gebuendelte
      Runtime mit `py_compile` erfolgreich statisch kompiliert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/llm/extraction_result_normalizer.py`
    - `server/careena_pipeline3/models/extraction/result.py`
    - `server/careena_pipeline3/models/extraction/__init__.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/services/extraction_service.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den zweiten LLM-Normalizer und die verbleibende Sammelrolle in
      `ResilientExtractionService` gezielt kleiner schneiden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 92 Datum: 10-06-26 03:38 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Call-1-Vertrag in
      `server/careena_pipeline3/models/workflow/intent_gateway.py`
      von flachen Bool-/Taskfeldern auf einen Scout-/Dispatch-Zuschnitt mit
      gruppierten Signalcontainern umgestellt
    - den Intent-Gateway-Prompt in
      `server/careena_pipeline3/llm/prompts/intent_gateway.py`
      auf das neue JSON-Zielbild mit
      `entry_signals`, `dispatch_signals`, `case_hints`,
      `dialogue_hints`, `safety_hints` und optionalem `profile`
      umgebaut
    - `EntryManager`, `Call2OperationModeService` und
      `RecommendationRequestService` auf den neuen Gateway-Vertrag
      angepasst, dabei aber die bestehende Turn-Pipeline ueber
      Kompatibilitaets-Properties bewusst weiter lauffaehig gehalten
    - die Modell-Exporte auf den neuen Gateway-Zuschnitt bereinigt und den
      alten `IntentGatewaySignals`-Export entfernt
  - Warum:
    - Block 3 aus `REFACTOR_PLAN_V3.md` verlangt kleinere sichtbare
      Entry-Signale statt einer weiter wachsenden flachen Feldsammlung
    - der neue Zuschnitt soll `Call 1` staerker als Scout-/Dispatch-Schicht
      lesbar machen, damit `Call 2` spaeter sauberer auf einem expliziteren
      Vertrag aufsetzen kann
  - Wirkung:
    - Call 1 liefert jetzt gruppierte Signalbereiche statt eines diffusen
      Sammelobjekts, bleibt aber fuer den restlichen aktiven Codepfad ueber
      kleine Helfer weiterhin anschlussfaehig
    - die Pipeline ist damit naeher an einem spaeter modular komponierbaren
      Call 2, ohne dass dessen eigentliche Kontext- und Claim-Vertraege in
      diesem Schritt schon mit umgebaut wurden
    - Verifikation blieb statisch:
      weder `python` noch `py` sind in dieser Umgebung verfuegbar, daher war
      keine lokale Compile-Pruefung moeglich
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/intent_gateway.py`
    - `server/careena_pipeline3/llm/prompts/intent_gateway.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/services/call2_operation_mode_service.py`
    - `server/careena_pipeline3/application/services/recommendation_request_service.py`
    - `server/careena_pipeline3/models/workflow/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den neuen Call-1-Vertrag gegen die Call-2-Kontextkante halten und
      daraus den kleineren dauerhaften Call-2-Inputvertrag schneiden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 91 Datum: 10-06-26 02:29 ===
  - Kategorie:
    - `cleanup`
  - Bereich:
    - `backend`
  - Aenderung:
    - nach dem letzten Vertragsumbau geprueft, ob `MessageDelta` im aktiven
      Python-Code noch irgendwo benoetigt wird
    - da keine aktive Referenz ausser der Altdatei selbst mehr uebrig war,
      `server/careena_pipeline3/models/turn/message_delta.py` ganz entfernt
    - die Block-2-Standnotiz in
      `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
      noch einmal nachgeschaerft:
      der alte `MessageDelta`-Typ ist jetzt nicht nur abgeloest, sondern als
      tote Resthuelle auch wirklich weg
  - Warum:
    - nach dem Wechsel auf `CaseUpdateBridge` sollte kein historischer
      Vertragstyp mehr als tote Huelse im aktiven Modellraum liegenbleiben
    - fuer einen wirklich sauberen Block-2-Abschluss war wichtig zu
      bestaetigen, dass die alte Datei nicht mehr implizit gebraucht wird
  - Wirkung:
    - der aktive Code kennt jetzt keinen `MessageDelta`-Vertrag mehr
    - Block 2 ist damit auch auf Dateiebene aufgeraeumt und nicht nur ueber
      neue Nebentypen ueberlagert
    - der naechste Schritt kann ohne Bridge-Altlasten klar in Block 3 oder 4
      gehen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/message_delta.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - zwischen Block 3 und Block 4 den naechsten Haupthebel waehlen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 90 Datum: 10-06-26 02:17 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den letzten aktiven Block-2-Vertragsschnitt gezogen:
      ein neuer expliziter Truth-Edge-Vertrag
      `CaseUpdateBridge` in
      `server/careena_pipeline3/models/turn/case_update_bridge.py`
      eingefuehrt, mit klar getrennten `claims` und `merge_hints`
    - `ExtractionResultMapper` baut jetzt diesen kleineren
      `CaseUpdateBridge` statt den historischen `MessageDelta`
    - `ExtractionPayload`, `CaseStateManager`, `SafetyManager`,
      `CaseMerger`, `CaseMergePolicy` und
      `ObservationIdentityResolver` auf den neuen Bridge-Vertrag
      umgestellt
    - die aktiven Turn-/Top-Level-Model-Exporte auf
      `CaseUpdateBridge`, `CaseUpdateClaims` und
      `CaseUpdateMergeHints` umgestellt; der alte `MessageDelta`-Typ bleibt
      nur noch als inaktiver Legacy-Rest in seiner Datei stehen
    - den Block-2-Stand in `REFACTOR_PLAN_V3.md` nachgeschaerft, damit
      sichtbar bleibt, dass der aktive Truth-Edge-Vertrag jetzt nicht mehr am
      historischen `MessageDelta`-Typ haengt
  - Warum:
    - nach den vorherigen Block-2-Schnitten war die inhaltliche Bridge schon
      stark verengt, aber der aktive Vertragstyp hing immer noch am
      historischen `MessageDelta`-Namen
    - fuer einen echten Block-2-Abschluss sollte nicht nur der Inhalt enger
      werden, sondern auch die aktive Typabhaengigkeit auf einen kleineren
      ehrlicheren Vertrag umgestellt werden
  - Wirkung:
    - der aktive Extraction->Case-Truth-Pfad ist jetzt auch auf Typ-Ebene
      sichtbar enger und weniger historisch aufgeladen
    - die verbleibende Bridge ist als kleiner gezielter Truth-Edge-Vertrag
      lesbar, statt als allgemeines Nachrichten-Delta missverstanden zu
      werden
    - Block 2 ist damit nicht nur inhaltlich, sondern auch strukturell
      deutlich sauberer abgeschlossen; Block 3 und 4 koennen nun auf
      stabileren Grenzen aufsetzen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/case_update_bridge.py`
    - `server/careena_pipeline3/models/turn/extraction_payload.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/application/managers/safety_manager.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/domain/case_merge_policy.py`
    - `server/careena_pipeline3/domain/observation_identity_resolver.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den naechsten Haupthebel zwischen Block 3 und Block 4 waehlen:
      kleine Entry-Signale oder engerer Call-2-Vertrag
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 89 Datum: 10-06-26 02:11 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - Block 2 in
      `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
      um eine explizite Standnotiz erweitert und fuer den aktuellen
      V3-Anspruch als sauber genug bearbeitet markiert
    - in der Standnotiz knapp festgehalten:
      `MessageDelta` ist jetzt auf `case_delta` plus kleine `merge_hints`
      begrenzt, die frueheren Nebensignalzonen sind entfernt, und die
      verbliebenen direkten Abhaengigkeiten sitzen bewusst nur noch in der
      Case-Truth-Zone
  - Warum:
    - nach den letzten Block-2-Schnitten sollte nicht nur der Codezustand,
      sondern auch der aktive Refactor-Plan klar zeigen, dass die Bridge-Zone
      fuer den aktuellen Boundary-First-Anspruch ausreichend begrenzt ist
    - zusaetzlich war eine explizite Einordnung noetig, dass die verbleibende
      Restkante in der Truth-Zone Block 2 nicht mehr verletzt, sondern
      bewusst als spaeter ersetzbarer Merge-Vertrag stehenbleibt
  - Wirkung:
    - der aktive V3-Plan dokumentiert jetzt sichtbar den Block-2-Abschluss
      statt ihn nur implizit aus verstreuten Chatschritten abzuleiten
    - die naechste Arbeit kann klarer an Block 3 und Block 4 ansetzen, ohne
      die Bridge-Frage erneut offen lassen zu muessen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - fuer den naechsten Schritt die kleine Entry-Signalgrenze oder den
      engeren Call-2-Vertrag als neuen Haupthebel waehlen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 88 Datum: 10-06-26 01:52 ===
  - Kategorie:
    - `cleanup`
  - Bereich:
    - `backend`
  - Aenderung:
    - den inzwischen leeren extraction-nahen Recommendation-Restvertrag
      entfernt:
      `ExtractionPayload` traegt kein
      `recommendation_requested` und keine `recommended_modules` mehr
    - den dazugehoerigen Anwendungsrest im `DialogueManager`
      entfernt:
      die bisherige `_apply_extraction_contract(...)`-Stufe sowie ihr Import-
      und Feldbedarf wurden gestrichen
    - die Payload-Doku in `models/turn/extraction_payload.py`
      nachgeschaerft, damit klarer bleibt, dass dort aktuell nur noch direkt
      gelesene Nachbarsignale und die Truth-Bridge zusammenlaufen
  - Warum:
    - nach den vorherigen Block-2-Schnitten blieb an der Extraction-Kante
      noch ein Scheinvertrag stehen:
      Recommendation-Anfrage kommt im aktuellen Code real aus
      `EntryDecision`, waehrend die extraction-nahen Felder nicht mehr mit
      echter Information befuellt wurden
    - V3 verlangt hier lieber sichtbare Verengung als tote Altvertraege
  - Wirkung:
    - die Extraction-Kante ist ehrlicher und traegt keinen leeren
      Recommendation-Umweg mehr
    - der `DialogueManager` liest an dieser Stelle nur noch die wirklich
      benoetigten Stufen
    - der Recommendation-Pfad bleibt im aktuellen Stand weiter an der
      frueheren Entry-/Intent-Seite verankert, bis spaeter bewusst etwas
      anderes gebaut wird
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/extraction_payload.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - die verbleibenden direkten `MessageDelta`-Abhaengigkeiten in
      `CaseStateManager`, `CaseMerger`, `CaseMergePolicy` und
      `ObservationIdentityResolver` noch einmal als bewusste Block-2-
      Restkante festhalten, bevor Block 3 oder 4 beginnt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 87 Datum: 10-06-26 01:50 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den verbleibenden Rest der Block-2-Bridge-Hinweise weiter verengt:
      in `models/turn/message_delta.py` die frueher breit klingenden
      `intent_signals` durch ein kleineres `MessageMergeHints`-Objekt ersetzt,
      das nur noch `message_role` und `possible_new_topic` traegt
    - `ExtractionResultMapper` baut die Bridge jetzt mit diesen explizit
      merge-spezifischen Hinweisen statt mit einem allgemein klingenden
      Intent-Signalobjekt
    - `CaseMerger`, `CaseMergePolicy` und
      `ObservationIdentityResolver` lesen die Resthinweise nun ueber
      `delta.merge_hints`, und die zugehoerigen Turn-/Top-Level-Exporte
      wurden entsprechend nachgezogen
  - Warum:
    - nach dem ersten Block-2-Schnitt war die Bridge zwar bereits kleiner,
      trug aber immer noch einen Namen, der breiter klang als das reale
      Verhalten
    - gemaess V3 sollte hier keine neue Fachlogik erfunden werden, sondern
      die aktuelle Restrolle ehrlicher und enger markiert werden
  - Wirkung:
    - `MessageDelta` wirkt weniger wie ein allgemeiner Nachrichten- oder
      Intent-Behaelter und klarer wie ein enger
      Extraction->Case-Truth-Uebergangsvertrag
    - die verbleibende Bridge-Last ist jetzt besser auf den realen Merge- und
      Identity-Bedarf begrenzt
    - der spaetere Schritt zu noch kleineren speziellen Hint-Vertraegen oder
      einer vollstaendigeren Ablosung der Bridge ist besser vorbereitet
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/message_delta.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/domain/case_merge_policy.py`
    - `server/careena_pipeline3/domain/observation_identity_resolver.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - innerhalb von Block 2 noch die angrenzenden Klassen gegen direkte
      `MessageDelta`-Abhaengigkeit pruefen und markieren, was fuer Block 3/4
      bewusst liegenbleibt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 86 Datum: 10-06-26 01:43 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die Block-2-Bridge-Zone um `MessageDelta` enger gezogen:
      in `models/turn/message_delta.py` die bisher mitgetragenen
      `requirement`-, `planner`-, `trace`- und `staging`-Signalschichten aus
      dem transitionalen Bridge-Objekt entfernt
    - `MessageDelta` ist jetzt expliziter nur noch auf
      `case_delta` plus die wenigen noch fuer Merge und
      Observation-Identitaet benoetigten `intent_signals` begrenzt
    - `ExtractionResultMapper` erzeugt fuer diese Nachbarsignale keine
      `MessageDelta`-Unterobjekte mehr; die kleine Ableitung
      `active_modules(...)` bleibt als direkte Mapper-Hilfe ausserhalb der
      Bridge erhalten
    - `ExtractionManager` liest Requirement-Aktivierung nun direkt ueber diese
      kleine Mapper-Hilfe statt ueber `message_delta.requirement_signals`,
      und die veralteten Turn-/Top-Level-Exporte der entfernten Signaltypen
      wurden bereinigt
  - Warum:
    - `SYSTEM_OVERVIEW.md` und `REFACTOR_PLAN_V3.md` bestaetigen beide, dass
      die Bridge nur Uebergang an der Truth-Kante sein soll und keine
      heimliche Sammelstelle fuer mehrere Wahrheitsarten oder
      Nachbarsignale
    - vor dem tieferen `Call 1`-/`Call 2`-Refactor war daher der naechste
      saubere Schritt, `MessageDelta` auf seine real noch benoetigte Rolle zu
      reduzieren
  - Wirkung:
    - die Extraction->Truth-Bridge ist kleiner, ehrlicher und enger an der
      realen Case-Update-Kante
    - orchestrierungsnahe oder prozessuale Nachbarsignale werden nicht weiter
      still im Bridge-Objekt konserviert
    - ein spaeterer echter Ersatz von `MessageDelta` ist dadurch besser
      vorbereitet, ohne die aktuelle Merge-/Identity-Kante schon neu
      erfinden zu muessen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/message_delta.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - als naechsten Block-2-Schritt die verbleibenden `intent_signals` an der
      Bridge gegen einen noch kleineren Merge-spezifischen Hint-Vertrag
      pruefen und danach erst `Call 1` / `Call 2` enger schneiden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 85 Datum: 10-06-26 00:52 ===
  - Kategorie:
    - `test`
  - Bereich:
    - `backend`
  - Aenderung:
    - in `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
      direkt unter Block 1 eine kurze Standnotiz eingetragen, dass der
      `DialogueManager` fuer den aktuellen V3-Anspruch als sauber genug
      bearbeitet gilt und der naechste strukturelle Hebel nun an Block 2
      liegt
    - zusaetzlich einen kleinen isolierten Python-Unit-Test
      `server/tests/test_dialogue_manager.py` angelegt, der den gesaeuberten
      Orchestrierungsvertrag des `DialogueManager` mit Stub-Komponenten
      prueft:
      sichtbare Turn-Reihenfolge, angewendete Response-Wahrheit im
      `TurnContext` und Rueckgabe des finalen `TurnResult`
  - Warum:
    - nach dem Block-1-Abschluss sollte nicht nur der Plan aktualisiert,
      sondern auch die neue saubere Orchestrierungsform testbar gemacht
      werden
    - da im Workspace noch keine Teststruktur und kein `pytest`-Eintrag
      vorhanden war, wurde bewusst ein leichtgewichtiger `unittest`-Test
      ohne neue Abhaengigkeit angelegt
  - Wirkung:
    - der Refactor-Plan dokumentiert jetzt explizit, dass Block 1 fuer den
      `DialogueManager` aus heutiger Sicht ausreichend eingelost ist
    - es existiert nun ein erster klarer Testanker fuer den zentralen
      Turn-Orchestrator, der spaeter sowohl mit `python -m unittest` als auch
      typischerweise mit `pytest` mitlaufen kann
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/tests/test_dialogue_manager.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei spaeterer Testinfrastruktur den neuen `DialogueManager`-Test
      wirklich ausfuehren und danach den naechsten Block-2-Schnitt an der
      `MessageDelta`-Bridge absichern
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 84 Datum: 10-06-26 00:52 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die finale Response-Kante im `DialogueManager` saubergezogen:
      `TurnContext` traegt jetzt auch `response_text` und
      `recommendation_result`, `_apply_response_contract(...)` schreibt damit
      die komplette spaete Response-Wahrheit in den Turn-Kontext, und
      `TurnResult` wird anschliessend aus dieser einen angewendeten
      Kontextwahrheit statt parallel noch einmal direkt aus `response_plan`
      gebaut
    - in `run_turn(...)` kurze einzeilige Leitkommentare ueber die einzelnen
      Turn-Stufen eingezogen, damit die sichtbare Sequenz schneller lesbar
      ist
    - im `ConfirmationManager` einen expliziten Architekturkommentar
      hinterlegt, wie Confirmation spaeter als Rueckkanal fuer vom Nutzer
      bestaetigte oder bearbeitete Fakten ueber `DialogueManager` in den
      Case-Update-Pfad zuruecklaufen soll
  - Warum:
    - der letzte Block-1-Review zeigte noch einen Architekturrest:
      die spaete Response-Wahrheit war halb im angewendeten Turn-Kontext und
      halb weiterhin im rohen `ResponsePlan` getragen
    - zusaetzlich sollte der Turn-Fluss fuer Menschen schneller lesbar und
      die Confirmation-Idee direkt im Code konserviert werden
  - Wirkung:
    - die spaete Antwortschicht hat jetzt eine deutlich eindeutigere
      Orchestrierungswahrheit
    - `run_turn(...)` liest sich klarer als sichtbare Vertragssequenz
    - der geplante Confirmation-Pfad ist trotz Placeholder-Status direkt im
      Code dokumentiert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/confirmation_manager.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den `DialogueManager` jetzt noch einmal explizit gegen die Block-1-
      Gates halten und dann entscheiden, ob Block 1 fuer die Orchestrierung
      sauber genug abgeschlossen ist
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 83 Datum: 10-06-26 00:20 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den spaeten Turn-Abschnitt im `DialogueManager` weiter als explizite
      Vertragsfolge geschaerft:
      Safety-Zustaende werden jetzt ueber eine gemeinsame
      `_apply_safety_state(...)`-Kante angewendet,
      `ResponsePlan` ueber `_apply_response_contract(...)`,
      und Confirmation laeuft nicht mehr als nacktes Bool, sondern als neues
      kleines Ergebnisobjekt `ConfirmationDecision`
    - dafuer `models/turn/confirmation_decision.py` eingefuehrt und
      `ConfirmationManager` von `should_request_confirmation(...) -> bool`
      auf `evaluate(...) -> ConfirmationDecision` umgestellt
    - die Modul-Doku in `DialogueManager` und `ConfirmationManager`
      nachgeschaerft, damit sichtbar bleibt, dass Confirmation aktuell noch
      placeholderhaft ist, aber trotzdem als spaete Grenzschicht lesbar sein
      soll
  - Warum:
    - V3 verlangt zuerst einen klar lesbaren `DialogueManager` als zentrale
      Souveraenitaetsstelle mit sichtbarer Turn-Sequenz, bevor Bridge-Zone
      oder spaetere Fachschichten tiefer umgebaut werden
    - nach den letzten Schritten waren Entry, Extraction, Process-State und
      Readiness bereits enger geschnitten; Safety, Response und Confirmation
      sollten nun dieselbe Grenzdisziplin bekommen
  - Wirkung:
    - der `DialogueManager` ist jetzt ueber den gesamten Turn hinweg
      gleichmaessiger als Orchestrierungsvertrag lesbar:
      Entry -> Extraction -> Case Truth -> Process State -> Readiness ->
      Safety -> Response -> Confirmation
    - Confirmation ist explizit als sichtbare Placeholder-Grenze markiert,
      statt heimlich als loses Bool am Ende zu haengen
    - es wurde keine neue fachliche Confirmation-/Safety-Logik erfunden,
      sondern nur Delegation und Vertragsklarheit verbessert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/confirmation_decision.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/application/managers/confirmation_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - Block 1 gegen seine Gates halten und dann entscheiden, welche direkten
      Bridge-Reste rund um `MessageDelta` in Block 2 als naechstes bewusst
      markiert und begrenzt werden sollen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 82 Datum: 09-06-26 23:59 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den naechsten Block-1-Schnitt im Turn-Vertrag umgesetzt:
      neue kleine Orchestrierungs-Ergebnisobjekte
      `ProcessStateUpdate` und `ReadinessStateUpdate` in
      `models/turn/state_updates.py` eingefuehrt
    - `DialogueStateService.sync_after_case_update(...)` liefert jetzt ein
      explizites `ProcessStateUpdate` statt nur das rohe `DialogueState`
    - `RecommendationStateService.sync_dialogue_state(...)` liefert jetzt ein
      explizites `ReadinessStateUpdate` statt eines losen
      `(dialogue_state, readiness)`-Tupels
    - `DialogueManager` appliziert diese beiden Stufen jetzt ueber eigene
      kleine Hilfsmethoden und zeigt den Turn-Fluss damit sichtbarer als:
      Case Truth -> Process State -> Readiness State
  - Warum:
    - laut `REFACTOR_PLAN_V3.md` soll die Orchestrierungsmitte zuerst ueber
      klarere Untervertraege lesbarer werden, bevor tiefere Fachschichten
      groesser umgebaut werden
    - bisher klebten Process-State- und Readiness-Mutationen noch relativ roh
      und direkt im Hauptfluss des `DialogueManager`
  - Wirkung:
    - der `DialogueManager` bleibt zentrale Souveraenitaetsstelle, liest die
      mittlere Turn-Progression aber jetzt in zwei expliziteren Stufen
    - Process-State und Recommendation-/Gate-State sind im Turn-Fluss besser
      getrennt sichtbar
    - das bereitet die spaetere V3-Arbeit an Requirement-, Follow-up- und
      Readiness-Grenzen vor, ohne ihre innere Fachlogik schon jetzt neu zu
      entwerfen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/state_updates.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/application/services/dialogue_state_service.py`
    - `server/careena_pipeline3/application/services/recommendation_state_service.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - als naechsten Block-1-Schritt pruefen, ob der `DialogueManager`
      Response-/Safety-/Confirmation-Vorbereitung noch als eigene kleine
      Vertragsstufen lesbarer machen sollte oder ob jetzt zuerst Block 2 um
      die Bridge-Zone sinnvoller ist
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 81 Datum: 09-06-26 23:40 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den ersten praktischen V3-Schritt am Turn-Vertrag umgesetzt:
      `ExtractionPayload` traegt jetzt explizite kleine Orchestrierungs-
      Outputs fuer `recommendation_requested` und `recommended_modules`
    - `ExtractionManager` fuellt diese kleinen Bridge-Outputs direkt aus dem
      aktuellen transitionalen `message_delta`
    - `DialogueManager` liest Recommendation-/Planner-Signale nun ueber
      diese engeren Extraction-Outputs und nicht mehr direkt aus
      `message_delta.planner_signals`; zusaetzlich wurden seine
      Entry-/Extraction-Vertragsanwendungen in eigene kleine Hilfsmethoden
      gezogen und die Rollenbeschreibung des Managers nachgeschaerft
  - Warum:
    - laut `REFACTOR_PLAN_V3.md` sollen zuerst die sichtbaren Grenzen rund um
      den `DialogueManager` enger werden, bevor `Call 2` selbst tiefer
      umgebaut wird
    - die bisherige direkte Verkabelung des Orchestrators an interne
      `message_delta`-Plannerdetails war genau die Art historischer
      Bridge-Kenntnis, die in diesem Schritt reduziert werden sollte
  - Wirkung:
    - der `DialogueManager` konsumiert jetzt kleinere explizitere
      Extraction-Signale
    - die schwere `message_delta`-Bridge bleibt vorerst bestehen, ist aber
      staerker auf die Case-Truth-Kante begrenzt
    - der Turn-Fluss ist damit naeher am V3-Zielbild:
      Orchestrierung liest kleine Outputs, waehrend tiefere
      Uebergangsprothesen nicht weiter in den Hauptfluss ausstrahlen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/extraction_payload.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - als naechsten V3-Schnitt die verbleibenden direkten Turn-Kontext-
      Mutationen im `DialogueManager` gegen kleinere Stufenvertraege fuer
      Process-State und Readiness pruefen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 80 Datum: 09-06-26 18:28 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - eine dritte Planfassung
      `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
      angelegt
    - dafuer `REFACTOR_PLAN_V2.md` gegen `REFACTOR_PLAN.md`, den aktuellen
      Code und die nun gefundene Datei
      `GENERAL_CODE_ARCHITECTURE_GUIDELINES.md` gehalten
    - die Reihenfolge der Refactor-Folge bewusst neu bewertet:
      zuerst Orchestrierungs- und Systemgrenzen rund um den
      `DialogueManager`, danach die Bridge-Zone um `MessageDelta`, erst
      anschliessend `Call 1` / `Call 2` enger schneiden
    - zusaetzlich eine neue Arbeitsregel fuer irrefuehrende Benennungen
      aufgenommen:
      Verhalten ist waehrend des Refactors wichtiger als der aktuelle Name;
      Renames folgen spaeter nach stabileren Rollen
    - aus den Entwicklerkommentaren in `autodoc/wiki/SYSTEM_OVERVIEW.md`
      gezielt blockbezogene Hints in die einzelnen Refactor-Bloecke
      uebernommen
  - Warum:
    - die vorherige V2-Fassung war in ihrer Boundary-First-Logik gut, aber
      die Reihenfolge noch zu stark auf `Call 2` fokussiert
    - der reale Codefluss spricht eher dafuer, zuerst die sichtbaren
      Systemgrenzen des Turn-Orchestrators und der aktuellen Bridge-Zone zu
      stabilisieren, bevor `Call 2` selbst neu gezogen wird
  - Wirkung:
    - `REFACTOR_PLAN_V3.md` ist jetzt die strategisch geschaerfte
      Arbeitsfassung fuer den naechsten Careena3-Refactor
    - das aktuelle haessliche Uebergangsobjekt darf darin bewusst temporaer
      mitgetragen werden, solange es als klar markierter Transitional Contract
      die Systemgrenzen eher schuetzt als verwischt
    - die gefundene allgemeine Guidelines-Datei ist eingearbeitet, aber
      bewusst niedriger gewichtet als `V2`, `SYSTEM_OVERVIEW.md` und
      `TARGET_MODEL6.md`
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - als ersten praktischen V3-Schritt den Turn-Vertrag rund um
      `DialogueManager` und seine direkten Untergrenzen sezieren und die
      aktuell wirklich noetigen Bridge-Outputs markieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 79 Datum: 09-06-26 18:28 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - im selben Tagesordner eine zweite Planfassung
      `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V2.md`
      angelegt
    - die V2-Fassung schaerft den aktiven Refactor-Rahmen in Richtung
      `boundary-first refactoring` nach:
      nicht jedes Architekturproblem muss sofort geloest werden, sondern
      zuerst sollen Verantwortungsgrenzen und Problemverdichtungen vom Kern
      nach aussen sauber definiert werden
    - zusaetzlich wurden erlaubte Placeholder-/Dummy-Logik und eine
      ausdrueckliche Dokumentationsdisziplin fuer semantisch umgeschnittene
      Module als eigene Arbeitsregeln aufgenommen
  - Warum:
    - fuer die naechsten Careena3-Schritte war eine wichtige Praezisierung
      noetig:
      saubere Grenzziehung ist bereits echter Fortschritt, auch wenn einzelne
      Module fachlich noch nicht voll ausgebaut sind
    - ohne diese Nachschaerfung droht der Refactor wieder in den Druck zu
      geraten, zu frueh unsaubere Scheinfertigstellungen statt sauberer
      Schichtgrenzen zu produzieren
  - Wirkung:
    - `REFACTOR_PLAN_V2.md` ist jetzt die geschaerfte Arbeitsfassung fuer den
      laufenden Careena3-Refactor
    - sichtbare Platzhalter sind darin ausdruecklich erlaubt, solange sie den
      Vertrag schuetzen, kommentiert sind und keine verdeckte Zweitlogik
      aufbauen
    - Modul-Dokumentation gehoert bei semantischen Refactor-Schnitten jetzt
      explizit zur eigentlichen Arbeit dazu
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN_V2.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - den minimalen Call-2-Outputvertrag als ersten praktischen
      Boundary-First-Schritt festziehen und dabei bereits die betroffenen
      Modul-Dokumentationen mitdenken
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 78 Datum: 09-06-26 18:02 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/workbench/2026-06-09/` einen
      neuen aktiven `REFACTOR_PLAN.md` angelegt
    - der neue Plan fuehrt `SYSTEM_OVERVIEW.md`, `TARGET_MODEL6.md`, den
      alten Refactor-Plan, `CODE_REVIEW_FRAMEWORK.md`, aktuellen Chatkontext
      und den realen Python-Code in einem neuen Steuerdokument zusammen
    - der Schwerpunkt wurde von einem allgemeinen Phasenplan staerker auf
      klare finale Verantwortungsbereiche, codebezogene Ist-Einordnung,
      Arbeitsdisziplin und die naechsten echten Architekturhebel
      verschoben
  - Warum:
    - seit dem alten Plan ist das Zielbild klarer geworden und ein grosser
      Teil der frueheren Phase-1-Arbeit ist im Code bereits eingelost
    - fuer die naechsten Schritte wird daher eher ein neuer codegeerdeter
      Verantwortungs- und Vertragsplan gebraucht als eine blosse Fortsetzung
      des frueheren Blockrasters
  - Wirkung:
    - `2026-06-09/REFACTOR_PLAN.md` ist jetzt der neue aktive Refactor-
      Anker fuer Careena3
    - die weitere Reihenfolge ist explizit neu gebuendelt:
      zuerst Call-2-Vertrag und Kontextpolitik,
      dann Extraction-zu-Truth-Bruecke,
      danach Requirement-/Readiness- und Response-Policy-Schichten
    - die fehlende Datei
      `GENERAL_GOOD_ARCHITECHTURE_GUIDELINES.md` ist im Plan transparent
      als nicht auffindbar markiert, ohne die gewuenschte
      Architekturhygiene still wegzulassen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-09/REFACTOR_PLAN.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - als erster praktischer Anschluss den minimalen Call-2-Outputvertrag
      knapp festziehen und danach `llm/context.py`,
      `case_extraction.py` und `resilient_extraction_service.py`
      gezielt dagegen sezieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 74 Datum: 09-06-26 04:15 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in `server/careena_pipeline3/autodoc/wiki/iteration_07/content/` eine
      neue Vergleichsdatei `CURRENT_CODE_VS_SYSTEM_OVERVIEW.md` angelegt
    - darin den aktuellen Codezustand von `server/careena_pipeline3/` und
      `server/careena3.py` gegen die neuere
      `iteration_07/content/SYSTEM_OVERVIEW.md` gehalten
    - die Auswertung trennt sichtbar zwischen bereits eingelosten
      Architekturideen, nur teilweise erreichten Zielbildern und den aktuell
      groessten Bruchstellen
  - Warum:
    - nach der neuen Overview wurde eine direkte Soll-Ist-Gegenpruefung
      gebraucht, damit das Wiki nicht nur Zielbilder sammelt, sondern auch den
      gegenwaertigen Codezustand daran misst
  - Wirkung:
    - `iteration_07/content/` enthaelt jetzt eine eigene Arbeitsfassung, die
      benannt festhaelt, wo Careena3 die Overview schon traegt und wo Safety,
      Confirmation, Merge-Semantik, Readiness und Response-Pfade noch deutlich
      transitional bleiben
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/content/CURRENT_CODE_VS_SYSTEM_OVERVIEW.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei Bedarf aus der Vergleichsdatei eine priorisierte Liste technischer
      Architekturbaustellen ableiten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 75 Datum: 09-06-26 04:29 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in `server/careena_pipeline3/autodoc/wiki/iteration_07/content/` eine
      kompakte Folgedatei
      `CURRENT_CODE_VS_SYSTEM_OVERVIEW_COMPACT.md` angelegt
    - darin die laengere Code-gegen-Overview-Auswertung auf Kurzurteil,
      tragende Staerken, wichtigste Probleme und einen priorisierten
      Folgeschwerpunkt verdichtet
  - Warum:
    - die ausfuehrlichere Vergleichsdatei ist als Arbeitsgrundlage nuetzlich,
      fuer schnellen Rueckgriff wurde aber noch eine kuerzere Lesefassung
      gebraucht
  - Wirkung:
    - `iteration_07/content/` enthaelt jetzt neben der breiten Vergleichsdatei
      auch eine schnelle Entscheidungs- und Orientierungsfassung
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/content/CURRENT_CODE_VS_SYSTEM_OVERVIEW_COMPACT.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei Bedarf aus der kompakten Fassung eine direkte technische
      Priorisierungsliste fuer Refactor-Schritte ableiten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 76 Datum: 09-06-26 04:29 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - die kompakte Vergleichsdatei
      `CURRENT_CODE_VS_SYSTEM_OVERVIEW_COMPACT.md` am Ende noch um einen
      kurzen Block zu den wichtigsten Klassen im aktuellen Code erweitert
  - Warum:
    - die verdichtete Lesefassung sollte nicht nur die Probleme benennen,
      sondern die zentralen Architekturanker im Code direkt referenzieren
  - Wirkung:
    - die kompakte Datei ist jetzt anschlussfaehiger fuer spaetere
      Refactor- oder Review-Arbeit, weil die wichtigsten Klassen sofort
      benannt sind
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/content/CURRENT_CODE_VS_SYSTEM_OVERVIEW_COMPACT.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei Bedarf denselben Klassenblock auch in die laengere Vergleichsdatei
      rueckspiegeln
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 77 Datum: 09-06-26 04:29 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - `CURRENT_CODE_VS_SYSTEM_OVERVIEW_COMPACT.md` noch einmal neu gefasst
    - die Fassung ist jetzt deutlich kompakter, ohne Flags und ohne separaten
      Klassenblock, und bleibt enger bei der eigentlichen Frage, wie weit der
      aktuelle Code den `SYSTEM_OVERVIEW` abbildet
  - Warum:
    - die vorige Kurzfassung war zu nah an der laengeren Vergleichsdatei und
      fuer eine schnelle menschliche Lesefassung noch zu technisch und zu
      markiert
  - Wirkung:
    - die kompakte Datei ist jetzt tatsaechlich eine kurze, gut lesbare
      Soll-Ist-Zusammenfassung statt einer zweiten technisch etikettierten
      Detailfassung
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/content/CURRENT_CODE_VS_SYSTEM_OVERVIEW_COMPACT.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei Bedarf die lange Vergleichsdatei spaeter ebenfalls stilistisch etwas
      entmarkieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 73 Datum: 09-06-26 20:16 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in `server/careena_pipeline3/autodoc/wiki/iteration_07/content/` eine
      neue `SYSTEM_OVERVIEW.md` angelegt
    - die Fassung zieht die Wiki-Iterationen `02` bis `07` zusammen und baut
      den allgemeinen Systemueberblick neu aus:
      mit aktualisiertem Wahrheitsmodell, staerkerer Call-2-/Truth-Kante,
      sichtbaren Soll-Ist-Spannungen und einer engeren Einbettung von
      Recommendation, Safety und Confirmation
  - Warum:
    - `iteration_04` und `iteration_06` trugen bereits fruehere
      Ueberblicksfassungen, aber `iteration_07` besitzt inzwischen genug neues
      Wissen aus Truth-, Architektur- und Verdichtungsdokumenten, um eine neue
      System-Overview auf aktuellem Wiki-Stand zu rechtfertigen
  - Wirkung:
    - `iteration_07/content/` enthaelt jetzt einen neuen zentralen
      Systemueberblick, der besser zum restlichen Ausbau der Iteration passt
      und die Careena-Gesamtlesart mit den spaeter erarbeiteten
      Wahrheits- und Architekturspannungen verknuepft
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/content/SYSTEM_OVERVIEW.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei Bedarf die neue `SYSTEM_OVERVIEW.md` noch gegen einzelne
      Spezialdokumente wie Call-2-Vertrag oder Recommendation-Pfad weiter
      ausfalten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 72 Datum: 09-06-26 20:08 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in `server/careena_pipeline3/autodoc/wiki/iteration_07/content/` eine
      zweite verdichtete Fassung der breiten Architektur-Sammlung angelegt:
      `ARCHITECTURE_IDEAS_DESIGN_PRINCIPLES_AND_APPROACHES_CONDENSED.md`
    - dabei die direkten Quellenlisten entfernt, sich ergaenzende Leitideen
      zusammengefuehrt und echte Soll-Ist- oder Konzeptspannungen explizit als
      `widerspruechlich` markiert
  - Warum:
    - die erste Sammeldatei war bewusst breit und quellennah, sollte jetzt
      aber noch in eine kompaktere Arbeitsfassung ueberfuehrt werden, die
      Ueberschneidungen reduziert und Widersprueche nicht verdeckt
  - Wirkung:
    - `iteration_07/content/` enthaelt jetzt neben der breiten Sammlung auch
      eine staerker zusammengezogene Lesefassung fuer wiederkehrende
      Careena-Prinzipien
    - offene Spannungen etwa bei Safety, Confirmation, Call-2-Groesse und
      Truth-Semantik bleiben dabei sichtbar statt still vereinheitlicht zu
      werden
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/content/ARCHITECTURE_IDEAS_DESIGN_PRINCIPLES_AND_APPROACHES_CONDENSED.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei Bedarf aus der verdichteten Fassung noch ein sehr kurzer
      Kernkatalog mit 8 bis 12 Careena-Prinzipien ziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 71 Datum: 09-06-26 20:00 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in `server/careena_pipeline3/autodoc/wiki/iteration_07/content/` eine
      neue Sammeldatei
      `ARCHITECTURE_IDEAS_DESIGN_PRINCIPLES_AND_APPROACHES.md` angelegt
    - darin wichtige Architekturideen, Designprinzipien und wiederkehrende
      Arbeitsansaetze fuer Careena stichpunktartig aus spaeten Verdichtungen,
      juengeren Careena3-Workbench-Dateien, fruehen Careena3-Vertragsdokus und
      aelteren `automatic_documentation`-Modell- und Worklist-Dokumenten
      zusammengezogen
    - die Punkte jeweils mit Quellenankern versehen, damit die Rueckspruenge in
      den grossen Dokumentbestand lesbar bleiben
  - Warum:
    - das bisherige `iteration_07`-Material war sehr fokussiert auf
      Observation-Identitaet und Merge-Semantik
    - zusaetzlich wurde jetzt ein breiteres Rueckgriffsdokument gebraucht, das
      die uebergreifenden Careena-Ideen aus vielen Entwicklungsstaenden
      zusammenhaelt
  - Wirkung:
    - `iteration_07/content/` enthaelt jetzt neben dem engen
      Truth-Detaildokument auch eine groessere Architektur- und
      Prinzipiensynthese
    - spaetere Wiki-Iterationen koennen damit leichter unterscheiden, welche
      Leitideen wirklich wiederkehren und welche eher lokale Zwischenreparatur
      waren
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/content/ARCHITECTURE_IDEAS_DESIGN_PRINCIPLES_AND_APPROACHES.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - aus dieser Sammlung bei Bedarf noch einzelne Themen in kleinere
      Folgedokumente schneiden, etwa nur `Call 2`, nur
      `Recommendation/Gating` oder nur `Designethik`
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 70 Datum: 09-06-26 19:36 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/wiki/iteration_07/` eine neue
      fokussierte Detailiteration angelegt
    - als zentrales Content-Dokument
      `OBSERVATION_IDENTITY_AND_MERGE_SEMANTICS.md` erstellt, das
      Observation-Identitaet, Update-Arten, Ambiguitaet sowie Konflikt- gegen
      Enrichment-Semantik als eigenen Wahrheitskern zusammenzieht
    - dazu im `WORKING/`-Bereich die direkte Quellenbasis, offene Detailregeln
      und den wahrscheinlichsten Anschluss dokumentiert
  - Warum:
    - nach `iteration_05` und `iteration_06` war der staerkste verbleibende
      offene Hebel die Frage, wie Careena zwischen Extraktion und
      `MedicalCase` dieselbe Observation, Korrektur, Bestaetigung,
      Ergaenzung oder Widerspruch unterscheidet
  - Wirkung:
    - das Wiki besitzt jetzt ein eigenes Detailkerndokument fuer die
      semantische Mitte der Truth-Schicht, ohne die groesseren Kerndokumente
      erneut breit umschreiben zu muessen
    - zugleich bleiben die offenen Detailregeln sichtbar markiert, statt zu
      frueh kanonisiert zu werden
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_07/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - bei Bedarf eine kleine Semantikmatrix fuer `enrich`, `correct`,
      `confirm`, `conflict` und `defer` ausarbeiten und weiter gegen
      Originalquellen sowie realen Codezustand pruefen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 69 Datum: 09-06-26 00:24 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/wiki/iteration_06/` eine
      Ausbauiteration angelegt, die die fuehrenden Kerndokumente
      `SYSTEM_OVERVIEW.md` und `CASE_TRUTH_AND_PROCESS_STATE.md` in neue
      Arbeitsfassungen portiert und gezielt nachschaerft
    - dabei bestehende gesicherte Bloecke weitgehend uebernommen und nur
      solche Stellen ausgebaut, an denen der groessere Dokumentbestand echte
      Praezisierungen fuer bisherige `wahrscheinlich`, `offen` oder
      `widerspruechlich`-Bloecke getragen hat
    - zusaetzlich in `WORKING/` die Ausbaupunkte und Restspannungen dokumentiert
  - Warum:
    - statt immer neue Themenartefakte zu erzeugen, sollte die naechste
      Iteration die bereits tragfaehigen Kerndokumente kontrolliert
      weitertragen und verfeinern
  - Wirkung:
    - das Wiki besitzt jetzt zwei staerkere Copy-forward-Fassungen seiner
      wichtigsten Kerndokumente, mit klareren Aussagen zu
      Dialogue-Manager-Souveraenitaet, task-/mode-sensitivem Call 2,
      Recommendation-/Response-Vertrag, Requirement-Signalen und den
      Wahrheitsgrauzonen zwischen Signal, Prozessspur und Fallwahrheit
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_06/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - entscheiden, ob als naechste Ausbauiteration weiter an denselben
      Kerndokumenten konsolidiert oder gezielt ein Detailkerndokument zu
      `Observation Identity` und `Merge Semantics` eingefuehrt wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 68 Datum: 08-06-26 20:27 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/wiki/iteration_05/` die
      naechste Detailiteration zum inneren Wahrheitsvertrag angelegt
    - als zentrales Content-Dokument
      `CASE_TRUTH_AND_PROCESS_STATE.md` erstellt, das `MedicalCase`,
      `DialogueState`, Nachrichtensignale und abgeleitete
      Entscheidungszustaende sichtbar gegeneinander abgrenzt
    - dabei die Aussagen erneut direkt gegen die urspruenglichen
      Kernquellen gelesen und blockweise mit `gesichert`, `wahrscheinlich`,
      `offen` oder `widerspruechlich` markiert
  - Warum:
    - nach dem allgemeinen `SYSTEM_OVERVIEW` war der naechste sinnvolle
      Schritt, die inneren Wahrheitsgrenzen explizit zu machen, weil davon
      spaetere Merge-, Requirement-, Confirmation- und Recommendation-Dokus
      direkt abhaengen
  - Wirkung:
    - das Wiki besitzt jetzt einen deutlich schaerferen Vertrag dafuer, was
      Fallwahrheit, Prozessspur, turn-lokales Signal und
      Entscheidungsbewertung jeweils sein sollen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_05/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - als naechstes die `Observation Identity` und `Merge Semantics` als
      eigenen Detailkern ausformulieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 67 Datum: 08-06-26 19:32 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/wiki/iteration_04/` die erste
      inhaltlich ernsthafte Careena-Synthese angelegt
    - als zentrales Content-Dokument einen `SYSTEM_OVERVIEW.md` erstellt, der
      Careena im Kern beschreibt und jeden semantischen Textblock sichtbar mit
      `gesichert`, `wahrscheinlich`, `offen` oder `widerspruechlich` markiert
    - im `WORKING/`-Bereich die Quellenbasis, die wichtigsten Spannungen und
      den Anschluss an die naechsten Detaildokumente festgehalten
  - Warum:
    - nach Landschafts-Intake und Kernmarkierung war der naechste Schritt ein
      erster lesbarer Systemueberblick, ohne offene Architekturfragen schon zu
      frueh als fest zu behandeln
  - Wirkung:
    - das Wiki besitzt jetzt einen ersten belastbaren Careena-Kerntext mit
      sichtbarer Evidenzlogik und kann darauf in spaeteren Iterationen gezielt
      Detaildokumente aufbauen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_04/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - den Systemueberblick in einzelne Kerndokumente fuer Call-Architektur,
      Case-Truth/State und Observation-Identitaet entfalten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 66 Datum: 08-06-26 18:30 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/wiki/iteration_03/` die
      naechste Wiki-Iteration als Kernkarten-Schritt angelegt
    - pro Landschaft (`autodoc`, `automatic_documentation`,
      `AgentWorkProtocol`) fuehrende Kerne, wichtige Verdichtungen und
      Referenz- bzw. Driftspuren in einer `SOURCE_KERNEL_MAP.md`
      zusammengezogen
    - zusaetzlich in `WORKING/` die Begruendungen der Kernwahl und den
      Anschluss an eine spaetere erste Careena-Synthese festgehalten
  - Warum:
    - nach dem breiten Intake aus `iteration_02` sollte gemaess Wiki-Prozess
      zuerst sichtbar werden, welche Dokumente fuer die naechsten Iterationen
      wirklich fuehrend gelesen werden sollen
  - Wirkung:
    - das Wiki hat jetzt eine explizite Kernkarte der drei
      Dokumentlandschaften und kann spaetere Content-Iterationen deutlich
      fokussierter auf wenige Quellen stutzen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_03/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - `iteration_04` als erste inhaltlich ernsthafte Careena-Synthese fuer
      einen Systemueberblick auf Basis der markierten Kerndokumente anlegen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 65 Datum: 08-06-26 18:15 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/wiki/iteration_02/` die erste
      echte Wiki-Iteration angelegt
    - `iteration_02` liest `autodoc`, `automatic_documentation` und
      `AgentWorkProtocol` breit als drei unterschiedliche
      Dokumentlandschaften ein
    - in `content/` eine vorsichtige Careena-Kurzbeschreibung und eine erste
      Liste geplanter spaeterer Wiki-Dokumente abgelegt
    - in `WORKING/` Intake-, Zeitstempel-/Namenssignal- und
      Anschlussdokumente fuer den naechsten Wiki-Schnitt angelegt
  - Warum:
    - `iteration_01` sollte nur noch als leere Blaupause dienen und der erste
      echte Wiki-Schritt zunaechst nicht sofort kanonisieren, sondern die
      Quellenlandschaften kontrolliert einordnen
  - Wirkung:
    - das Wiki besitzt jetzt eine erste belastbare Arbeitsiteration, die den
      Entwicklungsraum von Careena grob kartiert und den naechsten
      Dokumentationsschnitt vorbereitet
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/iteration_02/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - pro Landschaft die fuehrenden Kerndokumente explizit markieren und
      danach die priorisierten Zieldokumente des Wikis inhaltlich ausarbeiten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 63 Datum: 08-06-26 ===
=== CHANGE NUMBER: 64 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - die neue Wiki von einer fruehen Zielsystem-Synthese auf einen
      Intake-Arbeitsraum zurueckgebaut
    - bisherige kanonische Architekturdateien inhaltlich auf `deferred`
      gesetzt und stattdessen Intake-Dokumente fuer Landschaften,
      Klassifikation, Zeitstempel-/Namenssignale und Kernkandidaten angelegt
  - Warum:
    - die inhaltliche Synthese war gegenueber dem Quellenbestand zu frueh und
      zog den Fokus zu schnell auf spaete Target-Model-Dateien
  - Wirkung:
    - die Wiki arbeitet jetzt zuerst als sauberer Intake- und
      Klassifikationsraum fuer `automatic_documentation`,
      `AgentWorkProtocol` und `autodoc`
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - die drei Landschaften weiter gegenlesen und aktive Kerne,
      Driftspuren und moegliche Ueberschreibungen noch praeziser markieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 63 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - unter `server/careena_pipeline3/autodoc/wiki/` eine neue Architektur-Wiki
      mit Masterdoc, Komponentenmodell, Truth-Modell, Flow-Dokumenten,
      Sollabweichungen, offenen Fragen und Traceability-Artefakten angelegt
    - zusaetzlich einen `WORKING/`-Bereich fuer Intake, Kernel-Extraktion,
      Zeitlinie und erste Iterationsspur aufgebaut
  - Warum:
    - die vorhandenen Dokumentquellen aus Careena3, aelterer
      `automatic_documentation` und `AgentWorkProtocol` sollten in ein
      lesbares, kanonisches Sollbild ueberfuehrt werden, ohne den historischen
      Widerspruchsraum zu verstecken
  - Wirkung:
    - es gibt jetzt einen klaren Einstiegspunkt fuer das beabsichtigte
      Careena-System und eine nachvollziehbare Ablage fuer Quellenlogik,
      Konflikte und Zwischensynthesen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/wiki/`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
  - Naechster Punkt:
    - die Wiki in weiteren Sichtungsrunden gegen die verbleibenden
      Careena3-Workbench-Dateien und offenen Konfliktzonen nachschaerfen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 62 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in der Workbench eine leere Matrix-Datei
      `CAREENA3_CALL2_WORK_AREAS_MATRIX.md` angelegt
    - darin die geplanten Call-2-Arbeitsbereiche als blankes Arbeitsgeruest
      vorbereitet
  - Warum:
    - vor weiterem Phase-2-Umbau soll die Zerlegung von Call 2 in
      Aufgabenbereiche separat und gezielt nachgeschaerft werden
  - Wirkung:
    - es gibt jetzt ein einfaches Geruest, das in einem separaten Chat
      fachlich oder architektonisch weiter ausgearbeitet werden kann
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_CALL2_WORK_AREAS_MATRIX.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - die Matrix inhaltlich schaerfen und danach den Kontextbuilder entlang
      dieser Bereiche neu zuschneiden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 59 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in der Workbench eine konkrete Phase-2-Vorschlagsdatei
      `CAREENA3_PHASE2_CALL2_PROPOSAL.md` angelegt
    - darin den Soll-Zuschnitt fuer Call 2 in drei Teilen verdichtet:
      minimaler Kontext, kleinerer primaerer Output und engere Rolle fuer
      objektweise Normalisierung bzw. einen moeglichen zweiten LLM-Schritt
  - Warum:
    - nach der Analyse von Prompt, Kontextbuilder, Normalisierungspfad und
      Logs war genug Klarheit da, um Phase 2 nicht nur als Problemaufnahme,
      sondern als konkreten Zielvorschlag zu formulieren
  - Wirkung:
    - es gibt jetzt ein explizites Arbeitsziel fuer den naechsten Phase-2-
      Schritt, ohne schon den grossen Umbau zu beginnen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_PHASE2_CALL2_PROPOSAL.md`
  - Naechster Punkt:
    - entscheiden, ob wir zuerst den primaeren Call-2-Kontext oder zuerst den
      zweiten Normalisierungspfad auf den kleineren Vertrag zuschneiden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 60 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - eine neue Workbench-Datei
      `CAREENA3_PHASE2_CALL2_PROPOSAL_REVISED.md` angelegt
    - darin den bisherigen Phase-2-Call-2-Vorschlag gegen das aktuelle
      Review-Ergebnis ueberarbeitet statt nur additiv erweitert
    - besonders geschaerft:
      Aufgabenbereiche von Call 2, Rolle des Kontextbuilders und der Status des
      grossen zweiten LLM-Normalizers als Abloesekandidat
  - Warum:
    - das Review nach `CODE_REVIEW_FRAMEWORK.md` hat gezeigt, dass der alte
      Vorschlag in der Richtung richtig war, aber den Aufgabenmix und die
      Vollschema-Re-Emission noch nicht hart genug benannt hat
  - Wirkung:
    - Phase 2 hat jetzt ein klareres und reviewgestuetztes Zielbild fuer die
      naechsten Schritte rund um Call 2
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_PHASE2_CALL2_PROPOSAL_REVISED.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - entscheiden, ob wir als ersten echten Phase-2-Codezug den primaeren
      Call-2-Kontext reduzieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 61 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - im Refactor-Plan fuer Phase 2 einen kurzen Exkurs-Vermerk ergaenzt
    - darin festgehalten, dass Call 2 vor weiterem Codeumbau kurz ueber
      Review- und Workbench-Dokumente neu geschaerft wird
    - die dafuer verwendeten Dokumente direkt im Plan benannt
  - Warum:
    - der aktuelle Phase-2-Schritt ist bewusst ein kurzer
      Architektur-/Vertragsabgleich, damit die naechsten Codeaenderungen am
      eigentlichen Hebel ansetzen
  - Wirkung:
    - im Plan ist jetzt sichtbar, warum Phase 2 gerade einen dokumentgestuetzten
      Exkurs macht und auf welcher Grundlage der naechste Umbau entschieden
      wird
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - den primaeren Call-2-Kontext als ersten echten Phase-2-Codezug
      reduzieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 62 Datum: 08-06-26 14:04 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in `autodoc/` eine neue minimalistische Datei `CHAT_HISTORY.md`
      angelegt
    - das Format bewusst schlank gehalten:
      Zeitstempel pro Eintrag, Nutzertext 1:1, Antwort kurz in ein bis zwei
      Saetzen
  - Warum:
    - zusaetzlich zur stark komprimierten `CHAT_COMPRESSION.md` wird eine
      fast woertliche, aber dennoch knappe Verlaufshistorie fuer den Chat
      gebraucht
  - Wirkung:
    - relevante Gespraechsschritte koennen jetzt in `autodoc/` auch als
      einfache Chat-History nachgelesen werden, ohne den groesseren
      Regelapparat der anderen Doku-Dateien mitzuschleppen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/CHAT_HISTORY.md`
    - `server/careena_pipeline3/autodoc/CHANGE_LOG.md`
    - `server/careena_pipeline3/autodoc/CHAT_COMPRESSION.md`
  - Naechster Punkt:
    - neue Verlaufseintraege bei kuenftigen relevanten Chat-Schritten im
      selben schlanken Stil fortfuehren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 1 Datum: 07-06-26 03:39 ===
  - Kategorie:
    - `rework`
  - Bereich:
    - `backend`
  - Aenderung:
    - Architekturvertrag fuer `careena_pipeline3` angelegt und das neue Paket
      mit `core`, Turn-Modellen, `SafetyState` und einem ersten
      `DialogueManager`-Geruest aufgebaut
  - Warum:
    - Die Migration soll entlang des Zielbilds aus Model 5 starten und nicht
      durch eine unreflektierte Spiegelung der Altstruktur
  - Wirkung:
    - `careena_pipeline3` hat jetzt eine belastbare Grundstruktur mit klarer
      Orchestrator-Rolle und einem 1:1 erhaltenen generischen Kern als
      Ausgangspunkt fuer die weitere Migration
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/ARCHITECTURE_CONTRACT.md`
    - `server/careena_pipeline3/core/`
    - `server/careena_pipeline3/models/`
    - `server/careena_pipeline3/application/`
  - Naechster Punkt:
    - Phase 2 vorbereiten: Manager-Vertraege und erste Application-Komposition
      ausformulieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 2 Datum: 07-06-26 03:41 ===
  - Kategorie:
    - `rework`
  - Bereich:
    - `backend`
  - Aenderung:
    - Manager-Vertraege fuer `Entry`, `Extraction`, `CaseState`, `Safety`,
      `Response` und `Confirmation` angelegt und den `DialogueManager`
      auf eine explizite Turn-Sequenz mit diesen Abhaengigkeiten umgestellt
  - Warum:
    - Die Zielarchitektur aus Model 5 soll nicht nur dokumentiert, sondern
      frueh als echte Kompositionsstruktur im Code verankert werden
  - Wirkung:
    - `careena_pipeline3` besitzt jetzt einen klaren orchestrierenden Einstieg,
      an den die fachliche Migration der Altlogik schrittweise angeschlossen
      werden kann
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/`
    - `server/careena_pipeline3/models/turn/`
  - Naechster Punkt:
    - stabile fachliche Modelle aus `careena_pipeline` fuer Case und Dialogue
      in die neue Struktur uebernehmen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 3 Datum: 07-06-26 03:45 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - stabile Domain- und Common-Modelle fuer `MedicalCase`, `DialogueState`,
      `Subject`, `CaseObservation`, Observation-Daten und gemeinsame Typen in
      `careena_pipeline3` angelegt und `TurnContext` auf diese neue Modellbasis
      umgestellt
  - Warum:
    - Die naechsten Migrationsschritte brauchen echte Fachvertraege in
      `careena_pipeline3`, ohne direkt an die alten Paketgrenzen gekoppelt zu
      bleiben
  - Wirkung:
    - Die neue Pipeline kann kuenftig Merge-, Focus- und State-Logik gegen
      eigene Modelle aufbauen; gleichzeitig wurde der alte
      RequirementRef-Zuschnitt im `DialogueState` bewusst vereinfacht
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/common/`
    - `server/careena_pipeline3/models/domain/`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/models/__init__.py`
  - Naechster Punkt:
    - `CaseMerger`, `DialogueFocusSync` und darauf aufbauend den neuen
      `CaseStateManager` gegen die migrierten Modelle anschliessen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 4 Datum: 07-06-26 03:46 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - `DialogueFocusSync` nach `careena_pipeline3` migriert und den neuen
      `CaseStateManager` so erweitert, dass Case- und Focus-Verknuepfungen
      bereits gegen die neue Modellbasis synchronisiert werden
  - Warum:
    - Die neue Pipeline soll nicht nur Struktur besitzen, sondern frueh erste
      stabile State-Synchronisation aus der Altlogik uebernehmen
  - Wirkung:
    - `TurnContext`, `MedicalCase` und `DialogueState` werden im neuen System
      bereits konsistent gekoppelt; damit ist eine wichtige Vorstufe fuer den
      spaeteren Merge-Pfad gelegt
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/dialogue_focus_sync.py`
    - `server/careena_pipeline3/domain/__init__.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
  - Naechster Punkt:
    - neuen Turn-Delta-Vertrag modellieren, damit `CaseMerger` und spaeter
      echte Extraction-Updates sauber angeschlossen werden koennen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 5 Datum: 07-06-26 03:54 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - neuen `MessageDelta`-Vertrag fuer Turn-Ergebnisse angelegt,
      `CaseMergePolicy` und `CaseMerger` gegen diesen Vertrag nach
      `careena_pipeline3` migriert und den `ExtractionManager` sowie
      `CaseStateManager` auf diesen Pfad angeschlossen
  - Warum:
    - Die weitere Migration soll echte fachliche Zustandsuebergaenge auf einer
      neuen Vertragsflaeche aufbauen statt den alten `MessageUpdate`-Sammeltyp
      direkt weiterzutragen
  - Wirkung:
    - `careena_pipeline3` besitzt jetzt einen ersten vollstaendigen Pfad von
      Extraction-Output ueber Delta-Vertrag bis zur kanonischen
      Case-State-Mutation
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/message_delta.py`
    - `server/careena_pipeline3/domain/case_merge_policy.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
  - Naechster Punkt:
    - Entry-, Safety- und Workflow-Modelle weiter migrieren, damit der
      Orchestrator schrittweise echtes Altverhalten uebernehmen kann
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 6 Datum: 07-06-26 03:58 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - Architekturvertrag und Refactoring-Plan um ausdrueckliche Guardrails
      gegen medizinische Sonderfall-Heuristiken, Keyword-Routing und andere
      fachlich unsaubere Alt-Workarounds erweitert
  - Warum:
    - Die weitere Migration soll nicht stillschweigend fragwuerdige
      medizinische Entscheidungslogik konservieren, sondern strikt gegen das
      Zielbild aus Model 5 und gegen fachliche Sauberkeit geprueft werden
  - Wirkung:
    - Fuer die naechsten Phasen ist jetzt verbindlich festgehalten, dass nur
      strukturell sinnvolle Logik frueh migriert wird und medizinische
      Hardcodings zuerst ausgesiebt oder neu begruendet werden muessen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/ARCHITECTURE_CONTRACT.md`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/REFACTORING_PLAN.md`
  - Naechster Punkt:
    - bei der naechsten fachlichen Migration zuerst Altlogik gegen diese
      Ausschlussliste und gegen `TARGET_MODEL5.md` abgleichen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 7 Datum: 07-06-26 04:08 ===
  - Kategorie:
    - `rework`
  - Bereich:
    - `backend`
  - Aenderung:
    - bisher migrierte Merge- und Orchestrierungsstrecke bereinigt:
      injury-spezifische Merge-Sonderheuristik entfernt, `DialogueManager`
      auf die Reihenfolge aus Model 5 umgestellt und den `SafetyManager` in
      Raw-, Extraction- und Case-Checks sauber getrennt
  - Warum:
    - Der Review hat gezeigt, dass sich bereits fachlich unsaubere Legacy-
      Abkuerzungen und eine falsche Turn-Reihenfolge in `careena_pipeline3`
      verfestigt haben
  - Wirkung:
    - Der aktuelle Stand folgt jetzt wieder klarer der Zielarchitektur, und
      medizinische Sonderfalllogik wird nicht mehr ueber den Merge-Pfad oder
      versteckte Ablaufreihenfolgen konserviert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/case_merge_policy.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/application/managers/safety_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/models/turn/context.py`
  - Naechster Punkt:
    - naechste fachliche Kandidaten nur noch nach ausdruecklichem Target-
      Model-5-Abgleich und gegen die medizinische Ausschlussliste migrieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 8 Datum: 07-06-26 04:13 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - Screening-Bericht fuer die naechsten Legacy-Kandidaten aus Entry- und
      Workflow-Naehe erstellt und darin sauber zwischen gut migrierbaren,
      spaeter vorsichtig zu migrierenden und aktuell auszuschliessenden Teilen
      unterschieden
  - Warum:
    - Die weitere Migration soll nach dem Aufraeumen nicht wieder in
      Bauchentscheidungen oder implizite Altlastenuebernahmen zurueckfallen
  - Wirkung:
    - Es ist jetzt schriftlich festgehalten, dass als naechster fachlicher
      Schritt nur der echte Call-1-/Entry-Pfad priorisiert werden soll,
      waehrend Follow-up-Shortcuts, Recommendation-Textmarker und grosse
      Workflow-Sammelservices vorerst draussen bleiben
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/ENTRY_WORKFLOW_SCREENING.md`
  - Naechster Punkt:
    - `LLMIntentGatewayExtractor` und eine saubere Call-1-Fehlerbehandlung in
      den `EntryManager` uebernehmen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 9 Datum: 07-06-26 04:17 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - echten Call-1-Pfad fuer `careena_pipeline3` angelegt: Workflow-Modelle
      fuer den Intent Gateway, Call-1-Kontextbuilder, Prompt, LLM-Extractor
      und schlanke Fehlerkapsel eingefuehrt und den `EntryManager` vom
      Scaffold auf diese neue Intake-Strecke umgestellt
  - Warum:
    - Nach dem Screening sollte als naechster fachlicher Schritt nur die
      saubere Entry-Logik aus Model 5 uebernommen werden, ohne Follow-up- oder
      Recommendation-Ballast mitzuschleppen
  - Wirkung:
    - `EntryManager` kann jetzt echte Call-1-Klassifikation auswerten und
      zwischen `extraction_required`, `out_of_scope` und
      `cannot_assess` unterscheiden, auch wenn die konkrete Runtime noch nicht
      verdrahtet ist
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/`
    - `server/careena_pipeline3/llm/`
    - `server/careena_pipeline3/application/services/intent_classification_service.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
  - Naechster Punkt:
    - Runtime-/Bootstrap-Seite so erweitern, dass der neue `EntryManager`
      einen echten `LLMIntentGatewayExtractor` injiziert bekommt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 10 Datum: 07-06-26 04:20 ===
  - Kategorie:
    - `config`
  - Bereich:
    - `backend`
  - Aenderung:
    - minimale Runtime- und Bootstrap-Verdrahtung fuer `careena_pipeline3`
      angelegt und dabei den neuen Call-1-Pfad bis in einen injizierten
      `EntryManager` durchverbunden; zusaetzlich einen einfachen Session-Store
      als Infrastrukturbaustein eingefuehrt
  - Warum:
    - Der neue `EntryManager` sollte nicht nur strukturell existieren, sondern
      ueber `build_pipeline_runtime()` und `build_default_services()` bereits
      sauber mit einem echten `LLMIntentGatewayExtractor` versorgt werden
  - Wirkung:
    - `careena_pipeline3` besitzt jetzt eine erste lauffaehige Service-
      Verdrahtung fuer Call 1, die spaetere HTTP- und Tooling-Anbindung
      vorbereitet, ohne schon die komplette Legacy-Runtime zu kopieren
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/runtime.py`
    - `server/careena_pipeline3/bootstrap.py`
    - `server/careena_pipeline3/infrastructure/session_store.py`
    - `server/careena_pipeline3/infrastructure/__init__.py`
    - `server/careena_pipeline3/application/managers/__init__.py`
  - Naechster Punkt:
    - naechsten sauberen Fachblock fuer `ExtractionManager` vorbereiten oder
      alternativ den Status gegen den Refactor-Plan festziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 11 Datum: 07-06-26 04:24 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - Call-2-Redesign-Leitplanke im Architekturvertrag und Refactoring-Plan
      verankert und einen eigenen Zielvertragsentwurf fuer den kuenftigen
      Extraction-Output von `careena_pipeline3` angelegt
  - Warum:
    - Der naechste groessere Fachblock soll nicht versehentlich ueber die alte
      medizinische Datenmodellierung aufgebaut werden; stattdessen braucht Call
      2 zuerst eine saubere Zielstruktur
  - Wirkung:
    - `MessageDelta` ist jetzt sichtbar als Uebergangsvertrag markiert, und
      fuer Call 2 gibt es eine getrennte Zielrichtung ueber
      `ExtractionResult`/`ExtractedObservation` statt direkte Altvertrags-
      Konservierung
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/ARCHITECTURE_CONTRACT.md`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/REFACTORING_PLAN.md`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/CALL2_REDESIGN_NOTES.md`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/CALL2_TARGET_CONTRACT.md`
    - `server/careena_pipeline3/models/extraction/`
    - `server/careena_pipeline3/models/turn/message_delta.py`
  - Naechster Punkt:
    - Adapter zwischen neuem Extraction-Zielvertrag und aktuellem
      `MessageDelta`-/Merge-Pfad entwerfen oder den `ExtractionManager`
      schrittweise darauf ausrichten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 12 Datum: 07-06-26 04:37 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - die bisherige Call-2-Scaffold-Strecke in `careena_pipeline3` durch eine
      echte Service- und Runtime-Verdrahtung ersetzt: `DialogueManager`
      uebergibt jetzt den Turn-Kontext an den `ExtractionManager`, dieser
      verwendet ein injizierbares `ExtractionService`, und die Runtime baut
      dafuer erstmals einen `LLMCaseExtractionExtractor`
  - Warum:
    - die Migration sollte aus der reinen Modell-/Planphase heraus und in
      einen praktisch ausfuehrbaren Call-2-Pfad uebergehen, ohne dabei die
      alte medizinische Speziallogik zu konservieren
  - Wirkung:
    - `careena_pipeline3` besitzt jetzt einen konservativen Call-2-Einstieg
      auf Basis des neuen `ExtractionResult`-Vertrags; der Uebergang in das
      alte `MessageDelta` bleibt sichtbar als Adapter, und unresolved
      follow-up-Bedarfe werden nur noch generisch als
      `requirement_resolution` signalisiert statt fachlich hartcodiert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/safety_manager.py`
    - `server/careena_pipeline3/application/services/extraction_service.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/careena_pipeline3/llm/__init__.py`
    - `server/careena_pipeline3/llm/prompts/__init__.py`
    - `server/careena_pipeline3/runtime.py`
  - Naechster Punkt:
    - den Call-2-Output gegen Altverhalten und Target Model 5 pruefen und
      danach gezielt entscheiden, welche Teile aus Legacy-Extraktion,
      Requirement-Logik und Logging ueberhaupt in den neuen Pfad gehoeren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 12 Datum: 07-06-26 18:05 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - Requirement-/Readiness-Pfad so umverdrahtet, dass die Subjekt-
      Klaerungslogik nicht mehr eigenstaendig an beliebigen Case-Indizien
      vorbeientscheidet, sondern die expliziten Personen-Signale aus Call 1
      bis in `RequirementPolicy` und `AssessmentReadinessEvaluator`
      durchgereicht bekommt
  - Warum:
    - Der bisherige Zustand lief dem Zielbild aus Target Model 5 entgegen:
      Call 1 hat bereits eine zentrale Einordnung der Personenlage, waehrend
      Requirement/Readiness spaeter erneut implizit geraten haben, ob ein
      `subject`-Follow-up noetig sei; genau diese verdeckte Nebenlogik sollte
      entfernt werden
  - Wirkung:
    - `DialogueManager` bleibt die zentrale Orchestrierungsstelle fuer die
      Turn-Entscheidung
    - `RecommendationStateService` und `RequirementPolicy` bewerten
      Personenunklarheit jetzt auf Basis des expliziten Turn-Vertrags
    - wenn Call 1 keine Personenreferenz oder keine Unklarheit meldet, soll
      der Downstream nicht mehr selbststaendig ein `subject`-Follow-up
      erzwingen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/services/dialogue_state_service.py`
    - `server/careena_pipeline3/application/services/recommendation_state_service.py`
    - `server/careena_pipeline3/application/services/readiness_evaluator.py`
    - `server/careena_pipeline3/domain/requirement_policy.py`
  - Naechster Punkt:
    - mit dieser sauberen Vertragskante zurueck an Call 2:
      Aufgabenreihe/Payload weiter aus dem Call-1-Vertrag ableiten und danach
      Requirement-/Readiness-Regeln nur noch gegen das Zielbild aus Model 5
      nachschaerfen, nicht gegen Legacy-Nebenverhalten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 13 Datum: 07-06-26 04:44 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - eine kleine `careena_pipeline3`-Observability-Basis und eine
      resiliente Call-2-Fehlergrenze eingefuehrt; der neue
      `LLMCaseExtractionExtractor` loggt jetzt seinen Kontext, und ein
      `ResilientExtractionService` faengt LLM-/Schema-Fehler ab und liefert
      stattdessen einen vertragstreuen Fallback
  - Warum:
    - aus der Legacy-Call-2-Strecke war vor allem die Fehlerabgrenzung
      brauchbar; fuer die Migration brauchen wir frueh sichtbare Debug-Spuren
      und einen stabilen Turn-Vertrag, ohne wieder die alten Follow-up-
      Workarounds zu kopieren
  - Wirkung:
    - Call 2 faellt bei Extraktionsfehlern nicht unkontrolliert aus dem
      Orchestrator; stattdessen bleibt der neue `ExtractionResult` erhalten,
      offene Rueckfragen koennen generisch markiert werden, und fuer spaetere
      Tests ueber Runtime oder `server/careena3.py` existiert bereits ein
      eigener Pipeline-3-Debug-Logpfad
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/infrastructure/logging.py`
    - `server/careena_pipeline3/infrastructure/__init__.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/runtime.py`
    - `server/careena_pipeline3/bootstrap.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/REFACTORING_PLAN.md`
  - Naechster Punkt:
    - als naechstes die Requirement-/Follow-up-Altlogik aus Call 2 kritisch
      zerlegen und nur den Teil uebernehmen, der als saubere zentrale
      Steuerungslogik im neuen Dialogue-/Response-Pfad bestehen kann
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 13 Datum: 07-06-26 18:18 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Call-2-Systemprompt von einer statischen Monolith-Vorgabe auf eine
      task-basierte Prompt-Komposition umgestellt; der Prompt wird jetzt pro
      Turn aus Basisvertrag plus angeforderter Aufgabenreihe aufgebaut
  - Warum:
    - Target Model 5 beschreibt Call 2 als zusammengesetzten
      Extraktionsschritt; die bisherige Verdrahtung kannte zwar schon
      `call2_tasks`, der eigentliche Prompt blieb aber noch zu sehr ein
      allgemeiner Alles-Extractor
  - Wirkung:
    - Call 2 bleibt ein einzelner LLM-Call
    - die operative Extraktionsanweisung folgt jetzt explizit der von Call 1
      gelieferten Task-Reihenfolge
    - symptom-, injury-, measurement-, medication- und subject-Kontext werden
      nur noch ueber eigene Task-Bloecke aktiviert statt nur implizit ueber
      allgemeine Verbote
    - der geloggte Call-2-Kontext zeigt jetzt auch den final aufgebauten
      Systemprompt zur besseren Debug-Pruefung
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/llm/prompts/__init__.py`
  - Naechster Punkt:
    - pruefen, ob die Requirement-/Readiness-Seite nur noch auf sauberem
      Extraction-Output aufsetzt und danach den Response-Pfad weiter von
      reinem Scaffold Richtung echte Zielrollen schieben
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 14 Datum: 07-06-26 04:49 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - eine erste zentrale Requirement-/Follow-up-Steuerung fuer
      `careena_pipeline3` eingefuehrt: offene und erfuellte Anforderungen
      werden jetzt aus dem kanonischen `MedicalCase` plus Fokuszustand
      abgeleitet, in den `DialogueState` synchronisiert und im
      `ResponseManager` als eigener `ask_followup`-Pfad ausgewertet
  - Warum:
    - die Legacy-Logik zeigte, dass der wertvolle Kern nicht im Slot-Filling
      selbst liegt, sondern in der zentralen Ableitung offener
      Informationsbedarfe; genau dieser Teil soll nach Model 5 in die
      Manager-Steuerung wandern statt als verstreute Spezialbehandlung
  - Wirkung:
    - `careena_pipeline3` haengt Follow-up-Bedarf nun nicht mehr nur an
      Extraktions-Hinweisen; wenn Module fehlen oder unvollstaendig sind,
      koennen sie aus dem Case rekonstruiert werden, und die Dialogsteuerung
      bekommt einen klareren zentralen Rueckfragepfad ohne alte Slot-Fill-
      Workarounds
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/requirement_policy.py`
    - `server/careena_pipeline3/application/services/dialogue_state_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/domain/__init__.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
  - Naechster Punkt:
    - als naechstes pruefen, welche Teile aus Readiness/Gating aus Legacy noch
      als zentrale Response-/Recommendation-Steuerung taugen und welche nur
      schwache Datenmodellierung kaschieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 14 Datum: 07-06-26 18:28 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - die Extraktionskante in `ResilientExtractionService` um eine kleine
      Vertragsnormalisierung erweitert, damit unangeforderte Subject-
      Platzhalter aus Call 2 nicht weiter in den Rest der Pipeline laufen
  - Warum:
    - im Testlog zeigte Call 2 trotz fehlendem
      `resolve_subject_context`-Task ein `subject`-Objekt mit
      `relation: unknown`; das war kein akuter Laufzeitfehler, aber
      unnÃ¶tiger Altballast gegen die neue task-basierte Extraktionsform
  - Wirkung:
    - wenn `resolve_subject_context` nicht angefordert wurde, werden
      leere/`unknown`-Subject-Platzhalter verworfen
    - unangeforderte `subject`-/`subject_age`-Fragen werden an derselben
      Vertragskante entfernt
    - die nachgelagerten Manager sehen dadurch eher den explizit bestellten
      Extraktionsumfang statt LLM-Default-Strukturen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
  - Naechster Punkt:
    - erneut im Server-Log pruefen, ob Call 2 bei reinem Symptom-Task jetzt
      wirklich ohne Subject-Ballast durchlaeuft und danach den Response-Pfad
      weiter in Richtung Zielrolle ausbauen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 15 Datum: 07-06-26 04:58 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - einen schlanken Readiness-Kern fuer `careena_pipeline3` eingefuehrt und
      in den `ResponseManager` integriert; die neue Auswertung basiert auf
      kanonischem `MedicalCase`, Fokuszustand und zentralen Pflichtfeldern,
      nicht auf dem alten Recommendation-Gate-Mix aus Fragekatalog,
      Aktionswahl und UI-Naehe
  - Warum:
    - im Legacy-System steckt in `readiness` ein brauchbarer Kern
      (fehlende Pflichtinfos), waehrend `recommendation_gate` viele wilde
      Prozess- und Textannahmen mitschleppt; mit der Target-Model-5-Brille
      soll nur der zentrale Steuerungsteil bleiben
  - Wirkung:
    - `careena_pipeline3` kann jetzt konservativ unterscheiden zwischen
      `cannot_assess`, `ask_followup`, `continue` und spaeter `recommend`,
      ohne die alte Gate-Schicht zu importieren; ausserdem werden eventuelle
      Recommendation-Signale am `DialogueState` mitgefuehrt statt implizit zu
      verschwinden
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/readiness.py`
    - `server/careena_pipeline3/models/workflow/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/application/services/readiness_evaluator.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/domain/requirement_policy.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
  - Naechster Punkt:
    - als naechstes pruefen, wie ein expliziter Recommendation-Trigger nach
      Model 5 aussehen soll und ob dafuer eher Entry-/Dialogue-Signale oder
      ein spaeter eigener Routing-Call die sauberere Quelle sind
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 15 Datum: 07-06-26 18:37 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - `pending_followup` im `DialogueManager` explizit zwischen
      persistiertem `DialogueState` und turn-lokalem `TurnContext`
      synchronisiert
  - Warum:
    - das Testlog zeigte einen sauberen Follow-up-Fehler im Laufvertrag:
      `DialogueState.pending_followup` war nach dem ersten Turn gesetzt, aber
      Entry- und Extraction-Pfad bekamen im naechsten Turn trotzdem
      `pending_slot: null`; dadurch wurde eine knappe Antwort wie `gestern`
      faelschlich als neue freie Nachricht statt als Antwort auf einen offenen
      Slot behandelt
  - Wirkung:
    - Follow-up-Antworten koennen jetzt den offenen Slot wieder in Call 1 und
      Call 2 hineintragen
    - der `DialogueManager` uebernimmt diese Kopplung zentral, statt dass
      einzelne Manager implizit raten muessen, ob ein Follow-up offen war
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
  - Naechster Punkt:
    - erneut mit knappem Follow-up-Test gegen das Server-Log pruefen, ob
      `pending_slot` im zweiten Turn jetzt wirklich gesetzt ist und ob daraus
      wieder ein sauberes Case-Update statt `cannot_assess` wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 16 Datum: 07-06-26 05:02 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - die Architektur fuer Recommendation-State in `careena_pipeline3`
      getrennt aufgezogen: `recommendation_requested` und
      `recommendation_ready` sind jetzt eigene Zustandsachsen, ein neuer
      `RecommendationStateService` synchronisiert die Readiness-basierten
      Flags, und der `ResponseManager` konsumiert diese nur noch statt sie
      selbst herzuleiten
  - Warum:
    - vor jeder spaeteren medizinischen Modellierung oder Recommendation-
      Ausarbeitung braucht die Pipeline erst eine saubere Architektur dafuer,
      dass Nutzerwunsch und Informationsreife nicht dasselbe sind
  - Wirkung:
    - `careena_pipeline3` kann jetzt explizit unterscheiden zwischen
      "Nutzer will Empfehlung" und "System ist dafuer informationsseitig
      bereit"; dadurch bleibt die spaetere Recommendation-Logik austauschbar,
      ohne den Dialogue- oder Response-Pfad erneut umzubauen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/recommendation_state_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/models/domain/dialogue.py`
    - `server/careena_pipeline3/models/turn/context.py`
  - Naechster Punkt:
    - als naechstes den expliziten Trigger fuer `recommendation_requested`
      sauber im neuen System verorten oder alternativ den Test-/Server-Einstieg
      `server/careena3.py` anlegen, sobald wir den Architekturstand praktisch
      pruefen wollen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 16 Datum: 07-06-26 18:49 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Response-Block in `careena_pipeline3` sauberer entlang Model 5
      zugeschnitten: `ResponseManager` waehlt jetzt den Antwortpfad, waehrend
      ein neuer `ResponseTextBuilder` den konkreten Wortlaut baut
  - Warum:
    - bisher lagen Pfadwahl und Antworttext noch als gemeinsames Scaffold in
      einer Klasse; das war funktional okay, aber architektonisch noch zu nah
      an der alten Vermischung aus Policy und Rendering
  - Wirkung:
    - `ResponseManager` traegt jetzt primaer die Turn-Policy
    - Follow-up-, Emergency-, Out-of-scope-, Cannot-assess-, Continue- und
      Recommendation-Texte werden ueber einen separaten Builder erzeugt
    - die `continue`-Spur ist im Trace nicht mehr als reines Scaffold markiert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena_pipeline3/application/services/__init__.py`
  - Naechster Punkt:
    - pruefen, ob die aktuelle Follow-up-Textauswahl und die Continue-/Cannot-
      assess-Texte fuer die neue Architektur ausreichen oder ob der naechste
      Schritt ein eigener Response-Renderer fuer spaetere Recommendation- und
      API-Varianten sein soll
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 17 Datum: 07-06-26 05:16 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - den expliziten Recommendation-Request-Trigger im Entry-Pfad verortet:
      ein neuer `RecommendationRequestService` erkennt konservativ klare
      Nutzeranfragen nach "was tun / wohin", `EntryDecision` traegt dieses
      Signal mit, und der `DialogueManager` uebernimmt es frueh in den
      `DialogueState`
  - Warum:
    - der Nutzerwunsch nach einer Empfehlung ist ein Eintrittssignal und soll
      architektonisch nicht erst spaeter aus Merge-, Extraction- oder
      Response-Logik rekonstruiert werden
  - Wirkung:
    - `careena_pipeline3` unterscheidet jetzt nicht nur konzeptionell, sondern
      auch technisch sauber zwischen Recommendation-Request des Nutzers und
      spaeterer Recommendation-Readiness; der Trigger sitzt frueh und bleibt
      ueber den Turn hinweg stabil erhalten
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/recommendation_request_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
  - Naechster Punkt:
    - naechsten Architekturblock fuer Testbarkeit und Integrationspfad
      entscheiden, also entweder `server/careena3.py` anlegen oder zuerst die
      Response-/Routing-Schnittstellen weiter scharfziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 17 Datum: 07-06-26 19:02 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - den persistierten Session-State endlich in den echten Turn-Vertrag
      aufgenommen: `TurnInput` traegt jetzt vorhandenen `MedicalCase` und
      `DialogueState`, und `careena3.py`/`DialogueManager` reichen diese
      Werte in den naechsten Turn durch
  - Warum:
    - das Log zeigte wiederholt leere `case_summary`- und
      `dialogue_summary`-Bloecke in spaeteren Turns, obwohl derselbe Chat
      bereits zuvor extrahierte Informationen aufgebaut hatte; der Grund war
      nicht die Session-Ablage, sondern dass der Turn-Einstieg den
      persistierten State gar nicht entgegennahm
  - Wirkung:
    - Folge-Turns koennen wieder auf den tatsaechlich gespeicherten Case- und
      Dialogue-State zugreifen
    - Call 1 und Call 2 sehen damit nicht nur Nachrichtenhistorie, sondern
      auch den kanonischen Zustand aus vorherigen Zuegen
    - das ist eine zentrale Architekturkorrektur im Sinne von Target Model 5,
      weil der Turn-Orchestrator jetzt mit echtem Dialogzustand statt mit
      impliziter Rekonstruktion arbeitet
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/input.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena3.py`
  - Naechster Punkt:
    - im Server-Log pruefen, ob `case_summary`/`dialogue_summary` in
      Folge-Turns jetzt gefuellt bleiben und danach die
      Recommendation-Anforderung als eigenen sauberen Response-Pfad
      nachziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 18 Datum: 07-06-26 05:19 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - einen ersten schlanken Test-/HTTP-Einstieg `server/careena3.py`
      angelegt, der direkt auf `careena_pipeline3` zeigt und Session,
      Warmup, Chat sowie eine einfache Case-Ansicht bereitstellt
  - Warum:
    - der Architekturstand von `careena_pipeline3` ist inzwischen weit genug,
      dass ein praktischer Integrationspfad sinnvoll wird; dafuer sollte kein
      kompletter Legacy-Server kopiert, sondern nur ein minimaler neuer
      Einstieg geschaffen werden
  - Wirkung:
    - `careena_pipeline3` kann jetzt ueber einen eigenen FastAPI-Einstieg
      angesprochen werden; Responses tragen bereits `response_mode`,
      `pending_followup`, `recommendation_requested` und
      `recommendation_ready`, sodass die neue Turn-Architektur sichtbar und
      testbar wird
  - Betroffene Dateien/Bereiche:
    - `server/careena3.py`
  - Naechster Punkt:
    - den neuen Einstieg praktisch anfahren oder alternativ die Response-/
      Routing-Strecke weiter ausbauen, jetzt wo ein Testpfad vorhanden ist
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 18 Datum: 07-06-26 19:10 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - `EntryManager` fuer medizinische No-Extraction-Turns entmaechtigt:
      dort wird kein automatischer `cannot_assess`-Hint mehr gesetzt; nur
      echte `out_of_scope`-Faelle bleiben ein frueher Entry-Hinweis
  - Warum:
    - das neue Log zeigte nach vorhandenem, bereits ausreichendem Case-State
      weiterhin `cannot_assess`, nur weil ein spaeterer kurzer Turn keine neue
      Extraktion ausloeste; damit ueberschrieb Entry die eigentliche
      Zustands- und Response-Logik des Dialogs
  - Wirkung:
    - Entry liefert in diesen Faellen wieder primaer Signale statt
      Endentscheidung
    - der `ResponseManager` kann den vorhandenen Case-/Dialogue-State nun
      wieder auswerten, statt von einem zu fruehen Hint abgeschnitten zu
      werden
    - das passt enger zu Target Model 5 und zur Leitplanke des Refactor-Plans
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/entry_manager.py`
  - Naechster Punkt:
    - im Log pruefen, ob kurze medizinische Folge-Turns mit bestehendem
      ausreichendem State jetzt nicht mehr unnoetig in `cannot_assess`
      laufen und danach den Recommendation-Anforderungspfad als eigene
      Response-Policy ausbauen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 19 Datum: 07-06-26 05:28 ===
  - Kategorie:
    - `bugfix`
  - Bereich:
    - `backend`
  - Aenderung:
    - zwei direkte Korrekturen aus dem ersten echten `careena3.py`-Testlauf
      umgesetzt: die Requirement-Logik erzwingt bei leerem Fallzustand nicht
      mehr voreilig eine `subject`-Rueckfrage, und der Call-2-Prompt wurde
      explizit auf das `ExtractionResult`-Schema mit korrekter Feldlage und
      Beobachtungsstruktur festgezogen
  - Warum:
    - das Debug-Log zeigte einerseits einen unpassenden `pending_followup`
      bei `out_of_scope` und andererseits einen Schema-Mismatch im neuen
      Extraction-Call, weil das Modell zu frei strukturierten Output lieferte
  - Wirkung:
    - nicht-medizinische oder noch leere Faelle sollten keine falsche
      Subjekt-Rueckfrage mehr ausloesen, und der neue Call 2 hat deutlich
      klarere Leitplanken fuer ein valides `ExtractionResult`
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/requirement_policy.py`
    - `server/careena_pipeline3/application/services/readiness_evaluator.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
  - Naechster Punkt:
    - den neuen Testlauf erneut gegen `debug_log_pipeline3.txt` spiegeln und
      danach die naechste echte Fehlstelle aus dem Integrationspfad schliessen
  - DEV_NOTE:
    - `workbench@freddy`


Format Ende

## Arbeitsbereich

=== CHANGE NUMBER: 19 Datum: 07-06-26 19:18 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - neues Autodoc-Artefakt `KNOWN_ISSUES.md` angelegt und dort die bewusst
      noch offen gelassenen Architekturprobleme aus der laufenden Migration
      festgehalten
  - Warum:
    - nicht jedes sichtbare Problem soll sofort mit ad-hoc-Logik repariert
      werden; besonders beim medizinischen Case-Merge und beim
      Recommendation-Pfad braucht es nachvollziehbare Zielentscheidungen statt
      schneller Nebenlogik
  - Wirkung:
    - der aktuell beobachtete Duplication-/Merge-Befund und der noch offene
      Recommendation-Response-Pfad sind jetzt explizit dokumentiert und fuer
      spaetere saubere Bearbeitung markiert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/KNOWN_ISSUES.md`
  - Naechster Punkt:
    - Recommendation-Anforderung als eigenen sauberen Response-Block
      ausarbeiten, statt weiter am Merge-Verhalten herumzudoktern
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 20 Datum: 07-06-26 19:25 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - Recommendation-Anforderung innerhalb des neuen Response-Blocks als
      eigene Policy-Spur sichtbar gemacht, ohne dafuer neue versteckte Modi
      oder Sonderrouten einzuziehen
  - Warum:
    - bisher wurde ein Recommendation-Request in blockierten Faellen ueber
      dieselben generischen Follow-up-/Cannot-assess-Texte behandelt; damit
      war fuer Nutzer und Debug-Sicht kaum sichtbar, dass eigentlich eine
      Recommendation gewuenscht, aber noch nicht freigegeben war
  - Wirkung:
    - bei offener Rueckfrage und gesetztem `recommendation_requested` wird der
      Follow-up-Text jetzt explizit als recommendation-blockierend formuliert
    - bei fehlender medizinischer Grundlage und gesetztem Request wird der
      Cannot-assess-Text recommendation-spezifisch formuliert
    - die Trace-Notes unterscheiden jetzt recommendation-blockierte Pfade von
      normalen Follow-up-/No-problem-Pfaden
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
  - Naechster Punkt:
    - im Log pruefen, ob Recommendation-Requests jetzt als eigene
      nachvollziehbare Nutzerstrecke erscheinen und danach entscheiden, ob als
      naechstes die eigentliche Recommendation-Ausgabe oder vorher die
      Observation-Identitaet/Case-Merge-Architektur dran ist
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 21 Datum: 07-06-26 06:06 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - den neuen Call-1-zu-Call-2-Vertrag entlang des Zielbilds aufgezogen:
      `IntentGateway` traegt jetzt explizite Signals fuer Personenbezug und
      medizinische Entitaetsarten sowie eine geordnete `call2_tasks`-Liste;
      diese Task-Reihe wird ueber `EntryDecision`, `ExtractionManager`,
      `ExtractionService`, `build_case_extraction_input()` und den Call-2-
      Prompt bis in den einen einzelnen Extraction-Call durchgereicht
  - Warum:
    - Call 2 soll nicht mehr blind die gesamte medizinische Welt auf einmal
      extrahieren, sondern nur noch die durch Call 1 angeforderten Aufgaben
      abarbeiten; damit bleibt die Steuerung sichtbar im Orchestrierungsmodell
      und nicht als versteckte Heuristik oder Mischlogik im Extraktor
  - Wirkung:
    - `careena_pipeline3` kann jetzt architektonisch sauber in die Richtung
      wachsen, dass Call 1 einen kleinen Satz Signals plus Task-Reihe setzt
      und Call 2 daraus einen fokussierten Prompt fuer genau einen Call baut;
      Recommendation-Request kommt dabei ebenfalls sichtbar aus Call 1 statt
      aus separater Keyword-Heuristik
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/common/types.py`
    - `server/careena_pipeline3/models/common/__init__.py`
    - `server/careena_pipeline3/models/workflow/intent_gateway.py`
    - `server/careena_pipeline3/models/workflow/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/services/extraction_service.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/application/services/recommendation_request_service.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/llm/prompts/intent_gateway.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
  - Naechster Punkt:
    - den neuen Vertrag ueber `careena3.py` praktisch pruefen und danach
      entscheiden, ob die Task-Liste schon fein genug ist oder ob die
      Personen-/Symptom-/Injury-Aufgaben noch weiter geschnitten werden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 21 Datum: 07-06-26 19:40 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - Call-Kontexte entlang ihrer tatsaechlichen Rolle gestrafft:
      `Call 1` bekommt in `careena_pipeline3` keinen vollen
      Case-/Dialogue-State mehr, und `Call 2` bekommt keine freien
      `recent_turns` mehr als zusaetzliches Extraktionsmaterial
  - Warum:
    - bei der Pruefung des Kontextbaus zeigte sich, dass zu viel blind aus dem
      alten Shared-Context-Modell uebernommen worden war; besonders `Call 2`
      nutzte breiten Verlaufskontext dadurch nicht nur zum Verstehen, sondern
      offenbar auch als Quelle fuer erneut materialisierte Symptome
  - Wirkung:
    - `Call 1` arbeitet jetzt mit einem schlankeren Intake-Kontext:
      `latest_user_message`, `pending_slot`, `last_assistant_question`,
      `recent_turns`
    - `Call 2` behaelt strukturierten Case-/Dialogue-Kontext, aber keine
      freien `recent_turns` mehr
    - der Call-2-Prompt stellt jetzt explizit klar, dass Kontext nur zur
      Interpretation der aktuellen Nachricht dient und nicht als eigene
      Faktenquelle
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
  - Naechster Punkt:
    - im Log pruefen, ob Follow-up-Antworten wie `gestern` jetzt weniger zur
      erneuten Symptommaterialisierung fuehren und danach entscheiden, ob der
      verbleibende Duplication-Befund rein im Merge liegt oder noch im
      Follow-up-Extraktionsvertrag
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 22 Datum: 07-06-26 06:17 ===
  - Kategorie:
    - `bugfix`
  - Bereich:
    - `backend`
  - Aenderung:
    - den neuen Call-1/Call-2-Vertrag nach dem ersten Task-basierten Testlauf
      weiter geschaerft: das vollstaendige `IntentGateway` wird jetzt geloggt,
      `call2_tasks` erscheinen in den Entry-Trace-Notes, und der Call-2-Prompt
      verbietet explizit subjektbezogene offene Fragen oder Rueckgaben, wenn
      `resolve_subject_context` gar nicht angefordert wurde
  - Warum:
    - der Loglauf zeigte, dass die Task-Reihe zwar technisch durchgereicht
      wurde, Call 2 aber trotz nur `extract_symptoms` wieder `subject` als
      offene Frage aufgemacht hat; das muss ueber den sichtbaren Vertrag
      adressiert werden, nicht ueber versteckte Nachfilterung
  - Wirkung:
    - der Integrationspfad macht jetzt besser sichtbar, welche Call-1-Signale
      und Tasks wirklich gesetzt wurden, und Call 2 hat strengere Vorgaben,
      sich nur auf angeforderte Aufgaben zu beschraenken
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/intent_classification_service.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
  - Naechster Punkt:
    - den naechsten `careena3.py`-Testlauf wieder von hinten im Log lesen und
      pruefen, ob `IntentGateway.signals`, `call2_tasks` und der
      `ExtractionResult` nun konsistenter zusammenlaufen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 22 Datum: 07-06-26 19:47 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `backend`
  - Aenderung:
    - den `continue`-Text im neuen Response-Builder vom leeren Ack auf einen
      zustandsbezogenen Fortschrittshinweis umgestellt
  - Warum:
    - nach der Context-Bereinigung wirkte der normale `continue`-Pfad im
      Nutzererlebnis noch zu leer; fuer Turns wie `und jetzt?` war zwar kein
      Follow-up mehr offen, die Antwort `Verstanden. Ich habe die Angaben
      aufgenommen.` blieb aber fachlich duenn
  - Wirkung:
    - wenn ein fokussiertes Problem vorhanden ist und der Mindestzustand fuer
      Recommendation erreicht wurde, nennt die Antwort jetzt den aktuellen
      Fokus explizit
    - ohne Fokus bleibt der Text weiterhin neutral
    - die Verbesserung haengt direkt am vorhandenen Case-/Dialogue-State und
      fuehrt keine zusaetzliche Entscheidungslogik ein
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/response_text_builder.py`
  - Naechster Punkt:
    - im Log pruefen, ob der `continue`-Pfad jetzt fuer abgeschlossene
      Mindestinformationsfaelle nachvollziehbarer wirkt und danach entscheiden,
      ob als naechster Refactor-Schritt die eigentliche Recommendation-
      Ausgabe oder vorher ein schmaler Call-3-Zielvertrag angelegt wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 23 Datum: 07-06-26 06:22 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die Manager-Kopplung entlang des Zielbilds wieder enger gezogen:
      `CaseStateManager` macht jetzt nur noch Case-/Merge-/Fokus-Arbeit,
      waehrend `DialogueManager` die Synchronisierung von Requirement-State,
      Recommendation-State und planner-bezogenen Dialogsignalen explizit als
      eigene Orchestrierungsschritte ausfuehrt
  - Warum:
    - die Rueckmeldung war berechtigt, dass sich zu viele Manager indirekt
      kennen und zusaetzliches Verhalten "nebenbei" in fremden Schichten
      landet; die zentrale Steuerung soll sichtbar beim `DialogueManager`
      bleiben
  - Wirkung:
    - `careena_pipeline3` folgt jetzt strikter der Idee aus Model 5, dass der
      `DialogueManager` der Manager aller Manager ist; Zustandsweitergabe und
      Folgeentscheidungen liegen sichtbarer in der Turn-Orchestrierung statt in
      einem fachfremd aufgeblÃ¤hten `CaseStateManager`
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
  - Naechster Punkt:
    - den naechsten Integrationslauf gegen `careena3.py` lesen und dann die
      Call-2-Task-Reihe oder die Response-/Routing-Grenzen weiter schaerfen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 23 Datum: 07-06-26 19:55 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - einen eigenen Zielvertrag fuer die spaetere Call-3-Schicht in
      `careena_pipeline3` angelegt
  - Warum:
    - fuer den naechsten Recommendation-/Response-Block musste zuerst klar
      festgehalten werden, ob Call 3 selbst fachlich entscheidet oder nur
      einen bereits freigegebenen Pfad in strukturierte Recommendation und
      spaetere Ausgabe ueberfuehrt
  - Wirkung:
    - `CALL3_TARGET_CONTRACT.md` beschreibt jetzt:
      - Zweck und Grenzen von Call 3
      - erlaubte Eingaben
      - verbotene Verantwortung
      - Zieltrennung zwischen `ResponseManager`, Call 3 und Text-Rendering
      - die offene, aber fuer die Migration vorlaeufig beantwortete Frage nach
        Pfadentscheidung vs. Inhaltsbildung
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/CALL3_TARGET_CONTRACT.md`
  - Naechster Punkt:
    - auf Basis dieses Zielvertrags entscheiden, ob zuerst ein strukturierter
      Recommendation-Result-Vertrag oder direkt ein erster Call-3-Inputvertrag
      in `careena_pipeline3` angelegt wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 24 Datum: 07-06-26 07:59 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - den ersten strukturierten Call-3-Ergebnisvertrag in
      `careena_pipeline3` technisch eingezogen: `RecommendationResult`
      wird jetzt ueber einen eigenen `RecommendationResultBuilder` aus dem
      kanonischen Turn-State erzeugt, in `ResponsePlan`/`TurnResult`
      mitgefuehrt und von `careena3.py` im HTTP-Response ausgegeben
  - Warum:
    - nach dem festgezogenen Call-3-Zielvertrag brauchte die Pipeline zuerst
      einen sauberen strukturierten Recommendation-Output, bevor spaetere
      Recommendation- oder Routinglogik sinnvoll migriert werden kann; die
      Pfadentscheidung sollte dabei weiter im `ResponseManager` bleiben
  - Wirkung:
    - der Recommendation-Pfad liefert jetzt neben Text auch ein explizites
      strukturiertes Ergebnisobjekt
    - die neue Schicht trifft noch keine medizinischen Zusatzentscheidungen,
      sondern beschreibt nur freigegebenen Recommendation-Kontext plus
      aktuelle Grenzen der noch fehlenden Engine
    - Text-Rendering und strukturiertes Ergebnis sind damit erstmals
      getrennt anschliessbar
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/recommendation_result.py`
    - `server/careena_pipeline3/models/workflow/__init__.py`
    - `server/careena_pipeline3/models/turn/response_plan.py`
    - `server/careena_pipeline3/models/turn/result.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/application/services/recommendation_result_builder.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena3.py`
  - Naechster Punkt:
    - den Recommendation-Output gegen den Refactor-Plan halten und danach den
      naechsten Architekturblock fuer echte Call-3-Inputs oder die weitere
      Call-2-/Response-Migration festziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 25 Datum: 07-06-26 12:20 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Case-Update-Kern in `careena_pipeline3` von implizitem
      Direkt-Merge auf eine erste explizite Update-Entscheidungsstruktur
      umgestellt; dazu wurden `ObservationMatchResult`,
      `ObservationUpdateDecision` und `CaseUpdateOutcome` eingefuehrt und
      `CaseMergePolicy`/`CaseMerger` entsprechend neu zugeschnitten
  - Warum:
    - fuer die weitere Migration brauchte der Medical-Case-State zuerst eine
      sauberere Zwischenarchitektur, in der unterschieden wird zwischen
      Match, Aenderungsart, Case-Aktion und moeglicher Dialogfolge, statt
      alles sofort still in denselben Mergepfad zu zwingen
  - Wirkung:
    - Beobachtungen werden jetzt expliziter als `create`, `enrich`,
      `correct`, `confirm`, `flag_conflict` oder `defer_update` behandelt
    - `source_span` ist nicht mehr das tragende Kriterium fuer Observation-
      Identitaet
    - Konflikt- und Mehrdeutigkeitsfaelle erzeugen vorerst Trace-Signale statt
      stiller Mutation, wodurch die spaetere Rueckfrage-Strecke sauberer
      anschliessbar wird
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/case_update.py`
    - `server/careena_pipeline3/domain/case_merge_policy.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/domain/__init__.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/CASE_UPDATE_CONTRACT.md`
  - Naechster Punkt:
    - pruefen, welche Konflikt- oder Ambiguitaetsfaelle jetzt im Trace
      sichtbar werden und danach entscheiden, wie davon gezielt eine
      Rueckfrage-Strecke im Dialogpfad abgeleitet werden soll
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 26 Datum: 07-06-26 13:20 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - eine erste sichtbare Call-2-Betriebsartensteuerung in
      `careena_pipeline3` eingezogen; `EntryManager` leitet jetzt einen
      `call2_operation_mode` aus Call 1 plus Dialogzustand ab, reicht ihn bis
      in den Call-2-Payload weiter und gibt ausserdem `message_role` aus Call 1
      bis in den `MessageDelta`-/Case-Update-Pfad durch
  - Warum:
    - die bisherigen Logs zeigten, dass Call 2 zwar schon task-basiert ist,
      aber noch zu oft wie ein allgemeiner Voll-Extraktor arbeitet; fuer
      Follow-up-, Korrektur- und dialogische Turns brauchte die Pipeline eine
      zusaetzliche sichtbare Steuerachse, damit spaetere Prompt- und
      Extraktionsgrenzen nicht nur als Sonderlogik entstehen
  - Wirkung:
    - Call 2 kennt jetzt erste Modi wie
      `focused_new_fact_extraction`, `followup_slot_update`,
      `existing_fact_revision`, `mixed_update_and_new_info` und
      `no_medical_update_expected`
    - der Payload enthaelt jetzt `operation_mode` plus Fokus-Metadaten
    - der Prompt kennt ausdrueckliche Modusregeln
    - Korrektur-/Follow-up-Rollen aus Call 1 gehen nicht mehr auf dem Weg in
      den Case-Update-Pfad verloren
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/common/types.py`
    - `server/careena_pipeline3/models/common/__init__.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/application/services/call2_operation_mode_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/services/extraction_service.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/CALL2_OPERATION_MODES.md`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/CALL2_MODE_RESOLUTION.md`
  - Naechster Punkt:
    - gegen frische Logs pruefen, ob `operation_mode` und `message_role`
      jetzt sichtbar ankommen und danach gezielt den
      `followup_slot_update`-Pfad gegen die Mehrfachanreicherung bestehender
      Symptome schaerfen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 27 Datum: 07-06-26 14:02 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - eine explizite Call-2-Kontext-Policy in der Workbench angelegt und
      direkt in `llm/context.py` kurz dokumentiert, dass Kontextfelder fuer
      Call 2 Interpretations- und Zielsignale sind, aber keine freie
      Faktenquelle
  - Warum:
    - nach der neuen Modussteuerung musste als naechste Leitplanke klargezogen
      werden, welche Kontextteile Call 2 wofuer bekommen soll und welche
      Missbraeuche ausdruecklich unerwuenscht sind; genau dieser Punkt war im
      Refactor-Strang der aktuelle Fokus
  - Wirkung:
    - die Rollen von `pending_slot`, Fokusfeldern, `case_summary` und
      `dialogue_summary` sind jetzt nachvollziehbarer beschrieben
    - pro `operation_mode` gibt es eine erste Kontext-Matrix
    - die Codekante in `build_case_extraction_input()` traegt jetzt eine
      direkte technische Erklaerung fuer spaetere Weiterarbeit
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-07/CALL2_CONTEXT_POLICY.md`
    - `server/careena_pipeline3/llm/context.py`
  - Naechster Punkt:
    - den `followup_slot_update`-Outputvertrag gegen diese Kontext-Policy
      pruefen und festziehen, damit kurze Follow-up-Antworten nicht mehr als
      neue Observations statt als Fokus-Updates herausfallen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 28 Datum: 07-06-26 14:11 ===
  - Kategorie:
    - `bugfix`
  - Bereich:
    - `backend`
  - Aenderung:
    - den `followup_slot_update`-Pfad an der Call-2-Ausgangskante enger
      gezogen; bekannte Fokus-Slot-Updates wie `duration_or_onset`,
      `severity`, `body_site`, `injury_context` und
      `functional_limitation` werden jetzt in
      `ResilientExtractionService` gezielt auf die fokussierte bestehende
      Observation zurueckgefuehrt statt als neue freie Observation
      weiterzulaufen
  - Warum:
    - die frischen Logs zeigten, dass die neue Modussteuerung zwar schon
      korrekt ankam, Call 2 aber Antworten wie `2 stunden` weiterhin als neue
      `measurement`-Observation herausgab; damit entstand downstream trotz
      richtigem Modus wieder `no_match -> create_observation`
  - Wirkung:
    - kurze bekannte Follow-up-Antworten koennen jetzt im
      `followup_slot_update`-Modus als Fokus-Update im bestehenden
      Uebergangsvertrag weiterlaufen
    - der Prompt fuer diesen Modus beschreibt zusaetzlich klarer, dass solche
      Slotwerte keine separate Measurement- oder Generic-Observation bilden
      sollen
    - die Normalisierung ist explizit an `operation_mode` und `pending_slot`
      gebunden statt als freie Speziallogik irgendwo im Merge zu sitzen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
  - Naechster Punkt:
    - im Server-Log pruefen, ob `2 stunden` oder aehnliche Antworten jetzt
      als Fokus-Update statt als neue Observation durchlaufen und danach den
      verbleibenden `mixed_update_and_new_info`-Pfad weiter schaerfen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 29 Datum: 07-06-26 14:21 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die neue `followup_slot_update`-Normalisierung in
      `ResilientExtractionService` einen Schritt generischer gemacht; statt
      mehrere bekannte Follow-up-Slots einzeln im Hauptzweig zu behandeln,
      laeuft die Feldzuordnung jetzt ueber eine kleine
      `FOLLOWUP_SLOT_ATTRIBUTE_MAP` plus eine schmale Hilfsfunktion fuer die
      Attributableitung
  - Warum:
    - die Rueckmeldung war berechtigt, dass die erste Korrektur noch zu
      slotweise und damit wieder zu speziell war; fuer die weitere
      Refactorbarkeit sollte derselbe Mechanismus moeglichst ueber eine kleine
      allgemeine Zuordnung statt ueber viele Einzelzweige wachsen
  - Wirkung:
    - `duration_or_onset`, `body_site`, `injury_context` und
      `functional_limitation` laufen jetzt ueber dieselbe generische
      Attributzuordnung
    - nur `severity` bleibt vorerst als eigener Fall, weil dort die
      Werteaufbereitung noch abweicht
    - die Korrektur bleibt funktional gleich, ist aber leichter auf spaetere
      Call-2- oder Datenmodell-Aenderungen anpassbar
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
  - Naechster Punkt:
    - bei weiterem Bedarf den letzten Sonderfall `severity` ebenfalls gegen
      einen allgemeineren Fokus-Attribut-Adapter pruefen und danach den Stand
      wieder gegen Refactor-Plan und `TARGET_MODEL5.md` halten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 30 Datum: 07-06-26 15:55 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Call-1-Vertrag um das explizite Signal
      `additional_medical_information` erweitert und die
      `Call2OperationModeService`-Aufloesung daran angepasst; bei offenem
      Follow-up kann dadurch jetzt sauber zwischen reinem
      `followup_slot_update` und `mixed_update_and_new_info` unterschieden
      werden
  - Warum:
    - der letzte Testlauf zeigte eine saubere, aber zu enge Wirkung der neuen
      Scope-Steuerung: eine Nachricht wie
      `seit gestern, seit heute auch noch fieber` wurde als reines
      Fokus-Update behandelt und verlor die neue Zusatzinformation
    - das Problem sollte nicht ueber spaete Prompt-Magie geloest werden,
      sondern ueber eine sichtbare Vertragskante zwischen Call 1 und Call 2
  - Wirkung:
    - Call 1 kann jetzt ausdruecklich markieren, dass eine Follow-up-Antwort
      zugleich weitere medizinische Information enthaelt
    - die Mode-Aufloesung kann in solchen Faellen gezielt auf
      `mixed_update_and_new_info` wechseln
    - die Logik bleibt klein, nachvollziehbar und an den Turn-Vertrag gebunden
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/intent_gateway.py`
    - `server/careena_pipeline3/llm/prompts/intent_gateway.py`
    - `server/careena_pipeline3/application/services/call2_operation_mode_service.py`
  - Naechster Punkt:
    - im Server-Log pruefen, ob gemischte Follow-up-Nachrichten jetzt
      tatsaechlich in `mixed_update_and_new_info` landen und ob der Call-2-
      Output beide Teile sauber trennt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 31 Datum: 07-06-26 16:04 ===
  - Kategorie:
    - `bugfix`
  - Bereich:
    - `backend`
  - Aenderung:
    - die Konfliktpruefung in `CaseMergePolicy` fuer unvollstaendige
      Update-Observations generischer gemacht; `unknown`-, `unklar`- oder
      leere Qualifier zaehlen bei `subject_ref`, `laterality`, `details` und
      `measurement` nicht mehr als harter Widerspruch
  - Warum:
    - der erste erfolgreiche `mixed_update_and_new_info`-Test zeigte, dass
      Call 2 zwar das Fokus-Update plus die neue Observation sauber
      extrahierte, der Merge aber das Fokus-Update wegen unvollstaendiger
      Ankerwerte faelschlich als Konflikt behandelte
    - das sollte nicht mit neuer medizinischer Sonderlogik geloest werden,
      sondern ueber eine generische Regel fuer unvollstaendige Update-Deltas
  - Wirkung:
    - fokusgebundene Updates mit fehlenden oder `unknown`-Qualifiers koennen
      eher wieder als `enrich` statt als kuenstlicher Konflikt durchlaufen
    - echte inhaltliche Widersprueche bleiben weiterhin als Konflikt sichtbar
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/case_merge_policy.py`
  - Naechster Punkt:
    - im Log pruefen, ob der `mixed_update_and_new_info`-Pfad jetzt sowohl
      das Fokus-Update als auch die neue Observation sauber verarbeitet
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 32 Datum: 07-06-26 16:18 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - eine eigene LLM-basierte Normalisierungsstufe hinter Call 2
      eingezogen; `ResilientExtractionService` kann jetzt ein bereits
      extrahiertes `ExtractionResult` noch einmal gegen Turn-Vertrag,
      Fokuskontext und Scope-Regeln normalisieren lassen, bevor der Output in
      den restlichen State-Pfad geht
  - Warum:
    - die aktuelle Baustelle zeigte, dass viele schwierige Mischfaelle nicht
      sauber ueber immer mehr Python-Sonderzweige geloest werden sollten
    - statt neue Hardcode-Schichten fuer Follow-up-/Mixed-/Korrekturfaelle
      einzuziehen, soll ein eng gefuehrter operativer LLM-Normalizer aehnliche
      Konflikte unter denselben klaren Grenzen ordnen
  - Wirkung:
    - `careena_pipeline3` besitzt jetzt einen neuen Architekturpunkt zwischen
      roher Call-2-Extraktion und dem bestehenden Delta-/Merge-Pfad
    - der Normalizer bekommt nur einen engen Kontext und darf medizinische
      Fakten nicht neu erfinden, sondern nur Extraktionsergebnisse
      umordnen/pruefen
    - wenn die Normalisierung ausfaellt, greift weiterhin der bisherige
      technische Follow-up-Fallback
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/extraction_service.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/call_control.py`
    - `server/careena_pipeline3/llm/extraction_result_normalizer.py`
    - `server/careena_pipeline3/llm/prompts/extraction_normalization.py`
    - `server/careena_pipeline3/llm/__init__.py`
    - `server/careena_pipeline3/runtime.py`
  - Naechster Punkt:
    - im Server-Log pruefen, wie sich der neue Normalizer bei gemischten
      Follow-up-Nachrichten verhaelt und ob die bisherigen Python-
      Normalisierungen dadurch weiter reduziert werden koennen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 33 Datum: 07-06-26 16:32 ===
  - Kategorie:
    - `cleanup`
  - Bereich:
    - `backend`
  - Aenderung:
    - den persistierten `DialogueState` und die fuer LLM-Kontexte gebaute
      `DialogueSummary` um nachweislich tote Uebergangsfelder bereinigt;
      `last_question_key`, `staged_followup_answers` und
      `awaiting_confirmation` wurden aus diesen aktiven Zustandsvertraegen
      entfernt
  - Warum:
    - im aktuellen `careena_pipeline3`-Laufweg wurden diese Felder nicht mehr
      aktiv gesetzt oder fachlich verwendet, aber weiterhin durch
      Zustandsmodelle, Logik und LLM-Kontexte mitgeschleppt
    - das ist genau die Art unnÃ¶tiger Zustandslast, die in Phase 6 des
      Refactor-Plans reduziert werden soll
  - Wirkung:
    - der aktive Dialogzustand ist schlanker und nÃ¤her an wirklich
      verwendetem persistentem Zustand
    - LLM-Kontexte enthalten weniger Alt-/Uebergangsrauschen
    - ohne in die aktuelle Follow-up-, Readiness- oder Response-Logik
      fachlich einzugreifen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/dialogue.py`
    - `server/careena_pipeline3/models/workflow/context.py`
    - `server/careena_pipeline3/llm/context.py`
  - Naechster Punkt:
    - als naechsten State-/Vertragsblock pruefen, ob `pending_followup` selbst
      noch zu grob modelliert ist und spaeter strukturierter werden sollte
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 34 Datum: 07-06-26 16:46 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - `pending_followup` von einem nackten Slot-String auf einen kleinen
      strukturierten Zustandsvertrag umgestellt; die neue Struktur traegt
      jetzt `requirement_key`, `slot` sowie optionalen Fokusbezug und wird
      durch Requirement-, Entry-, Extraction-, Context- und Response-Pfad
      hindurchgereicht
  - Warum:
    - `pending_followup` war inzwischen eine zentrale Steuerkante fuer mehrere
      Schichten, war aber selbst noch zu grob modelliert
    - fuer die weitere Migration passt ein expliziter kleiner Vertrag besser
      zu Model 5 als ein immer weiter ueberladener String
  - Wirkung:
    - Follow-up-Steuerung ist expliziter und leichter spaeter weiter
      ausbaubar
    - Entry und Extraction lesen jetzt bewusst den `slot` aus dem Vertrag,
      statt direkt den Gesamtzustand als String zu verwenden
    - die HTTP-Antwort gibt `pending_followup` jetzt bewusst als strukturierte
      Daten zurueck
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/dialogue.py`
    - `server/careena_pipeline3/models/domain/__init__.py`
    - `server/careena_pipeline3/models/workflow/context.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/models/__init__.py`
    - `server/careena_pipeline3/domain/requirement_policy.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena3.py`
  - Naechster Punkt:
    - kurzen Smoke-Test fahren und danach entscheiden, ob der naechste
      Architekturblock weiter bei Follow-up-/Dialogue-State bleibt oder wieder
      staerker zu Readiness/Recommendation zurueckschwenkt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 35 Datum: 07-06-26 16:54 ===
  - Kategorie:
    - `bugfix`
  - Bereich:
    - `backend`
  - Aenderung:
    - den `ExtractionResult`-Vertrag fuer optionale technische
      Beobachtungsreferenzen erweitert und das Mapping in `MessageDelta`
      entsprechend angepasst; `ExtractedObservation` darf jetzt ein optionales
      `observation_id` tragen, das bei vorhandener Belegung als
      `CaseObservation.id` uebernommen wird
  - Warum:
    - der neue LLM-Normalizer versuchte bei Fokus-Updates bereits sinnvoll,
      die bestehende Zielobservation technisch zu referenzieren
    - das bisherige Schema verbot diese Referenz jedoch noch, wodurch die
      Normalisierung unnoetig an der Validierung scheiterte
  - Wirkung:
    - der Normalizer kann bestehende Observations jetzt sauber adressieren,
      ohne aus dem erlaubten Vertrag zu fallen
    - der Downstream behaelt weiterhin sein bisheriges Verhalten fuer Faelle
      ohne gesetzte `observation_id`
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/extraction/result.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
  - Naechster Punkt:
    - im Log pruefen, ob die Normalisierungsstufe bei gemischten
      Follow-up-Turns jetzt nicht mehr an `observation_id` scheitert
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 36 Datum: 07-06-26 17:20 ===
  - Kategorie:
    - `feature`
  - Bereich:
    - `backend`
  - Aenderung:
    - die bestehende `simulation_runtime` aus der alten Pipeline als eigenes
      Paket nach `careena_pipeline3` uebernommen und an den neuen
      `DialogueManager`-Turn-Vertrag angebunden; Runner, Modelle, Personas,
      Prompts und Chat-Command-Helfer wurden weitgehend uebernommen, waehrend
      nur der System-Adapter und die Bootstrap-Kante auf die neue Pipeline
      angepasst wurden
  - Warum:
    - fuer die weiteren offenen Refactor-Bloecke wird ein besserer Testhebel
      gebraucht
    - die Simulation soll moeglichst entkoppelt von der Pipeline bleiben und
      eher den Gegenpol fuer wiederholbare Verifikation bilden
  - Wirkung:
    - `careena_pipeline3` besitzt jetzt wieder eine eigene generische
      Simulationslaufzeit
    - ueber `CareenaPipeline3Adapter` kann die neue Pipeline turnweise gegen
      simulierte Teilnehmer laufen
    - `build_simulation_runner()` in `bootstrap.py` baut dafuer direkt einen
      einsatzfaehigen Runner
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/simulation_runtime/`
    - `server/careena_pipeline3/bootstrap.py`
  - Naechster Punkt:
    - kurzer Lauf-/Importtest der neuen Simulationskante und danach mit ihr
      gezielter gegen die offenen Refactor-Bloecke testen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 36 Datum: 07-06-26 20:35 ===
  - Kategorie:
    - `runtime`
  - Bereich:
    - `simulation`
  - Aenderung:
    - den portierten Simulationspfad an die neue Runtime angepasst:
      Teilnehmerstandard jetzt `env` mit `medgemma:4b`, plus eigenes
      Simulationslog ohne Pipeline-Trace
  - Warum:
    - der Sim-Runner sollte standardmaessig nicht ueber das grosse
      Pipeline-Modell laufen, sondern ueber das kleinere Teilnehmermodell,
      und fuer Testlaeufe fehlte noch ein separater Blick auf den reinen
      Simulationsverlauf
  - Wirkung:
    - `build_simulation_runner()` nutzt jetzt fuer den Teilnehmer standardmaessig
      `env` mit Modell-Override `medgemma:4b`
    - Simulationslaeufe schreiben zusaetzlich nach
      `server/careena_pipeline3/infrastructure/logs/debug_log_simulation3.txt`
    - das Simulationslog enthaelt Request, Transcript und Ergebnis, ohne den
      uebrigen Pipeline-Debug-Output mitzuschleppen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/runtime.py`
    - `server/careena_pipeline3/bootstrap.py`
    - `server/careena_pipeline3/infrastructure/logging.py`
    - `server/careena_pipeline3/simulation_runtime/runner.py`
  - Naechster Punkt:
    - im separaten Simulationslog pruefen, ob das Teilnehmerverhalten mit
      `env`/`medgemma:4b` plausibel bleibt und danach die fachliche
      Subject-Resolution der Pipeline weiterziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 37 Datum: 07-06-26 20:48 ===
  - Kategorie:
    - `observability`
  - Bereich:
    - `simulation`
  - Aenderung:
    - Simulationslogging verschlankt und Logdateien pro Serverstart frisch aufgesetzt
  - Warum:
    - das neue Simulationslog war zu technisch und zu lang, weil es den kompletten
      Ergebniszustand mitschrieb; ausserdem sollten frische Testlaeufe nicht an
      immer weiter anwachsenden Altlogs haengen
  - Wirkung:
    - `debug_log_pipeline3.txt` und `debug_log_simulation3.txt` werden beim
      ersten Logging-Setup eines Serverstarts in timestampierte Archivdateien
      umbenannt, falls bereits Inhalt vorhanden ist
    - das aktuelle Simulationslog enthaelt jetzt vor allem Request, lesbares
      Transcript und ein kleines Ergebnis-Summary statt des kompletten
      technischen `SimulationResult`
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/infrastructure/logging.py`
    - `server/careena_pipeline3/simulation_runtime/runner.py`
  - Naechster Punkt:
    - nach dem naechsten Neustart kurz pruefen, ob die neuen Archivdateien
      entstehen und ob das Simulationslog fuer Debugging jetzt schlank genug ist
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 38 Datum: 07-06-26 21:03 ===
  - Kategorie:
    - `contract`
  - Bereich:
    - `extraction`
  - Aenderung:
    - `ExtractionSignal` akzeptiert jetzt auch einfache String-Evidenz und
      normalisiert sie in ein strukturiertes Signalobjekt
  - Warum:
    - die Subject-Resolution im Simrun scheiterte nicht fachlich, sondern an
      einer zu strengen Schema-Kante:
      `case_payload.subject.signals` kam aus dem LLM oft als Liste einfacher
      Strings wie `self` oder `Ich bin Lukas.`
  - Wirkung:
    - Strings in `signals` werden jetzt generisch zu
      `code=text_evidence`, `value=<text>`, `source_span=<text>`
      normalisiert
    - dadurch kann die Extraktion fuer Subject-/Personenklaerung auch dann
      weiterlaufen, wenn das LLM einfache Evidenz statt voller Signalobjekte
      liefert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/extraction/result.py`
  - Naechster Punkt:
    - im naechsten Simrun pruefen, ob die Schleife bei
      `Geht es um Sie selbst oder um eine andere Person?` verschwindet
      und danach die Benennung von `subject` gegen eine klarere
      Personen-/Affected-Person-Semantik ziehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 39 Datum: 07-06-26 21:31 ===
  - Kategorie:
    - `logic`
  - Bereich:
    - `response`
  - Aenderung:
    - den Response-Pfad um eine eigene Uebergangsstufe
      `guide_next_step` erweitert und den alten `continue`-Text entschaerft
  - Warum:
    - die letzten Simruns zeigten, dass `continue` zu viel Verantwortung
      trug: bei vorhandenem medizinischem Kern und erreichter Mindestlage
      antwortete das System immer wieder mit
      `Ich habe jetzt genug Informationen ...`, was keine saubere
      Dialogsteuerung war und in Schleifen kippte
  - Wirkung:
    - wenn medizinisch genug Information fuer eine Einordnung vorliegt, aber
      noch keine Recommendation angefordert wurde, waehlt `ResponseManager`
      jetzt `guide_next_step` statt blind `continue`
    - diese Stufe stellt bewusst eine sichtbare Uebergangsfrage:
      weitere Beschwerden oder erste Einordnung
    - der fruehere `continue`-Text behauptet nicht mehr, dass schon
      `genug Informationen` vorliegen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/common/types.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena3.py`
  - Naechster Punkt:
    - im naechsten Simrun pruefen, ob der Dialog nach erreichter
      Mindestlage jetzt aus der Bestatigungs-/Deutungsschleife herauskommt
      und ob `guide_next_step` gegen `TARGET_MODEL5.md` als eigene
      Uebergangskante tragfaehig bleibt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 40 Datum: 07-06-26 22:12 ===
  - Kategorie:
    - `contract`
  - Bereich:
    - `domain`
  - Aenderung:
    - den Injury-Feldvertrag im Domainmodell auf `injury_context` als
      kanonischen Schluessel umgestellt und den alten `context`-Pfad nur noch
      als explizite Uebergangsloesung belassen
  - Warum:
    - der aktuelle Injury-Follow-up-Loop entstand nicht primaer im Prompt,
      sondern an einer Feldinkonsistenz:
      Extraktion/Mapper lieferten `injury_context`, waehrend
      `CaseObservation` fuer Injury-Daten und Requirement-Erfuellung noch auf
      `details["context"]` schaute
  - Wirkung:
    - Injury-Daten werden jetzt bevorzugt aus `details["injury_context"]`
      gelesen und auch wieder dorthin geschrieben
    - der alte Schluessel `context` bleibt nur noch als klar markierter
      Legacy-Fallback erhalten
    - damit kann `RequirementPolicy` `injury.injury_context` wieder konsistent
      gegen den kanonischen Datenzustand pruefen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/observation.py`
  - Naechster Punkt:
    - im naechsten Simrun pruefen, ob der offene Injury-Context-Follow-up
      verschwindet; danach die zweite Kante bewerten, warum
      `Ich bin eben gestuerzt.` zusaetzlich noch als neue Injury materialisiert
      wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 41 Datum: 07-06-26 22:17 ===
  - Kategorie:
    - `runtime`
  - Bereich:
    - `simulation`
  - Aenderung:
    - die Standardlaenge fuer `simrun`-Testlaeufe von 8 auf 4 Turns reduziert
  - Warum:
    - die letzten Simruns dauerten fuer schnelle Iteration deutlich zu lange;
      fuer den aktuellen Refactor reichen kuerzere Laeufe, um Schleifen und
      Pfadfehler sichtbar zu machen
  - Wirkung:
    - `/simrun`
    - und `/simrun all`
      laufen jetzt mit `max_turns=4`
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/simulation_runtime/chat_commands.py`
  - Naechster Punkt:
    - den kuerzeren Simrun auf die reparierte Injury-Context-Kante laufen
      lassen und danach den verbleibenden Update-vs-neue-Injury-Befund pruefen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 42 Datum: 07-06-26 22:36 ===
  - Kategorie:
    - `ux`
  - Bereich:
    - `response`
  - Aenderung:
    - die `guide_next_step`-Frage enger formuliert, damit der naechste
      Nutzerturn besser steuerbar wird
  - Warum:
    - nach dem letzten Simrun war die neue Uebergangsstufe zwar sinnvoll,
      liess aber noch zu offene Antworten zu und fuehrte dadurch wieder in
      wiederholte bestaetigende Turns
  - Wirkung:
    - statt einer offenen Doppelfrage fordert der Pfad jetzt gezielt:
      `Gibt es noch weitere Beschwerden? Wenn nicht, dann antworten Sie kurz
      mit nein, und ich erstelle Ihre Empfehlung.`
    - damit soll die Zahl halb-offener Folgeantworten sinken, ohne schon neue
      tiefe Uebergangslogik einzuziehen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena3.py`
  - Naechster Punkt:
    - im naechsten Simrun pruefen, ob die engere Frage zu klareren
      Antwortmustern fuehrt oder ob danach doch eine kleine generische
      Transition-Logik noetig bleibt
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 43 Datum: 08-06-26 00:26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die implizite Case-Truth-Mitte im Observation-Update-Pfad in zwei
      explizite Domain-Bausteine aufgeschnitten:
      `ObservationNormalizer` fuer kanonische Oberflaechen-Normalisierung und
      `ObservationIdentityResolver` fuer Match-/Identitaetsaufloesung; die
      `CaseMergePolicy` delegiert diese Schritte jetzt sichtbar, statt
      Normalisierung und Identitaetslogik weiter intern zu vermischen
  - Warum:
    - der erste echte Phase-1-Schritt des Refactor-Plans soll die
      Wahrheitsbildung zwischen Extraktion und `MedicalCase` expliziter machen,
      ohne sofort die gesamte Merge-Semantik neu zu schreiben
    - damit wird das bisher implizite Wissen ueber Observation-Identitaet und
      kanonische Vorverarbeitung als eigene Truth-Schicht sichtbar und
      spaeter gezielter weiter ausbaubar
  - Wirkung:
    - `CaseMergePolicy` ist schmaler und fachlich klarer zugeschnitten
    - Normalisierung und Identitaetsmatch koennen ab jetzt separat erweitert,
      getestet und spaeter weiter Richtung `TARGET_MODEL6` entwickelt werden
    - das aktuelle Verhalten des Merge-Pfads bleibt bewusst konservativ nah am
      bisherigen Stand
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/observation_normalizer.py`
    - `server/careena_pipeline3/domain/observation_identity_resolver.py`
    - `server/careena_pipeline3/domain/case_merge_policy.py`
    - `server/careena_pipeline3/domain/__init__.py`
  - Naechster Punkt:
    - als naechsten Phase-1-Schnitt die Update-Entscheidung und den
      eigentlichen Case-Mutationsschritt noch klarer voneinander trennen,
      besonders rund um Konflikt-/Unsicherheitsfolgen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 44 Datum: 08-06-26 00:36 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den naechsten Phase-1-Schnitt umgesetzt:
      die eigentliche Case-Mutation aus `CaseMerger` in einen neuen
      `CaseUpdateApplier` herausgezogen, `CaseUpdateOutcome` um sichtbare
      `dialogue_consequences` und `decision_log` erweitert und den
      `CaseStateManager` so angepasst, dass diese Dialogfolgen im Turn-Trace
      sichtbar weitergetragen werden
  - Warum:
    - nach der ersten Trennung von Observation-Normalisierung und
      Identitaetsaufloesung sollte nun auch die Grenze zwischen
      Update-Entscheidung und tatsaechlicher Case-Mutation expliziter werden
    - ausserdem verlangt Phase 1, Konflikt- und Unsicherheitsfolgen nicht nur
      implizit in Merge-Notizen zu verstecken, sondern als eigene Rueckgabe
      sichtbar zu machen
  - Wirkung:
    - `CaseMerger` konzentriert sich staerker auf Turn-weise
      Update-Orchestrierung
    - die eigentliche Mutation lebt jetzt in einer eigenen Truth-Komponente
    - Konflikt-/Disambiguierungsfolgen koennen downstream gezielter konsumiert
      werden, statt nur indirekt aus Trace-Strings rekonstruiert zu werden
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/case_update_applier.py`
    - `server/careena_pipeline3/domain/case_update.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/domain/__init__.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
  - Naechster Punkt:
    - die neuen sichtbaren `dialogue_consequences` als echten Input fuer
      Follow-up-/Dialogue-State pruefen, statt sie vorerst nur im Trace zu
      konservieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 45 Datum: 08-06-26 00:46 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - an den frisch refaktorierten Klassen im Case-Truth-Bereich ein
      einheitliches Kurz-Dokuformat direkt ueber den Klassen ergaenzt
      (`Date`, `Last changed`, `Author`, `Short description`)
  - Warum:
    - fuer die neuen und umgeschnittenen Verantwortungen in Phase 1 soll die
      Rolle jeder Klasse im Code selbst schneller lesbar und wartbarer werden
  - Wirkung:
    - die neuen Truth-Bausteine und die angrenzenden Klassen sind direkt im
      Code besser einordenbar, ohne erst die Refactor-Dokumentation lesen zu
      muessen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/domain/observation_normalizer.py`
    - `server/careena_pipeline3/domain/observation_identity_resolver.py`
    - `server/careena_pipeline3/domain/case_merge_policy.py`
    - `server/careena_pipeline3/domain/case_update_applier.py`
    - `server/careena_pipeline3/domain/case_update.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
  - Naechster Punkt:
    - bei weiteren Phase-1-Schnitten dieselbe Dokuform direkt mitpflegen,
      damit neue Verantwortungen im Code sichtbar bleiben
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 46 Datum: 08-06-26 00:53 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die neuen `dialogue_consequences` aus dem Case-Update erstmals als
      echten Dialogue-State-Eingang angeschlossen:
      `PendingFollowup` traegt jetzt einen kleinen Typ
      (`requirement`, `conflict`, `disambiguation`), die
      `DialogueStateService`-/`RequirementPolicy`-Kette kann
      Konflikt-/Disambiguierungsfolgen in einen expliziten Follow-up-Zustand
      ueberfuehren, und Entry-/Call-2-Mode-/Extraction-Pfad behandeln nur noch
      requirement-getriebene Follow-ups als Slot-Update-Kandidaten
  - Warum:
    - der letzte Phase-1-Schritt hatte Konflikt- und Disambiguierungsfolgen
      bereits strukturiert aus dem Merge zurueckgegeben, sie wurden aber noch
      nicht als echter Dialogzustand genutzt
    - fuer die Zielarchitektur reicht es nicht, solche Folgen nur zu loggen;
      sie muessen sichtbar in die Follow-up-Steuerung eingehen, ohne dabei
      faelschlich wie normale Requirement-Slots behandelt zu werden
  - Wirkung:
    - widerspruechliche oder mehrdeutige Case-Updates koennen jetzt gezielt
      als eigener Follow-up-Typ in der Antwortlogik landen
    - `followup_slot_update` bleibt auf echte Requirement-Follow-ups begrenzt
      und springt nicht versehentlich auf Konflikt-/Disambiguierungsfragen an
    - die Response-Texte fuer diese neuen Follow-up-Typen sind jetzt separat
      formuliert
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/dialogue.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/case_state_manager.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/extraction_manager.py`
    - `server/careena_pipeline3/application/services/dialogue_state_service.py`
    - `server/careena_pipeline3/application/services/call2_operation_mode_service.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena_pipeline3/domain/requirement_policy.py`
  - Naechster Punkt:
    - pruefen, ob aus `decision_log` und `dialogue_consequences` als naechstes
      ein noch klarerer Konflikt-/Unsicherheitszustand im Dialogue-State
      modelliert werden sollte statt nur ein typisierter Follow-up
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 47 Datum: 08-06-26 01:22 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den naechsten offenen Phase-1-Punkt umgesetzt:
      Konflikt und Ambiguitaet werden jetzt als explizite `CaseIssue`-Objekte
      im kanonischen `MedicalCase` gehalten; nicht-mutierende
      Update-Entscheidungen wie `flag_conflict` und `defer_update` erzeugen
      diese sichtbaren Case-Issues statt nur indirekte Follow-up-Spuren
  - Warum:
    - Phase 1 verlangt, dass Konflikt und Unsicherheit nicht nur als
      Nebenfolge im Dialog auftauchen, sondern als sichtbarer Teil der
      Case-Truth-Schicht modelliert werden
    - die bisherige `dialogue_consequence`-Rueckgabe war ein guter Anfang, aber
      noch kein eigener stabiler Wahrheitszustand
  - Wirkung:
    - `MedicalCase` kann jetzt explizite ungelÃ¶ste Truth-Probleme tragen
    - `CaseMerger` / `CaseUpdateApplier` unterscheiden klarer zwischen
      mutierenden Updates und sichtbaren nicht-mutierenden Konfliktlagen
    - spaetere Phasen koennen diese `issues` fuer Follow-up, Readiness oder
      Response gezielter konsumieren
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/case_issue.py`
    - `server/careena_pipeline3/models/domain/case.py`
    - `server/careena_pipeline3/models/domain/__init__.py`
    - `server/careena_pipeline3/domain/case_update_applier.py`
    - `server/careena_pipeline3/domain/case_merger.py`
  - Naechster Punkt:
    - Phase 1 erneut gegen die Block-Gates halten und dann entscheiden, ob als
      letzter offener Phase-1-Zug eher `CaseObservation` weiter entlastet oder
      schon sauber in Phase 2 uebergegangen werden kann
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 48 Datum: 08-06-26 01:22 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - das vereinbarte Klassen-Dokuformat auch fuer die neu dazugekommenen
      Case-Issue-Dateien nachgezogen
  - Warum:
    - der neue Konflikt-/Unsicherheitszustand soll dieselbe direkte
      Code-Lesbarkeit tragen wie die vorherigen Phase-1-Schnitte
  - Wirkung:
    - `MedicalCase` und `CaseIssue` tragen jetzt ebenfalls die kurzen
      Metadaten- und Rollenbeschreibungen direkt ueber der Klasse
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/case.py`
    - `server/careena_pipeline3/models/domain/case_issue.py`
  - Naechster Punkt:
    - bei weiteren neuen Phase-1-/2-Klassen dieselbe Dokuform direkt
      miterzeugen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 49 Datum: 08-06-26 01:41 ===
  - Kategorie:
    - `cleanup`
  - Bereich:
    - `backend`
  - Aenderung:
    - den alten Injury-`context`-Legacy-Fallback aus `CaseObservation`
      entfernt und den ungenutzten Hilfszugang `runtime_detail_value(...)`
      mit aufgeraeumt
  - Warum:
    - die Pruefung des aktuellen Codes zeigte, dass der alte `context`-Pfad
      ausserhalb von `CaseObservation` nicht mehr aktiv genutzt wird und nur
      noch versteckte Legacy-Last im Wahrheitsmodell festhaelt
  - Wirkung:
    - Injury-Kontext wird im Domainmodell jetzt nur noch ueber den kanonischen
      Schluessel `injury_context` getragen
    - `CaseObservation` ist einen kleinen, aber echten Schritt weniger
      Reparatur-/Legacy-Schicht
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/observation.py`
  - Naechster Punkt:
    - weiter pruefen, welche Teile der internen `*_data`-
      Synchronisierungslogik in `CaseObservation` noch echte Nutzung haben und
      welche als naechste Legacy-Last entfernt werden koennen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 50 Datum: 08-06-26 01:46 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den groesseren `CaseObservation`-Synchronisierungsblock deutlich
      reduziert:
      die bidirektionale Selbstverkabelung zwischen kanonischen Feldern und
      `symptom_data` / `injury_data` / `measurement_data` /
      `medication_data` / `diagnosis_data` wurde entfernt; diese strukturierten
      Felder dienen jetzt nur noch als einseitige Rueckwaertskompatibilitaet,
      um alte gespeicherte Daten in den kanonischen Zustand zu hydrieren
  - Warum:
    - die Pruefung zeigte, dass der `*_data`-Block ausserhalb von
      `CaseObservation` kaum direkt genutzt wird und heute vor allem interne
      Selbstverkabelung darstellt
    - fuer Phase 1 soll `CaseObservation` weniger Reparatur- und mehr
      kanonisches Wahrheitsmodell sein
  - Wirkung:
    - Runtime-/Requirement-Pfade lesen jetzt direkter aus kanonischen Feldern
      und `details` / `measurement`
    - `CaseObservation` erzeugt keine neuen Spiegelobjekte mehr aus den
      kanonischen Feldern
    - alte persistierte strukturierte Daten koennen weiterhin eingelesen
      werden, druecken aber nicht mehr den laufenden Modellkern in beide
      Richtungen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/observation.py`
  - Naechster Punkt:
    - Phase 1 erneut gegen die Block-Gates halten; danach entscheiden, ob die
      verbliebenen `*_data`-Felder selbst noch entfernt werden sollen oder ob
      der Block damit sauber genug fuer den Uebergang nach Phase 2 ist
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 51 Datum: 08-06-26 02:04 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die verbliebenen strukturierten Legacy-Felder
      `symptom_data` / `injury_data` / `measurement_data` /
      `medication_data` / `diagnosis_data` aus `CaseObservation` entfernt und
      die letzte Structured-Data-Hydrierung aus dem laufenden Modellkern
      herausgenommen; `ObservationNormalizer` wurde entsprechend vereinfacht
      und Phase 1 im Refactor-Plan als abgeschlossen markiert
  - Warum:
    - nach den letzten Entlastungsschnitten waren diese Felder nur noch
      Rueckwaertskompatibilitaets-Reste ohne aktive Kernfunktion
    - fuer einen sauberen Phase-1-Abschluss sollte `CaseObservation` als
      kanonisches Wahrheitsmodell keine parallelen strukturierten Spiegel mehr
      tragen
  - Wirkung:
    - `CaseObservation` ist jetzt deutlich direkteres kanonisches Modell
    - `ObservationNormalizer` ist auf echte Oberflaechen-Normalisierung
      reduziert
    - der Phase-1-Abschluss ist jetzt auch am Codezustand glaubwuerdig
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/observation.py`
    - `server/careena_pipeline3/domain/observation_normalizer.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
  - Naechster Punkt:
    - Phase 2 offiziell aktiv ziehen und den Extraction-zu-Case-Uebergang an
      Mapper / `ResilientExtractionService` weiter entklemmen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 52 Datum: 08-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - im `ExtractionResultMapper` den ersten Phase-2-Vertragsschnitt gezogen:
      Surface-, Detail- und Measurement-Zuordnung jetzt staerker
      observationstypbezogen statt generisch ueber einen breiten
      `attributes`-Fallback
    - Measurement-Attribute werden nur noch fuer `measurement`-Observations
      uebernommen; unbekannte Detail-Keys werden nicht mehr implizit in
      `details` weitergereicht
  - Warum:
    - die Executive Summary priorisiert sichtbare Uebergangsvertraege zwischen
      Call 2 und Case-Truth statt stiller Mapper-Prothesen
    - Phase 2 soll den Extraction->Truth-Uebergang lesbarer machen, ohne schon
      neue Domain-Heuristik oder einen grossen Delta-Umbau einzuziehen
  - Wirkung:
    - der Mapper zeigt klarer, welche Attributklassen fuer welchen
      Observation-Typ ueberhaupt kanonisch anerkannt werden
    - generisches `details`-Kippen wird reduziert und der verbleibende
      Restvertrag wird expliziter sichtbar
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
  - Naechster Punkt:
    - den `ResilientExtractionService` als naechsten Phase-2-Kandidaten gegen
      dieselbe Vertragstrennung sezieren und dabei den offenen
      `severity`-Befund neu verorten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 53 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Refactor-Plan in Phase 2 um einen Zusatzbefund geschaerft:
      ein relevanter Teil der aktuellen Normalisierungs- und
      Fehlerbehebungslast entsteht vermutlich aus einem zu grossen oder zu
      unscharfen Call-2-Outputvertrag und nicht nur aus lokalen Mapper- oder
      Serviceproblemen
  - Warum:
    - die aktuelle Diskussion und die frischen Laufbeobachtungen zeigen, dass
      wir Phase 2 nicht nur als Aufraeumen von Reparaturlogik lesen sollten,
      sondern zuerst auch als Verkleinerung und Klaerung des
      Extraction-Vertrags selbst
  - Wirkung:
    - Phase 2 ist jetzt klarer gerahmt:
      erst Outputvertrag schaerfen, dann Mapper- und
      `ResilientExtractionService`-Last gegen diesen kleineren Vertrag neu
      bewerten
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
  - Naechster Punkt:
    - Call-2-Prompt, `ExtractionResult` und nachgelagerte Reparaturlogik
      gezielt darauf sezieren, welche Teile nur wegen ueberladener
      Ergebnisstruktur existieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 54 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - Phase 2 im Refactor-Plan um zwei konkrete Architekturhinweise
      geschaerft:
      der aktuelle Kontextbuilder ist selbst als Uebergangsprothese
      verdaechtig, und die kuenftige Normalisierung soll eher auf kleinen
      Objekten mit engen Guardrails als auf grossen Sammelstrukturen laufen
  - Warum:
    - die aktuelle Analyse des Call-2-Pfads zeigt, dass nicht nur Mapper und
      Fehlerbehebung, sondern schon Kontextpaket und Ergebniszuschnitt die
      spaetere Komplexitaet treiben
    - zusaetzlich wurde als wertvolle Richtung festgehalten, dass enge
      LLM-Hilfsschritte eher fuer objektweise Normalisierung und
      Konfliktentscheidung taugen als fuer breite Re-Emission grosser JSONs
  - Wirkung:
    - Phase 2 ist jetzt klarer auf kleinen Objektvertraegen, enger
      Normalisierung und einer kritischen Neubewertung des Kontextbuilders
      ausgerichtet
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
  - Naechster Punkt:
    - aus diesen Leitplanken einen konkreten Soll-Zuschnitt fuer Call 2,
      Kontextbuilder und objektweise Normalisierung ableiten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 55 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - Phase 2 im Refactor-Plan um die gemeinsame Arbeitsannahme erweitert,
      dass Call 2 nicht das breite Case-Objekt zusammenbauen soll, sondern den
      Case-Truth-Layer mit kleinen medizinischen Eintraegen befuellt
  - Warum:
    - die laufende Analyse des Kontextbuilders und des grossen
      Extraction-Vertrags zeigt, dass die aktuelle Ueberfrachtung auch daraus
      entsteht, dass Call 2 zu viel Fallreprasentation auf einmal tragen soll
  - Wirkung:
    - die naechste Phase-2-Sezierung ist klarer ausgerichtet:
      knapper relevanter Kontext fuer Call 2 statt breite Fall- und
      Dialogpakete
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
  - Naechster Punkt:
    - den Kontextbuilder Feld fuer Feld gegen diese Zielrolle pruefen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 56 Datum: 08-06-26 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - in der Workbench eine neue Zwischenstandsdoku
      `CAREENA3_CURRENT_WEAKNESSES.md` angelegt, die die aktuell groessten
      Schwachstellen aus Refactor-, Log- und Architekturkontext kompakt
      buendelt
  - Warum:
    - die laufende Phase-2-Analyse produziert inzwischen genug klares Material,
      dass ein eigener schneller Ueberblick ueber die groessten Baustellen
      nuetzlich ist
  - Wirkung:
    - es gibt jetzt ein separates Arbeitsbild fuer:
      ueberladenen Call-2-Vertrag, problematischen Kontextbuilder, schweren
      Normalisierungspfad, Sammelrolle von
      `ResilientExtractionService` und das offene `guide_next_step`-
      Transitionsthema
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/workbench/2026-06-08/CAREENA3_CURRENT_WEAKNESSES.md`
  - Naechster Punkt:
    - auf Basis dieser Verdichtung den kleineren Sollvertrag fuer Call 2
      formulieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 57 Datum: 08-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den aktiven Paketordner `server/careena_pipeline3/infrastructure/` nach
      `server/careena_pipeline3/server_log/` umgestellt und die laufenden
      Imports auf `careena_pipeline3.server_log` bzw.
      `careena_pipeline3.server_log.logging` angepasst
    - das neue `server_log/__init__.py` intern auf den umbenannten Paketpfad
      korrigiert
  - Warum:
    - der Nutzer wollte den Infrastrukturordner in `server_log` umbenennen und
      die Referenzen entsprechend bereinigen
  - Wirkung:
    - aktive Codepfade importieren Logging und Session-Store jetzt ueber
      `server_log`
    - im alten Ordner bleibt vorerst nur `infrastructure/logs` zurueck, weil
      die aktuell geoeffneten Logdateien den kompletten Ordnerumzug blockiert
      haben; neuer Code zeigt aber bereits auf `server_log/logs`
  - Betroffene Dateien/Bereiche:
    - `server/careena3.py`
    - `server/careena_pipeline3/bootstrap.py`
    - `server/careena_pipeline3/runtime.py`
    - `server/careena_pipeline3/simulation_runtime/runner.py`
    - `server/careena_pipeline3/application/services/intent_classification_service.py`
    - `server/careena_pipeline3/application/services/resilient_extraction_service.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/llm/extraction_result_normalizer.py`
    - `server/careena_pipeline3/server_log/__init__.py`
  - Naechster Punkt:
    - nach einem Prozess-/Handle-Wechsel den verbliebenen alten
      `infrastructure/logs`-Restordner aufraeumen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 58 Datum: 08-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die Umbenennung nachgeschliffen:
      `session_store.py` wieder nach
      `server/careena_pipeline3/infrastructure/` zurueckgelegt und die
      Runtime-/Bootstrap-Imports entsprechend aufgeteilt
    - `server_log` exportiert jetzt nur noch Logging, waehrend
      `infrastructure` wieder den Session-Store kapselt
  - Warum:
    - der Nutzer wollte den `session_store` explizit zurueck in
      `infrastructure`, statt ihn mit dem Logging-Rename mitzuziehen
  - Wirkung:
    - Paketgrenzen sind jetzt klarer:
      `server_log` fuer Logging,
      `infrastructure` fuer Session-Store
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/infrastructure/session_store.py`
    - `server/careena_pipeline3/infrastructure/__init__.py`
    - `server/careena_pipeline3/server_log/__init__.py`
    - `server/careena_pipeline3/bootstrap.py`
    - `server/careena_pipeline3/runtime.py`
  - Naechster Punkt:
    - optional den verbliebenen alten Log-Restpfad spaeter weiter bereinigen,
      falls die Handle-Situation das zulaesst
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 59 Datum: 10-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - fuer Block 5 einen kleinen expliziten Process-State-Vertrag eingefuehrt:
      `ProcessStateSignals` haelt jetzt getrennt sichtbar fest, ob ein offenes
      Requirement-Follow-up beantwortet wurde und ob im selben Turn
      zusaetzliche medizinische Information erkannt wurde
    - `EntryDecision` traegt das bestehende kleine Call-1-Signal
      `additional_medical_information` jetzt explizit weiter, statt dass die
      spaetere Process-State-Schicht es indirekt erraten muss
    - `DialogueStateService` bildet nach dem Case-Update aus alter
      `pending_followup`-Lage und neuer Requirement-Aufloesung ein kleines
      Prozessresultat; der `DialogueManager` uebernimmt diese Signale jetzt
      sichtbar in den `TurnContext`
    - den vorhandenen Unit-Test gegen die reale Manager-Grenze nachgeschliffen
      und einen gezielten Test fuer den Mischfall
      `answered follow-up + additional info` hinzugefuegt
  - Warum:
    - Block 5 sollte laut V3 zuerst Process-State, Requirement-Resolution und
      Gate deutlicher trennen, ohne neue versteckte Fachheuristik einzuziehen
    - der Mischfall sollte als gleichzeitige Doppelspur sichtbar werden, ohne
      daraus eine neue vermischte Wahrheitszone zu machen
  - Wirkung:
    - Follow-up-Erfuellung ist jetzt als Prozesssignal lesbar, waehrend neue
      medizinische Information weiterhin Case-seitig bleibt
    - `RecommendationStateService` muss diese Lage nicht selbst reparieren,
      sondern kann spaeter auf bereits explizitere Prozess- und
      Requirement-Signale lesen
    - der eigentliche Mischfall ist jetzt vertraglich sichtbar, auch wenn die
      tiefere Call-2-/Merge-Behandlung solcher Turns spaeter noch weiter
      verfeinert werden kann
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/state_updates.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/services/dialogue_state_service.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/tests/test_dialogue_manager.py`
  - Naechster Punkt:
    - im naechsten Block-5-Nachschnitt pruefen, ob `mixed_update_and_new_info`
      an der Call-2-/Truth-Kante selbst noch enger an Fokus-Update und
      Zusatzinformation getrennt werden muss, damit die sichtbare
      Prozessspur auch im Laufverhalten konsequent bedient wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 60 Datum: 10-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den aktiven Uebergangsadapter von `Call2ExtractionResult` auf
      `ExtractionResult` so nachgeschaerft, dass `focus_update` und
      `new_items` ihre kleine Vertragsrolle ueber technische
      `call2_contract_role`-Signals in den transitional Pfad mitnehmen
    - `PythonExtractionResultNormalizer` fuer
      `mixed_update_and_new_info` erweitert:
      wenn ein Requirement-Follow-up plus Zusatzinfo im selben Turn vorliegt,
      wird der markierte `focus_update` jetzt gezielt an die bestehende
      Fokus-Observation gebunden, waehrend getrennte Zusatzfakten als
      weitere Observationen erhalten bleiben
    - die Follow-up-Slot-Normalisierung enger gemacht:
      wenn der primaere Call den eigentlichen Slotwert bereits klein in
      `attributes` geliefert hat, wird dieser Wert bevorzugt statt den ganzen
      Rohsatz in den Fokus-Update zu schreiben
    - den Call-2-Prompt fuer `mixed_update_and_new_info` leicht nachgeschaerft
      und einen gezielten Unit-Test fuer die neue Kante hinzugefuegt
  - Warum:
    - der verbleibende Rest nach Block 5 sass nicht mehr in der
      Process-State-Schicht, sondern an der Call-2-/Truth-Kante:
      der aktive Runtime-Pfad konnte die vorhandene Trennung
      `focus_update` vs `new_items` noch nicht robust genug bewahren
  - Wirkung:
    - der Mischfall `Follow-up beantwortet + neue Information` bleibt jetzt
      nicht nur prozessual sichtbar, sondern wird auch an der
      Extraktions-/Truth-Kante sauberer in Fokus-Update und Zusatzfakt
      getrennt
    - die Runtime ist dadurch naeher am schon dokumentierten Call-2-Vertrag,
      ohne dass dafuer neue Prozessheuristik in spaetere Schichten gezogen
      werden musste
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/extraction/result.py`
    - `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/tests/test_python_extraction_result_normalizer.py`
  - Naechster Punkt:
    - im Laufverhalten pruefen, ob der neue Mischmodus jetzt auch in echten
      Dialogen die Wiederholung derselben Rueckfrage verhindert; falls nein,
      als naechsten kleinen Schnitt die Merge-/Fokus-Weitergabe des
      gemischten Turns selbst untersuchen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 61 Datum: 10-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den ersten Block-6-Schnitt umgesetzt:
      `guide_next_step` ist nicht mehr nur ein Textmodus, sondern setzt jetzt
      einen kleinen expliziten dialogischen Transition-Zustand im
      `DialogueState` ueber `PendingDialogueTransition`
    - `ResponseManager` schreibt diesen kleinen Freigabe-Zustand bei
      `guide_next_step` sichtbar in den `ResponsePlan`, waehrend der
      `DialogueManager` ihn anschliessend in den laufenden Dialogzustand
      uebernimmt oder wieder loescht
    - `EntryManager` liest diesen dialogischen Transition-Zustand jetzt vor
      Call 1:
      Antworten wie `Nein.` auf den Recommendation-Abschluss-Check werden
      direkt als dialogische Freigabe fuer Recommendation behandelt
      statt nochmals als medizinischer Extraktions-Turn durch Call 1 / Call 2
      zu laufen
    - einen gezielten Block-6-Testpfad hinzugefuegt:
      `guide_next_step -> Nein. -> recommend`
  - Warum:
    - der aktuelle Logrest sass nicht mehr in Block 5, sondern an der
      hinteren Response-/Recommendation-Transition:
      Text behauptete bereits einen Abschlussknoten, waehrend der Zustand
      diesen noch nicht sauber trug
  - Wirkung:
    - medizinische Requirement-Follow-ups und dialogische
      Abschluss-/Freigabe-Follow-ups sind jetzt erstmals explizit getrennt
    - der hintere Knoten ist sauberer verkabelt:
      `Nein.` nach `guide_next_step` kann Recommendation freigeben, ohne
      vorher wieder in unnnoetige Extraktion abzugleiten
    - die spaetere Inhaltsfrage
      `Call 3` vs. anderer Werkzeugkasten-Modus
      bleibt dabei bewusst offen und wurde nicht vorschnell in diesen Schnitt
      hineingezogen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/dialogue.py`
    - `server/careena_pipeline3/models/domain/__init__.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/models/turn/response_plan.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - im echten Lauf-/Simrun pruefen, ob der Recommendation-Abschluss-Check
      jetzt stabil funktioniert und welche weiteren Antworten ausser
      explizitem `Nein.` noch als dialogische Freigabe oder als neue
      medizinische Information gelesen werden sollten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 62 Datum: 10-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den neuen Recommendation-Abschlussknoten im Code noch enger an das
      Block-6-Konzept angezogen:
      `PendingDialogueTransition` traegt jetzt explizit die erlaubten
      semantischen Abschlussaktionen
      `request_recommendation`
      und
      `report_more_information`
    - `EntryDecision` bekam dafuer ein kleines
      `dialogue_transition_action`, damit der Entry-Vertrag den hinteren
      Zwei-Wege-Knoten jetzt nicht nur implizit, sondern sichtbar tragen kann
    - `EntryManager` behandelt dadurch jetzt nicht nur
      `Nein.` als Recommendation-Freigabe,
      sondern markiert medizinische Antworten auf denselben Abschlussknoten
      explizit als
      `report_more_information`,
      loest den dialogischen Transition-State auf
      und fuehrt sauber zurueck in den medizinischen Pfad
    - den Gegenpfad mit eigenem Unit-Test abgesichert
  - Warum:
    - der erste Block-6-Schnitt loeste bereits den Recommendation-Commit,
      trug aber die Zwei-Wege-Semantik aus dem Konzept noch nicht explizit
      genug im Vertrag selbst
  - Wirkung:
    - der Recommendation-Abschluss ist jetzt im Code nicht mehr nur
      `Nein. -> recommend`,
      sondern ein kleiner expliziter Zustandsknoten mit zwei erlaubten
      semantischen Ausgaengen
    - damit passen Konzept, Policy-Kante und spaetere moegliche
      Frontend-Antwortvorschlaege enger zusammen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/dialogue.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - im echten Lauf-/Simrun pruefen, wie breit die Recommendation-Freigabe-
      Formulierungen sein duerfen
      und welche freien Antworten noch als
      `report_more_information`
      gegen denselben Abschlussknoten gelesen werden sollen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 63 Datum: 10-06-26 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Block-6-Abschlussknoten im `EntryManager` von der groben
      Kategorie-Abfrage `gateway.is_medical` auf echte Call-1-Eingangssignale
      umgestellt:
      `report_more_information` wird jetzt aus dem Scout-Vertrag abgeleitet,
      primaer ueber `next_step:extract`,
      `medical_relevance:*`
      und vorhandene Case-Hinweise
    - `request_recommendation` laesst sich jetzt neben der Kurzform
      `Nein.`
      auch aus den normalen Recommendation-Signalen des Gateways ableiten
    - nicht aufloesende soziale Antworten auf den aktiven
      Recommendation-Abschlussknoten loesen den Transition-State nicht mehr
      vorschnell auf,
      sondern halten ihn offen und fuehren wieder in denselben
      `guide_next_step`-Pfad zurueck
    - die sichtbare Abschlussfrage fuer `guide_next_step` enger auf die
      Zwei-Wege-Semantik umformuliert:
      Versorgungsempfehlung jetzt
      oder weitere Beschwerden
    - den neuen Signalvertrag mit zusaetzlichen Unit-Tests fuer
      expliziten Recommendation-Wunsch,
      nicht aufloesende soziale Antwort
      und den wiederholten Transition-Pfad abgesichert
  - Warum:
    - der Block-6-Knoten sollte sich laut Konzept aus den Eingangssignalen
      ableiten lassen und nicht nur ueber eine zu grobe
      medizinisch/nicht-medizinisch-Heuristik laufen
  - Wirkung:
    - der hintere Zwei-Wege-Knoten ist jetzt naeher am eigentlichen
      Call-1-Scout-Vertrag
      und reagiert damit robuster auf freie Eingaben
    - soziale oder unklare Zwischenantworten werfen den Nutzer nicht mehr so
      leicht aus dem Recommendation-Abschlussfluss heraus
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/workflow/intent_gateway.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - im echten Lauf pruefen, ob die realen Call-1-Signale fuer freie
      Abschlussantworten breit genug sind
      oder ob am Prompt noch feinere Dialoghinweise gebraucht werden
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 103 Datum: 12-06-26 03:56 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - den neuen Architektur-Experimententwurf
      `autodoc/2026-06-11/ARCHITECTURE_REDUCTION_REBUILD_CONCEPT.md`
      grundsaetzlich von einer zu engen `careena_pipeline3`-Innenansicht auf
      das allgemeine Careena-System umgebaut
    - dabei den historischen Ursprung als freierer Chat mit Master Prompt,
      die heutige Produktschale in `server/careena3.py`,
      Session-/Logging-/Simulationshuelle
      sowie die Zielspannung zwischen Chat-Vorderseite und strukturierter
      Rueckseite explizit aufgenommen
    - den Reduktionspass jetzt bewusst bis zur elementaren allgemeinen
      Systemform
      `Nachricht -> Anliegen deuten -> strukturierte Wahrheit updaten ->
      begrenzten naechsten Zug waehlen -> antworten`
      heruntergezogen
    - den Wiederaufbau anschliessend ueber
      Gespraechsflaeche,
      concern-Lage,
      medizinische Wahrheit,
      Dialogsteuerung,
      Readiness/Gate,
      Antwortstrategie
      und Recommendation-Inhalt neu gefasst
    - mehrere neue Mermaid-Bilder fuer Gesamtsystem,
      Reduktionsstufen,
      Sollbild,
      Aussenhuelle
      und Entwicklungsstufen ergaenzt
  - Warum:
    - der erste Entwurf war zu stark auf den engeren Turn-Kern bezogen
      und machte die allgemeine Careena-Architektur noch nicht ausreichend
      sichtbar
  - Wirkung:
    - die Synchronisationsdatei beschreibt Careena jetzt hoeher und
      vollstaendiger:
      nicht nur als Manager-/Turn-System,
      sondern als bounded conversational medical system
    - zugleich wird klarer,
      dass die fehlende concern-nahe Lage ein Gesamtproblem des Systems ist
      und nicht nur ein lokaler `pipeline3`-Bug
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/2026-06-11/ARCHITECTURE_REDUCTION_REBUILD_CONCEPT.md`
  - Naechster Punkt:
    - dieses Gesamtbild nun gegen
      `REFACTOR_PLAN_V4.md`
      lesen
      und daraus spaeter ableiten,
      welche bestehenden aktiven Pfade zuerst von
      `primary_focus`-gekoppelter auf concern-nahe Semantik umgestellt werden
      sollten
  - DEV_NOTE:
    - `workbench@codex`

=== CHANGE NUMBER: 104 Datum: 12-06-26 04:07 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Architekturentwurf um den bisher zu wenig sichtbaren
      Mittelstreifen zwischen
      `Entry peek`,
      optionaler tieferer Verarbeitung,
      `Truth write ja/nein`
      und begrenztem Antwortpfad erweitert
    - dafuer im Reduktionspass eine eigene Stufe
      `Der Mittelstreifen Zwischen Peek, Extraktion, Wahrheit Und Antwort`
      ergaenzt
      und im Wiederaufbau das Sollbild so erweitert,
      dass diese Steuerzone nicht mehr als implizite Restflaeche erscheint
    - zusaetzlich die heutigen Antwortoptionen dieser Mittelzone explizit
      gemacht:
      keine Extraktion,
      Extraktion ohne Truth-Write,
      Extraktion mit Truth-Write,
      sowie die daran anschliessenden begrenzten Response-Bahnen
    - die Rollen von `Entry`,
      `Call 2`,
      `MedicalCase`
      und `Response`
      nochmals schaerfer voneinander getrennt beschrieben
  - Warum:
    - im ersten Gesamtentwurf war zwar die hohe Careena-Systembrille klarer,
      aber der eigentliche Steuerkern zwischen kurzem Nachricht-Peek,
      optionaler Extraktion,
      Fallwahrheit
      und Antwortpfad noch zu flach dargestellt
  - Wirkung:
    - das Konzept beschreibt Careena jetzt naeher an der eigentlichen
      Produktidee:
      Nutzerangaben strukturiert erfassen
      und gleichzeitig die Antwort- und Verarbeitungsachsen des LLM intern
      eng begrenzen
    - dadurch wird besser sichtbar,
      dass die Steuerbarkeit des Systems nicht nur an
      `MedicalCase`
      oder `Response`,
      sondern besonders an dieser mittleren Kontrollzone haengt
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/2026-06-11/ARCHITECTURE_REDUCTION_REBUILD_CONCEPT.md`
  - Naechster Punkt:
    - spaeter aus diesem Mittelstreifen-Modell ableiten,
      welche aktiven Runtime-Pfade heute schon
      `Entry -> Call 2 -> Truth write -> Response`
      sauber tragen
      und wo noch implizite Mischpfade bestehen
  - DEV_NOTE:
    - `workbench@codex`

=== CHANGE NUMBER: 105 Datum: 12-06-26 04:14 ===
  - Kategorie:
    - `doc`
  - Bereich:
    - `backend`
  - Aenderung:
    - den Architekturentwurf um eine konkrete Runtime-Abbildung des
      Mittelstreifens erweitert:
      `DialogueManager`,
      `EntryManager`,
      `ExtractionManager`,
      `CaseStateManager`,
      `DialogueStateService`,
      `RecommendationStateService`,
      `ResponseManager`
      und `ResponseGenerationService`
      sind jetzt als realer Laufpfad im Dokument gespiegelt
    - dabei explizit gemacht,
      dass `EntryManager` heute den echten kurzen Peek traegt,
      `ExtractionManager` nur optional tiefer arbeitet,
      `CaseStateManager` die reale Truth-Kante ueber
      `case_update_bridge`
      haelt
      und `ResponseManager` die begrenzten Antwortbahnen waehlt
    - zusaetzlich die aktuellen Restmischstellen dieser Runtime-Lesart
      benannt,
      besonders:
      implizite Truth-write-Schwelle,
      ueberladene Entry-Kreuzung,
      concern-freie obere Antwortbahnen
  - Warum:
    - nach der hoehere Architekturbrille fehlte noch die direkte Bruecke in
      den echten heutigen Runtime-Pfad,
      damit der Mittelstreifen nicht nur konzeptionell,
      sondern im aktiven Code lesbar wird
  - Wirkung:
    - das Konzept zeigt nun nicht nur Sollstruktur,
      sondern auch,
      welche realen Klassen den Steuerkern heute bereits tragen
    - dadurch ist klarer erkennbar,
      welche Teile des Systems schon nah an der Produktidee sind
      und wo noch implizite Mischungen fuer spaetere Refactor-Schritte
      aufgebrochen werden muessen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/2026-06-11/ARCHITECTURE_REDUCTION_REBUILD_CONCEPT.md`
  - Naechster Punkt:
    - aus dieser Runtime-Abbildung spaeter eine noch schaerfere Liste
      konkreter Umhaengepunkte ableiten:
      welche aktiven Lesepfade von
      `primary_focus`
      oder impliziter Gate-Logik
      zuerst auf concern-nahe Semantik umgestellt werden sollten
  - DEV_NOTE:
    - `workbench@codex`

=== CHANGE NUMBER: 106 Datum: 12-06-26 11:24 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - einen kleinen expliziten `ConcernState` als eigene concern-nahe Schicht
      eingefuehrt
      statt das Nutzeranliegen schon jetzt in `MedicalCase`,
      `DialogueState`
      oder `Readiness` hineinzumischen
    - dazu einen bewusst kleinen `ConcernStateService` angelegt,
      der aktuell nur zwei ehrliche Aufgaben traegt:
      vorhandenen Concern-Zustand sicher initialisieren
      und nach Case-Updates verwaiste Observation-Links bereinigen
    - `ConcernState` durch die aktive Runtime verdrahtet:
      Session-Store,
      `TurnInput`,
      `TurnContext`,
      `DialogueManager`,
      HTTP-Chatpfad in `careena3.py`
      und Simulation-Adapter
    - den `DialogueManager` so erweitert,
      dass der persistierte Concern-Zustand jetzt frueh in den Turn geladen
      und nach der Truth-Kante sichtbar normalisiert wird,
      ohne ihm schon Recommendation- oder Response-Policy-Macht zu geben
    - den `GET /case`-Pfad erweitert,
      damit `concern_state` auch dann sichtbar bleibt,
      wenn noch kein `MedicalCase` existiert
    - die Orchestrierungs- und Concern-Service-Kante mit kleinen Unit-Tests
      abgesichert;
      fuer den Testlauf wurden in den bestehenden Testdateien die in dieser
      Umgebung fehlenden Module
      `openai`
      und
      `dotenv`
      testseitig gestubbt
  - Warum:
    - das Nutzeranliegen sollte im Code jetzt sichtbar werden,
      ohne gleich einen grossen Umbau oder neue Mischlogik zu erzwingen
    - V4 verlangt hier eine kleine ehrliche Schicht statt einer fachlich
      scheinbar cleveren Abkuerzung
  - Wirkung:
    - Careena hat nun eine erste echte concern-nahe Laufspur,
      die parallel zum `MedicalCase` mitgefuehrt werden kann,
      ohne schon die halbe Runtime umzustellen
    - der Einbau bleibt bewusst defensiv:
      Sichtbarkeit und Persistenz ja,
      neue verdeckte Policy oder Heuristik nein
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/concern.py`
    - `server/careena_pipeline3/models/domain/__init__.py`
    - `server/careena_pipeline3/application/services/concern_state_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/models/turn/input.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/infrastructure/session_store.py`
    - `server/careena3.py`
    - `server/careena_pipeline3/simulation_runtime/adapters/careena_pipeline3.py`
    - `server/tests/test_dialogue_manager.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - als naechstes nur gezielt lesen,
      welche bestehenden Runtime-Pfade diesen Concern-Zustand bereits passiv
      mitlesen sollten,
      bevor daraus spaeter eng begrenzte concern-nahe Steuerung entsteht
  - DEV_NOTE:
    - `workbench@codex`

=== CHANGE NUMBER: 107 Datum: 12-06-26 14:37 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - Block 1 aus `REFACTOR_PLAN_V5.md` als kleiner echter
      concern-/fortschrittsnaher Runtime-Vertrag begonnen,
      statt `recommendation_ready`
      und lokales Antwortverhalten weiter still dieselbe Semantik tragen zu
      lassen
    - `ConcernState` um minimale persistente Signale erweitert:
      `active_concern_id`,
      `phase`,
      `information_sufficiency`
      und
      `active_closing_node`
    - im Turn-Kontext und im `EntryDecision` neue kleine turn-lokale Signale
      sichtbar gemacht:
      `concern_relation`,
      `latest_turn_role`
      und
      `allowed_next_step`
    - `EntryManager` so erweitert,
      dass vorhandene Steuersignale aus Gateway und
      Recommendation-Transition jetzt direkt auf diese concern-nahe
      Lesart abgebildet werden,
      statt nur implizit in Trace-Notizen oder spaeteren Response-Regeln zu
      leben
    - `ConcernStateService` von reiner Initialisierung/Pruning-Logik auf einen
      kleinen V5-konformen Dreischritt erweitert:
      nach Entry,
      nach Case-Update,
      nach Readiness;
      dabei werden concern-nahe Phase,
      Informationsstand
      und der erlaubte naechste Zug explizit abgeleitet
    - `DialogueManager` so nachgezogen,
      dass diese Signale jetzt sichtbar durch den aktiven Turn laufen
      und nicht erst spaet wieder aus verteilten Booleans rekonstruiert werden
    - `RecommendationStateService` und `ResponseManager` auf die neue
      Vertragslage umgelegt:
      `Readiness` bleibt Input,
      aber Recommendation- und sichtbare Response-Pfade lesen jetzt zusaetzlich
      den concern-nahen Fortschrittsvertrag,
      besonders ueber
      `allowed_next_step`
    - die betroffenen Unit-Tests angepasst
      und um einen kleinen Concern-Progress-Test erweitert
  - Warum:
    - V5 verlangt zuerst eine minimale explizite concern-/Fortschrittssemantik,
      bevor Freigabelogik,
      Response
      und spaeter Call 2 wieder sauber gegeneinander ausgerichtet werden
      koennen
    - damit wird `Readiness` sichtbar entlastet:
      sie beantwortet weiter Mindestinformationsfragen,
      aber nicht mehr allein die gesamte Abschluss- und Freigabelogik
  - Wirkung:
    - Careena hat jetzt im aktiven Lauf erstmals eine kleine explizite
      concern-nahe Fortschrittslesart,
      die zwischen medizinischer Wahrheit,
      Readiness
      und sichtbarer Antwortwahl vermittelt
    - vorhandene Steuersignale wie
      `recommendation_ready_check`,
      Recommendation-Request
      und medizinische Rueckkehrpfade laufen jetzt ueber einen kleineren,
      expliziteren Vertrag statt nur ueber verstreute Spezialableitungen
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/concern.py`
    - `server/careena_pipeline3/models/domain/__init__.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/services/concern_state_service.py`
    - `server/careena_pipeline3/application/services/recommendation_state_service.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/tests/test_dialogue_manager.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - als naechstes gezielt pruefen,
      ob die neue concern-/fortschrittsnahe Lesart an den heutigen
      Freigabe- und Response-Kanten schon ausreicht
      oder wo Block 2 daraus jetzt einen kleineren expliziten
      Freigabevertrag schneiden sollte
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 108 Datum: 12-06-26 14:49 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - Block 2 aus `REFACTOR_PLAN_V5.md` als kleinen expliziten
      Freigabevertrag begonnen
      und die bisher noch verteilte Abschluss-/Rueckweglogik auf eine
      sichtbare Gate-Stufe gezogen
    - in `ReadinessStateUpdate` eine explizite
      `RecommendationGateDecision`
      eingefuehrt,
      die `Readiness` von der Frage trennt,
      welcher naechste Zug tatsaechlich erlaubt ist
    - `RecommendationStateService` so erweitert,
      dass nach der Mindestinformationspruefung jetzt kleine explizite
      Gate-Lagen gebildet werden,
      etwa:
      `cannot_assess`,
      `concern_clarification`,
      `closing_check`,
      `return_to_medical`,
      `recommendation_open`,
      `recommendation_allowed`
    - `DialogueManager` uebernimmt diese Gate-Entscheidung jetzt sichtbar in
      den Turn-Kontext
      und leitet daraus weiterhin `allowed_next_step` als kleinere
      Orchestrierungsachse ab
    - `ConcernStateService` so nachgezogen,
      dass concern-nahe Phase und Informationsstand jetzt gegen die neue
      Gate-Entscheidung synchronisiert werden,
      statt die Freigabelogik selbst wieder implizit zu tragen
    - `ResponseManager` auf die neue Gate-Stufe umgelegt:
      die sichtbaren Recommendation-,
      Abschluss-
      und Rueckwegpfade lesen jetzt primaer die explizite Gate-Lage
      statt nur verstreute Ready-/Transition-Kombinationen
    - die Tests nachgezogen
      und um einen kleinen Gate-spezifischen Vertragstest erweitert
  - Warum:
    - Block 2 verlangt,
      dass Abschlussknoten,
      Rueckwege
      und Recommendation-Freigabe an einer expliziteren Freigabelogik haengen
      und nicht weiter nur indirekt aus
      `Readiness`
      plus spaeterem Antwortpfad abgeleitet werden
    - damit wird die Trennung
      `Readiness-Teilbefund`
      vs.
      `tatsaechlich erlaubter naechster Zug`
      im Code erstmals direkt sichtbar
  - Wirkung:
    - Careena hat jetzt hinter Process-State und `Readiness` eine kleine
      sichtbare Gate-Lesart,
      die Abschlussfrage,
      Rueckkehr in den medizinischen Pfad
      und Recommendation-Freigabe expliziter zusammenbindet
    - die hintere Policy ist dadurch klarer lesbar
      und weniger darauf angewiesen,
      spaet wieder implizite Mischlogik aus
      `recommendation_ready`,
      Transition-State
      und Response-Fallbacks zu erraten
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/state_updates.py`
    - `server/careena_pipeline3/models/turn/__init__.py`
    - `server/careena_pipeline3/models/turn/context.py`
    - `server/careena_pipeline3/application/services/recommendation_state_service.py`
    - `server/careena_pipeline3/application/services/concern_state_service.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/tests/test_dialogue_manager.py`
    - `server/tests/test_block6_response_transition.py`
  - Naechster Punkt:
    - als naechstes Block 3 an die neue Gate-Lage anschliessen
      und die sichtbaren Response-Familien noch enger gegen
      `gate_decision`
      stabilisieren
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 109 Datum: 12-06-26 16:10 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - Block 3 aus `REFACTOR_PLAN_V5.md` als kleinen sichtbaren
      Response-Schnitt begonnen
    - `ResponseManager` so nachgeschaerft,
      dass der `continue`-Pfad nicht mehr pauschal in einen freien
      `llm_continue`-Kanal faellt:
      Rueckweg bleibt statisch,
      enger freier KI-Pfad laeuft nur noch fuer echte medizinische
      Explorations-/Klaerungszuege,
      und ein kleiner expliziter statischer medizinischer
      Acknowledgement-Pfad deckt den restlichen `continue`-Bereich ab
    - `ResponseStrategy` um
      `static_medical_acknowledgement`
      erweitert
      und `ResponseTextBuilder` entsprechend darauf ausgerichtet
    - `ResponseGenerationService` und
      `LLMResponseGenerationService`
      so umgestellt,
      dass die freie Antwortschicht die neue concern-/gate-nahe Lage
      expliziter mitbekommt,
      statt weiter nur auf aeltere Response-/Readiness-Reste zu schauen
    - die Tests um kleine direkte Block-3-Pruefungen erweitert:
      wann `continue` wirklich den freien Pfad bekommt
      und wie der neue statische medizinische Acknowledgement-Pfad aussieht
  - Warum:
    - Block 3 verlangt,
      dass sichtbare Antwortfamilien kleiner,
      ehrlicher
      und enger an der neuen Freigabelogik haengen,
      statt dass ein breiter Restpfad semantisch zu viel kaschiert
    - damit wird der freie KI-Pfad strenger begrenzt
      und die statische vs. freie Antworttrennung klarer
  - Wirkung:
    - Careena hat jetzt hinten eine etwas diszipliniertere Antwortschicht:
      `guide_next_step`,
      Recommendation,
      Rueckweg,
      Follow-up
      und `cannot_assess`
      bleiben klare sichtbare Familien,
      waehrend `continue`
      nicht mehr automatisch derselbe freie Antwortkanal ist
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/response_strategy.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/response_generation_service.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena_pipeline3/application/services/llm_response_generation_service.py`
    - `server/tests/test_dialogue_manager.py`
  - Naechster Punkt:
    - als naechstes Block 4 gegen denselben Gate-Schnitt lesen
      und pruefen,
      welche sichtbaren Antwortreste eigentlich noch von zu breiten oder
      unnoetigen Extraktionsstarts kommen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 110 Datum: 12-06-26 17:20 ===
  - Kategorie:
    - `docs`
  - Bereich:
    - `backend`
  - Aenderung:
    - ein eigenes Architekturpapier
      `BOUNDED_MASTER_PROMPT_RESPONSE_LANE.md`
      angelegt,
      das einen moeglichen bewussten Entstau-Schritt festhaelt:
      kurzfristig wieder intelligentere Gespraechsfuehrung ueber einen
      staerkeren LLM-Antwortcall mit Rueckgriff auf den historischen
      `MASTER_PROMPT`,
      aber als bewusst begrenzte Response-Lane
      statt als unkontrollierte Rueckkehr zum alten Voll-Chat
  - Warum:
    - die aktuelle Runtime wird architektonisch klarer,
      aber der sichtbare Gespraechsfluss bleibt noch zu stumpf;
      dieser Schritt soll helfen,
      die weitere Refactor-Arbeit nicht auf einer zu schwachen
      Antwortschicht aufbauen zu muessen
  - Wirkung:
    - der moegliche Zwischenpfad ist jetzt sauber dokumentiert:
      mehr kurzfristige Gespraechsintelligenz ja,
      aber weiter unter Concern-,
      Gate-,
      Safety-
      und Runtime-Grenzen
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/autodoc/2026-06-12/BOUNDED_MASTER_PROMPT_RESPONSE_LANE.md`
  - Naechster Punkt:
    - bei Bedarf aus diesem Papier einen kleinen praktischen
      Response-Lane-Einbau ableiten
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 111 Datum: 12-06-26 18:56 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die zuvor nur dokumentierte
      `bounded master prompt response lane`
      als ersten praktischen Antwortpfad eingebaut
    - `ResponseManager` so erweitert,
      dass Requirement-Follow-ups
      und der enge medizinische `continue`-Pfad jetzt ueber einen staerkeren
      begrenzten LLM-Antwortkanal laufen koennen,
      waehrend harte Sonderpfade weiter statisch bleiben
    - `ResponseStrategy` um
      `llm_bounded_response`
      erweitert
      und `ResponseGenerationService`/`LLMResponseGenerationService` darauf
      umgestellt
    - den historischen `MASTER_PROMPT` weiter als Basis genutzt,
      aber die freie Antwort durch zusaetzliche Guardrails,
      Antwortfamilien
      und Concern-/Gate-Signale enger begrenzt
    - die Tests um einen direkten Check erweitert,
      dass Requirement-Follow-ups jetzt diesen bounded LLM-Pfad bekommen
  - Warum:
    - die reine Hardcode-Antwortlogik war fuer einen guten Gespraechsverlauf
      zu stumpf;
      gleichzeitig sollte keine unkontrollierte Rueckkehr zum alten
      Voll-Chat entstehen
  - Wirkung:
    - Careena hat jetzt einen staerkeren,
      aber weiter begrenzten LLM-Antwortpfad fuer normale medizinische
      Gespraechsfuehrung,
      ohne Notfall-,
      Recommendation-
      oder andere harte Sonderpfade aufzuweichen
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/response_strategy.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/response_generation_service.py`
    - `server/careena_pipeline3/application/services/llm_response_generation_service.py`
    - `server/tests/test_dialogue_manager.py`
  - Naechster Punkt:
    - den neuen bounded Antwortpfad gegen echte Laufpfade beobachten
      und danach entscheiden,
      wie weit spaeter gezielte Rueckfragengenerierung oder begrenzte
      Antwortarbeit weiter Richtung `Call 2` andocken soll
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 112 Datum: 12-06-26 19:02 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die neue Response-Lane observability-seitig nachgeschaerft:
      `ResponseManager` schreibt die gewaehlte `response_strategy` jetzt
      explizit in die `trace_notes`,
      damit im Server-Log direkt sichtbar wird,
      ob z. B.
      `llm_bounded_response`
      oder ein statischer Pfad gezogen wurde
  - Warum:
    - die bounded LLM-Response-Lane war fachlich schon aktiv,
      aber im Log noch nicht explizit genug erkennbar
  - Wirkung:
    - kuenftige Pipeline-Logs koennen die tatsaechlich gezogene
      Antwortstrategie direkt ausweisen
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/application/managers/response_manager.py`
  - Naechster Punkt:
    - bei Bedarf den frischen Server-Log erneut lesen
      und pruefen,
      ob `response_strategy:llm_bounded_response`
      jetzt real auftaucht
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 113 Datum: 12-06-26 19:45 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - fuer den begonnenen V5-Block-4-Schnitt den aktiven Call-2-Vertrag um
      ein kleines explizites Ergebnisfeld
      `case_extension_status`
      erweitert,
      damit die Extraktion jetzt sichtbar zwischen
      `no_relevant_change`,
      `updates_existing_information`,
      `adds_new_information`
      und
      `mixed_update_and_new`
      unterscheiden kann
    - den Call-2-Prompt auf diese explizite Fall-Erweiterungslesart
      ausgerichtet
      und den Extractor observability-seitig so nachgezogen,
      dass der neue Status im Lauf direkt geloggt wird
    - den Python-Normalizer erweitert,
      damit er diese neue Ergebnislesart eng gegen die vorhandenen
      Vertragsrollen
      `focus_update`
      vs.
      `new_item`
      und gegen den
      `operation_mode`
      validiert bzw. klein nachschaerft,
      statt sie nur implizit aus spaeterem Merge-Verhalten erraten zu lassen
    - die Tests um direkte Block-4-Checks fuer den neuen
      `case_extension_status`
      erweitert
  - Warum:
    - Block 4 soll Call 2 nicht breiter oder "klueger" machen,
      sondern seinen aktuellen Extraktionsvertrag ehrlicher lesbar machen
    - insbesondere sollte der Lauf jetzt expliziter sehen koennen,
      ob eine Nachricht den Fall wirklich erweitert,
      nur bestehende Information aktualisiert
      oder praktisch keinen relevanten medizinischen Zuwachs bringt
  - Wirkung:
    - die Extraktionsstrecke hat jetzt eine kleine zusaetzliche
      Vertragsachse,
      die spaeter vor dem Merge sauberer gelesen werden kann,
      ohne Confirmation oder den grossen Werkzeugkasten vorwegzunehmen
    - der neue Status ist sowohl im strukturierten Ergebnis
      als auch ueber Trace-/Log-Signale sichtbar
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager server.tests.test_block6_response_transition`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/extraction/result.py`
    - `server/careena_pipeline3/models/extraction/__init__.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/careena_pipeline3/llm/case_extraction_extractor.py`
    - `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
    - `server/tests/test_dialogue_manager.py`
  - Naechster Punkt:
    - als naechstes pruefen,
      ob die Merge-Kante dieses neue Ergebnisfeld nur observability-seitig
      lesen
      oder bereits in kleinen Guards gegen unnoetige Fallfortschreibung
      einbeziehen sollte
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 114 Datum: 12-06-26 22:39 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - die Truth-Write-Kante jetzt nicht mehr nur observability-seitig,
      sondern mit einem kleinen expliziten Merge-Hinweis
      `case_extension_status`
      im
      `CaseUpdateBridge`
      verbunden
    - den `CaseMerger` so nachgezogen,
      dass
      `no_relevant_change`
      normale Observation-Writes hart ueberspringt,
      aber Subject-Updates und die bestehende Abschlusslogik unberuehrt laesst
    - die implizite starke Kopplung
      `confirm_observation -> user_confirmed`
      geloest:
      `user_confirmed`
      entsteht jetzt nur noch aus echten
      `confirmation`-Turns,
      nicht mehr aus normalem Wiedererkennen einer bekannten Observation
    - den Python-Normalizer geschaerft,
      damit bei leerem write-relevantem Observation-Payload
      wieder sauber auf
      `no_relevant_change`
      zurueckgefallen wird,
      statt weiter ein kuenstlich starkes Update zu behaupten
    - die Block-4-Tests um direkte Truth-edge-Checks
      fuer Bridge-Hinweis,
      Skip-Write bei
      `no_relevant_change`
      und die neue Confirmation-Semantik erweitert
  - Warum:
    - der neue
      `case_extension_status`
      sollte nicht nur sichtbar sein,
      sondern die erste kleine ehrliche Steuerung direkt vor dem
      Case-Write uebernehmen
    - gleichzeitig sollte normales Re-Match bekannter Information
      nicht denselben starken Status tragen wie eine ausdrueckliche
      Nutzerbestaetigung
  - Wirkung:
    - der Truth-Write-Pfad ist jetzt enger und nachvollziehbarer:
      irrelevant markierte Extraktion schreibt keine normalen Observations
      mehr in den Case
    - bestaetigende Statuswerte im Case werden nicht mehr aus reinem
      Match-Verhalten ueberdehnt
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest server.tests.test_dialogue_manager.Call2Block4ContractTest server.tests.test_dialogue_manager.TruthWriteEdgeTest`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/turn/case_update_bridge.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/domain/case_update_applier.py`
    - `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
    - `server/tests/test_dialogue_manager.py`
  - Naechster Punkt:
    - als naechstes pruefen,
      ob aus dem kleinen Truth-edge-Hinweis noch eine noch engere
      Write-Intention
      (`update` vs. `create`)
      direkt an den Merge-Rand gezogen werden soll,
      ohne den aktuellen Schnitt wieder aufzublaehen
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 115 Datum: 13-06-26 13:11 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - im
      `MedicalCase`
      einen kleinen expliziten medizinischen Themenanker
      `case_topic_label`
      eingefuehrt
      und mit
      `current_topic_label()`
      einen klaren Lesepfad
      `case_topic -> primary_focus`
      angelegt
    - den Call-2-Vertrag um ein optionales
      `case_topic_label`
      erweitert,
      den Prompt darauf ausgerichtet
      und die Python-Normalisierung so geschaerft,
      dass das Feld nur bei realem Observation-Signal erhalten bleibt
    - den Truth-Edge ueber
      `CaseUpdateBridge`
      bis in den
      `CaseMerger`
      durchgezogen,
      sodass der Themenanker kontrolliert und nur einmalig in den Case
      geschrieben wird
    - `ConcernState`
      auf eine klarere Spiegelrolle gezogen:
      `summary`
      wird jetzt aus dem Case-Themenanker gespiegelt
      statt als halb-eigene Themenquelle weiterzulaufen
    - Response-,
      Prompt-,
      Recommendation-
      und Simulations-Zusammenfassungen auf den neuen priorisierten
      Lesepfad umgestellt,
      damit das medizinische Thema nicht mehr implizit aus
      `ConcernState`
      oder nur aus
      `primary_focus`
      gezogen wird
    - innerhalb von
      `server/careena_pipeline3/tests/`
      eine gezielte neue Testsuite fuer den Themenanker angelegt
  - Warum:
    - das medizinische Thema des laufenden Falls sollte als explizite
      Case-Wahrheit sichtbar sein,
      statt weiter verteilt zwischen
      `primary_focus`,
      `ConcernState`
      und spaeterer Antwortlogik zu driften
    - dadurch wird
      `DialogueState`
      als Prozessspur entlastet
      und
      `ConcernState`
      verliert eine unscharfe Halb-Verantwortung
  - Wirkung:
    - der laufende Fall hat jetzt einen kleinen kanonischen Themenanker im
      Truth-Pfad
    - Call 2 kann dieses Thema vorschlagen,
      aber nicht direkt als Wahrheit setzen;
      der Write bleibt kontrolliert im Case-Pfad
    - Concern und Response lesen denselben priorisierten Themenanker,
      wodurch der Bezugspunkt fuer Folgefragen und Bestaetigungen klarer
      wird
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\careena_pipeline3\\tests\\test_case_topic_anchor.py`
      lief erfolgreich durch
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\tests\\test_dialogue_manager.py`
      lief erfolgreich durch
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m unittest C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\tests\\test_block6_response_transition.py`
      lief erfolgreich durch
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/case.py`
    - `server/careena_pipeline3/models/extraction/result.py`
    - `server/careena_pipeline3/models/turn/case_update_bridge.py`
    - `server/careena_pipeline3/application/services/extraction_result_mapper.py`
    - `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`
    - `server/careena_pipeline3/domain/case_update_applier.py`
    - `server/careena_pipeline3/domain/case_merger.py`
    - `server/careena_pipeline3/application/services/concern_state_service.py`
    - `server/careena_pipeline3/application/services/response_text_builder.py`
    - `server/careena_pipeline3/application/services/llm_response_generation_service.py`
    - `server/careena_pipeline3/application/services/recommendation_result_builder.py`
    - `server/careena_pipeline3/llm/prompts/case_extraction.py`
    - `server/careena_pipeline3/simulation_runtime/adapters/careena_pipeline3.py`
    - `server/careena_pipeline3/tests/test_case_topic_anchor.py`
  - Naechster Punkt:
    - als naechstes im realen Lauf pruefen,
      ob der neue Themenanker schon ausreicht,
      um die Response-Kante stabiler auf dem eigentlichen medizinischen Thema
      zu halten,
      oder ob spaeter noch eine getrennte concern-nahe
      Verlaufssemantik gebraucht wird
  - DEV_NOTE:
    - `workbench@freddy`

=== CHANGE NUMBER: 116 Datum: 14-06-26 10:47 ===
  - Kategorie:
    - `refactor`
  - Bereich:
    - `backend`
  - Aenderung:
    - den alten Recommendation-Abschluss-Hook aus
      `DialogueState`
      entfernt und durch einen kleinen expliziten Prozessvertrag
      `pending_choice_prompt`
      mit
      `kind="recommendation_choice"`
      ersetzt
    - Entry-,
      Gate-,
      Concern-,
      LLM-Kontext-
      und Boundary-Pfade auf diesen neuen Choice-Prompt-Vertrag umgezogen
      und die alten Felder
      `pending_dialogue_transition`
      sowie
      `recommendation_ready`
      aus dem aktiven Runtime-Pfad entfernt
    - den kleinen Recommendation-Resolver und seinen LLM-Extractor auf
      Choice-Begriffe umbenannt,
      `ResponsePlan`
      vom alten Transition-Payload bereinigt
      und
      `careena3.py`
      auf einen rein abgeleiteten Kompatibilitaetswert fuer
      `recommendation_ready`
      umgestellt
  - Warum:
    - der spaete Abschlussknoten sollte nicht weiter ueber einen toten
      Legacy-Transition-Hook plus eine zweite Readiness-Wahrheit getragen
      werden
    - `allowed_next_step`
      soll die einzige aktive post-processing-Handlungswahrheit bleiben,
      waehrend offene Systemrueckfragen als eigener kleiner
      Dialogprozessvertrag sichtbar sind
  - Wirkung:
    - `guide_next_step`
      setzt jetzt sichtbar genau einen offenen Choice-Prompt,
      den der naechste Turn explizit aufloesen oder beenden kann
    - aktive Produktpfade lesen und schreiben keine
      `pending_dialogue_transition`-
      oder
      `recommendation_ready`-
      Wahrheit mehr
    - Verifikation:
      `C:\\Users\\WahnWitz\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m compileall C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\careena_pipeline3 C:\\Users\\WahnWitz\\Documents\\IMB\\MEP\\Projekt\\MEP_SS26\\server\\careena3.py`
      lief erfolgreich durch
    - Verifikation:
      zwei kleine Smoke-Checks mit dem gebuendelten Python und lokal
      gestubbten
      `openai`-
      und
      `dotenv`-
      Modulen bestaetigten,
      dass
      `request_recommendation`
      den Choice-Prompt sauber aufloest
      und
      `guide_next_step`
      den neuen
      `pending_choice_prompt`
      korrekt setzt
  - Betroffene Dateien/Bereiche:
    - `server/careena_pipeline3/models/domain/dialogue.py`
    - `server/careena_pipeline3/models/domain/__init__.py`
    - `server/careena_pipeline3/models/workflow/context.py`
    - `server/careena_pipeline3/models/turn/entry_decision.py`
    - `server/careena_pipeline3/models/turn/response_plan.py`
    - `server/careena_pipeline3/models/turn/state_updates.py`
    - `server/careena_pipeline3/application/managers/entry_manager.py`
    - `server/careena_pipeline3/application/managers/dialogue_manager.py`
    - `server/careena_pipeline3/application/managers/response_manager.py`
    - `server/careena_pipeline3/application/services/recommendation_state_service.py`
    - `server/careena_pipeline3/application/services/concern_state_service.py`
    - `server/careena_pipeline3/application/services/recommendation_transition_service.py`
    - `server/careena_pipeline3/application/services/__init__.py`
    - `server/careena_pipeline3/llm/context.py`
    - `server/careena_pipeline3/llm/prompts/intent_gateway.py`
    - `server/careena_pipeline3/llm/prompts/recommendation_transition.py`
    - `server/careena_pipeline3/llm/recommendation_transition_extractor.py`
    - `server/careena_pipeline3/llm/__init__.py`
    - `server/careena_pipeline3/runtime.py`
    - `server/careena3.py`
  - Naechster Punkt:
    - als naechstes pruefen,
      ob der Truth-Write-Rand nach dem beruhigten Abschlussknoten jetzt der
      kleinere und sinnvollere Refactor-Hebel ist
  - DEV_NOTE:
    - `workbench@freddy`
