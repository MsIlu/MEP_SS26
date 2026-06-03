# Current Careena Pipeline Overview

Allgemeine Anmerkung:
KI generiert - so circa 85 % sind richtig würd ich sagen

## Ausgangspunkt

Früher war Careena im Wesentlichen ein KI-Chatbot mit einem Masterprompt: Eine Nutzernachricht ging in einen großen Prompt hinein, und das Modell sollte gleichzeitig verstehen, strukturieren, nachfragen, priorisieren und antworten.

Der aktuelle Stand ist deutlich stärker in einzelne technische Schritte aufgeteilt. Die KI ist jetzt nicht mehr ein einziger "Alles-in-einem"-Call, sondern Teil einer orchestrierten Decision Pipeline mit klaren Zwischenobjekten, Zuständen und Fallbacks.

Wichtig: Diese Beschreibung bezieht sich auf den aktuellen Runtime-Code. Die Inhalte unter `automatic_documentation/` werden hier bewusst nicht als Quelle verwendet.

## Was jetzt zusätzlich im System steckt

Der Code bringt heute deutlich mehr mit als einen Chatbot:

- eine mehrstufige Decision Pipeline statt eines einzelnen Antwort-Prompts
- strukturierte LLM-Aufrufe mit Pydantic-Schemas statt freier Textlogik
- Session-State über mehrere Nachrichten hinweg
- ein internes `MedicalCase`-Modell als langlebige Fallrepräsentation
- ein separates `DialogueState`-Modell für Prozess- und Gesprächszustand
- deterministische Safety-Prüfung auf Red Flags [importiert red flag logik]
- Readiness-Logik: Das System entscheidet, ob schon genug Informationen vorliegen [das ist ziemlich kritisch]
- Requirement-/Slot-Logik für gezielte Rückfragen
- Confirmation-Flow zum Bestätigen, Ablehnen oder Korrigieren erkannter Angaben
- Recommendation-Gating: Empfehlung erst dann, wenn der Fall dafür freigegeben ist
- Routing-/Empfehlungslogik als eigener Schritt
- Fallback-Verhalten bei LLM-Ausfällen oder unbrauchbaren Outputs [naja reden wir nicht drüber]
- Observability/Debug-Logging für jeden wichtigen Zwischenschritt
- Test-/Scenario-Tooling mit synthetischem Patienten [aktivierbar im frontend via eingabe: /testrun , /testrun 2 etc, aktuell mit medgemma:4b]

## High-Level-Architektur

Der zentrale Einstieg ist `CareenaDecisionPipeline` in [pipeline.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/pipeline.py).

Ein Durchlauf ist grob in vier Phasen geteilt:

1. Message Parsing
2. Structured Safety
3. Action Planning
4. Recommendation

Die Pipeline produziert am Ende ein `CareenaPipelineResult` mit:

- `case`
- `dialogue_state`
- `message_update`
- `readiness`
- `recommendation_gate`
- `recommendation`
- `response_mode`

Damit ist die Antwort nicht mehr nur "Text vom Modell", sondern das Ergebnis eines nachvollziehbareren internen Entscheidungsprozesses.

## Lauf zur Laufzeit

### 1. Server-Ebene

Der Runtime-Server liegt in [pipe_server_decision.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/pipe_server_decision.py).

Die wichtigsten Endpunkte:

- `POST /session`: erzeugt eine neue Session
- `POST /warmup`: einfacher Health/Warmup-Endpunkt
- `POST /chatscreen`: Haupt-Chat-Endpunkt
- `GET /case/{session_id}`: liefert den aktuellen strukturierten Fall
- `POST /case/confirm`: verarbeitet Bestätigungen/Korrekturen [nicht richtig eingebunden derzeit]
- `POST /scenario/run`: startet einen synthetischen Szenario-Test

Für jede Session werden gespeichert:

- aktueller `MedicalCase`
- aktueller `DialogueState`
- bisherige Chat-Nachrichten

Das ist ein großer Unterschied zum alten Masterprompt-Denken: Der Fall und der Prozesszustand leben explizit im Backend weiter.

### 2. Bootstrap / Dependency-Aufbau

In [bootstrap.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/bootstrap.py) werden die Bausteine verdrahtet.

Es gibt dabei mehrere spezialisierte LLM-Rollen:

- `LLMIntentGatewayExtractor`: Call 1, grobe Nachrichteneinordnung
- `LLMCaseUpdateExtractor`: Call 2, strukturierte Fallaktualisierung
- `LLMNextStepAdvisor`: optionaler LLM-Support für Rückfrage-/Nächster-Schritt-Entscheidungen
- `LLMRoutingAdvisor`: Call 3, strukturierte Versorgungsempfehlung

Zusätzlich gibt es:

- `RecommendationGate` als deterministischen Gatekeeper
- `RecommendationEngine` als deterministischen Routing-Fallback
- `CareenaSessionStore` für Sessions
- `ConfirmationService` für UI-seitige Fallbestätigung
- `SyntheticPatientRunner` für Testdialoge

## Die eigentliche Pipeline

[Da ist noch einiges verwässert, message parsing ist ein fiebertraum, genauso wie einige andere sinnlos lange dateien. bin ich noch am bereinigen aber es zieht sich]

### Phase A: Message Parsing

Der Start liegt in [message_parsing.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/flow/message_parsing.py).

Hier passieren mehrere Dinge:

- bestehender Fall wird vorbereitet
- bestehender Gesprächszustand wird geladen oder erzeugt
- eventuell offener Follow-up-Slot wird berücksichtigt
- rohe Safety-Prüfung auf den aktuellen User-Text wird ausgeführt
- Nachricht wird aufgelöst und in ein `MessageUpdate` übersetzt
- `MessageUpdate` wird auf `MedicalCase` und `DialogueState` angewendet

Das Parsing ist also schon kein reines "Text verstehen" mehr, sondern der Einstieg in den gesamten State-Übergang.

### Phase A1: Intent Gateway

In [intent_gateway_extractor.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/llm/intent_gateway_extractor.py) wird zuerst grob klassifiziert:

- ist die Nachricht medizinisch?
- ist überhaupt eine tiefere Extraktion nötig?
- ist es eher neue Information, Smalltalk, eine Antwort auf eine Rückfrage, eine Korrektur usw.?

Das ist ein vorgeschalteter Guardrail-Call. Er dient dazu, nicht jede Nachricht sofort wie einen neuen vollständigen medizinischen Extraktionsauftrag zu behandeln.

### Phase A2: Slot-Fill-Shortcut

In [message_resolution.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/flow/message_resolution.py) gibt es einen wichtigen Shortcut:

Wenn bereits eine gezielte Rückfrage offen ist und die neue Nachricht wie eine passende Antwort aussieht, versucht das System zuerst ein gezieltes Slot Filling, statt die gesamte Fall-Extraktion neu anzustoßen.

Das bringt:

- effizientere Verarbeitung
- weniger unnötige LLM-Arbeit
- stabilere Follow-up-Konversationen

### Phase A3: Strukturierte Case-Extraktion

Wenn mehr als ein Slot-Shortcut nötig ist, übernimmt [case_update_extractor.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/llm/case_update_extractor.py).

Dieser Schritt baut aus einer Nutzernachricht ein strukturiertes `MessageUpdate`, unter anderem mit:

- Intent-Signalen
- Subject-Informationen
- neu erkannten Beobachtungen
- negierten Beobachtungen
- aktiven Modulen
- erforderlichen Feldern
- bereits aufgelösten Anforderungen
- Hinweisen für nachgelagerte Planung

Das ist einer der größten Fortschritte gegenüber dem alten Setup: Das Modell produziert nicht direkt die finale Chatantwort, sondern ein maschinenlesbares Update des internen Fallmodells.

### Phase A4: Merge in den persistenten Fall

Das `MessageUpdate` wird in [message_transition.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/flow/message_transition.py) auf den Zustand angewendet.

Der eigentliche Merge passiert in [case_merger.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/state/case_merger.py).

Der Merger kann heute:

- neue Beobachtungen anhängen
- bestehende Beobachtungen anhand von ID oder Fokus zusammenführen
- Korrekturen gezielt überschreiben
- Bestätigungen und Ablehnungen als Status markieren
- den Primärfokus des Falls pflegen
- Topic-Shifts berücksichtigen

Damit ist der Fall nicht nur eine lose Chat-Historie, sondern ein eigenständiges, fortschreibbares Datenmodell.

## State statt nur Chatverlauf

### MedicalCase

Der `MedicalCase` ist die inhaltliche Wahrheit des Falls:

- Subject
- Beobachtungen
- Hauptproblem / Fokus
- Problemgruppen
- Status einzelner Beobachtungen

Er ist das zentrale Arbeitsobjekt für Readiness, Safety und Empfehlung.

### DialogueState

Der `DialogueState` ist die prozessuale Wahrheit des Dialogs. In [dialogue_state_manager.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/state/dialogue_state_manager.py) wird unter anderem gepflegt:

- aktueller Fokus
- Topic-Status
- offene Anforderungen
- gelöste Anforderungen
- aktuell offene Rückfrage
- letzte Frage
- ob auf Bestätigung gewartet wird
- welche Module gerade aktiv oder empfohlen sind
- ob die Nutzerin/der Nutzer bereits eine Empfehlung verlangt hat

Das ist konzeptionell neu: Früher hätte der Prompt versuchen müssen, sich das alles implizit "zu merken". Jetzt ist es expliziter Backend-Zustand.

## Requirement- und Follow-up-Logik

In [module_registry.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/state/module_registry.py) ist definiert, welche fachlichen Module es gibt und welche Pflichtinformationen sie typischerweise brauchen.

Beispiele:

- `case.main_complaint`
- `subject.subject_relation`
- `symptom.duration_or_onset`
- `injury.injury_context`
- `measurement.kind`
- `measurement.value`

Diese Requirement-Ebene ermöglicht:

- gezielte Rückfragen statt generischem Nachhaken
- saubere Erkennung, welche Information noch fehlt
- explizite Nachverfolgung gelöster und offener Felder
- modulbezogene Steuerung der nächsten Schritte

Das System fragt also nicht mehr nur "irgendetwas Medizinisches" nach, sondern kann bestimmte Informationslücken technisch repräsentieren.

## Safety ist jetzt ein echter Pipeline-Schritt

In [gate.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/safety/gate.py) wird Safety nicht als beiläufiger Prompt-Hinweis behandelt.

Es gibt zwei Safety-Momente:

- rohe Prüfung auf dem eingehenden User-Text
- strukturierte Prüfung nach der Fallaktualisierung, also auch auf Fallinhalt

Wenn eine Red Flag erkannt wird, stoppt die normale Pipeline und liefert `response_mode = "emergency"`.

Das bringt:

- klare Unterbrechung des normalen Antwortflusses
- nachvollziehbare Notfallbegründung
- weniger Vermischung von Chatantwort und Sicherheitslogik

## Readiness: Darf schon empfohlen werden?

Die Entscheidung, ob Careena schon eine Versorgungsempfehlung geben darf, liegt nicht direkt beim Modell.

In [readiness.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/planning/readiness.py) wird heuristisch bewertet:

- gibt es überhaupt ein medizinisches Problem?
- ist nur eine unspezifische Sorge vorhanden?
- fehlen noch Pflichtinformationen?
- ist eine Subjekt-/Themen-Disambiguierung nötig?
- wartet das System auf eine Bestätigung?

Das Ergebnis ist ein `AssessmentReadiness`.

Diese Zwischenschicht ist wichtig, weil damit "genug Information für Empfehlung" als explizite Regel existiert und nicht nur als Bauchgefühl des Modells.

## Recommendation Gate: Deterministischer Prozesswächter

In [recommendation_gate.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/planning/recommendation_gate.py) wird aus der Readiness einer von drei nächsten Schritten abgeleitet:

- `ask_followup`
- `confirm_information`
- `recommend`

Das Gate erzeugt zusätzlich:

- Gründe für die Entscheidung
- offene Informationslücken
- die nächste Frage
- aktivierte Planungsmodule

Das ist ein zentraler Unterschied zum alten Stil: Die Entscheidung "noch fragen oder schon empfehlen?" ist jetzt ein eigener technischer Mechanismus.

## LLM nur noch innerhalb klarer Grenzen

### Next Step Advisor

In [next_step_advisor.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/llm/next_step_advisor.py) darf das LLM helfen, wenn eine Rückfrage formuliert oder verfeinert werden soll.

Aber wichtig:

- die deterministische Gate-Entscheidung bleibt maßgeblich
- das LLM darf keine schon freigegebene Empfehlung wieder zurückdrehen
- das LLM darf nicht frei über den ganzen Prozess herrschen

Das Modell unterstützt also den Prozess, statt ihn komplett zu kontrollieren.

### Routing Advisor

In [routing_advisor.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/llm/routing_advisor.py) erzeugt ein weiterer strukturierter LLM-Call die eigentliche Empfehlung:

- Versorgungsebene
- Dringlichkeit
- Fachrichtung
- Confidence
- Reasoning Tags
- Erklärung

Wenn dieser Call fehlschlägt, springt die deterministische `RecommendationEngine` ein.

## Deterministische Fallbacks

In [fallback_engine.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/routing/fallback_engine.py) liegt eine einfache regelbasierte Routing-Logik.

Sie ist aktuell noch bewusst schlicht, aber sehr wichtig:

- das System bleibt lauffähig, auch wenn ein LLM-Call scheitert
- Empfehlungen sind nicht ausschließlich vom Erfolg eines einzigen Modellaufrufs abhängig
- die Pipeline bleibt technisch robuster und testbarer

Auch bei Next-Step-Entscheidungen gibt es Fallback auf das deterministische Gate.

## Antwortgenerierung ist jetzt Adapter-Logik

In [chat_adapter.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/response/chat_adapter.py) wird aus dem strukturierten Pipeline-Resultat die eigentliche UI-Antwort gebaut.

Die Antwort hängt vom `response_mode` ab:

- `emergency`
- `confirm_information`
- `ask_followup`
- `recommend`
- `out_of_scope`
- `cannot_assess`

Das ist ebenfalls eine klare Veränderung:

- interne Entscheidungslogik und sichtbarer Chattext sind getrennt
- dieselbe Pipeline könnte später auch andere Response-Formate bedienen
- die UI-Antwort ist aus Zustand und Ergebnis ableitbar

## Confirmation-Flow

Mit [confirmation_service.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/state/confirmation_service.py) gibt es jetzt einen expliziten Bestätigungsmechanismus.

Die UI kann:

- Beobachtungen bestätigen
- Beobachtungen ablehnen
- Beobachtungen korrigieren
- zusätzliche Beobachtungen hinzufügen

Das ist ein echtes Plus gegenüber einem Chatbot, der nur textuell "verstanden" haben will, was gemeint war. Der Benutzer kann direkt am strukturierten Fall arbeiten.

## Observability und Debugbarkeit

In [logging.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/observability/logging.py) werden viele Zwischenschritte geloggt, zum Beispiel:

- Pipeline-Input
- rohe und strukturierte Safety
- Intent-Gateway-Context und Ergebnis
- Case-Update-Context und Ergebnis
- Case-Snapshot nach Merge
- Assessment-Readiness
- Recommendation-Gate
- finaler Pipeline-Outcome

Das bringt einen großen operativen Vorteil:

- man kann echte Fehlverläufe nachvollziehen
- man sieht, ob der Fehler beim Verstehen, beim Merge, beim Gate oder beim Routing lag
- das System ist viel besser debuggbar als ein einzelner Masterprompt

## Scenario-/Testrun-Tooling

Mit [runner.py](/C:/Users/WahnWitz/Documents/IMB/MEP/Projekt/MEP_SS26/server/careena_pipeline/tooling/scenario/runner.py) gibt es ein eingebautes Testwerkzeug mit synthetischem Patienten.

Das System kann damit:

- automatisch Testdialoge gegen die eigene Pipeline fahren
- ein Szenario über mehrere Turns simulieren
- prüfen, wann die Pipeline stoppt
- finalen Case und finalen Response Mode inspizieren

Das ist für Entwicklung und Regressionstests sehr wertvoll, weil das System nicht mehr nur per Hand im Frontend getestet werden muss.

## Was das gegenüber dem alten Masterprompt konkret bedeutet

Verglichen mit einem einfachen KI-Chatbot bringt der aktuelle Stand vor allem diese Fähigkeiten:

- explizite Trennung von Verstehen, State-Update, Safety, Planning und Empfehlung
- strukturierte interne Daten statt reinem Freitext
- persistente Sessions mit fortschreibbarem Fallmodell
- gezielte Rückfragen auf Basis fehlender Anforderungen
- differenzierte Behandlung von Follow-up-Antworten, Korrekturen und Topic-Shifts
- Notfallunterbrechung als eigener Kontrollpfad
- Bestätigungs- und Korrekturfluss für erkannte Angaben
- robuste Fallbacks bei fehlerhaften LLM-Antworten
- bessere Nachvollziehbarkeit und Debugbarkeit
- eingebaute Simulations- und Testrun-Möglichkeiten

Kurz gesagt:

Der aktuelle Code ist nicht mehr bloß ein Chatbot mit medizinischem Prompt, sondern eine zustandsbehaftete, mehrstufige Entscheidungs- und Extraktionspipeline mit klaren Kontrollpunkten.

## Noch wichtige Einordnung

Trotz der deutlichen Weiterentwicklung ist nicht alles schon "fertig" oder maximal ausgebaut:

- einige deterministische Routing-Regeln sind noch relativ einfach
- viel medizinische Qualität hängt weiterhin an guten strukturierten LLM-Outputs
- Sessions liegen aktuell im In-Memory-Store, also nicht persistent über Prozessneustarts
- die Pipeline ist architektonisch schon deutlich erwachsener als der alte Bot, aber fachlich noch ausbaubar

## Fazit

Der größte Sprung ist nicht nur "mehr Code", sondern eine andere Systemidee:

Von:

- ein Modell soll alles auf einmal verstehen und beantworten

Zu:

- mehrere spezialisierte Schritte erzeugen und pflegen einen strukturierten Fall
- der Prozesszustand wird separat geführt
- deterministische Regeln steuern, wann nachgefragt, bestätigt, eskaliert oder empfohlen wird
- LLMs sind eingebettet in einen kontrollierten Orchestrierungsrahmen

Damit ist Careena im aktuellen Stand eher eine medizinische Dialogue-/Decision-Engine als nur ein KI-Chat mit Masterprompt.
