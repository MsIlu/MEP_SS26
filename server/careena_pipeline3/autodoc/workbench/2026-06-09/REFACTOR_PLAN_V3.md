# Careena3 Refactor Plan V3

Stand: 2026-06-09
Status: aktiv
Baut auf:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN.md`
- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V2.md`
- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `autodoc/workbench/2026-06-08/TARGET_MODEL6.md`


## Zweck

Diese dritte Fassung behaelt die Boundary-First-Praezision aus `V2`, bewertet
die Reihenfolge aber neu.

Der zentrale neue Entscheid lautet:

- nicht zuerst `Call 2` isoliert perfektionieren
- sondern zuerst die sichtbaren Systemgrenzen vom `DialogueManager` aus nach
  unten sauberziehen
- dabei das heutige haessliche Uebergangsobjekt voruebergehend bewusst
  mittragen, solange es als klar markierter Bridge-Vertrag dient
- danach `Call 2` und seine Kontexte auf schon stabileren Grenzen enger
  zuschneiden

V3 ist damit staerker:

- orchestrierungsorientiert
- grenzorientiert
- naming-skeptisch
- und bewusster darin, vorhandene Uebergangsobjekte erst dann abzuloesen,
  wenn ihre Umgebung sauber genug dafuer ist


## Quellenbasis und Gewichtung

Hoechste Gewichtung:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V2.md`
- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `autodoc/workbench/2026-06-08/TARGET_MODEL6.md`

Mittlere Gewichtung:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN.md`
- `autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
- `autodoc/workbench/2026-06-08/CODE_REVIEW_FRAMEWORK.md`

Niedrigere Zusatzgewichtung:

- `autodoc/workbench/2026-06-08/GENERAL_CODE_ARCHITECTURE_GUIDELINES.md`

Warum niedriger:

- die Datei ist nuetzlich und konsistent
- sie doppelt aber vieles, was in `SYSTEM_OVERVIEW.md`, `TARGET_MODEL6.md`,
  `CODE_REVIEW_FRAMEWORK.md` und `V2` bereits konkreter auf Careena3
  zugespitzt ist


## Was aus der Guidelines-Datei zusaetzlich mitgenommen wird

Mit niedrigerer, aber sinnvoller Gewichtung fliessen vor allem diese Punkte
ein:

- zentrale Orchestrierung ist wertvoll, wenn Gesamtentscheidungen sichtbar an
  einem Ort zusammenlaufen
- Unterkomponenten sollen Ergebnisse und Signale liefern, aber keine
  versteckten Gesamtentscheidungen
- Extraktion, Interpretation, Normalisierung, Zustand und Ausgabe sind
  verschiedene Verantwortungen
- textliche Antwort darf fehlende Semantik nicht kaschieren
- eine Serviceklasse, die Fallbacks, Reparaturen, Mapping und Sonderregeln
  sammelt, ist ein Warnsignal
- Kontextpakete wachsen typischerweise, wenn Kernvertraege zu unscharf sind
- Refactoring sollte Uebergangsprothesen abbauen, nicht sie nur eleganter
  verstecken


## Neuer Hauptentscheid zur Reihenfolge

## Bewertung der Reihenfolgefrage

Interne Entscheidung fuer V3:

- zuerst sichtbare Systemgrenzen vom `DialogueManager` aus nach unten
  festziehen
- das aktuelle Call-2-/Bridge-Ergebnisobjekt vorerst als bewusst markierten
  Transitional Contract behalten
- erst danach `Call 2` selbst enger und kleiner schneiden

## Warum diese Reihenfolge sinnvoller ist

Der aktuelle Code zeigt:

- `DialogueManager` ist bereits reale Orchestrierungsmitte
- `MessageDelta` ist haesslich, aber als Bridge schon explizit als
  transitional markiert
- mehrere Folgeschichten lesen heute noch direkt oder indirekt diese
  Bridge-Verkabelung
- wenn `Call 2` sofort neu gebaut wird, bevor die Systemgrenzen darunter und
  darueber sauber sind, droht die neue Extraction erneut in alte unsaubere
  Anschlussstellen zu kippen

Deshalb ist V3 bewusst konservativer:

- erst Schichtgrenzen
- dann Bridge sauber begrenzen
- dann `Call 2`
- dann spaetere Policy- und Ausbaupfade


## Naming-Regel fuer den Refactor

Eine wichtige neue Arbeitsregel lautet:

- Verhalten ist wichtiger als Benennung

Der aktuelle Code und auch `SYSTEM_OVERVIEW.md` zeigen bereits, dass mehrere
Namen irrefuehrend oder historisch verrutscht sind.

Beispielrichtung:

- `subject` klingt kleiner und klarer, als die tatsaechliche fachliche Rolle
  derzeit ist
- `ResponseManager` ist teils noch Policy, teils Pfadwahl, nicht nur
  "Response"
- `MessageDelta` klingt kleiner, traegt aber aktuell mehrere Signalarten
- manche `signals` oder `modules` koennen semantisch mehrdeutig sein

## Praktische Naming-Regel

Waehren des Refactors gilt:

1. zunaechst nach realem Verhalten urteilen, nicht nach dem Namen
2. Verantwortung erst sauber schneiden
3. erst danach umbenennen, wenn die neue Rolle stabil genug ist

Nicht sinnvoll waere:

- fruehe Cosmetic-Renames, waehrend die Schicht selbst noch unklar ist

Sinnvoll ist:

- Rename als spaeterer Klarstellungsschritt, wenn ein Modul oder Attribut
  bereits vertraglich enger geworden ist


## Zielbild von V3

Careena3 soll schrittweise in klar erkennbare Ebenen auseinandergezogen
werden:

1. sichtbare Orchestrierung
2. kleine Entry-Signale
3. Extraction als begrenzter Claim-Lieferant
4. klare Truth-Fortschreibung
5. Process-State als Prozessspur
6. abgeleitete Gate-/Readiness-Wahrheit
7. Response-Policy
8. finaler Text
9. spaeter Safety-, Confirmation- und Recommendation-Ausbau

Die wichtigste Schutzregel bleibt:

- keine Schicht soll still mehr entscheiden, als ihr Vertrag hergibt


## Aktuelle Code-Einordnung in V3

| Element | V3-Lesart | Hauptproblem | V3-Bewegung |
|---|---|---|---|
| `DialogueManager` | guter sichtbarer Systemkern | traegt noch Uebergangsverkabelung ueber `message_delta` und Rest-Signale | zuerst seine Systemgrenzen und Ein-/Ausgaenge schaerfen |
| `EntryManager` | brauchbarer frueher Signallieferant | kleine Signale und spaetere Bedeutung sind noch nicht immer sauber getrennt | nach Orchestrierungsgrenze enger an kleine Steuersignale binden |
| `ExtractionManager` | aktuell Mischung aus Delegation und Bridge-Weiterreichung | haengt noch am `MessageDelta`-Pfad und Modul-Nachzug | nach Boundary-Schnitt als kleinere Extraction-Fassade lesen |
| `MessageDelta` | haessliches, aber gerade nuetzliches Transitional Object | traegt mehrere Signalzonen gleichzeitig | vorerst bewusst mitschleppen, aber enger markieren und spaeter abbauen |
| `ExtractionResultMapper` | adapterhafte Problemverdichtung | mischt Claims, Requirements und Signaluebersetzung | nach Boundary-Schnitt gezielt verkleinern |
| `ResilientExtractionService` | Sammelstelle fuer zu viele Restprobleme | Fehlergrenze, LLM-Normalisierung und Follow-up-Reparatur zugleich | nach Boundary-Schnitt in klarere Teilrollen schneiden |
| `CaseStateManager` / `CaseMergePolicy` / `CaseMerger` | staerkste reale Architekturmitte | Truth-Mitte gut, aber Umgebung noch unsauber angeschlossen | erhalten und als Zielanker fuer angrenzende Grenzen nutzen |
| `DialogueStateService` / `RequirementPolicy` / `RecommendationStateService` | Prozess- und Gate-Mischzone | Requirement, Process-State und Gate sind noch nicht fein genug getrennt | nach Truth- und Boundary-Schnitt neu ordnen |
| `ResponseManager` / `ResponseTextBuilder` | Policy-Text-Mischzone | Text kaschiert noch fehlende Zustandssemantik | spaeter explizit trennen |
| `SafetyManager` / `ConfirmationManager` | erlaubte Placeholder-Schichten | architektonisch vorgesehen, praktisch noch schwach | bewusst spaeter, aber sauber markiert ausbauen |


## V3-Leitprinzipien

## 1. Boundary first, not feature first

Grenzen werden zuerst geklaert, bevor Fachlogik weiterwuchert.

## 2. Orchestration first, then deeper layers

Die Reihenfolge folgt dem realen Turn-Fluss:

- `DialogueManager`
- angrenzende Manager-Grenzen
- Bridge-Vertrag
- `Call 2`
- tiefere Policy-Schichten

## 3. Transitional objects duerfen temporaer bleiben

Ein haessliches Objekt darf voruebergehend bleiben, wenn es:

- klar als transitional markiert ist
- Grenzen stabilisiert statt verwischt
- spaetere echte Ablosung vorbereitet

## 4. Behavior over names

Was der Code tut, ist wichtiger als wie etwas heisst.

## 5. Kommentare duerfen Unfertigkeit benennen

Sichtbare Placeholder- oder Dummy-Logik ist erlaubt, wenn sie:

- die Schicht schuetzt
- kommentiert ist
- keine falsche Reife vortaeuscht

## 6. Developer-Hints aus `SYSTEM_OVERVIEW.md` sind erlaubt

Die Kommentare in der Overview sollen nicht als harte Wahrheit behandelt
werden, aber als wertvolle Arbeits-Hints in den passenden Bloecken.


## Dokumentationsregel in V3

Wenn ein Modul semantisch umgeschnitten wird, soll eine kleine strukturierte
Modul-Dokumentation mitlaufen oder aktualisiert werden.

Bevorzugte Minimalinhalte:

- Rolle
- Eingangsvertrag
- Ausgangsvertrag
- was das Modul explizit nicht entscheidet
- ob es noch transitional ist

Wenn ein Name offensichtlich irrefuehrend ist, aber noch nicht umbenannt
wird, darf eine kurze Dokuzeile das explizit benennen.

Beispiel:

- `Subject` ist aktuell historisch benannt; fachlich geht es hier um den
  betroffenen Personenbezug und nicht bloss um ein kleines Nebenfeld


## Neue globale Reihenfolge

1. sichtbare Systemgrenzen rund um den `DialogueManager` festziehen
2. die aktuelle Bridge-Zone bewusst begrenzen und temporaer stabil halten
3. erst dann `Call 1` / `Call 2` / Kontextpolitik enger schneiden
4. danach Requirement-, Follow-up- und Readiness-Schicht sauberer trennen
5. danach Response-Policy und finalen Text entkoppeln
6. Safety und Confirmation als saubere, vorerst auch placeholderhafte
   Schichten vorbereiten
7. spaetere kleine Signalgrammatik und Prompt-Komposition auf diese Grenzen
   aufbauen
8. Recommendation-Content, Call 3 und aeussere Integration zuletzt ausbauen


## Block 0: Boundary-First-Arbeitsvertrag [aktiv]

## Ziel

Den Refactor so fuehren, dass Grenzdefinition als echter Fortschritt gilt.

## Zusatzausfuehrung

Ein Schritt ist bereits gut, wenn:

- eine Grenze klarer ist
- eine Sammelklasse enger wird
- ein Restproblem sauber eingegrenzt wird
- ein Placeholder versteckte Logik ersetzt

## V3-Schutzregel

Keine fruehe Loesung ist besser als eine spaetere saubere Loesung, wenn die
fruehe Loesung die Grenze wieder verwischt.


## Block 1: DialogueManager-Grenzen und Turn-Vertraege festziehen [hoechste Prioritaet]

## Ziel

Den `DialogueManager` explizit als Souveraenitaetsstelle behandeln und seine
Vertraege zu den Unterkomponenten klarer machen.

## Warum jetzt zuerst

Der reale Turn laeuft heute bereits dort zusammen.
Wenn diese Grenze unscharf bleibt, wird jeder tiefere Refactor wieder gegen
eine instabile Orchestrierung arbeiten.

## Aktueller Codebefund

- `DialogueManager` orchestriert sichtbar
- traegt aber noch Uebergangsweitergaben wie:
  `message_delta`-abhaengige Recommendation-Signale,
  Follow-up-Weiterreichung,
  Placeholder-Confirmation,
  und mehrere direkte State-Mutationen im Turn-Kontext

## Sollzustand

- der `DialogueManager` bleibt zentral
- aber seine Ein- und Ausgaenge zu den Untermanagern werden expliziter
- jede Unterkomponente liefert kleine klar lesbare Ergebnisse
- der `DialogueManager` muss weniger wissen, welche historische Altform ein
  Zwischenobjekt intern gerade noch hat

## Kernaufgaben

1. die Turn-Sequenz als bewussten Vertrag lesen:
   Entry,
   Extraction,
   Case Truth,
   Process State,
   Readiness,
   Safety,
   Response
2. sichtbare Ergebnisobjekte pro Grenzschritt pruefen
3. direkte Altverkabelung im `DialogueManager` benennen und schrittweise
   reduzieren
4. Modul-Doku des `DialogueManager` bei Rollen- oder Vertragsklarstellung
   nachziehen

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- der `DialogueManager` ist die zentrale Souveraenitaetsstelle
- er soll koordinieren, aber moeglichst keine versteckten Gesamtentscheidungen
  treffen
- wie weit er spaeter entlastet wird, bleibt offen, solange Untervertraege
  noch nicht stabil genug sind

## Block-Gate / Done

- der Turn-Fluss ist klarer als vorher
- die Grenze zwischen Orchestrierung und Unterentscheidung ist sichtbarer
- historische Direktverkabelung ist reduziert oder wenigstens bewusst markiert

### Stand 10-06-26 [bearbeitet]

- der `DialogueManager` liest den Turn jetzt sichtbar als Folge kleinerer
  Vertragsstufen:
  Entry -> Extraction -> Case Truth -> Process State -> Readiness -> Safety
  -> Response -> Confirmation
- direkte `message_delta`-Planner-Verkabelung im `DialogueManager` wurde
  reduziert; Recommendation-Signale laufen ueber explizitere
  `ExtractionPayload`-Outputs
- Process-State, Readiness, Response und Confirmation werden ueber kleine
  Ergebnisobjekte bzw. klarere Anwendungsstellen sichtbar gehalten
- Safety und Confirmation bleiben bewusst placeholderhaft; das verletzt den
  Block nicht, solange ihre spaete Grenzrolle sichtbar bleibt
- fuer den aktuellen V3-Anspruch ist Block 1 damit fuer den
  `DialogueManager` sauber genug abgeschlossen; der naechste strukturelle
  Hebel liegt nun in Block 2 an der Bridge-Zone um `MessageDelta`



## Block 2: Die Bridge-Zone bewusst begrenzen, nicht sofort aufloesen [sehr hoch]

## Ziel

Das haessliche Uebergangsobjekt und seine direkte Umgebung erst einmal sauber
abgrenzen, statt es zu frueh zu ersetzen.

## Warum vor `Call 2`

Heute ist nicht nur `Call 2` das Problem, sondern die ganze Zone zwischen
Extraction und den Folgeschichten.
Wenn diese Zone unklar bleibt, kippt ein neuer `Call 2` wieder in alte
unsaubere Anschlussstellen.

## Aktueller Codebefund

- `MessageDelta` ist explizit transitional
- `ExtractionManager` und `CaseStateManager` greifen noch daran entlang
- `DialogueManager` und Folgeschichten konsumieren indirekt noch Reste daraus

## Sollzustand

- die Bridge ist klar als Bridge benannt
- ihre Verantwortung ist enger
- sie wird vorerst mitgeschleppt, aber nicht weiter vergroessert
- angrenzende Schichten wissen weniger ueber ihre Innereien

## Kernaufgaben

1. klar markieren, welche Anteile an `MessageDelta` wirklich noch aktiv
   benoetigt werden
2. pruefen, welche Felder nur Altlast oder Mischsignal sind
3. angrenzende Klassen weniger direkt auf historische Teilstrukturen
   ausrichten
4. Kommentare und Doku dort nachziehen, wo Objektname und tatsaechliche Rolle
   auseinanderlaufen

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- Eingangs- und Brueckenobjekte sind wichtige Arbeitsmodelle, aber nicht die
  dauerhafte Fallwahrheit
- problematisch wird es, wenn sie mehrere Wahrheitsarten zugleich tragen

## Block-Gate / Done

- die Bridge-Zone ist bewusster begrenzt
- das Objekt darf haesslich bleiben, aber weniger heimlich sein
- eine spaetere echte Ablosung ist besser vorbereitet

### Stand 10-06-26 [bearbeitet]

- der aktive Truth-Edge-Vertrag haengt im Code nicht mehr am historischen
  `MessageDelta`-Typ, sondern an einem kleineren expliziten
  `CaseUpdateBridge`
- dieser Bridge-Vertrag ist auf `claims` plus kleine `merge_hints` fuer die
  aktuelle Truth-Kante begrenzt
- planner-, requirement-, trace-, staging- und der leere extraction-nahe
  Recommendation-Restvertrag wurden aus der Bridge-Zone bzw. ihrer direkten
  Nachbarschaft entfernt
- der `DialogueManager` liest die Bridge nicht mehr direkt; verbliebene
  direkte Bridge-Abhaengigkeiten sitzen bewusst in der
  Case-Truth-Zone bei `CaseStateManager`, `CaseMerger`,
  `CaseMergePolicy` und `ObservationIdentityResolver`
- der alte `MessageDelta`-Typ ist nicht mehr Teil des aktiven Codepfads und
  wurde als letzte tote Resthuelle ganz entfernt
- diese Restkante verletzt Block 2 nicht, weil sie jetzt sichtbar auf den
  aktuellen Merge-/Identity-Bedarf begrenzt ist und eine spaetere Ablosung
  durch einen noch schmaleren Case-Update-Vertrag vorbereitet
- fuer den aktuellen V3-Anspruch ist Block 2 damit sauber genug
  abgeschlossen; der naechste strukturelle Hebel liegt nun an Block 3 und
  Block 4, also bei kleinen Entry-Signalen und dem engeren Call-2-Vertrag


## Block 3: Entry-/Call-1-Grenze und kleine sichtbare Signale schaerfen [hoch]

## Ziel

`Call 1` klein und rollenrein halten.

## Warum jetzt

Wenn die Orchestrierungs- und Bridge-Grenze klarer ist, kann `Call 1`
deutlicher als kleiner Signallieferant gelesen werden.

## Sollzustand

- `EntryManager` liefert kleine sichtbare Steuersignale
- keine breite medizinische Wahrheit
- keine spaete Pfadpolitik
- Signale bleiben klein, generisch und wiederverwendbar

## Kernaufgaben

1. `EntryDecision`-Felder danach bewerten, ob sie echte kleine Signale sind
2. alles vermeiden, was `Call 1` zur Sammelstelle spaeterer Spezialfaelle
   macht
3. bei unklaren Signalen lieber offen markieren statt neue implizite
   Spezialflags einzufuehren

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- `Call 1` soll klein bleiben
- fruehe Einordnung ja, fruehe Schein-Autoritaet nein
- kleine sichtbare Signale sind wichtig, duerfen aber nicht zur endlosen
  Spezialfallgrammatik werden

## Block-Gate / Done

- `Call 1` ist klarer kleiner als vorher
- seine Signale sind besser von spaeterer Bedeutungsueberladung geschuetzt

### Stand 10-06-26 [bearbeitet]

- der aktive Call-1-/`IntentGateway`-Vertrag wurde von einer flachen
  Bool-/Tasksammlung auf gruppierte Signalcontainer fuer Entry, Dispatch,
  Case-Hints, Dialogue-Hints und Safety-Hints umgezogen
- der neue Vertrag bleibt bewusst klein genug fuer Block 3:
  er liefert Scout-/Dispatch-Signale, aber noch keine Case-Wahrheit,
  Merge-Semantik, Readiness- oder Response-Politik
- top-level `category`, `message_role` und ein kleines `profile` bleiben
  vorerst als explizite fruehe Anker erhalten, waehrend die gruppierten
  Signalcontainer jetzt die primaere Vertragsflaeche bilden
- der bestehende Codepfad wurde absichtlich ueber kleine
  Kompatibilitaets-Properties weiter lauffaehig gehalten; die eigentliche
  naechste Hauptarbeit liegt damit jetzt an Block 4, also an der Frage, wie
  `Call 2` sauberer und kleiner auf diesen neuen Call-1-Vertrag aufsetzt


## Block 4: Call-2-Vertrag und Kontextpolitik auf stabileren Grenzen verengen [hoch]

## Ziel

Erst jetzt `Call 2` selbst enger machen, nachdem Orchestrierung und Bridge
klarer sind.

## Warum erst hier

`Call 2` ist wichtig, aber nicht isoliert.
Er sollte nicht gegen instabile obere und untere Nachbarschichten neu gebaut
werden.

## Sollzustand

- `Call 2` liefert kleine medizinische Claims
- keine breite Fallzweitwahrheit
- Kontext bleibt klein, fokusbezogen und modussensitiv
- `Call 2` kann optional bleiben, wenn `Call 1` ihn nicht braucht

## Kernaufgaben

1. minimalen dauerhaften Call-2-Outputvertrag definieren
2. `llm/context.py` gegen dirty-context-Risiken sezieren
3. `case_summary` / `dialogue_summary` nur dort lassen, wo wirklich noetig
4. `ResilientExtractionService` nicht weiter als Verlegenheitsreparatur
   benutzen
5. Doku in `ExtractionManager`, `llm/context.py` und angrenzenden Teilen
   nachziehen

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- `Call 2` ist eigentlicher medizinischer Extraktionsschritt
- er soll nicht den kanonischen `MedicalCase` direkt festlegen
- Zielbild:
  task-komponiert,
  modussensitiv,
  enger am offenen Fokus
- breite Summary- oder Vollkontext-Mitgabe ist verdaechtig
- `Call 2` kann optional sein

## Block-Gate / Done

- `Call 2` ist kleiner und ehrlicher beschrieben
- sein Kontext ist weniger zweitwaehrheitsgefaehrdet
- neue Extraktionslogik baut auf stabileren Systemgrenzen auf

### Stand 10-06-26 [bearbeitet]

- der primaere Call-2-Input in `llm/context.py` wurde hart verkleinert:
  breite `case_summary`-/`dialogue_summary`-Pakete sind aus dem primaeren
  LLM-Call herausgenommen
- an ihrer Stelle traegt der primaere Call jetzt nur noch kleine
  Interpretationssignale wie `pending_slot`, `last_assistant_question`,
  optional `focus_observation`, optional kleine
  `relevant_existing_observations` und ein kleines `profile`
- der primaere Call-2-LLM-Schritt liefert jetzt bereits einen kleineren
  internen Vertrag mit `subject_update`, `focus_update`, `new_items` und
  `open_questions`
- der restliche aktive Codepfad bleibt ueber eine bewusste Uebergangsadaption
  zurueck auf `ExtractionResult` vorerst lauffaehig
- der grosse zweite LLM-Normalizer ist aus dem aktiven Runtime-Pfad entfernt;
  die verbliebene Nachbearbeitung laeuft jetzt ueber eine kleine Python-
  Normalisierung statt ueber einen zweiten breiten Extraction-/Re-Emissions-
  Pass
- `ResilientExtractionService` wurde dabei auf Extraktion, Failure-Fallback
  und schmale Post-Processing-Orchestrierung reduziert; der fruehere
  Mischcharakter ist damit deutlich kleiner geworden
- fuer den aktuellen V3-Anspruch ist Block 4 damit sauber genug bearbeitet;
  die groesste verbleibende Restkante liegt nicht mehr in der Call-2-
  Kontextpolitik, sondern spaeter in der weiteren Entkopplung von
  Requirement-/Readiness-/Response-Schichten

### Bewusst stehen gelassen

- die Rueckadaption vom kleineren internen `Call2ExtractionResult` auf das
  bestehende `ExtractionResult` bleibt als bewusster Uebergangsadapter stehen,
  damit Block 5 nicht sofort denselben Schnitt mittragen muss
- das kleine `profile` bleibt vorerst als harmloser frueher Anker erhalten;
  es traegt aktuell noch keine eigene grosse Steuergrammatik
- die Werkzeugkasten-Komposition von `Call 2` ist noch nicht voll dynamisch;
  der Vertrag ist dafuer bereits vorbereitet, aber die spaetere feinere
  Prompt-/Task-Komposition gehoert nicht mehr zu diesem Block-4-Abschluss


## Block 5: Requirement-, Follow-up- und Readiness-Schicht in echte Prozess- und Gate-Teile schneiden [mittel]

## Ziel

Requirement, Process-State und Gate nicht mehr als diffuse Mischzone tragen.

## Sollzustand

- Requirements haengen sichtbar an Case-Wahrheit
- Follow-up ist Prozessspur
- Readiness ist abgeleitete Entscheidungswahrheit
- Konflikte und Unsicherheit bleiben sichtbar

## Kernaufgaben

1. `RequirementPolicy` als Problemverdichtung lesen:
   was ist dort wirklich Requirement und was eigentlich Prozess- oder
   Gate-Logik
2. `RecommendationStateService` und Evaluator enger trennen
3. bei Bedarf lieber klar markierten Placeholder fuer spaeter feinere
   RecommendationReadiness setzen als neue Heuristik verteilen

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- Requirement gilt fachlich erst dann als geloest, wenn es sichtbar im
  `MedicalCase` angekommen ist
- Readiness und Gate sollen dieselbe Wahrheit lesen
- aktuelle Pflichtfelddefinition ist noch wackelig

## Block-Gate / Done

- Process-State, Requirement und Gate sind besser voneinander getrennt

### Stand 10-06-26 [bearbeitet, mit offenem Rand zu Block 6]

- der fruehere Mischfall
  `answer_to_followup` plus zusaetzliche neue medizinische Information
  wurde inzwischen an zwei Kanten sichtbar geschnitten:
  in der Prozessspur ueber kleine `ProcessStateSignals`
  und an der Call-2-/Truth-Kante ueber die sauberere Trennung von
  `focus_update` und `new_items`
- damit ist der urspruengliche Block-5-Bugreport inhaltlich nicht mehr der
  aktuelle Hauptrest:
  Follow-up-Erfuellung,
  Requirement-Resolution
  und zusaetzliche neue Fakten sind jetzt deutlich lesbarer als getrennte,
  aber kombinierbare Spuren
- `RequirementPolicy` bleibt dabei truth-nah,
  `DialogueStateService` traegt die sichtbare Prozessspur
  und `RecommendationStateService` liest weiter nur die abgeleitete
  Gate-/Readiness-Lage
- der aktuell sichtbare Runtime-Rest liegt nun nicht mehr primaer in dieser
  Mischzone, sondern an der spaeteren Transition:
  `Nein.` auf
  `Gibt es noch weitere Beschwerden? ... dann antworten Sie kurz mit nein, und ich erstelle Ihre Empfehlung.`
  wird noch als medizinischer Extraktions-Turn behandelt
  statt als Recommendation-/Response-Uebergang
- fuer den aktuellen V3-Anspruch ist Block 5 damit deutlich bearbeitet,
  aber noch nicht voll abgeschlossen:
  sein offener Rand kippt bereits in Block 6 hinein


## Block 6: Response-Policy von Text entkoppeln [mittel]

## Ziel

Antwortpfad und Antwortformulierung als getrennte Verantwortungen schaerfen.

## Sollzustand

- `ResponseManager` ist klarer Policy als Textsteuerung
- `ResponseTextBuilder` kaschiert weniger fehlende Semantik
- `guide_next_step` wird entweder ersetzt oder klein vertraglich geerdet

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- Recommendation und Response sollen spaete eigene Schichten sein
- Response-Texte sollen auf echtem Zustand aufbauen
- `guide_next_step` ist ein uebergangsnahes Problem

## Block-Gate / Done

- Text behauptet weniger als der Zustand traegt

### Stand 10-06-26 [jetzt primaerer Folgeschritt]

- Block 6 ist nach dem aktuellen Code- und Logabgleich der naechste
  strukturelle Haupthebel
- `ResponseManager` ist bereits als eigene Policy-Schicht sichtbar,
  aber der Uebergang zwischen
  `continue`,
  `guide_next_step`
  und `recommend`
  ist noch nicht klein genug vertraglich geerdet
- der aktuelle Logrest zeigt genau diese Kante:
  `guide_next_step` erzeugt eine textliche Abschlussfrage,
  aber die Antwort `Nein.` wird anschliessend in Call 1 / Entry noch als
  medizinischer Extraktions-Turn gelesen
  statt als sichtbarer Recommendation-/Response-Transition
- damit ist Block 6 nicht veraltet, sondern durch die juengsten
  Strukturveraenderungen sogar deutlicher fokussiert:
  der offene Rest ist heute klarer ein Response-/Transition-Problem
  und weniger noch ein Block-5-Mischproblem


## Block 7: Safety und Confirmation als bewusst vorbereitete Schichten [spaeter]

## Ziel

Safety und Confirmation nicht vergessen, aber auch nicht zu frueh ueberladen.

## Sollzustand

- beide Schichten sind strukturell vorgesehen
- Dummy- oder Placeholder-Logik ist erlaubt, wenn klar kommentiert
- keine falsche Reifevortaeuschung

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- Safety ist eigene Architekturachse, aktuell aber fachlich noch schwach
- Confirmation ist wichtig, historisch aber nicht stabil ausgebaut
- Confirmation ist vermutlich fachlich nicht unloesbar, nur bisher nicht
  priorisiert

### Stand 10-06-26 [weiter relevant, noch nicht ueberholt]

- Block 7 bleibt inhaltlich weiter gueltig
- der aktuelle Code bestaetigt die damalige Lesart sogar:
  `SafetyManager` ist weiterhin bewusst scaffold-/placeholderhaft,
  `ConfirmationManager` ist ein klar markierter Platzhalter mit sichtbarem
  Spaeht-Hook im `DialogueManager`
- dieser Block ist daher nicht veraltet,
  aber auch weiterhin nicht der naechste Hebel,
  solange Block 6 noch eine offenere Response-/Transition-Kante zeigt


## Block 8: Kleine Signalgrammatik, spaetere Prompt-Komposition und Call 3 [spaeter]

## Ziel

Spaetere Signallogik, Skip-Hints und Recommendation-Content erst nach
stabileren Grenzen aufbauen.

## Developer-Hints aus `SYSTEM_OVERVIEW.md`

- kleine sichtbare Signale sind wertvoll
- Signalbereich ist aktuell chaotisch
- `Call 3` ist moegliche spaetere Recommendation-/Response-Inhaltskante
- erst Vertrag, dann Verhalten

### Stand 10-06-26 [teilweise veraltet, teilweise weiter relevant]

- der Block ist nicht komplett ueberholt,
  aber seine Formulierung ist inzwischen nur noch teilweise passend
- teilweise veraltet ist vor allem der Teil
  `kleine Signalgrammatik`:
  die wirklich noetige kleine sichtbare Signalstruktur wurde faktisch schon
  frueher in Block 3 und Block 4 vorgezogen
  ueber `IntentGateway`,
  `operation_mode`,
  `call2_tasks`
  und die kleineren Process-/Call-2-Vertraege
- weiter relevant bleiben dagegen:
  spaetere feinere Prompt-Komposition,
  moeglicher `Call 3`,
  Recommendation-Content
  und aeussere Integrationslogik
- fuer einen spaeteren Plan-Nachschnitt waere daher sinnvoll,
  Block 8 enger umzubenennen in Richtung:
  `spaetere Prompt-Komposition, Recommendation-Content und Call 3`


## Block 9: Naming- und Rename-Nachschnitt [spaeter querliegend]

## Ziel

Irrefuehrende Klassen- und Attributnamen erst dann gezielt nachschaerfen,
wenn ihre Rollen stabil genug geworden sind.

## Warum eigener Block

Naming ist wichtig, aber fruehe Renames ohne stabile Rolle erzeugen oft nur
teure Bewegungen ohne echten Architekturgewinn.

## Kernaufgaben

1. Stellen sammeln, an denen Name und Verhalten sichtbar auseinanderlaufen
2. diese Diskrepanz voruebergehend in Modul-Doku oder Kommentaren benennen
3. echten Rename erst dann ziehen, wenn der Vertrag des Elements stabil genug
   ist

## Kandidaten/Hints

- `subject`
- `ResponseManager`
- `MessageDelta`
- moeglicherweise `active_modules`
- moeglicherweise einzelne `signals`- oder `planner`-Begriffe

## Block-Gate / Done

- wichtige Missnamer sind gesammelt und spaeter gezielt angehbar
- der Refactor urteilt nicht mehr naiv nach Namen

### Stand 10-06-26 [weiter relevant, aber nachrangig]

- Block 9 bleibt weiter sinnvoll und ist nicht veraltet
- mehrere Missnamer existieren im aktuellen Code weiterhin sichtbar,
  etwa `subject`,
  Teile von `ResponseManager`
  oder einzelne `signals`-/`modules`-Begriffe
- zugleich bestaetigt der bisherige Refactor die V3-Regel:
  die Rolle vieler Komponenten ist jetzt klarer als frueher,
  aber fuer mehrere Stellen noch nicht stabil genug,
  um schon den teuereren Rename-Nachschnitt zu rechtfertigen
- dieser Block bleibt damit ein spaeterer Querschnittsblock
  nach den noch offenen Policy-/Transition-Schnitten


## Konkrete Startempfehlung fuer V3

Der naechste beste erste praktische Schritt ist jetzt nicht mehr:

- sofort den finalen `Call 2` neu bauen

sondern:

1. `DialogueManager` und seine direkten Untergrenzen kurz als echten
   Turn-Vertrag sezieren
2. dabei festhalten, welche Outputs die Untermanager jeweils wirklich
   zurueckgeben sollten
3. `MessageDelta` / Bridge-Zone fuer den Moment bewusst als transitional
   contract einfrieren und sauber markieren
4. erst dann `Call 1` und `Call 2` gegen diese stabileren Grenzen verengen


## Schlussbewertung

V3 verschiebt den Fokus noch einmal nuetzlich:

- weg von "welcher inhaltliche Block ist theoretisch am wichtigsten"
- hin zu "welche Reihenfolge stabilisiert den realen Turn-Fluss am saubersten"

Der wichtigste neue Merksatz lautet:

- lieber zuerst die Systemgrenzen vom `DialogueManager` aus sauberziehen und
  ein haessliches Bridge-Objekt temporaer bewusst mittragen,
  als `Call 2` vorzeitig zu perfektionieren und ihn danach wieder an unsaubere
  Nachbarschichten anschliessen zu muessen.


## Planabgleich 10-06-26 nach dem aktuellen Codeschnitt

Verdichtete Einordnung der spaeteren Bloecke:

- Block 5:
  nicht mehr nur Bugreport-Zone, sondern bereits deutlich bearbeitet;
  der offene Rest kippt heute eher in Block 6
- Block 6:
  jetzt der naechste primaere Arbeitsblock
- Block 7:
  weiter relevant, aber weiterhin spaeter
- Block 8:
  teilweise veraltet in der Formulierung;
  die kleine Signalgrammatik wurde schon frueher gezogen,
  waehrend Prompt-Komposition / `Call 3` / Recommendation-Content spaeter
  weiter relevant bleiben
- Block 9:
  weiter relevant, aber bewusst nachrangig

Praktische neue Reihenfolge ab hier:

1. Block 6:
   Response-/Recommendation-Transition und `guide_next_step` sauberer
   vertraglich schneiden
2. Block 7:
   Safety / Confirmation nur dann vorziehen, wenn ein neuer konkreter
   Produktdruck entsteht
3. Block 8:
   spaetere Prompt-Komposition, Recommendation-Content und moeglicher
   `Call 3`
4. Block 9:
   Naming-/Rename-Nachschnitt auf stabileren Rollen
