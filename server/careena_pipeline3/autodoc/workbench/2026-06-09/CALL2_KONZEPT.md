# Careena3 Call 2 Konzept

Stand: 2026-06-10
Status: Arbeitsfassung fuer Block 4

Baut auf:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `autodoc/workbench/2026-06-08/CAREENA3_PHASE2_CALL2_PROPOSAL.md`
- `autodoc/workbench/2026-06-08/CAREENA3_PHASE2_CALL2_PROPOSAL_REVISED.md`


## Zweck

Dieses Dokument zieht aus:

- dem neuen Block-3-Call-1-Vertrag
- dem aktuellen Codezustand
- und den aelteren Call-2-Proposals

einen neuen arbeitsnahen Block-4-Zuschnitt fuer `Call 2`.

Es ist bewusst kein Endentwurf fuer die spaetere Vollarchitektur.
Es soll vor allem:

- den aktuellen Ist-Zustand sauber benennen
- die Zielrolle von `Call 2` nach dem neuen `Call 1` festziehen
- und den naechsten echten Refactor-Schnitt vorbereiten


## Kurzfassung

`Call 2` soll in Careena3 kein breiter Fall-Rekonstruktionscall sein.

Er soll:

- anhand des neuen Scout-/Dispatch-Vertrags aus `Call 1`
- die aktuelle Nachricht gezielt lesen
- kleine medizinische Claims oder Updates liefern
- und dabei moeglichst wenig Kontext und moeglichst wenig implizite
  Nebenpolitik tragen

Der aktuelle Code ist dafuer noch nicht sauber genug.

Im Ist-Zustand ist `Call 2` noch immer:

- ein einzelner breiter Extraktionscall
- plus ein zweiter LLM-Schritt, der praktisch eher ein weiterer
  Extraktions-/Re-Emissionspass als ein enger Normalizer ist
- plus eine Python-Sammelschicht in `ResilientExtractionService`,
  die Fehlergrenze, Follow-up-Reparatur und Rest-Normalisierung zugleich traegt

Deshalb ist der naechste saubere Hebel:

- zuerst den kuenftigen Call-2-Vertrag explizit machen
- dann den Inputkontext hart verkleinern
- dann den Aufgabenmix im primaeren Call sichtbar schneiden
- und erst danach den aktuellen Output-/Normalizer-Pfad ablösen


## 1. Block-4-Lesart nach dem neuen Call 1

Seit dem Block-3-Schnitt liefert `Call 1` jetzt gruppierte Signale:

- `entry_signals`
- `dispatch_signals`
- `case_hints`
- `dialogue_hints`
- `safety_hints`

Damit verschiebt sich die Rolle von `Call 2` klarer:

- `Call 1` scoutet und verteilt
- `Call 2` arbeitet

Wichtige Folge:

- `Call 2` muss weniger selbst rekonstruieren, was fuer ein Turn das ist
- `Call 2` soll staerker als konfigurierbarer Werkzeugkasten lesbar werden
- `Call 2` soll nicht noch einmal dieselbe fruehe Einordnung in einem breiten
  Kontextpaket implizit neu bauen muessen


## 2. Aktueller Ist-Zustand von Call 2

## 2.1 Aktive Codekante

Heute laeuft `Call 2` grob ueber:

- `application/managers/extraction_manager.py`
- `llm/case_extraction_extractor.py`
- `llm/context.py`
- `application/services/resilient_extraction_service.py`
- `llm/extraction_result_normalizer.py`

## 2.2 Sichtbare Probleme im Ist-Zustand

### A. Der primaere Input ist noch zu breit

`build_case_extraction_input(...)` gibt aktuell u. a. mit:

- `call2_tasks`
- `operation_mode`
- `target_scope`
- `allow_new_observations`
- `focus_observation_id`
- `focus_label`
- `focus_type`
- `last_assistant_question`
- `case_summary`
- `dialogue_summary`

Problem:

- mehrere Steuerarten liegen doppelt oder ueberlappend vor
- `case_summary` und `dialogue_summary` sind fuer den primaeren Call noch zu
  breit
- `Call 2` bekommt damit weiter Gelegenheit, Kontext als Zweitwahrheit zu lesen

### B. Der primaere Output ist noch zu breit und transitional

Heute liefert der aktive Call weiter `ExtractionResult`.

Das ist fuer den momentanen Codepfad noch brauchbar, aber als Zielvertrag zu
schwer.

Problem:

- `ExtractionResult` ist noch eher turn- und pipelineorientiert als
  klein-claim-orientiert
- die aktuelle Struktur ist naeher an einem Uebergangsarbeitsmodell als an
  einem kleinen dauerhaften Call-2-Vertrag

### C. Der zweite LLM-Schritt ist kein echter kleiner Normalizer

`LLMExtractionResultNormalizer` bekommt:

- breiten Kontrollkontext
- das komplette `initial_extraction_result`
- und soll wieder ein volles `ExtractionResult` ausgeben

Problem:

- das ist strukturell naeher an einem zweiten Extraktionspass
  als an enger Normalisierung

### D. `ResilientExtractionService` ist noch zu sehr Sammelklasse

Dort kleben aktuell zusammen:

- Fehlergrenze
- Subject-/Question-Bereinigung
- optionaler zweiter LLM-Schritt
- Follow-up-Slot-Reparatur in Python

Problem:

- genau diese Mischrolle ist nach V3 ein Warnsignal


## 3. Zielrolle von Call 2

`Call 2` soll:

- die aktuelle Nachricht medizinisch lesen
- den von `Call 1` vorgegebenen Arbeitsmodus respektieren
- nur die angeforderten Aufgabenbereiche bearbeiten
- kleine Claims oder Updates liefern
- Unsicherheit sichtbar lassen

`Call 2` soll nicht:

- einen breiten Fallzustand neu materialisieren
- Readiness, Response oder Merge-Semantik selbst entscheiden
- einen grossen zweiten LLM-Schritt zur Ergebnis-Re-Emission brauchen
- diffuse Kontrollsprachen aus mehreren Feldern gleichzeitig aufloesen muessen


## 4. Arbeitsmodell fuer Call 2

Die Kernidee fuer Careena3 lautet:

- ein primaerer Call
- mehrere kleine Aufgabenbereiche
- ein enger konfigurierbarer Input
- ein kleinerer Output

Das ist kein Mehr-Call-Zwang.

Es bedeutet nur:

- auch wenn heute technisch noch ein Call laeuft,
  soll der Vertrag intern schon wie ein Werkzeugkasten lesbar sein


## 5. Sinnvolle Aufgabenbereiche fuer Call 2

Diese Bereiche erscheinen im aktuellen Stand am sinnvollsten.

## 5.1 `subject_resolution`

Rolle:

- betroffene Person nur dann aufloesen, wenn `Call 1` das wirklich fordert
  oder wenn es fuer die aktuelle Nachricht fachlich noetig ist

Warum:

- Personenbezug ist eigene Arbeit und sollte nicht implizit mitten in normaler
  Symptomextraktion verschwinden

## 5.2 `focus_update`

Rolle:

- wenn ein Follow-up-Kontext aktiv ist:
  pruefen, ob die aktuelle Nachricht primaer ein Update auf den offenen Fokus
  ist

Warum:

- genau hier sitzt heute viel Mischlogik aus Follow-up-Deutung,
  Slot-Update und spaeter Python-Reparatur

## 5.3 `additional_new_info`

Rolle:

- neben einem Fokus-Update klar getrennte neue medizinische Information als
  eigene kleine Claims liefern

Warum:

- heute ist dieser Fall mit dem Fokus-Update zu stark vermischt

## 5.4 `open_question_check`

Rolle:

- knapp markieren, was im angefragten Bereich trotz aktueller Nachricht offen
  bleibt

Warum:

- offene Fragen sollen nicht nur Nebenprodukt eines grossen JSON sein

## 5.5 spaeter optional `object_conflict_resolution`

Rolle:

- bei zwei kleinen konkurrierenden Eintraegen eine enge Konfliktdeutung
  unter Guardrails treffen

Warum:

- dafuer koennte spaeter ein enger LLM-Hilfsschritt sinnvoll sein
- das gehoert aber nicht in den primaeren Block-4-Schnitt


## 6. Geplanter Inputvertrag fuer den primaeren Call 2

## Muss bleiben

- `latest_user_message`
- `call2_tasks`
- `operation_mode`
- `last_assistant_question` nur wenn vorhanden
- `pending_slot` nur wenn vorhanden

Warum:

- das sind die kleinsten noetigen Arbeits- und Interpretationssignale

## Nur bei Fokus-/Follow-up-Bedarf

- `focus_observation`

Vorgeschlagene kleine Form:

```json
{
  "type": "symptom",
  "label": "Bauchschmerz",
  "concept": "abdominal_pain",
  "attributes": {
    "body_site": "abdomen",
    "temporality": "acute",
    "severity": 6
  }
}
```

Wichtig:

- kein voller Beobachtungszustand
- keine interne technische ID
- nur das, was fuer die Deutung des aktuellen Turns wirklich noetig ist

## Optional nur wenn wirklich noetig

- `relevant_existing_observations`

Nur dann, wenn:

- Duplikatvermeidung oder Einordnung gegen bestehende Eintraege sonst nicht
  sauber moeglich ist

## Sollte aus dem primaeren LLM-Input raus

- `target_scope`
- `allow_new_observations`
- `focus_observation_id`
- breite `case_summary`
- breite `dialogue_summary`
- `active_problem_ids`
- `recommended_modules`
- breite `open_requirements`

Begruendung:

- zu viel doppelte Steuerung
- zu viel Rauschen
- zu hohe Zweitwahrheitsgefahr


## 7. Geplanter Outputvertrag fuer den primaeren Call 2

Der primaere Output sollte nicht mehr als breites `ExtractionResult`
gedacht werden.

Zielrichtung:

- kleine Claims
- kleine Update-Signale
- kleine offene Fragen

Vorschlag:

```json
{
  "subject_update": {
    "relation": "self"
  },
  "focus_update": {
    "observation_type": "symptom",
    "label": "Bauchschmerz",
    "concept": "abdominal_pain",
    "attributes": {
      "temporality": "seit gestern"
    }
  },
  "new_items": [
    {
      "observation_type": "symptom",
      "label": "Uebelkeit",
      "concept": "nausea",
      "attributes": {}
    }
  ],
  "open_questions": [],
  "trace_notes": [
    "resolved followup and found additional symptom"
  ]
}
```

Wichtige Lesart:

- `focus_update` ist nicht dieselbe Kategorie wie `new_items`
- genau diese Trennung ist fuer spaetere Merge-/Truth-Logik wertvoll


## 8. Rolle von `profile`

Ein kleines `profile` aus `Call 1` ist okay, aber nur als Nebenanker.

Es sollte:

- keine zweite grosse Steuergrammatik werden
- nicht `call2_tasks` und `operation_mode` ersetzen
- und vorerst nur klein bleiben

Aktuell sinnvoll:

- `profile: default`

Spaeter eventuell:

- `profile: followup_heavy`
- `profile: social_only`
- `profile: recommendation_transition`

Aber:

- erst wenn sich dafuer wirklich stabile Unterschiede zeigen


## 9. Rolle von Python vs. Rolle des LLM

## Sollte eher Python machen

- banale Ableitungen aus `operation_mode`
- Leer-/Unknown-Bereinigung
- triviale Alias- oder Feldsaeuberung
- Routing kleiner Outputs in die passende Weiterverarbeitung

## Sollte das LLM eher machen duerfen

- kleine Claim-Bildung aus Freitext
- enge Deutung eines Fokus-Updates
- Erkennen zusaetzlicher neuer Information in demselben Turn
- kleine offene-Fragen-Markierung

Nicht sinnvoll als Zielbild:

- denselben Output noch einmal als volles `ExtractionResult` neu schreiben
  lassen


## 10. Naechster konkreter Refactor-Schnitt

Aus diesem Konzept ergibt sich fuer Block 4 diese sinnvolle Reihenfolge:

1. `llm/context.py` fuer den primaeren Call-2-Input hart verkleinern
2. den primaeren Call-2-Prompt explizit nach
   `subject_resolution`, `focus_update`, `additional_new_info`,
   `open_question_check` lesbar machen
3. einen kleineren primaeren Outputvertrag modellieren
4. `ExtractionManager` und den Mapper auf diesen kleineren Output ausrichten
5. erst dann den heutigen grossen zweiten LLM-Normalizer gezielt ablösen


## 11. Entscheidung fuer jetzt

Fuer den aktuellen Stand ist es sinnvoller,

- zuerst diesen Call-2-Zuschnitt explizit festzuhalten

als sofort blind den ganzen aktiven Call-2-Pfad umzubauen.

Warum:

- der neue Block-3-Call-1-Vertrag ist frisch
- der Call-2-Ist-Zustand hat noch mehrere Uebergangslasten
- und ohne expliziten Zielvertrag wuerde der Umbau leicht wieder in lokale
  Reparaturschnitte kippen


## Verdichtetes Fazit

`Call 2` ist in Careena3 am besten als konfigurierbarer Werkzeugkasten zu
lesen.

Konfiguriert wird er durch `Call 1`.
Arbeiten soll er aber nur auf:

- der aktuellen Nachricht
- kleinen expliziten Arbeitsmodi
- kleinen Aufgabenbereichen
- und einem moeglichst engen medizinischen Outputvertrag

Der naechste richtige Schritt ist deshalb:

- nicht sofort den ganzen Pfad umwerfen
- sondern den kleinen dauerhaften Call-2-Input-/Outputvertrag aus diesem
  Konzept jetzt praktisch schneiden
