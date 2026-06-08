# Careena3 Refactoring Plan

Stand: 2026-06-08

Bezug:

- `TARGET_MODEL5.md`
- `TARGET_MODEL6.md`
- `CAREENA3_ARCHITECTURE_EXECUTIVE_SUMMARY.md`
- `CAREENA3_ARCHITECTURE_KNOWLEDGE_SYNTHESIS.md`
- `CAREENA3_IST_VS_SOLL_ANALYSE.md`


## Zweck

Dieser Plan soll nicht nur einen einmaligen Umbau beschreiben, sondern als
laufendes Steuerdokument waehrend des Refactorings dienen.

Er verfolgt drei Ziele zugleich:

1. die naechsten grossen Refactor-Bloecke sinnvoll priorisieren
2. kleine lokale Probleme waehrend der Arbeit pragmatisch behandeln, ohne den
   Hauptstrang zu verlieren
3. neue Erkenntnisse, Ideen und groessere Zusatzbaustellen direkt in den
   passenden Block rueckschreiben koennen


## Grundhaltung fuer das Refactoring

Nicht jedes Problem muss sofort geloest werden.

Die Leitfrage waehrend der Arbeit lautet immer zuerst:

- ist das ein kleines lokales Problem
- oder zeigt es ein uebergeordnetes strukturelles Problem?

Arbeitsregel:

- kleines Problem:
  - schneller, lokaler Fix
  - danach sofort zurueck auf den Hauptblock
- groesseres Problem:
  - nicht ad hoc ausfransen
  - im passenden Refactor-Block als neue Addition eintragen
  - mit Zeitstempel, kurzer Beschreibung und geplanter Einordnung

Damit soll verhindert werden:

- dass der Refactor in Nebenbaustellen zerfasert
- dass groessere neue Architekturprobleme unsichtbar unter kleinen Fixes
  verschwinden


## Entscheidungsregel: Klein vs. uebergeordnet

Ein Problem gilt vorlaeufig als `klein`, wenn:

- eine falsche Zuordnung oder ein Alias lokal klar identifizierbar ist
- die Korrektur keinen neuen Vertrag braucht
- die Korrektur innerhalb derselben Schicht bleibt
- die Aenderung keine neue Folgegrammatik fuer andere Manager erzeugt

Typische kleine Probleme:

- falscher Feldname
- fehlerhafte Mapper-Zuordnung
- inkonsistenter Default
- lokaler Text, der dem bereits bestehenden Zustand widerspricht
- fehlende Null-/Leerbehandlung

Ein Problem gilt vorlaeufig als `uebergeordnet`, wenn:

- unklar wird, welcher Vertrag eigentlich gelten soll
- mehrere Schichten denselben Sachverhalt unterschiedlich modellieren
- eine Korrektur neue Steuer-, Merge- oder Zustandssemantik braucht
- das Problem auf eine falsche Verantwortungsverteilung hindeutet
- man versucht, einen Effekt mit einer Spezialregel zu retten, obwohl die
  eigentliche Wahrheitsschicht unsauber ist

Typische uebergeordnete Probleme:

- Observation-Identitaet
- Update-vs-Neuanlage
- Follow-up-/Transition-Semantik
- Anliegen- und Zielstatus ueber mehrere Turns
- Prompt-/Orchestrierungsvertrag mit Skip-Signalen


## Globale Prioritaetslogik

Die Refactor-Reihenfolge folgt nicht "sichtbarstes Symptom zuerst", sondern:

1. semantische Mitte stabilisieren
2. danach Dialog- und Response-Uebergaenge klarziehen
3. danach Signale, Prompt-Komposition und zusaetzliche Steuerintelligenz
   ausbauen
4. Server-/Runtime- und Restentkopplung spaeter nachziehen

Begruendung:

- Die zentrale Wahrheitsbildung im Case-State ist aktuell der wichtigste
  Engpass.
- Readiness, Follow-up, Recommendation und spaetere Prompt-Schaerfung bauen
  alle auf dieser Mitte auf.


## Arbeitsformat pro Block

Jeder Refactor-Block enthaelt:

- Ziel
- Warum jetzt
- Sollzustand
- Kernaufgaben
- betroffene Dateien/Klassen
- kleine Sofortfixes, die innerhalb des Blocks erlaubt sind
- Block-Gates / Definition of Done
- `Additionslog`
- `Ideenbereich`

Regel:

- `Additionslog` ist fuer spaeter neu entdeckte groessere Themen
- `Ideenbereich` ist fuer noch unscharfe, aber relevante Richtungen


## Phase 0: Arbeitsvertrag fuer laufendes Refactoring

## Ziel

Vor dem eigentlichen Umbau eine kleine gemeinsame Arbeitsgrammatik festziehen,
damit der Refactor nicht jedes Mal neu entscheidet, wie mit neuen Problemen
umzugehen ist.

## Warum jetzt

Weil der Wunsch explizit ist:

- kleine Probleme schnell fixen
- groessere Probleme systematisch an passender Stelle sammeln

## Sollzustand

- dieser Refactor-Plan wird als laufendes Arbeitsdokument benutzt
- groessere neue Baustellen landen mit Zeitstempel im passenden Block
- kleine lokale Fixes blockieren nicht den Hauptstrang

## Kernaufgaben

- Arbeits-Regel anwenden
- bei jedem groesseren neuen Problem:
  - passenden Block waehlen
  - Kurzbeschreibung eintragen
  - Zeitstempel setzen
  - spaetere Bearbeitungsidee notieren

## Betroffene Dateien/Klassen

- dieser Plan selbst

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- formale Nachschaerfungen am Plan
- Umbenennung oder Klarstellung von Blocktiteln

## Block-Gate / Done

- der Plan ist als Arbeitsinstrument brauchbar
- jeder Folgeblock hat Platz fuer Additionen und Ideen

## Additionslog

- 2026-06-08 00:00
  - Initiale Fassung angelegt.

## Ideenbereich

- moeglicherweise spaeter einen knappen Statusmarker pro Block einfuehren:
  `open`, `active`, `paused`, `mostly_done`


## Phase 1: Case-Truth-Schicht explizit machen [abgeschlossen]

Status:

- abgeschlossen
- Observation-Normalisierung und Observation-Identitaet als eigene
  Truth-Bausteine sichtbar gemacht
- `CaseMerger`-Mutation in expliziteren Applier-/Issue-Pfad geschnitten;
  Konflikt-/Dialogfolgen und sichtbare Case-Issues modelliert
- `CaseObservation` von aktiver Legacy-Selbstverkabelung entlastet

## Ziel

Den Kern aus `TARGET_MODEL6.md` realisieren:

- zwischen Extraktion und `MedicalCase` liegt eine explizite
  Wahrheits-/Update-Schicht

## Warum jetzt

Weil fast alle spaeteren Probleme daran haengen:

- Requirement-Aktivierung
- Follow-up
- Readiness
- Recommendation
- nachvollziehbare Dialogsteuerung

## Sollzustand

- Observation-Identitaet ist expliziter modelliert
- Update-Semantik ist sichtbarer
- Konflikte und Unsicherheit koennen benannt statt still repariert werden
- der `MedicalCase` ist stabiler und weniger aliasgetrieben

## Kernaufgaben

1. expliziten Zielvertrag fuer Observation-Update aus `case_update.py`,
   `CASE_UPDATE_CONTRACT.md` und `TARGET_MODEL6.md` zur realen Mitte des
   Refactors machen
2. `CaseMergePolicy` staerker auf:
   - match
   - change kind
   - action
   - dialogue consequence
   ausrichten
3. entscheiden, welche zusaetzliche Schicht explizit benoetigt wird:
   - `ObservationNormalizer`
   - `ObservationIdentityResolver`
   - oder aehnliche Zuschnitte
4. `CaseObservation` von Legacy-Harmonisierung und Alias-Reparatur entlasten
5. Konflikte / Unsicherheit nicht sofort "wegmergen", sondern sichtbar machen

## Betroffene Dateien/Klassen

- `server/careena_pipeline3/domain/case_update.py`
- `server/careena_pipeline3/domain/case_merge_policy.py`
- `server/careena_pipeline3/domain/case_merger.py`
- `server/careena_pipeline3/models/domain/observation.py`
- `server/careena_pipeline3/application/managers/case_state_manager.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- lokale falsche Feldzuordnung im Observation-/Merge-Pfad
- klarer Alias-Fix, wenn keine neue Semantik eingefuehrt wird
- lokale Konfliktbehandlung fuer eindeutig fehlerhafte Spezialfaelle

## Nicht innerhalb dieses Blocks still loesen

- neue medizinische Sonderfall-Heuristiken
- dedup-Hacks ohne Identitaetsvertrag
- Follow-up- oder Recommendation-Probleme, die nur Symptome der unsauberen
  Wahrheitsbildung sind

## Block-Gate / Done

- es gibt einen sichtbaren technischen Mittelpunkt fuer Observation-Identitaet
  und Update-Entscheidung
- `CaseObservation` ist einfacher und weniger Reparaturschicht
- `CaseMerger` arbeitet auf klarerer Update-Semantik
- mindestens ein Teil von Konflikt / Unsicherheit ist sichtbar modelliert

## Additionslog

- 2026-06-08 00:00
  - Initialblock aus `TARGET_MODEL6` und Ist-vs-Soll-Analyse priorisiert.
- 2026-06-08 00:29
  - `[bearbeitet]` erster Phase-1-Schnitt umgesetzt:
    `ObservationNormalizer` und `ObservationIdentityResolver` eingefuehrt;
    naechster direkter Folgeschritt ist die weitere Trennung von
    Update-Entscheidung, Case-Mutation und sichtbaren Konflikt-/Dialogfolgen
- 2026-06-08 02:01
  - `[abgeschlossen]` Phase 1 praktisch eingelost:
    sichtbare Truth-Mitte fuer Observation-Identitaet und Update-Entscheidung,
    explizite Konflikt-/Issue-Modellierung und `CaseObservation` ohne aktive
    Legacy-Selbstverkabelung.

## Ideenbereich

- `ObservationIdentityResolver` koennte spaeter als eigener schmaler
  Domain-Dienst wertvoll sein
- Konflikt- und Unsicherheitsstatus eventuell nicht direkt in Observation,
  sondern als kleiner separater View-/State-Aspekt
- spaeter moeglicherweise kleine LLM-Hilfe fuer schwer hardcodierbare
  Update-Zuordnungen, aber erst nach explizitem Basiskontrakt


## Phase 2: Extraction-zu-Case-Uebergang entklemmen [bearbeitet]

## Ziel

Die groessten Uebergangsprothesen zwischen Call 2 und Case-Truth abbauen.

## Warum jetzt

Selbst eine bessere Merge-Semantik bleibt fragil, wenn der Input weiterhin
verlustreich oder semantisch driftend geliefert wird.

## Sollzustand

- `ExtractionResult` bleibt sauberer als direkte Wahrheit
- der Uebergang in die Truth-Schicht ist expliziter
- weniger generisches `details`-/`attributes`-Kippen
- `ResilientExtractionService` traegt nicht mehr alle Reparaturen zugleich

## Kernaufgaben

1. `ExtractionResultMapper` kritisch zurueckbauen oder durch schmalere
   Uebergangskomponenten ersetzen
2. Semantik von:
   - Belegsignal
   - Arbeitsmarke
   - Steuerhinweis
   in `models/extraction/result.py` klarer trennen
3. `ResilientExtractionService` in kleinere Verantwortungen schneiden:
   - Fehlergrenze
   - Ergebnisnormalisierung
   - Follow-up-Update-Anpassung
   - Subject-Gating
4. pruefen, welche Teile des aktuellen `MessageDelta` noch gebraucht werden
   und welche nur Migrationslast sind

## Betroffene Dateien/Klassen

- `server/careena_pipeline3/application/services/resilient_extraction_service.py`
- `server/careena_pipeline3/application/services/extraction_result_mapper.py`
- `server/careena_pipeline3/models/extraction/result.py`
- `server/careena_pipeline3/models/turn/message_delta.py`
- `server/careena_pipeline3/application/managers/extraction_manager.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- lokale Attribut-/Details-Zuordnungsfehler
- unnutzes Trace-/Signal-Rauschen
- klar tote Delta-Reste, wenn ihr Entfernen keine neue Vertragsfrage oeffnet

## Nicht innerhalb dieses Blocks still loesen

- neue Domain-Aliase nur zur Schadensbegrenzung
- Merge-Spezialregeln, um Mapper-Schwund zu uebertuenchen

## Block-Gate / Done

- der Uebergang Extraction -> Truth ist leichter lesbar
- `ResilientExtractionService` ist nicht mehr Sammelbehaelter fuer jede
  Korrektur
- der Delta-/Mapper-Pfad ist semantisch klarer oder sichtbar als Restvertrag
  markiert

## Additionslog

- 2026-06-08 00:00
  - Initialblock aus Ist-Zustand rund um Mapper und ResilientExtractionService angelegt.
- 2026-06-08
  - `[bearbeitet]` erster Phase-2-Schnitt im `ExtractionResultMapper`:
    typbezogene Surface-/Detail-/Measurement-Vertraege expliziter gemacht und
    generisches Attribut-Kippen fuer unbekannte Keys deutlich reduziert.
- 2026-06-08
  - Zusatzbefund:
    ein Teil der heutigen Normalisierungs- und Fehlerbehebungslast scheint
    nicht aus Randfaellen zu kommen, sondern aus einem zu grossen bzw. zu
    unscharfen Call-2-Outputvertrag; Phase 2 deshalb nicht nur als
    Mapper-/Service-Aufraeumen lesen, sondern zuerst auch als Verkleinerung und
    Schaerfung des Extraction-Vertrags.
- 2026-06-08
  - Zusatzrichtung:
    der aktuelle Kontextbuilder selbst ist als Phase-2-Baustelle verdaechtig;
    Zielbild eher viele kleine, einfachere Extraktionsobjekte mit klarer
    Sortierung und enger objektweiser Normalisierung statt grosse
    Sammelstrukturen mit breitem Kontextpaket.
- 2026-06-08
  - Zusatzrichtung:
    Normalisierung soll moeglichst auf kleinen Objekten mit konkreten
    Guardrails stattfinden; Konfliktentscheidung zwischen zwei konkurrierenden
    Objekten kann ein geeigneter enger LLM-Hilfsschritt sein, wenn keine klare
    harte Indikation vorliegt.
- 2026-06-08
  - Zusatzrichtung:
    Call 2 soll nicht das Case-Objekt oder eine breite Fallreprasentation
    zusammenbauen, sondern den Case-Truth-Layer mit kleinen medizinischen
    Eintraegen befuellen; dafuer braucht er eher knappen Follow-up-/Dialog-
    Kontext und relevante bestehende kleine Observations als breite
    `case_summary`-/`dialogue_summary`-Pakete.
- 2026-06-08 01:19
  - Log-Befund:
    nichtnumerische `severity`-Werte wie `severe` gehen im aktuellen
    Extraction->Mapper-Uebergang verloren; als Phase-2-Thema sauber ueber den
    Call-2-/Normalisierungsvertrag behandeln, nicht ueber neue Python-
    Sonderlogik im Mapper retten.

## Ideenbereich

- ggf. `MessageDelta` mittelfristig aufspalten statt weiter wachsen lassen
- `ExtractionResult` koennte spaeter explizite operative Arbeitsmarken tragen,
  wenn deren Semantik sauber getrennt ist


## Phase 3: Requirement-, Follow-up- und Readiness-Steuerung an Case-Truth binden

## Ziel

Requirement- und Follow-up-Steuerung staerker aus dem kanonischen Zustand
ableiten und von bruechigen Mischsignalen loesen.

## Warum jetzt

Sobald die Case-Mitte sauberer wird, muss die naechste sichtbare Wirkung in
Requirements, Follow-up und Readiness ankommen.

## Sollzustand

- `active_modules` haengen nicht mehr uebermaessig an Call-1-/Mapper-Resten
- Follow-up ergibt sich sichtbar aus Fallwahrheit plus Fokus
- Readiness wird weniger Kompensation und mehr ehrliche Zustandsauswertung

## Kernaufgaben

1. `active_modules`-Herkunft neu bewerten:
   - was kommt noch aus Entry
   - was muss aus Case-Truth nachgezogen werden
2. `RequirementPolicy` staerker an kanonischen Observationen ausrichten
3. `AssessmentReadinessEvaluator` darauf neu absichern
4. Follow-up-Priorisierung pruefen:
   - nur erstes offenes Requirement
   - Fokusbindung
   - spaetere Konflikt-/Uncertainty-Folgen

## Betroffene Dateien/Klassen

- `server/careena_pipeline3/domain/requirement_policy.py`
- `server/careena_pipeline3/application/services/dialogue_state_service.py`
- `server/careena_pipeline3/application/services/readiness_evaluator.py`
- `server/careena_pipeline3/application/services/recommendation_state_service.py`
- `server/careena_pipeline3/application/managers/extraction_manager.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- lokale Modulaktivierungsfehler
- klar falsche Requirement-Aliaszuordnung
- kleine Follow-up-Order-Korrekturen ohne neue Dialoggrammatik

## Nicht innerhalb dieses Blocks still loesen

- Recommendation-Textprobleme als Ersatz fuer schwache Readiness
- neue Slot-Fill-Sonderfaelle

## Block-Gate / Done

- Requirement-/Follow-up-Pfad wirkt weniger signalgetrieben und mehr
  zustandsgetrieben
- Readiness erklaert sich staerker aus der Case-Wahrheit
- ein lokaler Bug in der Modulaktivierung zieht nicht mehr die ganze
  Follow-up-Steuerung schief

## Additionslog

- 2026-06-08 00:00
  - Initialblock fuer Requirement-/Readiness-Neubindung angelegt.

## Ideenbereich

- spaeter moeglicherweise `RecommendationReadiness` als expliziteres Modell
  statt nur Ergebnisobjekt aus Evaluator
- Follow-up koennte spaeter auch Konflikt-/Uncertainty-Folgen sichtbarer
  konsumieren


## Phase 4: Dialogue-Transition und Response-Policy sauber modellieren

## Ziel

Den Bereich zwischen "genug Informationen liegen vor" und "was antwortet das
System jetzt sinnvoll?" vertraglich klarziehen.

## Warum jetzt

Aktuell ist `guide_next_step` ein gutes Beispiel fuer eine sinnvolle Idee ohne
genug Zustand darunter.

## Sollzustand

- `guide_next_step` oder Nachfolger ist nicht nur Text, sondern kleiner
  sichtbarer Uebergangsvertrag
- Response-Policy kann ausdruecklicher mit Zielstatus, Follow-up-Ende und
  Recommendation-Freigabe umgehen
- Dialogantwort behauptet nicht mehr mehr als der Zustand hergibt

## Kernaufgaben

1. explizit entscheiden, was dieser Zwischenzustand ist:
   - Transition-State
   - Zielklaerungszustand
   - Recommendation-Vorfreigabe
2. `ResponseManager` darauf neu ausrichten
3. `ResponseTextBuilder` nur noch auf diesen Vertrag bauen lassen
4. klarmachen, wann ein Nutzerziel als:
   - noch offen
   - beantwortbar
   - erreicht
   gilt

## Betroffene Dateien/Klassen

- `server/careena_pipeline3/application/managers/response_manager.py`
- `server/careena_pipeline3/application/services/response_text_builder.py`
- `server/careena_pipeline3/application/services/recommendation_state_service.py`
- `server/careena_pipeline3/models/domain/dialogue.py`
- `server/careena_pipeline3/models/turn/context.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- Texte, die dem schon vorhandenen Zustand direkt widersprechen
- lokale falsche Branch-Reihenfolge in Response-Policy

## Nicht innerhalb dieses Blocks still loesen

- neue Textbausteine als Ersatz fuer fehlende Zustandssemantik
- Recommendation-Sonderpfade ohne klares Gate

## Block-Gate / Done

- Zwischenpfade wie `guide_next_step` sind zustandsseitig begruendet
- Response-Policy und Text sind konsistent
- Zielerreichung / Dialogfortschritt ist mindestens minimal modelliert

## Additionslog

- 2026-06-08 00:00
  - Initialblock fuer `guide_next_step` und Transition-Vertrag angelegt.
- 2026-06-08 01:10
  - Log-Befund:
    `guide_next_step` wird im aktuellen Lauf vor sauberer Zustandsfreigabe zu
    frueh aktiv und springt nach erledigtem Subject-Follow-up erneut an; das
    ist als Transition-/Response-Vertragsproblem in Phase 4 zu behandeln, nicht
    als lokaler Textfix.

## Ideenbereich

- moeglicher kleiner Zustand:
  `dialogue_goal_status`
- moegliche Werte spaeter:
  `collecting`, `ready_for_choice`, `ready_for_recommendation`,
  `goal_reached`, `blocked_by_conflict`


## Phase 5: Anliegen, Arbeitsmarken und interne Beobachtungen als erlaubte Steuerungsebene

## Ziel

Die bereits implizit vorhandenen `trace_notes`-, `signals`- und
Zwischenbeobachtungs-Ideen in eine kontrollierte, sichtbare Steuerungsebene
ueberfuehren.

## Warum jetzt

Diese Richtung ist wertvoll, sollte aber erst auf einem klareren
Truth-/Response-Unterbau aufgebaut werden.

## Sollzustand

- einzelne Schritte koennen kleine interne Beobachtungen hinterlassen
- diese Marken sind nicht nur Debug-Rauschen, sondern auswertbare Arbeitsmarken
- der Dialogzustand kann besser tragen:
  - welches Anliegen verfolgt der Nutzer gerade
  - was glaubt das System gerade zu bearbeiten
  - ob das Ziel erreicht ist

## Kernaufgaben

1. minimale Semantik fuer Arbeitsmarken definieren:
   - Evidenz
   - operative Beobachtung
   - Steuerhinweis
2. Turn-/Dialogue-Kontext um kleine erlaubte Ziel- und Statussignale erweitern
3. entscheiden, welche Marken:
   - nur turn-lokal
   - oder dialogpersistierend
   sein sollen
4. pruefen, wie diese Marken fuer:
   - Skip-Entscheidungen
   - Transition-Entscheidungen
   - Konflikt-/Klaerungszustand
   genutzt werden koennen

## Betroffene Dateien/Klassen

- `server/careena_pipeline3/models/turn/context.py`
- `server/careena_pipeline3/models/domain/dialogue.py`
- `server/careena_pipeline3/models/extraction/result.py`
- `server/careena_pipeline3/models/workflow/intent_gateway.py`
- `server/careena_pipeline3/application/managers/dialogue_manager.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- klar totes oder irrefuehrendes Trace-Signal
- lokale Vereinheitlichung von Namenskonventionen bei Notes/Signals

## Nicht innerhalb dieses Blocks still loesen

- ausufernde neue Flaglisten
- freie verdeckte Zweitlogik ueber Arbeitsmarken

## Block-Gate / Done

- es gibt eine kleine erlaubte Semantik fuer interne Beobachtungen
- Anliegen-/Zielstatus ist mindestens rudimentaer modelliert
- Arbeitsmarken helfen der Orchestrierung sichtbar, nicht heimlich

## Additionslog

- 2026-06-08 00:00
  - Initialblock aus Chat-Ideen zu Notizen, Kontext-Ping-Pong und Zielstatus angelegt.

## Ideenbereich

- moegliche Markentypen:
  `goal_signal`, `step_observation`, `followup_scope_hint`,
  `conflict_hint`, `skip_hint`
- strenge Regel:
  keine medizinische Endentscheidung in solchen Marken


## Phase 6: Prompt-Komposition mit Fragenbloecken und expliziten Skip-Signalen

## Ziel

Call-1-/Call-2- und spaeter moeglicherweise Call-3-Prompts von
statischem Regeltext in strukturiertere Frage-/Aufgabenbloecke ueberfuehren.

## Warum jetzt

Diese Idee ist stark, sollte aber erst eingefuehrt werden, wenn:

- Truth-Schicht
- Requirement-/Readiness-Basis
- Transition-Vertrag
- Arbeitsmarken-Semantik

nicht mehr auf Sand gebaut sind.

## Sollzustand

- Prompt-Bloecke beantworten klar definierte operative Fragen
- Bloecke koennen nachfolgende Bloecke explizit deaktivieren
- Skip-Signale sind sichtbare Ausgaenge statt impliziter Prompt-Effekt

## Kernaufgaben

1. pro Call-2-Hauptmodus grobe Blockstruktur entwerfen
2. Feldfragen explizit machen:
   - woraus darf dieses Feld entstehen
   - wann bleibt es leer
   - wann ist `unknown` korrekt
3. kleine Skip-Signale definieren:
   - prompt-intern
   - manager-relevant
4. entscheiden, welche Skip-Signale nur Promptstruktur bleiben und welche in
   den Turn-Vertrag gehoeren

## Betroffene Dateien/Klassen

- `server/careena_pipeline3/llm/prompts/case_extraction.py`
- `server/careena_pipeline3/llm/prompts/intent_gateway.py`
- `server/careena_pipeline3/llm/context.py`
- `server/careena_pipeline3/models/extraction/result.py`
- `server/careena_pipeline3/models/workflow/intent_gateway.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- klar unscharfe Feldfrage im Prompt
- Reihenfolge oder Formulierung eines Blocks, wenn der Vertrag schon steht

## Nicht innerhalb dieses Blocks still loesen

- massive neue Spezialpromptregeln ohne kleinen Vertrag
- Skip-Flag-Flut

## Block-Gate / Done

- mindestens ein Call-2-Pfad ist sichtbar block- und fragegetrieben
- Skip-Signale sind klein, generisch und auswertbar
- der Prompt ist besser steuerbar, ohne in Prompt-Buerokratie zu kippen

## Additionslog

- 2026-06-08 00:00
  - Initialblock aus Chat-Idee zu Fragebloecken und Skip-Signalen angelegt.

## Ideenbereich

- vorlaeufiger Leitname:
  `question-driven prompt composition with explicit skip signals`
- moegliche erste Signale:
  `followup_answer_only`,
  `additional_medical_information_present`,
  `skip_new_observation_block`,
  `response_can_be_resolved_from_state`


## Phase 7: Recommendation-/Response-Schicht gegen Target Model 6 ausbauen

## Ziel

Recommendation als echten freigegebenen Pfad ausbauen, nicht nur als
Placeholder oder Textversprechen.

## Warum jetzt

Erst wenn Wahrheitsbildung, Readiness und Transition stabiler sind, lohnt sich
die Empfehlungsschicht wirklich.

## Sollzustand

- `RecommendationReadiness` ist expliziter
- `ResponsePolicyManager`-Denken aus `TARGET_MODEL6` ist realer
- Call 3 bleibt Inhalts- und nicht Pfadentscheider

## Kernaufgaben

1. Recommendation-Gate expliziter machen
2. `recommendation_result`-Pfad an klare Freigabe koppeln
3. Call-3-Inputvertrag definieren
4. `ResponseManager` staerker Richtung `ResponsePolicyManager` schneiden

## Betroffene Dateien/Klassen

- `server/careena_pipeline3/application/managers/response_manager.py`
- `server/careena_pipeline3/application/services/recommendation_state_service.py`
- `server/careena_pipeline3/application/services/recommendation_result_builder.py`
- `server/careena_pipeline3/models/workflow/recommendation_result.py`
- `server/careena_pipeline3/llm/call_control.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- lokale Inkonsistenz Recommendation-Flag vs Recommendation-Output
- klarer Placeholder-Widerspruch

## Nicht innerhalb dieses Blocks still loesen

- medizinische Routing-/Versorgungsheuristik ohne explizite Freigabe

## Block-Gate / Done

- Recommendation ist klarer als gestufter Pfad modelliert
- Call 3 ist Inhaltsgenerator, nicht heimlicher Gesamtentscheider
- Response-Policy bleibt getrennt vom finalen Text

## Additionslog

- 2026-06-08 00:00
  - Initialblock fuer Recommendation-Ausbau aus `TARGET_MODEL6` angelegt.

## Ideenbereich

- eventuell spaeter explizite Trennung:
  `ResponsePolicyManager` und `FinalResponseComposer`


## Phase 8: Server-, Runtime- und Simulationsentkopplung

## Ziel

Die aktuell noetige, aber zu volle Integrationsoberflaeche spaeter entlasten.

## Warum jetzt

Bewusst spaet, weil die eigentliche Architekturqualitaet nicht hier entschieden
wird.

## Sollzustand

- `careena3.py` ist weniger Testharness
- Simulation bleibt wertvoller Gegenpol
- Runtime-Wiring ist klarer von Produktpfad getrennt

## Kernaufgaben

1. Produktpfad und Test-/Simulationseinstieg sauberer trennen
2. HTTP-Entry weiter auf stabile Application-Schnittstellen reduzieren
3. prüfen, ob `careena3.py` spaeter nur noch duenne Integration sein kann

## Betroffene Dateien/Klassen

- `server/careena3.py`
- `server/careena_pipeline3/bootstrap.py`
- `server/careena_pipeline3/runtime.py`
- `server/careena_pipeline3/simulation_runtime/*`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- lokale Serialisierungs- oder Endpunktunsauberkeit

## Nicht innerhalb dieses Blocks still loesen

- fachliche Architekturprobleme durch Endpunktumbau kaschieren

## Block-Gate / Done

- Server ist duennere Integrationsschicht
- Simulation bleibt erhalten, aber sauberer entkoppelt

## Additionslog

- 2026-06-08 00:00
  - Initialblock fuer spaetere Entrypoint-Entkopplung angelegt.

## Ideenbereich

- spaeter eventuell separater Dev-/Testserver fuer Simulationspfade


## Empfohlene konkrete Reihenfolge

1. Phase 1: Case-Truth-Schicht explizit machen
2. Phase 2: Extraction-zu-Case-Uebergang entklemmen
3. Phase 3: Requirement-, Follow-up- und Readiness-Steuerung an Case-Truth binden
4. Phase 4: Dialogue-Transition und Response-Policy sauber modellieren
5. Phase 5: Anliegen, Arbeitsmarken und interne Beobachtungen als erlaubte Steuerungsebene
6. Phase 6: Prompt-Komposition mit Fragenbloecken und expliziten Skip-Signalen
7. Phase 7: Recommendation-/Response-Schicht gegen Target Model 6 ausbauen
8. Phase 8: Server-, Runtime- und Simulationsentkopplung


## Was waehrend des Refactors bewusst vermieden werden soll

- neue medizinische Sonderfall-Heuristik als Reparaturersatz
- neue grosse Sammelklasse statt klarer Vertragsschnitte
- Prompt- oder Text-Finetuning als Ersatz fuer fehlende Zustands- oder
  Wahrheitssemantik
- Flag-Spam ohne kleine stabile Signalgrammatik
- verdeckte Zweitlogik ueber Notes, Traces oder Hilfsfelder
- grossflächiger Umbau des Servers, bevor die semantische Mitte stabiler ist


## Schlussbewertung

Der Refactor sollte Careena3 nicht "neu erfinden", sondern die bereits gute
Architekturmitte freilegen, die heute noch von Uebergangsprothesen verdeckt
wird.

Die wichtigste Regel fuer die naechsten Schritte lautet deshalb:

- erst die Wahrheitsbildung und ihre direkten Folgeschichten stabilisieren,
  dann die Dialogintelligenz ausbauen.
