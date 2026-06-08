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
