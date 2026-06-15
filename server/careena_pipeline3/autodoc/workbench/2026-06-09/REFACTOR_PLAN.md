# Careena3 Refactor Plan

Stand: 2026-06-09
Status: aktiv
Vorgaenger: `autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`


## Zweck

Dieser Plan ist der neue aktive Steuerrahmen fuer das laufende Careena3-
Refactoring.

Er soll drei Dinge gleichzeitig leisten:

1. die Zielarchitektur aus `SYSTEM_OVERVIEW.md` und `TARGET_MODEL6.md`
   staerker in reale Verantwortungsbereiche uebersetzen
2. den aktuellen Python-Code als Ist-Zustand ernst nehmen, damit die Planung
   nicht an vorhandenen Uebergangsprothesen vorbeigeht
3. die weitere Implementierungsarbeit so vorbereiten, dass spaetere
   Funktionserweiterungen nicht auf unsauberen Vertragsanfaengen aufbauen


## Warum ein neuer Plan noetig ist

Der Plan vom `2026-06-08` war als damaliger Arbeitsstand sinnvoll und hat
gute Prioritaeten gesetzt.

Trotzdem ist inzwischen ein neuer Plan sinnvoller als eine blosse Fortsetzung,
weil:

- das Architektur-Zielbild in `autodoc/wiki/SYSTEM_OVERVIEW.md` inzwischen
  klarer und konsistenter ist als zum Zeitpunkt des alten Plans
- Phase 1 des alten Plans im Code im Wesentlichen wirklich angekommen ist
- der alte Plan Phase 2 korrekt erkannt hat, aber der heutige Kern nicht mehr
  bloss "Mapper und Service aufraeumen" ist, sondern das Festziehen der
  finalen Schichtvertraege
- die weitere Arbeit staerker auf endgueltige Verantwortungsbereiche und
  begrenzte Entscheidungshoheiten zugeschnitten werden sollte

Dieser Plan ersetzt den alten Plan deshalb als aktives Arbeitsdokument, ohne
seine bereits richtigen Einsichten zu verwerfen.


## Quellenbasis

Fuehrende Soll-Quellen:

- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `autodoc/workbench/2026-06-08/TARGET_MODEL6.md`

Wichtige Prozess- und Review-Quellen:

- `autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
- `autodoc/workbench/2026-06-08/CODE_REVIEW_FRAMEWORK.md`

Wichtige Ist-Anker im Code:

- `application/managers/dialogue_manager.py`
- `application/managers/entry_manager.py`
- `application/managers/extraction_manager.py`
- `application/managers/case_state_manager.py`
- `application/managers/response_manager.py`
- `application/managers/safety_manager.py`
- `application/managers/confirmation_manager.py`
- `application/services/resilient_extraction_service.py`
- `application/services/extraction_result_mapper.py`
- `application/services/readiness_evaluator.py`
- `application/services/recommendation_state_service.py`
- `application/services/response_text_builder.py`
- `domain/requirement_policy.py`
- `domain/case_merge_policy.py`
- `domain/case_merger.py`
- `llm/context.py`
- `llm/prompts/case_extraction.py`
- `server/careena3.py`

Hinweis:

- die angefragte Datei
  `GENERAL_GOOD_ARCHITECHTURE_GUIDELINES.md` bzw.
  `GENERAL_GOOD_ARCHITECTURE_GUIDELINES.md` war beim Schreiben dieses Plans im
  aktuellen Workspace nicht auffindbar
- ihre beabsichtigte Rolle wird deshalb hier ueber explizite
  Architekturhygiene-Regeln aus `SYSTEM_OVERVIEW.md`, `TARGET_MODEL6.md`,
  `CODE_REVIEW_FRAMEWORK.md` und dem aktuellen Chatkontext mitgetragen


## Architektonische Leitthese

Careena soll nicht als grosse Pipeline mit diffusen Nebenentscheidungen
weiterwachsen, sondern als sichtbar orchestriertes System mit klar getrennten
Verantwortungsebenen.

Der entscheidende Architekturgedanke lautet:

- der `DialogueManager` bleibt die sichtbare Orchestrierungsmitte
- Unterkomponenten duerfen nur begrenzte, schichtgerechte Entscheidungen
  treffen
- jede Schicht arbeitet auf ihrer eigenen Wahrheits- oder Signalebene
- Uebergangsobjekte bleiben Arbeitsobjekte und werden nicht zur heimlichen
  Zweitwahrheit
- Recommendation, Response, Safety und spaetere Feature-Ausbauten duerfen
  nicht auf unsauberen Glue-Schichten aufbauen

Der Plan priorisiert deshalb nicht "mehr Verhalten", sondern:

1. Rollen klarziehen
2. Vertraege verkleinern
3. Entscheidungshoheiten begrenzen
4. erst danach komplexere Funktionserweiterungen aufsetzen


## Zielbild der finalen Verantwortungsbereiche

| Ebene | Heutige Hauptklassen | Soll-Verantwortung | Darf ausdruecklich nicht passieren |
|---|---|---|---|
| Orchestrierung | `DialogueManager` | sichtbare Turn-Reihenfolge, Delegation, Einsammeln kleiner Ergebnisse | heimliche medizinische Detaillogik, versteckte Recommendation- oder Response-Wahrheit |
| Entry / Call 1 | `EntryManager`, Intent-Gateway-Pfad | Nachricht einordnen und kleine Steuersignale erzeugen | breite Fallrekonstruktion oder spaete Pfadpolitik |
| Extraction / Call 2 | `ExtractionManager`, LLM-Extraction | kleine medizinische Claims aus der aktuellen Nachricht liefern | direktes Schreiben in `MedicalCase` oder breite Fallzweitwahrheit |
| Case Truth | `CaseStateManager`, `CaseMergePolicy`, `CaseMerger`, `MedicalCase` | kanonische Fallwahrheit fortschreiben, Identitaet, Update-Art, Konflikt und Unsicherheit sichtbar behandeln | Signale, Promptreste oder Textartefakte als Wahrheit uebernehmen |
| Process State | `DialogueStateService`, `DialogueState` | naechsten Dialogschritt, offene Klaerungen, Fokus und Follow-up aus sichtbarem Zustand ableiten | medizinische Endwahrheit parallel zum Case fuehren |
| Safety | `SafetyManager`, `SafetyState` | Safety-Pruefung auf mehreren Ebenen liefern | still die Gesamtantwort steuern, ohne dass der Vertrag sichtbar ist |
| Readiness / Gate | `AssessmentReadinessEvaluator`, `RecommendationStateService` | aus Case-Wahrheit und Prozesssignalen eine ehrliche Freigabelage ableiten | fehlende Wahrheit durch Heuristik kaschieren |
| Response Policy | aktuell `ResponseManager` | erlaubten Antwortpfad bestimmen | Wortlaut, Pfadpolitik und Ersatzsemantik vermischen |
| Response Text | `ResponseTextBuilder` | nur formulieren, was der bereits freigegebene Zustand hergibt | fehlende Zustandslogik sprachlich ueberspielen |
| Confirmation | `ConfirmationManager` | explizite Nutzerbestaetigung oder Korrektur in kontrollierte Updates ueberfuehren | als lose UI-Idee neben dem Wahrheitsmodell stehen bleiben |


## Aktuelle Code-Einordnung

Diese Einordnung folgt der Denkrichtung aus `CODE_REVIEW_FRAMEWORK.md`:
Rolle, tatsaechliches Verhalten, Wahrheitslage, Problemtyp, naechster
Bewegung.

| Datei/Klasse | Verantwortungsbereich | Status | Kernbeobachtung | Naechste sinnvolle Bewegung |
|---|---|---|---|---|
| `application/managers/dialogue_manager.py` | orchestration | `good-transitional` | Turn-Orchestrierung ist klarer als frueher, traegt aber noch Uebergangsverkabelung aus `message_delta` und Placeholder-Confirmation | behalten, spaeter an kleineren Vertraegen ausrichten |
| `application/managers/case_state_manager.py`, `domain/case_merge_policy.py`, `domain/case_merger.py` | case-truth | `good-transitional` | das staerkste bereits eingeloste Architekturzentrum; die Truth-Kante ist sichtbar | erhalten und semantisch weiterschaerfen statt neu erfinden |
| `application/services/extraction_result_mapper.py` | normalization | `refactor / structural-issue` | explizit transitionaler Adapter; uebersetzt Extraction weiterhin in `MessageDelta` und erzeugt Nebenwirkungen wie Modulaktivierung | gezielt zurueckbauen oder durch schmaleren Bridge-Vertrag ersetzen |
| `application/services/resilient_extraction_service.py` | extraction | `refactor / structural-issue` | traegt Fehlergrenze, LLM-Normalisierung, Subject-Gating und Follow-up-Reparatur zugleich | in kleinere Verantwortungen schneiden |
| `llm/context.py`, `llm/prompts/case_extraction.py` | extraction | `refactor / structural-issue` | Zielbild fuer Call 2 ist enger als der aktuelle Kontext- und Promptzuschnitt | zuerst Vertrag und Kontextpolitik verkleinern |
| `domain/requirement_policy.py` | requirements | `watch / structural-issue` | schon naeher an Case-Truth, aber Pflichtfeld- und Modulsemantik noch provisorisch | explizites Requirement-Modell nachziehen |
| `application/services/readiness_evaluator.py`, `application/services/recommendation_state_service.py` | readiness | `watch / structural-issue` | ehrlicher als frueher, aber noch zu nah an aktueller Requirement-Provisorik | auf klareres Requirement- und Gate-Modell umstellen |
| `application/managers/response_manager.py`, `application/services/response_text_builder.py` | response | `refactor / structural-issue` | `guide_next_step` und Placeholder-Wege zeigen noch fehlende Zustandssemantik zwischen readiness und finaler Antwort | Response-Policy und Text sauber trennen |
| `application/managers/safety_manager.py` | safety | `watch / structural-issue` | Schicht ist architektonisch vorgesehen, im Code aber fast nur Scaffold | nach den Kernvertraegen als echte Layer aufbauen |
| `application/managers/confirmation_manager.py` | confirmation | `replace / structural-issue` | aktuell reiner Platzhalter | spaeter als echten Korrekturpfad aufbauen |
| `server/careena3.py` | infrastructure | `watch` | brauchbare Integrationsoberflaeche, aber Produktpfad und Simulation liegen noch dicht beieinander | bewusst spaet ausduennen |


## Arbeitsweise fuer das Refactoring

## Grundregel

Der Plan ist kein Aufgabenstapel, sondern ein Vertrags- und
Verantwortungsplan.

Vor jeder groesseren Aenderung wird deshalb nicht zuerst gefragt
"wie kann ich das Verhalten retten?", sondern:

- welche Schicht sollte diese Entscheidung tragen
- welche Wahrheit liegt hier vor
- welches Objekt darf nach diesem Schritt stabiler werden


## Stetige Leitfragen pro Arbeitsschritt

Diese Fragen sollen waehrend der praktischen Arbeit bewusst wiederholt werden:

- Was ist die beabsichtigte Rolle dieser Klasse oder Datei?
- Was macht der Code tatsaechlich gerade?
- Arbeitet die Stelle auf Signal, Prozesszustand, Fallwahrheit oder
  abgeleiteter Entscheidungswahrheit?
- Entsteht das Verhalten aus einem sichtbaren Vertrag oder aus impliziter
  Kopplung?
- Wird hier normalisiert, gemerged, bewertet, gesteuert oder schon geantwortet?
- Wird ein Symptom lokal behandelt oder die eigentliche strukturelle Ursache?
- Erweitert diese Aenderung die Zielarchitektur oder stuetzt sie nur eine
  vorhandene Uebergangsprothese?
- Entsteht eine neue versteckte Entscheidungshoheit?
- Ist die verbleibende Unfertigkeit sichtbar oder wird sie unsichtbar falsch?


## Lokales Problem vs. strukturelles Problem

Ein Problem gilt vorlaeufig als lokal, wenn:

- es in derselben Schicht bleibt
- kein neuer Vertrag noetig wird
- die Verantwortung der beteiligten Klasse klar bleibt
- keine neue Signal-, Merge- oder Zustandssemantik entsteht

Ein Problem gilt vorlaeufig als strukturell, wenn:

- unklar ist, welche Schicht zustaendig sein sollte
- dieselbe Wahrheit auf mehreren Ebenen parallel modelliert wird
- eine neue Spezialregel nur alte Unschaerfe kaschiert
- Folgeentscheidungen auf instabilen Hilfssignalen beruhen
- eine Brueckenklasse zu dauerhaftem Zentraltraeger wird

Arbeitsregel:

- lokale Probleme duerfen innerhalb des aktiven Blocks pragmatisch geloest
  werden
- strukturelle Probleme duerfen nicht still mitgezogen werden, sondern muessen
  im passenden Block sichtbar landen


## Definition von gutem Fortschritt

Ein Refactor-Schritt gilt nicht schon dann als gut, wenn Verhalten irgendwie
funktioniert.

Guter Fortschritt bedeutet:

- eine Verantwortung ist klarer als zuvor
- ein Vertrag ist kleiner und expliziter als zuvor
- eine Klasse hat weniger verdeckte Gesamtentscheidungen als zuvor
- die Wahrheitsgrenze ist besser lesbar als zuvor
- spaetere Features koennen auf einer kleineren, stabileren Schicht aufsetzen


## Was bewusst vermieden werden soll

- neue medizinische Sonderfalllogik als Ersatz fuer Vertragsklarheit
- neue grosse Sammelklassen
- Prompt- oder Textfeintuning als Ersatz fuer Zustands- oder Wahrheitsmodell
- Flag-Spam ohne kleine stabile Signalgrammatik
- Brueckenobjekte, die gleichzeitig Signal, Prozesszustand und Fallwahrheit
  tragen
- Reaktion auf Laufprobleme durch weitere Reparaturmagie im Mapper oder in
  Response-Texten
- Server- oder Runtime-Umbau, solange die semantische Mitte noch driftet


## Empfohlene globale Reihenfolge

1. Call-2-Vertrag und Kontextpolitik festziehen
2. Extraction-zu-Truth-Bruecke de-transitionalisieren
3. Requirement-, Follow-up- und Readiness-Schicht auf expliziterer
   Case-Wahrheit neu begruenden
4. Response-Policy und Transition-Zustand sauber modellieren
5. Safety als echte Architekturachse aufbauen
6. Confirmation/Korrektur kontrolliert in den Truth-Pfad einfuehren
7. kleine Signalgrammatik, Prompt-Komposition und spaetere Recommendation-
   Freigaben darauf aufbauen
8. Runtime-/Server- und Simulationsentkopplung erst am Ende nachziehen


## Block 0: Arbeitsvertrag und Code-nahe Architekturdisziplin [aktiv]

## Ziel

Den Refactor so fuehren, dass Architekturfragen nicht wieder unter laufenden
Einzelfixes verschwinden.

## Warum jetzt

Ohne diesen Arbeitsvertrag kippt die weitere Arbeit schnell wieder in
Uebergangsreparaturen.

## Sollzustand

- jeder groessere Schritt bleibt an einer klaren Schicht orientiert
- neue Probleme werden sichtbar einsortiert statt still herumgetragen
- Dokumente und Code werden gemeinsam gelesen:
  Dokumente geben das Soll,
  Code zeigt den realen Ist-Zustand

## Kernaufgaben

1. vor jedem groesseren Block den betroffenen Code kurz gegen seine Rolle
   halten
2. neue strukturelle Probleme im passenden Block sammeln statt seitlich zu
   loesen
3. nach jedem echten Architekturschritt kurz pruefen:
   wurde eine Verantwortung kleiner oder nur verschoben

## Block-Gate / Done

- der Plan bleibt waehrend der Umsetzung lebendes Steuerdokument
- Architekturentscheidungen werden sichtbar begruendet


## Block 1: Call-2-Vertrag und Kontextpolitik neu zuschneiden [hoechste Prioritaet]

## Ziel

Call 2 auf eine kleinere, klarere Rolle festziehen:
Er liefert begrenzte medizinische Claims aus der aktuellen Nachricht, aber
keine breite Fallrekonstruktion.

## Warum jetzt

Der groesste verbleibende Architekturdrift sitzt aktuell vor der Truth-Kante:

- zu grosser Aufgabenmix
- zu breite Kontextpakete
- zu schwerer Nachnormalisierungspfad
- Gefahr, dass Kontext wieder zur stillen Zweitwahrheit wird

## Aktueller Codebefund

- `llm/context.py` baut weiterhin `case_summary` und `dialogue_summary` in den
  Call-2-Input ein
- `llm/prompts/case_extraction.py` traegt schon gute Guardrails, aber der
  Outputvertrag ist weiterhin relativ breit
- `ResilientExtractionService` kompensiert Unschaerfen des Call-2-Vertrags
  nachgelagert

## Sollzustand

- `latest_user_message` bleibt die primaere Faktquelle
- Kontext dient nur Einordnung, Begrenzung und Fokusbindung
- der Output von Call 2 ist kleiner als der heutige implizite
  Fallreprasentationsversuch
- der Vertrag unterscheidet sauber zwischen:
  medizinischem Claim,
  offener Rueckfrage,
  kleinem Arbeitssignal,
  rein technischem Trace

## Kernaufgaben

1. explizit entscheiden, welche minimalen Outputarten Call 2 dauerhaft
   liefern darf
2. `build_case_extraction_input(...)` modussensitiver und knapper schneiden
3. pruefen, ob `case_summary` und `dialogue_summary` voll gebraucht werden
   oder auf kleinere Fokuskontexte reduziert werden muessen
4. festlegen, welche Informationen eher in Python modelliert werden sollten
   und welche wirklich LLM-Arbeit bleiben
5. den zweiten grossen Re-Emissions-/Normalisierungscharakter von Call 2
   konsequent zurueckdruecken

## Betroffene Dateien/Klassen

- `llm/context.py`
- `llm/prompts/case_extraction.py`
- `models/extraction/result.py`
- `application/services/resilient_extraction_service.py`
- `application/managers/extraction_manager.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- klar ueberfluessige Kontextfelder
- kleine Feld- oder Aufgabeninkonsistenzen im Call-2-Vertrag
- lokaler Prompttext, wenn damit ein schon beschlossener Vertrag nur
  sauberer formuliert wird

## Nicht innerhalb dieses Blocks still loesen

- neue breite Mapper- oder Merge-Heuristiken als Nachrettung
- Featurelogik, die nur wegen des unscharfen Call-2-Vertrags noetig wirkt

## Block-Gate / Done

- Call 2 ist enger und rollenreiner beschrieben als zuvor
- sein Kontext ist knapper und fokusbezogener
- der Outputvertrag ist sichtbar kleiner und besser von Prozess- und
  Wahrheitslogik getrennt


## Block 2: Extraction-zu-Truth-Bruecke de-transitionalisieren [offen]

## Ziel

Den Uebergang von Extraction in die Truth-Schicht so schneiden, dass
Brueckenobjekte klein und lesbar bleiben und nicht mehrere Wahrheitsarten
zugleich tragen.

## Warum jetzt

Selbst ein besserer Call-2-Vertrag hilft nur begrenzt, wenn die naechste
Schicht ihn wieder in eine breite Altform zurueckbiegt.

## Aktueller Codebefund

- `ExtractionResultMapper` bezeichnet sich selbst als transitional mapper
- `MessageDelta` ist weiterhin wichtiger Zwischenadapter
- Modulaktivierung und Requirement-Hinweise werden teils ueber die
  Brueckenstrecke mitgetragen
- `ResilientExtractionService` enthaelt mit Follow-up-Update-Anpassung bereits
  nachgelagerte Reparatursemantik

## Sollzustand

- die Truth-Schicht konsumiert eine schmalere und explizitere Bruecke
- `ExtractionResultMapper` wird kleiner oder durch passendere Objekte ersetzt
- `MessageDelta` bleibt hoechstens ein bewusst begrenzter Migrationsadapter
- Follow-up-Update-Anpassungen sind keine versteckte Extraktionsreparatur mehr

## Kernaufgaben

1. entscheiden, ob `MessageDelta` weiter gebraucht wird oder schrittweise
   abgeloest werden soll
2. Modulaktivierung, Requirement-Hinweise und medizinische Claims sauberer
   voneinander trennen
3. `ResilientExtractionService` in kleinere Verantwortungen schneiden:
   Fehlergrenze,
   optionale Normalisierung,
   Follow-up-Anpassung,
   Subject-Gating
4. pruefen, ob ein expliziter `CaseUpdateRequest`- oder aehnlicher
   Brueckenvertrag sinnvoller ist als der heutige Mischpfad

## Betroffene Dateien/Klassen

- `application/services/extraction_result_mapper.py`
- `application/services/resilient_extraction_service.py`
- `models/turn/message_delta.py`
- `models/extraction/result.py`
- `application/managers/extraction_manager.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- klare Feldzuordnungsfehler
- totes oder irrefuehrendes Delta-Rauschen
- eng begrenzte Mapper-Fehler, wenn keine neue Semantik entsteht

## Nicht innerhalb dieses Blocks still loesen

- neue Spezialfaelle in `MessageDelta`, nur um Altpfade laenger am Leben zu
  halten
- Requirement- oder Response-Probleme ueber weitere Adapterfelder kaschieren

## Block-Gate / Done

- die Bruecke zwischen Extraction und Truth ist lesbarer und schmaler
- Mapper und Service tragen weniger Sammelverantwortung
- Brueckenobjekte sind klarer als Arbeitsobjekte und nicht als Zweitwahrheit
  erkennbar


## Block 3: Requirement-, Follow-up- und Readiness-Schicht neu begruenden [offen]

## Ziel

Process-State und Recommendation-Gate staerker aus expliziter Case-Wahrheit
ableiten und weniger aus impliziter Modul- oder Follow-up-Historie.

## Warum jetzt

Wenn Case-Truth und Extraction-Kante sauberer sind, muss die naechste echte
Wirkung in Requirement-, Follow-up- und Readiness-Logik sichtbar werden.

## Aktueller Codebefund

- `RequirementPolicy` liest schon `MedicalCase`, ist aber weiter stark auf
  aktuelle Module, Fokusheuristiken und starre Requirement-Listen gestuetzt
- `AssessmentReadinessEvaluator` ist konservativ, aber noch an die heutige
  provisorische Requirement-Semantik gekoppelt
- `RecommendationStateService` setzt im Kern noch ein Boolean-Gate auf den
  aktuellen Evaluator

## Sollzustand

- Requirements sind sichtbar an Fallwahrheit gekoppelt
- Follow-up ist erkennbar Prozesszustand, nicht extraktionsnaher Slot-Fill
- Readiness ist explizite Entscheidungswahrheit, nicht verstreute Hilfslogik
- Konflikte, Ambiguitaet und Subjektunklarheit koennen Gate- und Follow-up-
  Folgen ausloesen, ohne neue Wahrheit zu erfinden

## Kernaufgaben

1. explizit definieren, was ein Requirement in Careena fachlich bedeutet
2. `active_modules`-Semantik neu bewerten:
   Signalhilfe,
   Prozesshinweis,
   oder fachlicher Pflichtfeldtreiber
3. `RequirementPolicy` staerker an Beobachtungstypen, Fokuslage und
   sichtbaren Case-Issues ausrichten
4. `AssessmentReadinessEvaluator` auf ein klareres Requirement- und
   Konfliktmodell absichern
5. pruefen, ob `RecommendationReadiness` als eigenes expliziteres Modell
   sinnvoll ist

## Betroffene Dateien/Klassen

- `domain/requirement_policy.py`
- `application/services/dialogue_state_service.py`
- `application/services/readiness_evaluator.py`
- `application/services/recommendation_state_service.py`
- `models/domain/dialogue.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- klare Alias- oder Reihenfolgefehler bei Follow-up und Requirements
- kleine Fokusfehler, wenn keine neue Requirement-Semantik eingefuehrt wird

## Nicht innerhalb dieses Blocks still loesen

- Recommendation-Freigabe ueber Texttricks statt ueber ehrliche Gate-Logik
- neue Einzelfallslots ohne klares Requirement-Modell

## Block-Gate / Done

- Requirement- und Follow-up-Logik wirkt sichtbar zustandsgebundener
- Readiness ist als abgeleitete Wahrheit klarer von MedicalCase und
  DialogueState getrennt
- Gate-Entscheidungen driften weniger ueber Hilfssignale auseinander


## Block 4: Response-Policy und Transition-Zustand sauber modellieren [offen]

## Ziel

Den Bereich zwischen "Mindeststand erreicht" und "welcher Antwortpfad ist
freigegeben?" vertraglich sauber schneiden.

## Warum jetzt

Hier sitzt aktuell der deutlichste Rest von textlicher Ersatzsemantik:

- `guide_next_step`
- placeholderhafte Recommendation-Texte
- Confirmation-Text statt Confirmation-Vertrag

## Aktueller Codebefund

- `ResponseManager` waehlt Pfade schon sichtbar, ist aber noch eher
  Response-Pfadlogik als echte Policy-Schicht
- `ResponseTextBuilder` muss an mehreren Stellen fehlende Zustandssemantik
  auffangen
- der Uebergang zwischen `continue`, `ask_followup`, `guide_next_step` und
  `recommend` ist noch nicht klein genug modelliert

## Sollzustand

- Response-Policy ist von finalem Wortlaut getrennt
- ein kleiner expliziter Transition-Zustand ersetzt die heutige starke
  Textidee `guide_next_step`
- Recommendation-Freigabe, Follow-up-Ende und Dialogfortschritt sind
  zustandsseitig nachvollziehbar

## Kernaufgaben

1. kleinen Zwischenzustand definieren:
   etwa Zielstatus, Transition-Status oder Antwortfreigabestatus
2. `ResponseManager` schrittweise Richtung expliziter Policy-Schicht
   schneiden
3. `ResponseTextBuilder` nur noch auf sichtbaren freigegebenen Zustand bauen
4. klaeren, wann ein Nutzerziel:
   offen,
   klaerungsbeduerftig,
   beantwortbar,
   oder erreicht
   ist

## Betroffene Dateien/Klassen

- `application/managers/response_manager.py`
- `application/services/response_text_builder.py`
- `application/services/recommendation_state_service.py`
- `models/domain/dialogue.py`
- `models/turn/context.py`

## Kleine Sofortfixes innerhalb dieses Blocks erlaubt

- klare Branch-Reihenfolgefehler
- Texte, die dem bereits vorhandenen Zustand direkt widersprechen

## Nicht innerhalb dieses Blocks still loesen

- neue Textbausteine als Ersatz fuer fehlende Zustandsobjekte
- Recommendation-Pfade ohne explizite Freigabegrammatik

## Block-Gate / Done

- Response-Policy und Antworttext sind sauberer getrennt
- `guide_next_step` ist entweder ersetzt oder klar in kleinerer Semantik
  verankert
- der Dialog behauptet im Text nicht mehr mehr Fortschritt als der Zustand
  traegt


## Block 5: Safety als echte Architekturachse ausbauen [spaeter]

## Ziel

Safety von Scaffold zu einer sichtbaren, mehrstufigen Schicht entwickeln.

## Warum jetzt nicht frueher

Safety braucht klare Eingangsvertraege.
Sonst baut sie nur weitere Heuristik auf unsaubere Uebergangsobjekte.

## Aktueller Codebefund

- `SafetyManager` erzeugt bisher vor allem Scaffold-States und Trace-Notizen
- die vorgesehene Dreistufe
  Rohnachricht,
  normalisierte Information,
  kanonischer Fallzustand
  ist architektonisch benannt, aber noch nicht fachlich eingelost

## Sollzustand

- echte Safety-Signale pro Ebene
- sichtbare Begrenzung, welche Schicht welche Safety-Entscheidung tragen darf
- Safety beeinflusst Policy, ersetzt sie aber nicht

## Kernaufgaben

1. minimale Safety-Semantik pro Ebene definieren
2. klare Eingangsobjekte fuer Raw-, Extraction- und Case-Safety festziehen
3. festlegen, welche Safety-Folgen direkt emergency sind und welche nur Gate-
   oder Follow-up-Folgen haben

## Betroffene Dateien/Klassen

- `application/managers/safety_manager.py`
- `models/turn/safety_state.py`
- spaeter angrenzend `response_manager.py`

## Block-Gate / Done

- Safety ist mehr als Trace-Scaffold
- die Schicht ist sichtbar und begrenzt statt diffuse Zusatzheuristik


## Block 6: Confirmation und bewusste Korrektur als eigener Pfad [spaeter]

## Ziel

Nutzerbestaetigung und Nutzerkorrektur als kontrollierten Truth-Eingang
modellieren, nicht als lose spaetere UI-Idee.

## Warum jetzt nicht frueher

Confirmation braucht:

- klarere Case-Truth-Semantik
- klareren Process-State
- klarere Response-Policy

## Aktueller Codebefund

- `ConfirmationManager` ist noch reiner Placeholder
- `DialogueManager` markiert nur
  `confirmation_path_not_implemented`

## Sollzustand

- es gibt einen klaren Ausloeser fuer Confirmation
- bestaetigte oder korrigierte Information geht kontrolliert zurueck in die
  Truth-Schicht
- Confirmation erzeugt keine parallele Schattenwahrheit im UI oder in
  Hilfsfeldern

## Kernaufgaben

1. definieren, wann Confirmation in Careena ueberhaupt sinnvoll ist
2. festlegen, welches Objekt bestaetigt oder korrigiert wird
3. Rueckweg in Case-Truth und DialogueState sauber modellieren

## Betroffene Dateien/Klassen

- `application/managers/confirmation_manager.py`
- `application/managers/dialogue_manager.py`
- `models/domain/dialogue.py`
- spaeter angrenzend Case-Truth-Pfad

## Block-Gate / Done

- Confirmation ist als echter Produktpfad benennbar
- der Rueckweg in die Wahrheitsschicht ist explizit


## Block 7: Kleine Signalgrammatik und Prompt-Komposition kontrolliert aufbauen [spaeter]

## Ziel

Die wertvolle Idee kleiner sichtbarer Signale und spaeterer Prompt-
Fragenbloecke kontrolliert ausbauen, ohne neue Flag-Buerokratie zu erzeugen.

## Warum jetzt nicht frueher

Diese Ebene ist stark, aber nur auf stabileren Kernvertraegen.
Sonst konserviert sie bloss heutige Unklarheit in noch mehr Signalschildern.

## Sollzustand

- Signale bleiben klein, generisch und wiederverwendbar
- es gibt eine disziplinierte Trennung zwischen:
  technischem Trace,
  operativem Arbeitssignal,
  Prozesssignal,
  medizinischer Wahrheit
- spaetere Prompt-Bloecke koennen explizite Skip- oder Fokus-Signale liefern,
  ohne neue Zweitlogik zu werden

## Kernaufgaben

1. minimale erlaubte Signaltypen definieren
2. `trace_notes`, `signals` und aehnliche Marken auf ihre Rolle pruefen
3. promptnahe Skip-Signale nur dort in den Turn-Vertrag heben, wo sie auch
   ausserhalb des Prompts architektonisch echt gebraucht werden

## Betroffene Dateien/Klassen

- `models/extraction/result.py`
- `models/turn/context.py`
- `models/domain/dialogue.py`
- `llm/prompts/case_extraction.py`
- `llm/context.py`

## Block-Gate / Done

- Signale helfen der Orchestrierung sichtbar
- sie tragen keine freie versteckte Gesamtlogik


## Block 8: Recommendation-Content und aeussere Integration spaet anschliessen [spaeter]

## Ziel

Recommendation, Call 3 und aeussere Runtime-/Serverpfade erst dann
ausbauen, wenn die Kernarchitektur dafuer stabil genug ist.

## Warum jetzt bewusst spaet

Recommendation ist in Careena kein frueher Default-Ausgang.
Ein zu frueher Ausbau wuerde die aktuellen Uebergangsschichten nur weiter
verhaerten.

## Sollzustand

- Recommendation ist ein bewusst freigegebener Pfad
- ein spaeterer Call 3 ist Inhaltsgenerator und nicht heimlicher
  Pfadentscheider
- `careena3.py`, Runtime und Simulation bleiben duenne Integrationshaeute

## Kernaufgaben

1. Recommendation-Freigabe auf stabilere Readiness- und Response-Policy
   stuetzen
2. spaeteren Call-3-Inputvertrag bewusst klein halten
3. Server-/Simulationseinstieg erst danach weiter ausduennen

## Betroffene Dateien/Klassen

- `application/services/recommendation_result_builder.py`
- `models/workflow/recommendation_result.py`
- `llm/call_control.py`
- `server/careena3.py`
- `bootstrap.py`
- `runtime.py`
- `simulation_runtime/*`

## Block-Gate / Done

- Recommendation ist klarer gestuft
- Integrationsschichten verdecken keine fachlichen Kernprobleme mehr


## Konkrete Startempfehlung

Wenn der Plan schrittweise abgearbeitet wird, ist der naechste
wahrscheinlich beste erste praktische Zug nicht sofort ein grosser Codeumbau,
sondern:

1. den endgueltig gewollten minimalen Call-2-Outputvertrag kurz als kleine
   Arbeitsfassung festziehen
2. direkt danach `llm/context.py`, `case_extraction.py` und
   `resilient_extraction_service.py` gegen diesen Vertrag sezieren
3. erst dann entscheiden, wie viel von `ExtractionResultMapper` /
   `MessageDelta` danach noch sinnvoll uebrig bleibt


## Schlussbewertung

Die Architekturmitte von Careena3 ist heute nicht mehr unklar, sondern nur
noch ungleichmaessig eingelost.

Der neue Fokus lautet deshalb nicht:

- moeglichst schnell mehr Verhalten anschrauben

sondern:

- die bereits erkennbare Zielarchitektur so weit festziehen, dass jede
  komplexere Erweiterung spaeter auf kleineren, klareren und ehrlicheren
  Verantwortungsbereichen aufsetzen kann

Die wichtigste Regel fuer die naechsten Schritte lautet daher:

- zuerst Rollen, Wahrheitsgrenzen und Uebergangsvertraege sauberziehen,
  danach erst groessere neue Dialog- oder Recommendation-Intelligenz
  ausbauen.
