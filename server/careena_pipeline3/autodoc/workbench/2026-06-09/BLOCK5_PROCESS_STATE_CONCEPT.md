# Block-5-Konzept: Process-State, Follow-up und Readiness

Stand: 2026-06-10
Status: Entwurf
Bezug:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `application/services/dialogue_state_service.py`
- `domain/requirement_policy.py`
- `application/services/recommendation_state_service.py`
- `models/turn/state_updates.py`
- `models/domain/dialogue.py`


## Zweck

Dieses Konzept bereitet den naechsten Refactor-Schritt fuer Block 5 vor,
ohne den Code schon umzubauen.

Der Fokus liegt bewusst auf den V3-Regeln oberhalb der Refactor-Bloecke:

- boundary first
- behavior over names
- lieber sichtbare Uebergangsvertraege als unsaubere Scheinfertigstellung
- sichtbare Orchestrierung statt versteckter Prozessmagie


## Ausgangslage

Die Bloecke 1 bis 4 sind im aktuellen Stand weit genug fortgeschritten:

- der `DialogueManager` ist als sichtbare Turn-Orchestrierung lesbar
- die Bridge-Zone wurde verkleinert
- `Call 1` liefert kleinere Signale
- `Call 2` wurde kontextseitig und vertraglich enger

Der aktuell wichtigste offene Rest liegt jetzt in der Prozess-/Gate-Zone
zwischen:

- `DialogueStateService`
- `RequirementPolicy`
- `RecommendationStateService`

Genauer:

- dieselbe Nachricht kann gleichzeitig
  eine offene Rueckfrage beantworten
  und neue medizinische Information einbringen
- der aktuelle Ablauf behandelt diesen Mischfall noch nicht als zwei
  kombinierbare Spuren
- dadurch bleiben Requirements teils kuenstlich offen oder werden mit
  zusaetzlicher neuer Information unsauber vermischt


## V3-Lesart des Problems

Das Hauptproblem ist nicht zuerst eine "fehlende Spezialregel".

Das Hauptproblem ist:

- Prozessfortschritt,
- Requirement-Erfuellung
- und zusaetzlicher medizinischer Informationszuwachs

werden noch nicht als getrennte Wahrheitsarten sichtbar gemacht.

Dadurch drohen zwei schlechte Effekte:

1. der `DialogueState` traegt implizite Reparaturarbeit
2. `Readiness` liest Seiteneffekte statt klarer Prozessresultate


## Zielbild

Block 5 soll die Schicht lesbarer trennen in:

1. Case Truth
2. Process State
3. Requirement Resolution
4. Readiness / Gate

Wichtig ist dabei:

- Requirement-Erfuellung bleibt an sichtbarer Case-Wahrheit verankert
- Follow-up-Erfuellung ist ein Prozessereignis
- neue medizinische Information bleibt Case-seitig lesbar
- Readiness liest nur das stabilisierte Ergebnis dieser beiden Spuren


## Explizite Schutzregel

Dieses Konzept fuehrt bewusst noch keine neue komplexe Heuristik ein.

Insbesondere soll Block 5 nicht:

- `Call 1` wieder aufblasen
- `Call 2` mit Prozesspolitik beladen
- `RecommendationStateService` zur Reparaturstelle machen
- offene Probleme durch mehr Text- oder Flag-Magie kaschieren


## Konkreter Mischfall

Beispiel:

- Assistenz fragt: `Seit wann besteht die Beschwerde?`
- Nutzer antwortet: `seit gestern und fieber hab ich auch`

Darin stecken gleichzeitig:

- Follow-up-Antwort auf `duration_or_onset`
- neue medizinische Information: neues Symptom oder zusaetzlicher Claim

Architektonisch sollen diese Anteile nicht gegeneinander ausgespielt werden.

Stattdessen braucht der Turn sichtbar zwei parallele Lesarten:

- Prozessspur: die Rueckfrage wurde beantwortet
- Case-Spur: neue medizinische Information ist hinzugekommen


## Gewuenschte minimale Vertragsklaerung

Der naechste Refactor sollte einen kleinen expliziten
prozessnahen Ergebnisvertrag einfuehren oder vorbereiten.

Dieser Vertrag soll nicht alles koennen.
Er soll nur sichtbar machen, was bisher implizit ineinanderlaeuft.

Minimal benoetigte Aspekte:

- welche Follow-up-Frage in diesem Turn beantwortet wurde
- ob die Antwort zur offenen Rueckfrage passt
- ob zugleich neue medizinische Information vorliegt
- welche Requirements dadurch faktisch geschlossen sind
- ob dieselbe Nachricht noch weitere offene Requirements erzeugt


## Empfohlene neue Verantwortungsschnitte

### 1. `RequirementPolicy`

Soll staerker bleiben:

- Requirement-Katalog
- resolved vs open requirements
- pending follow-up aus sichtbarer Case-Wahrheit

Soll nicht zusaetzlich werden:

- Detektor fuer freie Dialogakte
- Parser fuer Mischturns
- Readiness-Reparaturstelle

Kurz:
`RequirementPolicy` bleibt eine Truth-nahe Requirement-Policy,
nicht ein Dialog-Interpretationszentrum.


### 2. `DialogueStateService`

Soll die primaere Process-State-Schicht werden fuer:

- sichtbare Prozessfortschreibung nach Case-Update
- Verknuepfung von pending follow-up und aktuellem Turn
- explizite Behandlung des Mischfalls

Soll nicht:

- selbst medizinische Wahrheit erfinden
- finale Readiness-Entscheidung treffen

Kurz:
Wenn Block 5 einen neuen kleinen Ergebnisvertrag braucht, ist
`DialogueStateService` der naheliegendste Ort dafuer.


### 3. `RecommendationStateService`

Soll lesbar bleiben als:

- reine Gate-/Readiness-Schicht

Soll nicht:

- Prozessluecken still schliessen
- Follow-up-Interpretation uebernehmen
- neue Requirement-Bedeutung erzeugen

Kurz:
`RecommendationStateService` soll die bereits sauber getrennten Spuren lesen,
nicht sie erst erzeugen.


## Empfohlene kleine Uebergangsobjekte

Noch kein finales Naming erzwingen.
Behavior first.

Trotzdem ist fuer Block 5 ein kleines sichtbares Ergebnisobjekt sinnvoll.

Arbeitsname:

- `FollowupProgress`
  oder
- `ProcessInterpretation`

Minimaler Inhalt:

- `answered_pending_followup: bool`
- `answered_requirement_key: str | None`
- `answered_slot: str | None`
- `answer_matches_focus: bool`
- `contains_additional_medical_information: bool`
- `trace_notes`

Optional spaeter:

- `staged_followup_answer`
- `closed_requirements`
- `remaining_open_requirements`

Wichtig:
Dieses Objekt soll keine neue medizinische Zweitwahrheit sein.
Es beschreibt nur den Prozesswert des aktuellen Turns.


## Beziehung zu bestehenden Modellen

Der aktuelle Code hat bereits kleine Ergebnisvertraege:

- `ProcessStateUpdate`
- `ReadinessStateUpdate`

Das ist gut und passt zu V3.

Naechste sinnvolle Bewegung:

- `ProcessStateUpdate` nicht nur als "mutierter DialogueState plus pending"
  lesen
- sondern um einen kleinen expliziten Prozessfortschritts-Baustein ergaenzen
  oder vorbereiten

Dadurch muesste der `DialogueManager` weniger implizit raten, was im Turn
prozessual eigentlich passiert ist.


## Vorschlag fuer die Reihenfolge des eigentlichen Refactors

### Schritt 1

In `DialogueStateService` den Mischfall als eigene sichtbare Rolle benennen.

Noch ohne grosse Logikexplosion.
Erst der Vertrag.

### Schritt 2

Kleines Prozess-Ergebnisobjekt einfuehren oder `ProcessStateUpdate` minimal
erweitern.

Ziel:

- beantwortete Rueckfrage sichtbar machen
- zusaetzliche neue Information sichtbar koexistieren lassen

### Schritt 3

`RequirementPolicy` nur noch die Requirement-Sicht rechnen lassen.

Keine neue Turn-Interpretation dort hineinziehen.

### Schritt 4

`RecommendationStateService` auf die stabilisierte Prozess-/Requirement-Wahrheit
setzen und bewusst dumm halten.

### Schritt 5

Erst danach Sim-/Laufverhalten pruefen:

- wiederholte Rueckfrage verschwindet
- neue Information geht nicht verloren
- Readiness kippt nicht durch verdeckte Seiteneffekte


## Was in diesem Schritt bewusst noch nicht geloest wird

- die endgueltige Pflichtfelddefinition pro Observation-Typ
- feinere Konflikt- oder Unsicherheitsobjekte
- neue komplexe `Call 1`-Signalsprache
- ein tiefer Umbau von `ResponseManager`
- Confirmation-Ausbau

Das ist Absicht.
Block 5 soll zuerst die Grenze klaeren, nicht das ganze System gleichzeitig
perfektionieren.


## Vorlaeufige Arbeitsentscheidung

Fuer den kommenden Refactor behandeln wir den Block-5-Kern so:

- `RequirementPolicy` bleibt truth-nah
- `DialogueStateService` wird zur sichtbaren Process-State-Verdichtung
- Mischturns werden dort als eigene Prozessrealitaet explizit gemacht
- `RecommendationStateService` bleibt abgeleitete Gate-Schicht

Der erste Erfolg ist damit nicht perfekte Fachlogik,
sondern eine klarere Prozessgrenze.


## Definition von Erfolg fuer den naechsten Schritt

Der naechste Code-Schritt ist bereits gut, wenn danach klarer ist:

- wo Follow-up-Erfuellung entschieden wird
- wo neue medizinische Zusatzinformation parallel dazu sichtbar bleibt
- wo Requirements auf Basis von Case-Wahrheit geschlossen werden
- dass `Readiness` diese Spuren nur noch liest statt repariert

Wenn das erreicht ist, ist Block 5 sauber eroeffnet, auch wenn die Fachlogik
noch nicht voll ausgebaut ist.
