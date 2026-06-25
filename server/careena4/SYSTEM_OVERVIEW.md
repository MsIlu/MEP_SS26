# Careena4 System Overview

Stand: 2026-06-16

## Zweck

Dieses Dokument beschreibt den aktuellen Ist-Zustand von `server/careena4/`
auf Basis des laufenden Codes. Primaere Wahrheitsquellen sind
`server/careena4.py`, `server/careena4/api.py`, `server/careena4/runtime.py`,
`server/careena4/application/orchestration/turn_engine.py` und die dazugehoerigen
Modelle.

Careena4 soll als begrenztes medizinisches Konversationssystem verstanden
werden. Es ist kein freier Diagnose-Chatbot, keine direkte medizinische
Wahrheit aus Rohtext und keine verdeckte Versorgungsempfehlung aus
Textgefuehl.

## Was Careena4 ist

Careena4 verarbeitet medizinische Nutzernachrichten in einem sichtbaren,
geschichteten Turn-Ablauf:

1. Eine Nutzernachricht trifft an der HTTP-Boundary ein.
2. Der aktuelle Sitzungszustand wird in ein `TurnInput` ueberfuehrt.
3. Der Turn wird auf Safety, Reichweite und offene Fragen gelesen.
4. Medizinische Claims werden nur bei Bedarf extrahiert.
5. Claims werden kontrolliert in einen kanonischen `MedicalCase` geschrieben.
6. Aus Fallzustand und Prozesszustand wird der naechste erlaubte Schritt
   bestimmt.
7. Erst danach wird ein sichtbarer Antworttext formuliert.

Die innere Leitidee ist: Chat vorne, begrenzte Vertragswelt hinten.

## Boundary und Laufzeitvertrag

`server/careena4.py` ist nur der schmale Einstieg und exportiert `app` aus
`server/careena4/api.py`.

`api.py` bildet die HTTP-Boundary und initialisiert ueber `bootstrap.py` und
`runtime.py` den Default-Runtime-Graphen.

### HTTP-Endpunkte

- `GET /`
  - liefert den einfachen Service-Status
- `POST /session`
  - erzeugt eine neue In-Memory-Session
- `POST /warmup`
  - einfacher Readiness-Endpoint ohne Fachlogik
- `POST /chatscreen`
  - fuehrt den normalen Chat-Turn aus
- `GET /case/{session_id}`
  - gibt den aktuell persistierten Sitzungszustand aus
- `POST /simulation/run`
  - fuehrt einen Simulationslauf ueber den separaten Simulation-Adapter aus

### Boundary-Vertrag fuer `/chatscreen`

Der normale Pfad ist bewusst klein:

`ChatRequest -> Session lesen -> TurnInput bauen -> TurnEngine.run_turn() -> Sessionzustand zurueckschreiben -> API-Response bauen`

`ChatRequest` enthaelt nur:

- `message`
- `session_id`

Vor dem Turn werden aus der Session gelesen:

- `messages`
- `case_topic`
- `medical_case`
- `conversation_state`
- `recommendation_state`

Nach dem Turn werden genau diese persistierten Kernobjekte wieder in die
Session zurueckgeschrieben.

### Sichtbare API-Antwort von `/chatscreen`

Die API antwortet mit einer reduzierten Sicht auf das Turn-Ergebnis:

- `response`
  - sichtbarer Antworttext
- `response_mode`
  - aktive Antwortbahn des Turns
- `red_flag`
  - nur ein abgeleitetes HTTP-Signal fuer Emergency-Antworten
- `trace_notes`
  - technische Laufspuren aus dem Turn
- `pending_followup`
  - Sicht auf die aktive Frage, falls sie eine medizinische Rueckfrage oder
    Subject-Klaerung ist
- `recommendation_requested`
  - ob der Nutzer bereits eine Empfehlung angefragt hat
- `recommendation_ready`
  - ob aktuell eine Empfehlung oder der naechste Empfehlungsschritt erlaubt
    ist
- `recommendation_result`
  - strukturierte Ergebnisdaten, falls eine Empfehlung bereits gebaut wurde

Diese Response ist nicht die gesamte Fachwahrheit. Sie ist nur die sichtbare
Boundary-Ausgabe fuer den aktuellen Turn.

## Kanonische Zustaende und ihre Rollen

Zwischen Turns lebt der Zustand in `Careena4SessionStore`. Pro Session werden
vier persistierte Kernobjekte gehalten.

### `CaseTopic`

`CaseTopic` ist die kleine sichtbare Falllesart.

- traegt:
  - initiales Thema
  - laufendes Kurzlabel
  - Falltyp
  - abgeleitete Erweiterungen wie `body_site`, `duration_or_onset`,
    `mechanism`
- ist nicht:
  - die medizinische Detailwahrheit
  - die Recommendation-Freigabe
  - der gesamte Dialogprozess

### `MedicalCase`

`MedicalCase` ist die kanonische medizinische Fallwahrheit.

- traegt:
  - `subject`
  - `observations`
  - `issues`
  - die relationale Zuordnung zum Fall ueber `topic_id`
- ist nicht:
  - der reine LLM-Rohoutput
  - eine freie Antwortgeschichte
  - die naechste Dialogentscheidung

Persistente medizinische Wahrheit entsteht erst nach kontrolliertem
Case-Write, nicht im Extraktionscall selbst.

### `ConversationState`

`ConversationState` ist der Prozesszustand des Gespraechs.

- traegt:
  - `phase`
  - `active_question`
  - `followup_needs`
  - `recommendation_requested`
  - `off_topic_state`
  - `topic_fit_state`
- ist nicht:
  - medizinische Fallwahrheit
  - finale Versorgungsempfehlung

### `RecommendationState`

`RecommendationState` ist die Freigabe- und Readiness-Sicht.

- traegt:
  - ob ein Empfehlungswunsch vorliegt
  - ob noch blocking Follow-ups offen sind
  - ob eine Empfehlung erlaubt ist
  - ob der Closing-Choice gerade aktiv ist
  - optional das gebaute `RecommendationResult`
- ist nicht:
  - der gesamte Dialogprozess
  - ein Ersatz fuer `MedicalCase`

### Turn-Arbeitsobjekte

`TurnInput` und `TurnResult` sind Arbeitsobjekte eines einzelnen Turns.

- `TurnInput` spiegelt den zuletzt persistierten Zustand plus reduzierte
  History-Slices in einen bearbeitbaren Turn-Kontext.
- `TurnResult` traegt das Ergebnis des gerade gelaufenen Turns zurueck zur
  Boundary.

Sie sind Arbeitszustand, nicht die dauerhafte Sitzungswahrheit.

## Echter Turn-Ablauf in der Orchestrierung

Die zentrale Orchestrierung sitzt in `TurnEngine.run_turn()`. Der reale Ablauf
ist:

1. Persistierten Zustand laden
   - `CaseTopic`, `MedicalCase`, `ConversationState` und
     `RecommendationState` werden aus `TurnInput` gelesen.
2. Raw-Safety pruefen
   - `RawRedFlagDetector` liest nur die aktuelle Nutzernachricht.
3. Safety-Klaerungsfrage bei Bedarf setzen
   - `SafetyClarificationBuilder` oeffnet eine strukturierte aktive Frage,
     bevor weitere Fachlogik laeuft.
4. Entry klassifizieren
   - `EntryClassifier` liest die Nachricht als Turn-Signal.
5. Out-of-scope frueh beenden
   - fachfremde Nachrichten enden frueh in einer sichtbaren Boundary-Antwort.
6. Aktive Frage aufloesen
   - `QuestionResolver` oder `SafetyClarificationResolver` lesen Antworten auf
     offene Fragen zuerst.
7. Bei medizinischer Information Claims extrahieren
   - `MedicalExtractor` erzeugt `ExtractionClaims`, wenn der Turn neue
     medizinische Information traegt.
8. Topic sicherstellen und Topic-Fit pruefen
   - `TopicManager` eroeffnet oder liest den Fallrahmen.
   - `CaseFrameRefiner` baut daraus eine verfeinerte Falllesart.
9. Case-Write planen und anwenden
   - `CaseWritePlanner` uebersetzt Claims in einen kleinen Write-Plan.
   - `CaseWriter` schreibt kontrolliert in `MedicalCase`.
10. Qualitaet und Follow-up-Bedarf ableiten
    - `ObservationQualityEvaluator`, `FollowupNeedBuilder` und
      `FollowupSelector` bestimmen, ob noch eine Rueckfrage noetig ist.
11. Readiness und Recommendation-Freigabe bestimmen
    - `ReadinessEvaluator` und `AssessmentReadinessBuilder` lesen, ob eine
      Empfehlung fachlich freigegeben werden darf.
12. Antwortmodus waehlen und Text rendern
    - `TurnDecision` legt die Bahn fest.
    - `ResponseBuilder` formuliert nur die bereits freigegebene Antwortfamilie.

Wichtig ist die Trennung:

- Signale kommen aus Entry, Safety und Extraction.
- persistente Wahrheit sitzt in `MedicalCase`, `CaseTopic`,
  `ConversationState`, `RecommendationState`.
- Policy sitzt im orchestrierten Turn-Ablauf.
- Text ist die spaete Ausgabe dieser Entscheidungen.

## Verantwortungen der Hauptschichten

### `core/`

- stellt LLM-Aufruf und schema-validierte Extraktion bereit
- kennt JSON-Parsing, Pydantic-Validierung und Fehlersignale
- kennt keine medizinische Wahrheit und keine spaete Dialogpolicy

### `application/entry`

- liest eine Nutzernachricht als Turn-Signal
- unterscheidet unter anderem neue Fallmeldung, Update, Antwort auf aktive
  Frage und Out-of-scope

### `application/extraction`

- erzeugt medizinische Claims
- liefert Signale fuer Thema, Subject und Observations
- schreibt noch nichts in den persistierten Fall

### `application/dialogue`

- baut aktive Fragen
- resolved Antworten auf aktive Fragen
- behandelt Safety-Klaerungen getrennt von normalen medizinischen Follow-ups

### `application/topic`

- eroeffnet einen kleinen Fallrahmen
- prueft Topic-Fit
- verfeinert die sichtbare Falllesart ueber `extensions`

### `domain/case_write`

- uebersetzt Claims in kontrollierte Create-, Enrich-, Negate- oder
  Ignore-Schritte
- ist die Kante, an der aus Claims persistente medizinische Wahrheit wird

### `domain/quality` und `domain/readiness`

- lesen die vorhandenen Beobachtungen als Qualitaetssignale
- leiten offenen Follow-up-Bedarf ab
- bestimmen, ob eine Empfehlung schon erlaubt ist oder noch blockiert bleibt

### `application/recommendation`

- baut eine konservative V1-Empfehlung aus dem vorhandenen Fall
- ist bewusst kleiner als eine vollstaendige Triage-Engine

### `application/response`

- rendert nur die bereits entschiedene Antwortbahn
- oeffnet keine eigene verdeckte Fachpolicy

### `infrastructure/`

- haelt den In-Memory-SessionStore
- haelt optional das SQL-basierte Safety-Katalog-Repository

### `simulation_runtime/`

- bildet eine Test- und Simulationshuelle fuer ganze Turn-Folgen
- nutzt denselben TurnEngine-Kern ueber einen Adapter

## LLM-Rolle und Fallbacks

LLM-Outputs sind in Careena4 Signale oder Claims. Sie sind nicht direkt die
kanonische medizinische Wahrheit.

### Aktive Call-Familien

- `entry_assessment`
  - liest die Nachricht als Turn-Signal
- `medical_extraction`
  - erzeugt strukturierte medizinische Claims
- `followup_resolution`
  - resolved Antworten auf aktive Rueckfragen
- `question_rendering`
  - formuliert eine bereits entschiedene Frage natuerlicher
- `recommendation_rendering`
  - formuliert eine bereits gebaute Empfehlung natuerlicher

### Fallbacks

Heuristische oder statische Fallbacks greifen, wenn ein LLM-Pfad nicht
verfuegbar ist oder am Vertrag scheitert:

- `EntryClassifier`
  - heuristische Klassifikation
- `MedicalExtractor`
  - heuristische Claim-Extraktion
- `QuestionResolver`
  - regelbasierte Antwortauflosung fuer aktive Fragen
- `QuestionBuilder`
  - statischer Fragetext statt LLM-Rendering
- `ResponseBuilder`
  - statische Recommendation- oder Standardtexte statt LLM-Rendering

Der Kernvertrag bleibt:

- LLM liefert Signale oder Claims.
- persistente Wahrheit entsteht erst nach `CaseWritePlanner` und
  `CaseWriter`.

## Antwortarten und sichtbares Verhalten

Die sichtbare Antwortbahn wird ueber `response_mode` transportiert.

### `emergency`

- entsteht bei bestaetigtem Notfall
- Wirkung:
  - sofortige Notfallantwort
- Turn-Verhalten:
  - praktisch terminal fuer den laufenden Gespraechsschritt

### `ask_safety_question`

- entsteht bei Safety-Klaerungsbedarf
- Wirkung:
  - strukturierte sicherheitsrelevante Rueckfrage
- Turn-Verhalten:
  - Gespraech bleibt offen, bis die Safety-Klaerung aufgeloest ist

### `ask_followup`

- entsteht bei offenem medizinischem Follow-up-Bedarf
- Wirkung:
  - konkrete Rueckfrage zu fehlender Fallinformation
- Turn-Verhalten:
  - Gespraech bleibt offen

### `request_case_description`

- entsteht, wenn noch kein tragfaehiger Fall vorliegt
- Wirkung:
  - explizite Bitte um Beschreibung des gesundheitlichen Anliegens
- Turn-Verhalten:
  - Gespraech bleibt offen

### `guide_next_step`

- entsteht, wenn fachlich genug Information vorliegt und Careena4 den
  Closing-Choice oeffnet
- Wirkung:
  - sichtbare Frage, ob jetzt eine Empfehlung gewuenscht ist oder noch weitere
    Angaben folgen
- Turn-Verhalten:
  - Gespraech bleibt offen

### `recommend`

- entsteht erst nach erreichter Readiness und expliziter Nutzerbestaetigung
- Wirkung:
  - sichtbare Versorgungsempfehlung
- Turn-Verhalten:
  - dieser Pfad ist fachlich der Abschluss der aktuellen Empfehlungsschiene

### `out_of_scope`

- entsteht bei fachfremden oder topic-fremden Nachrichten
- Wirkung:
  - sichtbare Begrenzung des Systems
- Turn-Verhalten:
  - beendet den laufenden Fachpfad frueh

### Closing-Choice

Careena4 gibt nicht automatisch bei jedem Empfehlungswunsch sofort eine
Empfehlung aus. Der aktuelle Vertrag ist:

1. Erst muessen Fall und blocking Follow-ups in einen ausreichend tragfaehigen
   Zustand gelangen.
2. Dann oeffnet Careena4 explizit den Closing-Choice.
3. Erst nach dieser sichtbaren Nutzerbestaetigung kann `recommend` entstehen.

Damit bleibt die Recommendation-Freigabe sichtbar und nicht implizit in
freiem Text versteckt.

## Aktuelle Grenzen und bewusste Vereinfachungen

Die aktuelle Fassung von Careena4 ist bewusst klein und nicht vollstaendig.

- Session-Persistenz
  - `Careena4SessionStore` lebt nur im Speicher
- Safety
  - arbeitet aktuell primaer ueber Raw-Message-Shortcut plus optionale
    Klaerung
- Recommendation
  - `RecommendationBuilder` ist konservative V1-Regellogik, keine volle
    medizinische Triage-Engine
- Prompt-Rendering
  - ist optional; bei Ausfall greifen statische Texte
- SQL-Safety-Katalog
  - ist optionale Zusatzinfrastruktur, nicht Kernvertrag des Systems

Diese Punkte sind aktueller Stand. Sie sollten nicht rueckwirkend als schon
voll ausgebaute Zielarchitektur gelesen werden.
