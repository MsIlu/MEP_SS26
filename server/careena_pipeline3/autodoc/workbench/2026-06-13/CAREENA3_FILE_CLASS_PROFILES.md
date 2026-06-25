# Careena3 File And Class Profiles

Stand: 2026-06-13
Status: Arbeitsdokument / Codebasierte Lesart

## Hinweis

- Dieses Dokument geht vom aktuellen Code aus, nicht von Wunscharchitektur.
- `Refactor-Status` ist ausdruecklich eine Vermutung.
- Skala:
  - `low` = aktuell eher stabil oder randstaendig
  - `medium` = wahrscheinlich betroffen, aber nicht primaerer Umbaukern
  - `high` = sehr wahrscheinlich im Zentrum kommender Refactors

## Einstieg und Runtime

### Datei: `server/careena3.py`

Kurzprofil:
FastAPI-Einstiegspunkt. Nimmt Requests an, verwaltet Sessions, ruft den Turn-Flow an und formt HTTP-Antworten.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ChatRequest`: Einfaches Request-Modell fuer Chatnachrichten. Refactor-Status-Vermutung: `low`.

Funktionen:
- `root`, `create_session`, `warmup`, `chat`, `get_case`, `run_simulation`: HTTP-Endpunkte. Der wichtigste Pfad ist `chat`, weil dort der Runtime-Turn gestartet wird.
- `_chat_response`, `_fallback_response_text`: Uebersetzen interner Turn-Ergebnisse in HTTP-Ausgabe. Diese Hilfsfunktionen koennen spaeter betroffen sein, wenn sichtbare API-Felder oder Response-Modi umgebaut werden.

### Datei: `server/careena_pipeline3/__init__.py`

Kurzprofil:
Paketmarker fuer `careena_pipeline3`.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/bootstrap.py`

Kurzprofil:
Kleine Bau-Schicht fuer Default-Services und Simulations-Runner. Macht die Runtime von aussen instanziierbar.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `PipelineServices`: Dataclass fuer den zusammengebauten Service-Satz. Refactor-Status-Vermutung: `medium`.

Funktionen:
- `build_default_services`: Baut die normale Runtime fuer den Server.
- `build_simulation_runner`: Baut die Simulationsverdrahtung.

### Datei: `server/careena_pipeline3/runtime.py`

Kurzprofil:
Zentrale Verdrahtung der produktiven Runtime. Hier werden LLM-Client, Extractor, Services, Manager und Session-Store zusammengesteckt.

Refactor-Status-Vermutung:
`high`

Klassen:
- `PipelineRuntimeServices`: Dataclass fuer den vollstaendigen Runtime-Baum. Refactor-Status-Vermutung: `medium`.

Funktionen:
- `build_llm_client`: Baut den technischen LLM-Zugriff.
- `build_pipeline_runtime`: Baut die gesamte Laufzeitstruktur. Stark betroffen, wenn Policy-, Response- oder Call-2-Schichten umgeschnitten werden.

## Infrastructure

### Datei: `server/careena_pipeline3/infrastructure/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer Infrastrukturklassen.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/infrastructure/session_store.py`

Kurzprofil:
In-Memory-Session-Speicher fuer Fall, Concern-State, Dialogue-State und Nachrichtenhistorie.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `PipelineSession`: Haltet den laufenden Session-Zustand. Refactor-Status-Vermutung: `medium`.
- `CareenaPipeline3SessionStore`: Verwaltet Sessions. Refactor-Status-Vermutung: `low`.

## Core

### Datei: `server/careena_pipeline3/core/__init__.py`

Kurzprofil:
Paketmarker fuer generische LLM-/Extraction-Infrastruktur.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/core/client.py`

Kurzprofil:
Technischer OpenAI-kompatibler Chat-Completion-Client. Traegt keine Careena-Fachlogik.

Refactor-Status-Vermutung:
`low`

Klassen:
- `LLMClient`: Reiner Transportadapter fuer Modellaufrufe. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/core/engine.py`

Kurzprofil:
Generischer Structured-Extraction-Wrapper ueber dem LLM-Client.

Refactor-Status-Vermutung:
`low`

Klassen:
- `ExtractionEngine`: Fuehrt schemaorientierte Extraktion durch. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/core/exceptions.py`

Kurzprofil:
Gemeinsame Fehlerklassen fuer LLM- und Extraktionsfehler.

Refactor-Status-Vermutung:
`low`

Klassen:
- `ExtractionError`
- `EmptyLLMResponseError`
- `InvalidJSONError`
- `SchemaValidationError`
- `LLMRequestError`

Alle fuenf Klassen sind einfache technische Ausnahmearten. Refactor-Status-Vermutung jeweils: `low`.

## Application Layer

### Datei: `server/careena_pipeline3/application/__init__.py`

Kurzprofil:
Paketmarker fuer die Application-Schicht.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/application/managers/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer die Manager.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/application/managers/dialogue_manager.py`

Kurzprofil:
Zentrale Turn-Orchestrierung. Fuehrt die Schichten in Reihenfolge aus: Entry, Extraction, Case-Truth, Process-State, Next-Step-Policy, Safety, Response, Confirmation.

Refactor-Status-Vermutung:
`high`

Klassen:
- `DialogueManager`: Wichtigste operative Mitte des Systems. Sehr wahrscheinlich weiter betroffen, weil hier die Grenzziehung zwischen Schichten praktisch sichtbar wird. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/application/managers/entry_manager.py`

Kurzprofil:
Uebersetzt Call-1-/Intent-Signale in einen kleineren Entry-Vertrag fuer den Turn. Hier sitzt auch die aktuelle Aufloesung des Recommendation-Abschlussknotens vor der eigentlichen Next-Step-Policy.

Refactor-Status-Vermutung:
`high`

Klassen:
- `EntryManager`: Stark betroffen, weil hier weiterhin Scout-Signale, soziale/out-of-scope-Lesart und Legacy-Transition-Reste aufeinandertreffen. Refactor-Status-Vermutung: `high`.

Funktionen:
- `_dialogue_transition_action_for_gateway`: Hilfsfunktion fuer die Abschlussknoten-Aufloesung. Wahrscheinlich spaeter wieder verschiebbar, wenn die Policy noch sauberer zugeschnitten wird.

### Datei: `server/careena_pipeline3/application/managers/extraction_manager.py`

Kurzprofil:
Startet Call 2 nur wenn noetig und baut aus dem normalisierten Ergebnis die truth-edge-orientierte `ExtractionPayload`.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ExtractionManager`: Eher stabiler als frueher, aber weiter relevant fuer spaetere Call-2-Schnitte. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/managers/case_state_manager.py`

Kurzprofil:
Haltet die kanonische Case-Fortschreibung an einer sichtbaren Stelle und delegiert den eigentlichen Merge in die Domain-Schicht.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `CaseStateManager`: Wahrscheinlich weiterhin wichtig, aber aktuell nicht primaere Restbaustelle. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/managers/response_manager.py`

Kurzprofil:
Spaete Policy-Schicht. Liest den gesetzten Zustand und waehlt sichtbare Reaktionsbahn plus Antwortstrategie.

Refactor-Status-Vermutung:
`high`

Klassen:
- `ResponseManager`: Sehr wahrscheinlich weiter im Fokus, weil hier aus `allowed_next_step` und Sonderfaellen die sichtbare Antwortfamilie abgeleitet wird. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/application/managers/safety_manager.py`

Kurzprofil:
Fuehrt rohe, extraktionsnahe und case-nahe Safety-Checks aus.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `SafetyManager`: Architektonisch vorhanden, fachlich aber noch eher duenn. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/managers/confirmation_manager.py`

Kurzprofil:
Aktuell nur sichtbarer Platzhalter fuer eine spaetere Confirmation-Strecke.

Refactor-Status-Vermutung:
`high`

Klassen:
- `ConfirmationManager`: Wird mit hoher Wahrscheinlichkeit spaeter noch deutlich umgebaut oder wirklich ausgebaut. Refactor-Status-Vermutung: `high`.

## Application Services

### Datei: `server/careena_pipeline3/application/services/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer Serviceklassen.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/application/services/recommendation_state_service.py`

Kurzprofil:
Ist aktuell faktisch die Next-Step-Policy-Schicht. Sie nimmt Readiness, Dialogue-State, Concern-State und Entry-Signale und leitet daraus `allowed_next_step` ab.

Refactor-Status-Vermutung:
`high`

Klassen:
- `RecommendationStateService`: Der Name passt inzwischen schlechter als die Rolle. Sehr wahrscheinlicher Kandidat fuer Umbenennung oder weitere Entzerrung. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/application/services/readiness_evaluator.py`

Kurzprofil:
Konservativer Mindestvoraussetzungs-Pruefer. Er beantwortet nicht den naechsten Zug, sondern nur, ob bestimmte Mindestbedingungen vorliegen.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `AssessmentReadinessEvaluator`: Wahrscheinlich fachlich enger stabil als die Policy-Schicht, aber weiter relevant fuer die Trennung `Teilbefund vs. Handlungsfreigabe`. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/dialogue_state_service.py`

Kurzprofil:
Synchronisiert Prozessspur nach Case-Updates, besonders Follow-up-Aufloesung und Mischfaelle aus beantworteter Rueckfrage plus neuer Information.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `DialogueStateService`: Wahrscheinlich weiter betroffen, aber weniger im Zentrum als Policy/Response. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/concern_state_service.py`

Kurzprofil:
Pflegt die kleine concern-nahe Laufspur ueber den Turn hinweg und spiegelt dort Abschlussphase, Exploration oder Klaerungsphase.

Refactor-Status-Vermutung:
`high`

Klassen:
- `ConcernStateService`: Wahrscheinlich stark betroffen, weil Concern noch bewusst als offene Hilfsschicht gilt. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/application/services/intent_classification_service.py`

Kurzprofil:
Stabilisiert Call 1 gegen technische Fehler und gibt am Ende den `IntentGateway`-Vertrag weiter.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `IntentClassificationService`: Wahrscheinlich eher mittel betroffen, vor allem wenn Call 1 spaeter anders zugeschnitten wird. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/recommendation_transition_service.py`

Kurzprofil:
Loest den aktiven Recommendation-Abschlussknoten in genau zwei semantische Aktionen auf.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `RecommendationTransitionService`: Weiter wichtig, aber durch die neue Policy-Kante etwas klarer eingehegt. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/recommendation_request_service.py`

Kurzprofil:
Liest expliziten Recommendation-Wunsch aus Call 1.

Refactor-Status-Vermutung:
`low`

Klassen:
- `RecommendationRequestService`: Kleine Hilfsschicht mit relativ klarer Aufgabe. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/application/services/recommendation_result_builder.py`

Kurzprofil:
Baut den strukturierten Recommendation-Output aus kanonischem Zustand.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `RecommendationResultBuilder`: Noch eher Platzhalter- oder Zwischenstand, aber klar nachgelagert. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/response_generation_service.py`

Kurzprofil:
Kleine Trennschicht zwischen Response-Policy und eigentlicher Textgenerierung.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ResponseGenerationService`: Wahrscheinlich stabil in der Rolle, aber betroffen wenn sich Strategie- und Textvertraege aendern. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/response_text_builder.py`

Kurzprofil:
Statischer Textbuilder fuer deterministische Antwortbahnen wie Follow-up, Abschlussknoten, Recommendation-Placeholder oder Rueckkehr in den medizinischen Pfad.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ResponseTextBuilder`: Wird wahrscheinlich weiter nachgezogen, wenn sichtbare Antwortfamilien geschaerft werden. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/llm_response_generation_service.py`

Kurzprofil:
Freie, aber begrenzte Antwortformulierungs-Schicht. Sie soll keine Policy entscheiden, sondern nur erlaubte Antwortfamilien sprachlich ausformulieren.

Refactor-Status-Vermutung:
`high`

Klassen:
- `LLMResponseGenerationService`: Hohe Betroffenheit, weil hier Policy-Grenzen und Prompt-Zuschnitt weiter austariert werden muessen. Refactor-Status-Vermutung: `high`.

Funktionen:
- `_build_system_prompt`, `_build_user_prompt`, `_format_conversation_history`, `_allowed_response_family`: Prompt- und Kontextaufbereitung. Wahrscheinlich mitbetroffen, wenn Next-Step-Policy und Antwortfamilien weiter geschliffen werden.

### Datei: `server/careena_pipeline3/application/services/call2_operation_mode_service.py`

Kurzprofil:
Leitet aus Call 1 und Follow-up-Lage den engeren Betriebsmodus fuer Call 2 ab.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `Call2OperationModeService`: Wahrscheinlich spaeter betroffen, wenn der Werkzeugkasten in Call 2 weiter differenziert wird. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/extraction_service.py`

Kurzprofil:
Definiert die schmale Service-Schnittstelle fuer Call-2-Extraktion und liefert mit `NoOpExtractionService` einen harmlosen Fallback.

Refactor-Status-Vermutung:
`low`

Klassen:
- `ExtractionService`: Abstrakte Vertragsschnittstelle. Refactor-Status-Vermutung: `low`.
- `ExtractionResultNormalizer`: Abstrakte Normalizer-Schnittstelle. Refactor-Status-Vermutung: `low`.
- `NoOpExtractionService`: Leerer Fallback ohne inhaltliche Extraktion. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/application/services/resilient_extraction_service.py`

Kurzprofil:
Operative Call-2-Laufschicht mit Primary-Extraktion, Fallback und enger Post-Processing-Stufe.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ResilientExtractionService`: Relativ zentral fuer den Call-2-Pfad, aber aktuell weniger in der Hauptkritik als Policy/Response. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/python_extraction_result_normalizer.py`

Kurzprofil:
Python-seitiger enger Nacharbeiter fuer Call 2. Verhindert, dass ein zweiter breiter LLM-Reparaturcall die Vertragswahrheit wieder verschmiert.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `PythonExtractionResultNormalizer`: Weiter wichtig, falls Call 2 noch feiner oder ehrlicher gemacht wird. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/extraction_result_mapper.py`

Kurzprofil:
Baut die truth-edge-Bridge aus dem aktiven Call-2-Vertrag und haelt noch einen alten Kompatibilitaetspfad fuer `ExtractionResult`.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ExtractionResultMapper`: Noch leicht transitional, weil alter und neuer Vertrag koexistieren. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/application/services/extraction_failure_fallback_builder.py`

Kurzprofil:
Baut den kleinen Fallback-Vertrag, wenn Call 2 technisch oder schema-seitig fehlschlaegt.

Refactor-Status-Vermutung:
`low`

Klassen:
- `ExtractionFailureFallbackBuilder`: Kleine Schutzschicht. Refactor-Status-Vermutung: `low`.

## Domain Layer

### Datei: `server/careena_pipeline3/domain/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer Domain-Bausteine.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/domain/requirement_policy.py`

Kurzprofil:
Bestimmt, welche Pflichtangaben fuer vorhandene Beobachtungen noch fehlen und wie Follow-ups daraus entstehen.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `RequirementPolicy`: Kern fuer Pflichtfelder und Follow-up-Generierung. Wahrscheinlich weiter betroffen, wenn Anliegen-Semantik und Readiness sauberer getrennt werden. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/domain/dialogue_focus_sync.py`

Kurzprofil:
Synchronisiert Fokus-Informationen zwischen Case und Dialogue-Prozessspur.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `DialogueFocusSync`: Hilft beim Fokus-/Cursor-Verhalten. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/domain/observation_identity_resolver.py`

Kurzprofil:
Hilft bei der Frage, ob eine neue Beobachtung einer bestehenden entspricht oder nicht.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ObservationIdentityResolver`: Weiter wichtig fuer Truth-Qualitaet, aber nicht die aktuelle Hauptumbaufront. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/domain/observation_normalizer.py`

Kurzprofil:
Normalisiert Beobachtungswerte fuer Merge- und Vergleichszwecke.

Refactor-Status-Vermutung:
`low`

Klassen:
- `ObservationNormalizer`: Eher technischer Stabilitaetsbaustein. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/domain/case_merge_policy.py`

Kurzprofil:
Entscheidet auf Domain-Ebene, welche bestehende Beobachtung fuer ein Update in Frage kommt und wann etwas als neu gilt.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `CaseMergePolicy`: Weiter relevant fuer medizinische Wahrheitsfortschreibung. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/domain/case_merger.py`

Kurzprofil:
Fuehrt den eigentlichen Delta-Merge in den `MedicalCase` durch.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `CaseMerger`: Zentral fuer Truth-Write, aktuell aber relativ klar eingehegt. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/domain/case_update_applier.py`

Kurzprofil:
Wendet explizite Update-Entscheidungen mutierend auf den `MedicalCase` an.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `CaseUpdateApplier`: Wahrscheinlich eher Feinarbeit als kompletter Richtungsumbau, aber weiter sensibel. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/domain/case_update.py`

Kurzprofil:
Gemeinsame Domain-Datentraeger fuer Match-, Update- und Merge-Ergebnisse.

Refactor-Status-Vermutung:
`low`

Klassen:
- `ObservationMatchResult`: Match-Ergebniscontainer. Refactor-Status-Vermutung: `low`.
- `ObservationUpdateDecision`: Update-Entscheidungscontainer. Refactor-Status-Vermutung: `low`.
- `CaseUpdateOutcome`: Merge-Ausgabecontainer. Refactor-Status-Vermutung: `low`.

## LLM Layer

### Datei: `server/careena_pipeline3/llm/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer LLM-Extractor.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/llm/call_control.py`

Kurzprofil:
Modell- und Call-Konfiguration pro LLM-Unterpfad.

Refactor-Status-Vermutung:
`low`

Klassen:
- `CallModelConfig`: Konfigurationsmodell fuer Modellauswahl. Refactor-Status-Vermutung: `low`.

Funktionen:
- `build_call_model_config`: Baut die aktive Call-Modellkonfiguration.

### Datei: `server/careena_pipeline3/llm/context.py`

Kurzprofil:
Stellt die reduzierten Kontexte fuer Call 1, Call 2 und Recommendation-Transition zusammen.

Refactor-Status-Vermutung:
`medium`

Funktionen:
- `build_intent_gateway_context`, `build_case_extraction_input`, `build_recommendation_transition_input`: Wichtige Kontextbuilder fuer die LLM-Calls.
- Hilfsfunktionen wie `_recent_turns`, `_last_assistant_question`, `_focus_observation_for_call2`: Starke Indikatoren dafuer, was das Modell wirklich sieht.

### Datei: `server/careena_pipeline3/llm/intent_gateway_extractor.py`

Kurzprofil:
LLM-Extractor fuer Call 1. Liefert den `IntentGateway`-Vertrag.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `LLMIntentGatewayExtractor`: Wichtiger Scout-Call, aber aktuell weniger im Zentrum als die nachgelagerte Policy. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/llm/case_extraction_extractor.py`

Kurzprofil:
LLM-Extractor fuer Call 2. Liefert direkt den kleineren Call-2-Vertrag.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `LLMCaseExtractionExtractor`: Weiter wichtig fuer Call-2-Qualitaet. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/llm/recommendation_transition_extractor.py`

Kurzprofil:
Kleiner Support-Call, der freie Antworten am Recommendation-Abschlussknoten auf die zwei erlaubten Aktionen normiert.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `LLMRecommendationTransitionExtractor`: Eingehegter Spezialcall. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/llm/prompts/__init__.py`

Kurzprofil:
Paketmarker fuer LLM-Prompts.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/llm/prompts/intent_gateway.py`

Kurzprofil:
Promptdefinition fuer Call 1 / Intent Gateway.

Refactor-Status-Vermutung:
`medium`

### Datei: `server/careena_pipeline3/llm/prompts/case_extraction.py`

Kurzprofil:
Promptdefinition fuer Call 2 / Case Extraction.

Refactor-Status-Vermutung:
`medium`

Funktionen:
- `build_case_extraction_system_prompt`: Baut den Systemprompt fuer Call 2.

### Datei: `server/careena_pipeline3/llm/prompts/recommendation_transition.py`

Kurzprofil:
Promptdefinition fuer die Zwei-Wege-Aufloesung des Recommendation-Abschlussknotens.

Refactor-Status-Vermutung:
`medium`

## Models Common

### Datei: `server/careena_pipeline3/models/__init__.py`

Kurzprofil:
Paketmarker fuer Modelle.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/models/common/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer gemeinsame Modellbasis.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/models/common/base.py`

Kurzprofil:
Pydantic-Basismodell fuer die Pipeline-Modelle.

Refactor-Status-Vermutung:
`low`

Klassen:
- `PipelineModel`: Gemeinsame Modellbasis. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/models/common/types.py`

Kurzprofil:
Sammlung zentraler Literal-Typen fuer Response-Modi, Message-Rollen, Call-2-Modi, Beobachtungstypen und aehnliche Querschnittsbegriffe.

Refactor-Status-Vermutung:
`high`

Grund:
Wenn die Zielarchitektur weiter begrifflich geschaerft wird, landen viele der sichtbaren Vertragsschnitte genau hier zuerst.

## Models Domain

### Datei: `server/careena_pipeline3/models/domain/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer Domain-Modelle.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/models/domain/case.py`

Kurzprofil:
Traegt den kanonischen medizinischen Fallzustand.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `MedicalCase`: Zentrale medizinische Wahrheitsquelle. Vermutlich stabil im Prinzip, aber weiter betroffen durch Wahrheits- und Fokusfragen. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/domain/case_issue.py`

Kurzprofil:
Modelliert Probleme oder Warnhinweise, die am Case haengen koennen.

Refactor-Status-Vermutung:
`low`

Klassen:
- `CaseIssue`: Einfacher Issue-Datentraeger. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/models/domain/concern.py`

Kurzprofil:
Concern-nahe Hilfsschicht fuer aktuelles Anliegen, Phase und Informationssuffizienz.

Refactor-Status-Vermutung:
`high`

Klassen:
- `ConcernState`: Wichtig, aber bewusst noch nicht final verankert. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/models/domain/dialogue.py`

Kurzprofil:
Traegt Prozesszustand wie offene Follow-ups, pending transition und Recommendation-Wunsch.

Refactor-Status-Vermutung:
`high`

Klassen:
- `StagedFollowupAnswer`: Kleiner Hilfstraeger fuer Folgeantworten. Refactor-Status-Vermutung: `low`.
- `PendingFollowup`: Modell fuer offene Rueckfragen. Refactor-Status-Vermutung: `medium`.
- `PendingDialogueTransition`: Legacy-Modell fuer den Recommendation-Abschlussknoten. Refactor-Status-Vermutung: `high`.
- `DialogueState`: Persistente Prozessspur. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/models/domain/observation.py`

Kurzprofil:
Traegt einzelne medizinische Beobachtungen inklusive Laufzeit- und Requirement-Hilfsmethoden.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `CaseObservation`: Kernmodell fuer medizinische Einzelbeobachtungen. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/domain/observation_data.py`

Kurzprofil:
Typisierte Zusatzdatenmodelle fuer verschiedene Beobachtungsarten.

Refactor-Status-Vermutung:
`low`

Klassen:
- `SymptomObservationData`
- `InjuryObservationData`
- `MeasurementObservationData`
- `MedicationObservationData`
- `DiagnosisObservationData`

Alle fuenf Klassen sind strukturierende Datentraeger. Refactor-Status-Vermutung jeweils: `low`.

### Datei: `server/careena_pipeline3/models/domain/provenance.py`

Kurzprofil:
Traegt Herkunftsinformation zu medizinischen Daten.

Refactor-Status-Vermutung:
`low`

Klassen:
- `Provenance`: Einfacher Herkunftsdatentraeger. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/models/domain/subject.py`

Kurzprofil:
Subjekt-/Betroffenenmodell fuer den Fall.

Refactor-Status-Vermutung:
`low`

Klassen:
- `Subject`: Einfacher Subjekt-Datentraeger. Refactor-Status-Vermutung: `low`.

## Models Extraction

### Datei: `server/careena_pipeline3/models/extraction/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer Extraktionsmodelle.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/models/extraction/result.py`

Kurzprofil:
Modelle fuer Call-2-Ausgabe. Der aktive Vertrag ist `Call2ExtractionResult`; `ExtractionResult` lebt noch als Kompatibilitaets- und Diagnosehuelle weiter.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ExtractionSignal`: Kleines Signalschema fuer Extraktion. Refactor-Status-Vermutung: `low`.
- `ExtractedSubject`: Extrahiertes Subjektmodell. Refactor-Status-Vermutung: `low`.
- `ExtractedObservation`: Extrahierte Beobachtung. Refactor-Status-Vermutung: `medium`.
- `ExtractedCasePayload`: Alter breiter Case-Payload-Traeger. Refactor-Status-Vermutung: `medium`.
- `Call2ExtractionResult`: Aktiver Call-2-Vertrag. Refactor-Status-Vermutung: `medium`.
- `ExtractionResult`: Uebergangs-/Kompatibilitaetsmodell. Refactor-Status-Vermutung: `high`.

## Models Turn

### Datei: `server/careena_pipeline3/models/turn/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer Turn-Vertraege.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/models/turn/input.py`

Kurzprofil:
Turn-Eingangsvertrag fuer die zentrale Orchestrierung.

Refactor-Status-Vermutung:
`low`

Klassen:
- `TurnInput`: Reiner Eingangscontainer. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/models/turn/context.py`

Kurzprofil:
Turn-lokaler Arbeitszustand waehrend der Ausfuehrung. Traegt viele Zwischen- und Ableitungssignale.

Refactor-Status-Vermutung:
`high`

Klassen:
- `TurnContext`: Sehr wahrscheinlicher Refactor-Kandidat, weil hier weiterhin mehrere Schichten, Spiegelwerte und Zwischenzustaende zusammenlaufen. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/models/turn/entry_decision.py`

Kurzprofil:
Kleiner Entry-Vertrag nach Call 1. Traegt Extraktionsbedarf, Rollen, Kontextsignale und noch einige Legacy-Transition-Hilfen.

Refactor-Status-Vermutung:
`high`

Klassen:
- `EntryDecision`: Sehr wahrscheinlich weiter betroffen, weil hier aktive und legacy-nahe Signale noch nebeneinander liegen. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/models/turn/extraction_payload.py`

Kurzprofil:
Orchestrierungsvertrag fuer den Extraction-Ausgang Richtung Truth-Write.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ExtractionPayload`: Schon deutlich kleiner als frueher, aber weiter mitten im Turn-Pfad. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/turn/case_update_bridge.py`

Kurzprofil:
Begrenzter truth-edge-Vertrag zwischen Extraktion und kanonischer Case-Mutation.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `CaseUpdateClaims`: Kanonische Update-Claims. Refactor-Status-Vermutung: `medium`.
- `CaseUpdateMergeHints`: Merge-Hilfssignale. Refactor-Status-Vermutung: `medium`.
- `CaseUpdateBridge`: Zentraler truth-edge-Vertrag. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/turn/state_updates.py`

Kurzprofil:
Vertraege fuer Process-State- und Policy-Aktualisierung innerhalb des Turns.

Refactor-Status-Vermutung:
`high`

Klassen:
- `ProcessStateSignals`: Prozesslokale Signale. Refactor-Status-Vermutung: `medium`.
- `ProcessStateUpdate`: Update-Vertrag fuer Dialogue-/Process-State. Refactor-Status-Vermutung: `medium`.
- `ReadinessStateUpdate`: Update-Vertrag fuer Readiness plus Policy. Refactor-Status-Vermutung: `high`.
- `RecommendationGateDecision`: Aktueller Traeger der Next-Step-Policy plus Beobachtbarkeit. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/models/turn/response_state.py`

Kurzprofil:
Kleiner spaeter Reaktionskern fuer die Policy-Schicht.

Refactor-Status-Vermutung:
`high`

Klassen:
- `ResponseState`: Wahrscheinlich weiter betroffen, weil Recommendation-/Transition-Achsen noch nicht endgueltig geschnitten sind. Refactor-Status-Vermutung: `high`.

### Datei: `server/careena_pipeline3/models/turn/response_strategy.py`

Kurzprofil:
Trennt sichtbare Reaktionsbahn von der konkreten Antwortstrategie.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ResponseStrategy`: Wahrscheinlich stabil in der Grundidee, aber einzelne Strategietypen koennen weiter angepasst werden. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/turn/response_plan.py`

Kurzprofil:
Gesammelter Output der spaeten Response-Policy vor der finalen Anwendung in den Turn.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ResponsePlan`: Wichtiger Sammelvertrag, aber konzeptionell schon recht klar. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/turn/confirmation_decision.py`

Kurzprofil:
Kleiner Confirmation-Ausgangsvertrag.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `ConfirmationDecision`: Noch Platzhalter-nah, aber als Vertrag sinnvoll. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/turn/safety_state.py`

Kurzprofil:
Safety-Ergebnisvertrag fuer rohe, extrahierte oder kanonische Sicht.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `SafetyState`: Wahrscheinlich eher fachlich als strukturell betroffen. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/turn/result.py`

Kurzprofil:
Ausgangsvertrag des gesamten Turns.

Refactor-Status-Vermutung:
`low`

Klassen:
- `TurnResult`: Reiner Ergebniscontainer. Refactor-Status-Vermutung: `low`.

## Models Workflow

### Datei: `server/careena_pipeline3/models/workflow/__init__.py`

Kurzprofil:
Re-Export-Schicht fuer Workflow-/LLM-Vertraege.

Refactor-Status-Vermutung:
`low`

### Datei: `server/careena_pipeline3/models/workflow/context.py`

Kurzprofil:
Hilfsmodelle fuer die LLM-Kontextaufbereitung.

Refactor-Status-Vermutung:
`low`

Klassen:
- `ConversationTurn`
- `CaseSummaryObservation`
- `CaseSummary`
- `DialogueSummary`
- `IntentGatewayContext`

Alle fuenf Klassen sind Kontext-/Transportmodelle fuer LLM-Aufbereitung. Refactor-Status-Vermutung jeweils: `low`.

### Datei: `server/careena_pipeline3/models/workflow/intent_gateway.py`

Kurzprofil:
Aktiver Call-1-Vertrag. Liefert kleine gruppierte Signale fuer den Rest des Systems.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `IntentGateway`: Wichtiges Scout-Modell. Eher evolutionaer als komplett instabil, aber klar relevant fuer spaetere Entry-Schnitte. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/workflow/readiness.py`

Kurzprofil:
Readiness-Teilbefundmodell.

Refactor-Status-Vermutung:
`low`

Klassen:
- `AssessmentReadiness`: Reiner Teilbefundcontainer. Refactor-Status-Vermutung: `low`.

### Datei: `server/careena_pipeline3/models/workflow/recommendation_result.py`

Kurzprofil:
Strukturierter Recommendation-Outputvertrag.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `RecommendationResult`: Noch in einer insgesamt unreifen Recommendation-Strecke eingebettet. Refactor-Status-Vermutung: `medium`.

### Datei: `server/careena_pipeline3/models/workflow/recommendation_transition.py`

Kurzprofil:
Zwei-Wege-Ergebnis fuer den Recommendation-Abschlussknoten.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `RecommendationTransitionResolution`: Kleine, ziemlich saubere Uebergangsform fuer den Abschlussknoten. Refactor-Status-Vermutung: `medium`.

## Tests

### Datei: `server/careena_pipeline3/tests/test_case_frame_contract.py`

Kurzprofil:
Sichert Vertragslogik rund um Case-Frame, targeted follow-ups und Readiness/Follow-up-Konsistenz.

Refactor-Status-Vermutung:
`medium`

Klassen:
- `MedicalCaseFrameContractTest`: Fokussiert auf Case-Frame- und Label-Verhalten. Refactor-Status-Vermutung: `medium`.
- `RequirementAndReadinessContractTest`: Fokussiert auf Readiness-/Follow-up-Vertraege. Refactor-Status-Vermutung: `medium`.

## Was aktuell besonders wahrscheinlich weiter refactored wird

- `application/managers/dialogue_manager.py`
- `application/managers/entry_manager.py`
- `application/managers/response_manager.py`
- `application/services/recommendation_state_service.py`
- `application/services/concern_state_service.py`
- `application/services/llm_response_generation_service.py`
- `models/common/types.py`
- `models/domain/dialogue.py`
- `models/domain/concern.py`
- `models/turn/context.py`
- `models/turn/entry_decision.py`
- `models/turn/state_updates.py`
- `models/turn/response_state.py`

## Was im aktuellen Codebild vergleichsweise stabiler wirkt

- `core/*`
- `infrastructure/session_store.py`
- einfache Datenmodelle unter `models/domain/*` und `models/workflow/*`
- `application/services/recommendation_request_service.py`
- `application/services/extraction_failure_fallback_builder.py`
