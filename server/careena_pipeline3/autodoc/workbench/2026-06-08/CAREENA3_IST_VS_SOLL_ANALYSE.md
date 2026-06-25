# Careena3 Ist-vs-Soll-Analyse

Stand: 2026-06-07 Codebasis, Analyse abgelegt am 2026-06-08

## Zweck

Dieses Dokument vergleicht den tatsaechlichen aktuellen Codezustand von
`server/careena_pipeline3/` mit dem Sollbild aus:

- `TARGET_MODEL5.md`
- `REFACTORING_PLAN.md`
- `WORKING_VIEW_AND_PLAN_REVIEW.md`
- `HANDOVER_PROTOCOL.md`
- `KNOWN_ISSUES.md`
- den Reviews in `review_pass_01/`
- den juengeren Designgedanken zu:
  - fragegetriebener Prompt-Komposition
  - expliziten Skip-Signalen
  - internen Arbeitsnotizen / Steuerungsmarken
  - staerkerem Anliegen-/Zielverstaendnis im Dialogzustand

Die Leitfrage ist nicht:

- "wo ist ein Bug?"

sondern:

- "wie weit ist der reale Code bereits beim gewollten System?"
- "welche Teile sind tragfaehig?"
- "wo sitzen die Uebergangsprothesen?"
- "welche Schichten blockieren den naechsten sauberen Refactor?"


## Bewertungslegende

- `gut passend`
  - liegt bereits nah am Zielbild
- `tragfaehig, aber transitional`
  - richtige Richtung, aber noch Uebergangslogik oder Vertragsreste
- `kritische Uebergangsprothese`
  - aktuell funktional wichtig, aber architektonisch der falsche Dauerort
- `stub / vorgelagert / noch nicht eingelost`
  - bewusst unvollstaendig oder nur vorbereitet


## Gesamturteil

Der aktuelle Codezustand bestaetigt die wichtigste Lesart der Dokumente:

- die grossen Architekturachsen sind schon besser als der operative Klebstoff
  dazwischen
- `careena_pipeline3` ist nicht mehr "roh", sondern bereits sichtbar entlang
  des Zielmodells organisiert
- die eigentlichen Sollabweichungen sitzen nicht primaer in der zentralen
  Orchestrierung, sondern in den Uebergangsschichten zwischen
  Extraktion, Mapping, Merge, Requirement-Ableitung und Response-Uebergang

Kurz:

- Das System sieht im Kern schon wie Careena3 aus.
- Es verhaelt sich in den heiklen Stellen aber noch oft wie eine
  sauberer verpackte Migrationsstrecke.


## Wichtigste Gesamtbefunde

## 1. Der orchestrierende Kern ist real vorhanden

Der Code bestaetigt den Sollanspruch eines zentralen `DialogueManager`.

Positiv:

- die Turn-Reihenfolge ist sichtbar
- Entry, Extraction, Case, Recommendation-State und Response sind als eigene
  Rollen materialisiert
- Unterkomponenten werden orchestriert statt lose nebeneinander betrieben

Einschraenkung:

- die Souveraenitaet des `DialogueManager` wird an mehreren Stellen noch durch
  zu starke Uebergangsschichten oder textliche Behauptungen unterlaufen


## 2. Die groesste Sollabweichung liegt zwischen Call 2 und kanonischem Case

Das ist der mit Abstand wichtigste Befund.

Das Sollbild fordert:

- Extraktion
- klaren Zwischenvertrag
- explizite Update-/Merge-Entscheidung
- kanonischen Case-State

Der Ist-Zustand hat zwar fast alle Bausteine schon, aber die kritischsten
Stellen sind noch nicht sauber:

- `ResilientExtractionService`
- `ExtractionResultMapper`
- `CaseObservation`
- Teile von `CaseMergePolicy` / `CaseMerger`

Dadurch bleibt die Grundfrage noch nicht explizit genug beantwortet:

- wann erweitert neue Information dieselbe Observation
- wann ist sie Korrektur
- wann ist sie neue Instanz


## 3. Requirement-, Follow-up- und Readiness-Steuerung haengen noch zu stark
## an Mischsignalen

Das Sollbild will sichtbare Ableitung aus dem kanonischen Zustand.
Der Ist-Zustand arbeitet teilweise schon so, teilweise aber noch ueber
Signalreste aus Entry/Extraction.

Das Problem ist nicht, dass `RequirementPolicy` oder `AssessmentReadinessEvaluator`
falsch gedacht waeren.
Das Problem ist:

- ihre Eingaben sind noch nicht stabil genug


## 4. Response ist sauberer geschnitten, aber noch nicht voll vertraglich

Die Trennung Policy/Text ist real umgesetzt.
Das ist ein grosser Fortschritt.

Aber:

- `guide_next_step` ist eher eine textliche Uebergangsidee als ein sauber
  modellierter Dialogvertrag
- Recommendation-Uebergaenge sind zustandsseitig noch nicht stark genug
  materialisiert


## 5. Die neuen Designideen aus den letzten Nachrichten sind im Code erst
## als Vorformen vorhanden

Teilweise sichtbar:

- `trace_notes`
- `signals`
- `operation_mode`
- `call2_tasks`
- Fokus- und Pending-Followup-Signale

Noch nicht sichtbar genug:

- fragegetriebene Prompt-Bloecke mit klarer Feldfrage
- explizite Skip-Signale fuer nachgelagerte Schritte oder Prompt-Bloecke
- eine kleine Arbeitsmarken-Ebene fuer Anliegen, Zielstatus und
  Bearbeitungsfortschritt des Dialogs

Das heisst:

- diese Ideen sind gut anschlussfaehig
- aber noch kein echter Bestandteil des aktuellen Betriebsvertrags


## Sollabgleich nach Architekturthemen

## A. Zentrale Orchestrierung

Soll:

- `DialogueManager` als sichtbare Hauptachse
- Untermanager liefern Signale und Ergebnisse
- keine versteckten Gesamtentscheidungen in Seitenschichten

Ist:

- klar weitgehend erreicht

Einschaetzung:

- `gut passend`

Begruendung:

- `dialogue_manager.py` fuehrt den Turn real zentral aus
- die Reihenfolge entspricht der gewollten Architektur deutlich besser als ein
  Legacy-Sammelpfad
- die Datei wirkt eher wie echter Orchestrator als wie verkleideter Altcode

Restrisiko:

- einige Uebergangsentscheidungen werden weiterhin indirekt von
  Uebergangsschichten vorgeformt


## B. Entry / Call 1

Soll:

- kleiner Intake-Schritt
- minimale Einordnung
- Signale fuer Call 2
- kein spaeter verdeckter Endentscheider

Ist:

- in grossen Teilen erreicht

Einschaetzung:

- `gut passend` bis `tragfaehig, aber transitional`

Begruendung:

- `EntryManager` ist schlank
- `IntentGateway` liefert sinnvolle kleine Signale
- `call2_tasks` und `message_role` sind richtige Architekturbausteine

Abweichung:

- das aktuelle Entry-Modell kennt noch kaum Formen von Anliegen- oder
  Zielverfolgung jenseits medizinischer Klassifikation
- die neue Idee eines echten "was will der Nutzer gerade erreichen?" ist hier
  noch nicht modelliert


## C. Extraction / Call 2

Soll:

- einzelner, aber komponierter Call
- task-basiert
- modussensitiv
- enger Kontext
- Extraktion nicht gleich Kanonisierung

Ist:

- strukturell stark verbessert, fachlich noch Uebergangszone

Einschaetzung:

- `tragfaehig, aber transitional`

Begruendung:

- `llm/context.py` setzt die Kontextpolitik bereits sichtbar um
- `case_extraction.py` kennt Tasks, Modi und Scope-Grenzen
- `Call2OperationModeService` ist klein und passend

Hauptabweichung:

- der Prompt ist zwar schon kontrollierter, aber noch nicht als echte
  fragegetriebene Arbeitsstruktur organisiert
- es gibt noch keine expliziten Skip-Signale
- es gibt noch keine bewusst gefuehrte Notiz-/Arbeitsmarken-Ausgabe fuer
  nachgelagerte Orchestrierung

Strategischer Befund:

- Der aktuelle Call-2-Pfad ist ein guter Sockel fuer die naechste Designrunde,
  aber noch nicht die gewollte Zielgestalt.


## D. Kanonischer Case-State

Soll:

- klare Wahrheitsquelle
- explizite Observation-Identitaet
- klare Update-Semantik
- keine versteckten Reparaturen im Domainmodell

Ist:

- konzeptionell vorhanden, semantisch noch nicht stabil

Einschaetzung:

- `kritische Uebergangsprothese`

Begruendung:

- `CaseMergePolicy` und `CaseMerger` gehen schon sichtbar in die richtige
  Richtung
- `case_update.py` liefert bereits gutes Entscheidungs-Vokabular

Aber:

- `ExtractionResultMapper` driftet Felder in generische `details`
- `CaseObservation` repariert und harmonisiert zu viel im Modell selbst
- dadurch bleibt die Case-Wahrheit zu indirekt und zu wenig vertraglich

Das ist die zentrale Sollluecke des Systems.


## E. Requirements und Follow-up

Soll:

- offene Informationsbedarfe aus kanonischem Zustand ableiten
- keine harte Slot-Fill-Magie
- Follow-up als sichtbare Konsequenz, nicht als Schattensystem

Ist:

- Richtung stimmt, Grundlage ist noch instabil

Einschaetzung:

- `tragfaehig, aber transitional`

Begruendung:

- `RequirementPolicy` ist als zentrale Policy sinnvoll platziert
- `pending_followup` als Objekt ist ein echter Fortschritt

Abweichung:

- `active_modules` werden noch zu stark ueber Uebergangssignale getragen
- der Requirement-Pfad haengt noch nicht stark genug am Case-Truth

Konsequenz:

- Follow-up ist strukturell da
- aber noch nicht robust genug als Zielarchitektur


## F. Readiness und Recommendation-State

Soll:

- klare Trennung:
  - Wunsch
  - Reife
  - Pfadfreigabe
  - Recommendation-Inhalt

Ist:

- gute Grundtrennung, aber noch schwacher Uebergang zwischen
  Dialogsteuerung und Recommendation-Pfad

Einschaetzung:

- `tragfaehig, aber transitional`

Begruendung:

- `RecommendationStateService` trennt `recommendation_requested` und
  `recommendation_ready` sauber
- `AssessmentReadinessEvaluator` ist konservativ und dem Zielbild nahe

Abweichung:

- `guide_next_step` sagt mehr, als der Systemzustand eigentlich hergibt
- Recommendation-Inhalt bleibt Placeholder


## G. Response-Policy und Text

Soll:

- Pfadwahl getrennt von Wortlaut
- sichtbare Dialogsteuerung
- keine falschen Versprechen im Text

Ist:

- Trennung real vorhanden
- Pfadgrammatik noch zu grob

Einschaetzung:

- `gut passend` fuer den Zuschnitt
- `tragfaehig, aber transitional` fuer die inhaltliche Steuerlogik

Begruendung:

- `ResponseManager` und `ResponseTextBuilder` sind richtig getrennt
- das Zielmodell ist hier klar besser umgesetzt als in vielen anderen Teilen

Abweichung:

- `guide_next_step` ist noch kein echter Vertragszustand
- die neue Idee von Zielstatus, Anliegenfortschritt und "ist das Ziel jetzt
  erreicht?" ist noch nicht modelliert


## H. Prompt-/Signallogik der naechsten Designrunde

Sollerweiterung aus juengeren Gedanken:

- Prompt als Aufgaben- und Fragenbloecke
- daraus ableitbare Skip-Signale
- interne Arbeitsnotizen fuer Steuerung
- besseres Tracking des Nutzeranliegens und des Bearbeitungsstatus

Ist:

- nur als Vorform vorhanden

Einschaetzung:

- `noch nicht eingelost, aber gut anschlussfaehig`

Begruendung:

- `trace_notes`, `signals`, `call2_tasks`, `operation_mode` und Fokusfelder
  zeigen bereits dieselbe Denkrichtung
- es fehlt aber noch ein expliziter kleiner Zielvertrag fuer:
  - skip / proceed
  - "enthaelt weitere Information?"
  - "welches Anliegen wird gerade verfolgt?"
  - "ist das Ziel bereits erreicht?"


## Bewertung pro zentraler Datei / Klasse

## 1. `server/careena3.py`

Bewertung:

- `kritische Uebergangsprothese`

Ist-Zustand:

- Produktserver
- Session-Adapter
- Response-Serializer
- `/simrun`-Steuerung
- Simulation-Endpunkt

Sollabgleich:

- zu viel Verantwortung am HTTP-Einstieg
- fuer aktuelle Migration praktisch
- als Zielzustand zu voll

Wert:

- aktuell nuetzlich als Integrationsoberflaeche

Problem:

- vermischt Produktpfad und Testharness


## 2. `application/managers/dialogue_manager.py`

Bewertung:

- `gut passend`

Staerken:

- klare zentrale Sequenz
- wenig Schichtgeruch
- sichtbare Orchestrierung

Abweichung:

- koennte spaeter noch mit besseren expliziten Uebergangsvertraegen
  profitieren, ist aber nicht das Kernproblem


## 3. `application/managers/entry_manager.py`

Bewertung:

- `gut passend`

Staerken:

- schlank
- sinnvoll begrenzt
- gute Rolle fuer Call 1

Abweichung:

- noch keine explizite Anliegen- oder Zielstatus-Semantik


## 4. `application/managers/extraction_manager.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- selbst schlank
- sauber als Schichtgrenze

Abweichung:

- lebt von schwachen Rueckgaben aus Mapper und Extraction-Service
- `active_modules`-Rueckfuehrung ist nicht stabil genug


## 5. `application/managers/response_manager.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- richtige Rolle
- gute Trennung zum Textbuilder

Abweichung:

- `guide_next_step` ist noch textlich, nicht vertraglich
- kein echter kleiner Transition-State


## 6. `application/managers/case_state_manager.py`

Bewertung:

- `gut passend` auf Rollenniveau

Staerken:

- gute Einbettung im Orchestrator
- geringe Eigenkomplexitaet

Abweichung:

- die Probleme liegen darunter, nicht in der Klasse selbst


## 7. `application/services/resilient_extraction_service.py`

Bewertung:

- `kritische Uebergangsprothese`

Warum:

- vereinigt Fehlergrenze, Normalisierung, Subject-Gating,
  Follow-up-Korrekturen und Fallback-Logik

Sollabweichung:

- zu viele operative Reparaturen an einem Ort
- idealer Sammelpunkt fuer künftige Edge-Case-Anlagerungen

Zukunft:

- eher zerlegen als weiter anreichern


## 8. `application/services/extraction_result_mapper.py`

Bewertung:

- `kritische Uebergangsprothese`

Warum:

- verliert Struktur
- driftet Attribute in generische Haufenform
- erzeugt Alias- und Detailprobleme downstream

Sollabweichung:

- steht genau zwischen sauberem Extraktionsvertrag und unsauberer
  Domain-Uebergabe


## 9. `domain/requirement_policy.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- zentrale Policy ist der richtige Ort
- Fokus- und Requirement-Denken ist im Prinzip gesund

Abweichung:

- lebt noch zu stark von `active_modules`
- braucht stabilere semantische Eingaben aus dem Case


## 10. `application/services/readiness_evaluator.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- konservativ
- sauber genug zugeschnitten

Abweichung:

- nur so gut wie Case- und Requirement-Grundlage


## 11. `models/domain/observation.py`

Bewertung:

- `kritische Uebergangsprothese`

Warum:

- Domainmodell plus Legacy-Harmonisierung plus Feldaliasing plus Reparatur

Sollabweichung:

- das zentrale Domainobjekt traegt noch zu viel Migrationslast

Folge:

- Case-Truth bleibt schwer vorhersagbar


## 12. `domain/case_update.py`

Bewertung:

- `gut passend`

Staerken:

- sehr gutes Entscheidungs-Vokabular
- nah am gewollten Zielvertrag

Abweichung:

- Nutzung im Gesamtsystem noch nicht voll ausgeschoepft


## 13. `domain/case_merge_policy.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- versucht bereits explizite Update-Entscheidungen
- kein blosser stiller Merge

Abweichung:

- Observation-Identitaet noch nicht stark genug
- Konfliktlogik und Spezifitaetslogik bleiben noch heuristisch


## 14. `domain/case_merger.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- arbeitet sichtbar auf Basis von Entscheidungen

Abweichung:

- merge-orientiert statt noch klarer update-orientiert
- lebt von den Unschaerfen aus Mapper und Observation-Modell


## 15. `llm/context.py`

Bewertung:

- `gut passend`

Staerken:

- klare Kontextpolitik
- gute Rollentrennung
- richtige Begrenzungslogik

Abweichung:

- neue Konzepte wie Anliegenstatus, Arbeitsnotizen und Skip-Signale fehlen
  noch als expliziter Vertrag


## 16. `llm/prompts/case_extraction.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- gute globale Leitplanken
- Task-Gating
- Modusregeln

Abweichung:

- noch eher Regeltext als echte Frage-/Block-Komposition
- keine strukturierten Skip-Ausgaenge
- keine expliziten Selbstnotizen / Arbeitsmarken


## 17. `llm/prompts/intent_gateway.py`

Bewertung:

- `gut passend`

Staerken:

- klare Minimalrolle fuer Call 1
- gute Begrenzung
- `additional_medical_information` ist wertvoll

Abweichung:

- das Gateway modelliert noch nicht explizit genug das uebergeordnete
  Nutzeranliegen oder einen Bearbeitungsstatus


## 18. `models/turn/context.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- gutes Turn-Rueckgrat

Abweichung:

- traegt noch keine explizite Ebene fuer:
  - Zielstatus
  - Arbeitsnotizen pro Schritt
  - Skip-/Proceed-Marken
  - Anliegenverstaendnis


## 19. `models/workflow/intent_gateway.py`

Bewertung:

- `gut passend`

Staerken:

- kleine sichtbare Signale
- guter Grundvertrag fuer Call 1 -> Call 2

Abweichung:

- Signalraum sollte spaeter eher qualitativ verbessert als nur groesser
  gemacht werden


## 20. `models/extraction/result.py`

Bewertung:

- `tragfaehig, aber transitional`

Staerken:

- sauberer als direkter Delta- oder Case-Vertrag
- `signals` als First-Class-Ausgang ist wertvoll

Abweichung:

- Signale sind semantisch noch zu offen
- es fehlt eine klare Trennung zwischen:
  - Belegsignal
  - Arbeitsmarke
  - Steuerhinweis


## Welche Sollideen im Code schon sichtbar angelegt sind

- zentrale Orchestrierung statt Pipeline-Sammelklasse
- task-basierter und modussensitiver Call 2
- Kontext als Begrenzung statt freie Faktenquelle
- Trennung Recommendation-Wunsch vs Recommendation-Reife
- explizite Update-Sprache im Case-Bereich
- Text getrennt von Policy
- kleine sichtbare Signale als wachsender Architekturansatz


## Welche Sollideen im Code noch klar fehlen

- expliziter Zielvertrag fuer `guide_next_step` oder vergleichbare
  Dialogue-Transitions
- robuste Observation-Identitaet und Update-Semantik
- konsequente Rueckbindung von Requirement-Aktivierung an kanonische
  Fallwahrheit
- fragegetriebene Prompt-Bloecke statt nur regelreicher Prompts
- explizite Skip-Signale fuer Prompt-/Manager-Komposition
- bewusste Arbeitsnotizen / interne Beobachtungen als zulaessige
  Steuerungsebene
- ein klarer Zustand oder Teilzustand fuer:
  - aktuelles Nutzeranliegen
  - was das System glaubt, gerade zu bearbeiten
  - ob das Ziel erreicht ist


## Strategische Schlussfolgerung

Wenn man den realen Code gegen das beschriebene Sollbild liest, ergibt sich
folgende Prioritaetslogik:

1. Nicht zuerst weitere Text- oder Prompt-Kosmetik.
2. Nicht zuerst noch mehr lokale Follow-up- oder Recommendation-Logik.
3. Zuerst die semantische Mitte staerken:
   - Observation-Identitaet
   - Update-Vertrag
   - Mapper-/Observation-Uebergang
   - Requirement-Aktivierung aus Case-Truth
4. Danach den Dialogue-/Transition-Vertrag erweitern:
   - `guide_next_step`
   - Anliegenstatus
   - Zielerreichung
   - kleine Arbeitsmarken
5. Darauf aufbauend dann die naechste Prompt-/Signalrunde:
   - Fragebloecke
   - Skip-Signale
   - auswertbare interne Notizen


## Verdichtetes Fazit

`careena_pipeline3` ist architektonisch bereits deutlich naeher am gewollten
System als an der alten Pipeline.

Der aktuelle Engpass ist nicht mehr fehlende Grobstruktur, sondern fehlende
semantische Schaerfe an den Uebergangskanten.

Die wichtigste praktische Lesart fuer den naechsten Refactoring-Plan ist
deshalb:

- Der Refactor sollte nicht "alles verbessern", sondern gezielt die
  Uebergangsprothesen abbauen, die heute noch zwischen sauberem
  Zielvertrag und realem Zustand vermitteln.
