# Careena Pipeline Architecture

Diese Datei beschreibt den aktuellen Ist-Zustand der `careena_pipeline`.

## Einstieg

Der zentrale Einstiegspunkt ist:

- `server/careena_pipeline/pipeline.py`

Die Standardverdrahtung der Services passiert in:

- `server/careena_pipeline/bootstrap.py`

`bootstrap.py` baut:

- den transportnahen `LLMClient`
- die generische `ExtractionEngine`
- die drei LLM-Fachmodule
- die `CareenaDecisionPipeline`
- Session- und Scenario-Services

Der LLM-Zugriff ist austauschbar:

- `build_default_services(llm_mode="env")` verwendet `LITELLM_*` aus `.env` via `server/config.py`
- `build_default_services(llm_mode="local")` verwendet die lokale Ollama-Konfiguration

## Pipeline-Ablauf

`CareenaDecisionPipeline.run(...)` verarbeitet eine Nachricht in vier expliziten Steps:

1. `MessageParsingStep`
2. `StructuredSafetyStep`
3. `ActionPlanningStep`
4. `RecommendationStep`

Die Step-Dateien liegen in:

- `server/careena_pipeline/flow/`

### 1. MessageParsingStep

Datei:

- `server/careena_pipeline/flow/message_parsing.py`

Verantwortung:

- rohes Text-Safety-Screening ueber `SafetyGate.evaluate(raw_text=...)`
- vorhandenen `DialogueState` initialisieren oder fortsetzen
- vorhandene Follow-up-Slots heuristisch direkt fuellen
- sonst LLM-Extraktion ueber `LLMCaseUpdateExtractor`
- `MessageUpdate` in `MedicalCase` und `DialogueState` ueberfuehren

Moegliche fruehe Ausgaenge:

- `emergency`
- `out_of_scope`
- `cannot_assess`

Wichtiger Sonderfall:

- Wenn die LLM-Extraktion fehlschlaegt, aber ein offener Follow-up-Slot existiert, erzwingt der Step einen deterministischen Gate-Pfad statt sofort abzubrechen.

### 2. StructuredSafetyStep

Datei:

- `server/careena_pipeline/flow/safety.py`

Verantwortung:

- case-aware Safety-Pruefung nach erfolgreichem Parsing
- verwendet `SafetyGate.evaluate(raw_text=..., case=...)`

Wenn `red_flag_detected` gesetzt ist, endet die Pipeline mit:

- `response_mode="emergency"`

### 3. ActionPlanningStep

Datei:

- `server/careena_pipeline/flow/action_planning.py`

Verantwortung:

- `AssessmentReadiness` berechnen
- `DialogueState` anhand der Readiness aktualisieren
- den naechsten Prozessschritt festlegen

Entscheidungslogik:

- primaer ueber `LLMNextStepAdvisor`, falls vorhanden
- fallback auf deterministische `RecommendationGate`-Logik
- erzwungen deterministisch bei `force_deterministic_gate=True`

Moegliche Gate-Aktionen:

- `ask_followup`
- `confirm_information`
- `recommend`

### 4. RecommendationStep

Datei:

- `server/careena_pipeline/flow/recommendation.py`

Verantwortung:

- finale Routing-Empfehlung erzeugen, sobald Planning sie freigibt

Strategie:

- mit `LLMRoutingAdvisor`, falls vorhanden
- sonst ueber deterministischen `RecommendationEngine`

## LLM-Architektur

Die Infrastruktur fuer strukturierte Modellaufrufe liegt in:

- `server/careena_pipeline/core/client.py`
- `server/careena_pipeline/core/engine.py`
- `server/careena_pipeline/core/exceptions.py`

### LLMClient

`LLMClient` ist die reine Transport-Schicht:

- OpenAI-kompatibler API-Client
- `base_url`, `api_key`, `model`
- optional JSON-Modus

### ExtractionEngine

`ExtractionEngine` ist die generische strukturierte Extraktionsschicht:

- sendet Prompt + Input an das Modell
- parst JSON
- validiert gegen Pydantic-Schemas
- wirft gezielte Fehler bei leerer Antwort, JSON-Fehlern und Schemafehlern

### Fachmodule unter `llm/`

#### `LLMCaseUpdateExtractor`

Datei:

- `server/careena_pipeline/llm/case_update_extractor.py`

Input:

- aktuelle Nachricht
- optional vorhandener Fall
- optional `DialogueState`
- optional pending follow-up slot
- optional bisherige Conversation-Messages

Output:

- internes `MessageUpdate`

Verwendetes LLM-Schema:

- `server/careena_pipeline/models/llm/case_update_result.py`

Prompt:

- `server/careena_pipeline/llm/prompts/case_update.py`

#### `LLMNextStepAdvisor`

Datei:

- `server/careena_pipeline/llm/next_step_advisor.py`

Input:

- `MedicalCase`
- `DialogueState`
- `MessageUpdate`
- `SafetyResult`
- `AssessmentReadiness`
- letzte User-Nachricht

Output:

- `RecommendationGateDecision`

Fallback:

- deterministische `RecommendationGate`

Verwendetes LLM-Schema:

- `server/careena_pipeline/models/llm/next_step_result.py`

Prompt:

- `server/careena_pipeline/llm/prompts/next_step.py`

#### `LLMRoutingAdvisor`

Datei:

- `server/careena_pipeline/llm/routing_advisor.py`

Input:

- `MedicalCase`
- `SafetyResult`
- `RecommendationGateDecision`

Output:

- `Recommendation`

Fallback:

- deterministischer `RecommendationEngine`

Verwendetes LLM-Schema:

- `server/careena_pipeline/models/llm/routing_result.py`

Prompt:

- `server/careena_pipeline/llm/prompts/routing.py`

## Zustand und Register

### `state/module_registry.py`

Zentrale Arbeitsgrammatik der Pipeline:

- erlaubte `ModuleName`
- `RequirementDef`
- `ModuleDef`
- `RequirementRef`
- Mapping von Observation-Typen auf Module
- Normalisierung und Parsing von Requirement-Referenzen
- Follow-up-Slot-Ableitung

Hier liegt die Definition dafuer, welche Informationen pro Modul benoetigt werden.

### `state/dialogue_state_manager.py`

Verantwortung:

- `DialogueState` initialisieren
- `MessageUpdate`, `AssessmentReadiness` und `RecommendationGateDecision` in State ueberfuehren
- Fokus und offene Requirements mit dem `MedicalCase` synchron halten

### Weitere State-Komponenten

- `state/case_merger.py`: merge von `MessageUpdate` in `MedicalCase`
- `state/session_store.py`: Session-/Case-Ablage
- `state/confirmation_service.py`: Bestaetigungs-Handling

## Deterministische Planung und Routinglogik

### `planning/readiness.py`

Die `AssessmentReadinessEvaluator`-Logik prueft unter anderem:

- gibt es ueberhaupt ein medizinisches Hauptproblem?
- welche Module sind aktiv?
- welche Pflichtfelder fehlen noch?
- liegt eine Topic-/Subject-Mehrdeutigkeit vor?
- ist eine Bestaetigung noetig?

Sie erzeugt:

- `AssessmentReadiness`

### `planning/recommendation_gate.py`

`RecommendationGate` trennt Prozesssteuerung von medizinischer Empfehlung.

Sie entscheidet:

- follow-up noetig
- confirmation noetig
- Empfehlung erlaubt

### `routing/fallback_engine.py`

Deterministische Fallback-Empfehlung, wenn kein LLM-Routing genutzt werden kann oder soll.

Ergaenzende Routing-Helfer:

- `routing/normalizer.py`
- `routing/reason_builder.py`

## Modelle nach Rolle

Die Modelle sind entlang ihrer Rolle getrennt:

- `models/domain/`: persistente Fachzustaende wie `MedicalCase`, `DialogueState`, `CaseObservation`
- `models/workflow/`: Zwischen- und Ergebnisobjekte eines Pipeline-Laufs
- `models/llm/`: reine LLM-I/O-Schemas
- `models/common/`: Basisklasse und Enums/Typen
- `models/system/`: gemeinsame Basisschemata fuer LLM-Ausgaben

## Response-Adapter

Die Ausgabe in Richtung Server/UI liegt in:

- `server/careena_pipeline/response/chat_adapter.py`
- `server/careena_pipeline/response/case_adapter.py`

Diese Schicht formt `CareenaPipelineResult` und `MedicalCase` in die benoetigten Payloads um.

## Observability und Test-Tooling

### Logging

Dateien:

- `server/careena_pipeline/observability/logging.py`
- `server/careena_pipeline/observability/logs/debug_log_pipeline.txt`
- `server/careena_pipeline/observability/logs/debug_log_testrun.txt`

Geloggt werden unter anderem:

- Pipeline-Input
- raw safety
- case update prompt/context
- case snapshot
- readiness
- gate
- recommendation
- finaler Pipeline-Outcome

### Scenario Tooling

Dateien:

- `server/careena_pipeline/tooling/scenario/prompts.py`
- `server/careena_pipeline/tooling/scenario/runner.py`

Damit laesst sich die Pipeline gegen einen synthetischen Patienten testen.

## Wichtigste Dateien fuer fachliche Aenderungen

Wenn sich Verhalten aendern soll, sind das meist die ersten Einstiegspunkte:

- `server/careena_pipeline/pipeline.py`
- `server/careena_pipeline/flow/message_parsing.py`
- `server/careena_pipeline/flow/action_planning.py`
- `server/careena_pipeline/planning/readiness.py`
- `server/careena_pipeline/planning/recommendation_gate.py`
- `server/careena_pipeline/llm/case_update_extractor.py`
- `server/careena_pipeline/llm/next_step_advisor.py`
- `server/careena_pipeline/llm/routing_advisor.py`
- `server/careena_pipeline/state/module_registry.py`
- `server/careena_pipeline/state/dialogue_state_manager.py`
- `server/careena_pipeline/response/chat_adapter.py`
