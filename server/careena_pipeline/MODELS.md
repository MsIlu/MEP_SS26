# Careena Models

Diese Datei beschreibt die aktuell aktiven Modellgruppen der `careena_pipeline`.

Die wichtigste Trennung ist:

- `domain/` = persistente Fachzustaende
- `workflow/` = Zwischen- und Ergebnisobjekte eines Laufs
- `llm/` = Schemas fuer Modell-I/O
- `common/` = Basisklasse und gemeinsame Typen
- `state/module_registry.py` = Arbeitsgrammatik fuer Module und Requirements

## Domain-Modelle

### `MedicalCase`

Datei:

- `server/careena_pipeline/models/domain/case.py`

Zweck:

- haelt den aktuellen medizinischen Fallzustand

Wichtige Felder:

- `case_id`
- `subject`
- `observations`
- `primary_problem_id`

Wichtige Helfer:

- `active_observations(...)`
- `observations_of_type(...)`
- `complaint_observations()`
- `problem_observations()`
- `active_problem_ids()`
- `primary_observation()`
- `primary_focus_label()`
- `ensure_primary_problem()`

Mentales Modell:

- `MedicalCase` ist die medizinische Wahrheit des aktuellen Falls.

### `CaseObservation`

Datei:

- `server/careena_pipeline/models/domain/observation.py`

Zweck:

- repraesentiert eine einzelne medizinische Beobachtung oder Angabe

Wichtige Felder:

- `id`
- `type`
- `label`
- `display_label`
- `concept`
- `source_span`
- `negated`
- `certainty`
- `temporality`
- `severity`
- `body_site`
- `laterality`
- `course`
- `measurement`
- `subject_ref`
- `details`
- `status`
- `confidence`
- `provenance`

Wichtige Eigenschaften:

- `patient_label`
- `searchable_text`

Hinweis:

- `severity` wird per Validator normalisiert, zum Beispiel von Textwerten wie `leicht` oder `stark`.

### `Subject`

Datei:

- `server/careena_pipeline/models/domain/subject.py`

Zweck:

- beschreibt, auf wen sich der Fall bezieht

Typische Inhalte:

- Relation zur schreibenden Person
- Beschreibung
- Alter
- Geschlecht
- Confidence

### `Provenance`

Datei:

- `server/careena_pipeline/models/domain/provenance.py`

Zweck:

- dokumentiert Herkunft und Confidence einzelner extrahierter Angaben

### `DialogueState`

Datei:

- `server/careena_pipeline/models/domain/dialogue.py`

Zweck:

- haelt den prozessualen Gespraechszustand getrennt vom `MedicalCase`

Wichtige Felder:

- `conversation_id`
- `active_case_id`
- `current_topic_status`
- `last_question_key`
- `active_modules`
- `open_requirements`
- `resolved_requirements`
- `pending_followup`
- `awaiting_confirmation`
- `recommendation_requested`
- `recommended_modules`
- `focus_observation_id`
- `focus_label`

Mentales Modell:

- `DialogueState` beschreibt, woran das System gerade arbeitet und was noch offen ist.

## Workflow-Modelle

### `MessageUpdate`

Datei:

- `server/careena_pipeline/models/workflow/message_update.py`

Zweck:

- internes Ergebnis des Message-Verstehens fuer genau eine Nachricht

Wichtige Felder:

- `raw_text`
- `intent_category`
- `is_medical`
- `extraction_required`
- `intent_confidence`
- `subject`
- `observations_added`
- `negated_observations_added`
- `user_requests_recommendation`
- `possible_new_topic`
- `notes`
- `message_role`
- `active_modules`
- `required_fields`
- `resolved_fields`
- `recommended_modules`

Kompatibilitaets-Properties:

- `subject_update`
- `extracted_requirements`
- `resolved_requirements`

Mentales Modell:

- `MessageUpdate` ist das Delta bzw. die Interpretation der aktuellen Nachricht, nicht der ganze Fall.

### `CaseUpdate`

Datei:

- `server/careena_pipeline/models/workflow/case_update.py`

Zweck:

- strukturiert ein zusammengefasstes Update auf Fallebene

Hinweis:

- Das Modell existiert weiterhin im Workflow-Bereich, aber der aktuelle Hauptpfad arbeitet primaer direkt mit `MessageUpdate`.

### `ConfirmationUpdate`

Datei:

- `server/careena_pipeline/models/workflow/confirmation.py`

Zweck:

- beschreibt Bestaetigungs- oder Korrekturentscheidungen bezogen auf bestehende Angaben

### `CaseUpdateContext`

Datei:

- `server/careena_pipeline/models/workflow/context.py`

Zweck:

- serialisierbares Kontextobjekt fuer den Case-Update-LLM-Call

Wichtige Teilmodelle:

- `ConversationTurn`
- `CaseSummary`
- `CaseSummaryObservation`
- `DialogueSummary`

### `AssessmentReadiness`

Datei:

- `server/careena_pipeline/models/workflow/readiness.py`

Zweck:

- beschreibt, ob der aktuelle Fall fuer eine erste Empfehlung ausreicht

Wichtige Felder:

- `ready`
- `missing_information`
- `next_question`
- `reason_tags`
- `blocking_requirements`
- `confidence_gaps`
- `disambiguation_needed`
- `confirmation_needed`
- `recommended_modules`

Mentales Modell:

- `AssessmentReadiness` ist eine aktuelle Bewertung, kein persistenter Langzeitzustand.

### `RecommendationGateDecision`

Datei:

- `server/careena_pipeline/models/workflow/recommendation_gate.py`

Zweck:

- Prozessentscheidung nach der Readiness-Pruefung

Wichtige Felder:

- `action`
- `question`
- `reasons`
- `missing_information`
- `can_recommend_with_uncertainty`
- `activated_modules`

Moegliche Aktionen:

- `ask_followup`
- `confirm_information`
- `recommend`

### `Recommendation`

Datei:

- `server/careena_pipeline/models/workflow/recommendation.py`

Zweck:

- finale Routing-/Versorgungsempfehlung

Wichtige Felder:

- `care_level`
- `urgency_level`
- `specialty`
- `urgency`
- `confidence`
- `reasoning_tags`
- `reasons`
- `explanation`

### `SafetyResult`

Datei:

- `server/careena_pipeline/models/workflow/safety.py`

Zweck:

- Ergebnis der Safety-Pruefung

Typische Inhalte:

- Red-Flag-Signal
- Gruende bzw. Safety-relevante Einordnung

### `CareenaPipelineResult`

Datei:

- `server/careena_pipeline/models/workflow/result.py`

Zweck:

- aggregiertes Rueckgabeobjekt eines kompletten Pipeline-Laufs

Wichtige Felder:

- `raw_text`
- `safety`
- `case`
- `dialogue_state`
- `message_update`
- `readiness`
- `recommendation_gate`
- `recommendation`
- `response_mode`

Mentales Modell:

- Das ist die Gesamtsicht eines Laufs, nicht selbst ein medizinisches Fachmodell.

## LLM-Schemas

Die LLM-Schemas liegen in:

- `server/careena_pipeline/models/llm/`

Sie sind reine I/O-Vertraege zum Modell und nicht automatisch identisch mit den internen Workflow-Objekten.

### `LLMCaseUpdateResult`

Datei:

- `server/careena_pipeline/models/llm/case_update_result.py`

Wichtige Teilmodelle:

- `LLMCaseUpdateIntent`
- `LLMCaseUpdateSubject`
- `LLMCaseUpdateObservation`

Zweck:

- strukturiertes Ergebnis fuer den Case-Update-/Message-Understanding-Call

Wichtige Felder auf Top-Level:

- `intent`
- `subject`
- `observations_added`
- `negated_observations_added`
- `user_requests_recommendation`
- `possible_new_topic`
- `message_role`
- `active_modules`
- `required_fields`
- `resolved_fields`
- `recommended_modules`
- `notes`

### `LLMNextStepResult`

Datei:

- `server/careena_pipeline/models/llm/next_step_result.py`

Zweck:

- strukturiertes Ergebnis fuer den Next-Step-Decision-Call

Felder:

- `action`
- `question`
- `missing_information`
- `reasons`
- `can_recommend_with_uncertainty`
- `activated_modules`

### `LLMRoutingResult`

Datei:

- `server/careena_pipeline/models/llm/routing_result.py`

Zweck:

- strukturiertes Ergebnis fuer den Routing-Call

Felder:

- `care_level`
- `urgency_level`
- `specialty`
- `urgency`
- `confidence`
- `reasoning_tags`
- `reasons`
- `explanation`

## Gemeinsame Modellbasis

### `PipelineModel`

Datei:

- `server/careena_pipeline/models/common/base.py`

Zweck:

- gemeinsame Pydantic-Basisklasse fuer interne Modelle

### Gemeinsame Typen

Datei:

- `server/careena_pipeline/models/common/types.py`

Hier liegen zentrale Enums/Literals wie:

- `ResponseMode`
- `RecommendationGateAction`
- `PlannerModule`
- `ObservationType`
- `ObservationStatus`
- `MessageRole`
- `DialogueTopicStatus`
- `CareLevel`
- `UrgencyAssessment`
- `Urgency`
- `Specialty`
- `SubjectRelation`
- `ProvenanceSource`

## Requirements und Modulgrammatik

Datei:

- `server/careena_pipeline/state/module_registry.py`

Diese Datei ist kein klassischer Modellordner, aber sie definiert die Arbeitsgrammatik der Pipeline.

Wichtige Typen:

- `ModuleName`
- `RequirementDef`
- `ModuleDef`
- `RequirementRef`

Wichtige Funktionen:

- `normalize_modules(...)`
- `parse_requirement(...)`
- `parse_requirements(...)`
- `requirement_to_string(...)`
- `requirement_strings(...)`
- `followup_slot_for_requirement(...)`
- `infer_active_modules(...)`
- `required_fields_for_modules(...)`

Mentales Modell:

- `MedicalCase` und `DialogueState` halten Zustand
- `module_registry.py` definiert, welche Informationsbausteine pro Modul erwartet werden

## Wichtigste Unterscheidungen

### `MedicalCase` vs `MessageUpdate`

- `MedicalCase` = aktueller gesamter Fallzustand
- `MessageUpdate` = was eine einzelne Nachricht neu beigetragen oder veraendert hat

### `DialogueState` vs `AssessmentReadiness`

- `DialogueState` = persistenter Prozesszustand ueber mehrere Turns
- `AssessmentReadiness` = aktuelle Bewertung, ob genug Informationen fuer eine Empfehlung vorliegen

### `LLMCaseUpdateResult` vs `MessageUpdate`

- `LLMCaseUpdateResult` = rohes, modellnahes Ausgabeformat des LLM
- `MessageUpdate` = adaptiertes internes Workflow-Objekt

### `RecommendationGateDecision` vs `Recommendation`

- `RecommendationGateDecision` = darf die Pipeline schon empfehlen oder muss sie noch fragen?
- `Recommendation` = eigentliche finale Versorgungsempfehlung
