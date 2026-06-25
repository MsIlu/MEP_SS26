# Careena3 Refactor Plan V5

Stand: 2026-06-12
Status: working draft

Baut auf:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
- `autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
- `autodoc/2026-06-11/ARCHITECTURE_REDUCTION_REBUILD_CONCEPT.md`
- `autodoc/2026-06-12/TARGET_ARCHITECTURE_OBJECT_MODEL.md`
- `autodoc/2026-06-12/CAREENA_ZIELBILD_UND_AUFARBEITUNG_2026-06-12.md`
- `autodoc/2026-06-11/BUG_REPORTS_V4.md`


## Zweck

V5 soll den Refactor nicht einfach fortsetzen,
sondern die aktuelle Lage ehrlicher neu ordnen.

Der Plan folgt bewusst dem Stil,
der V3 stark gemacht hat:

- wenige klare Hauptentscheidungen
- Reihenfolge als Architekturfrage
- offene Punkte sichtbar lassen
- nichts vorwegnehmen,
  was der aktuelle Problemknoten noch nicht traegt

Ziel von V5 ist nicht,
jetzt schon die schoenste Endarchitektur auszumalen.

Ziel ist:

1. die heutigen parallel sichtbaren Probleme auf ihren gemeinsamen Kern
   zurueckfuehren
2. daraus eine sinnvolle Eingriffsreihenfolge ableiten
3. das Framework moeglichst schnell wieder so glattziehen,
   dass Careena end-to-end sauberer laeuft
4. erst danach die feineren fachlichen und dialogischen Ausbauten ansetzen


## Warum ein neuer Plan noetig ist

V3 war stark,
weil er die Reihenfolge
`Orchestrierung -> Bridge -> kleine Signale -> engerer Call 2 -> Process-State -> Response`
sauber gelesen hat.

V4 war stark,
weil er gezeigt hat,
dass die aktuelle Hauptkante real hinten bei
Transition,
Freigabelogik,
Antwortstrategie
und Recommendation-Abschluss sitzt.

Trotzdem reicht eine blosse Fortschreibung von V4 im Moment nicht ganz.

Der neue Kernbefund lautet:

- das sichtbare schlechte Antwortverhalten
- das unfertige Call-2-/Extraktionssystem
- und die fehlende Semantik dafuer,
  wann Careena fuer das aktuelle Anliegen "weit genug" ist

sind keine drei getrennten Baustellen.

Sie verfaelschen sich gegenseitig.

Genauer:

- Response wirkt schlechter,
  weil das System noch kein sauberes Anliegen-/Fortschrittsmodell hat
- Call 2 wirkt instabiler,
  weil er gegen unklare Abschluss- und Freigabelogik arbeitet
- Readiness wirkt zu aggressiv,
  weil sie teils noch Funktionen traegt,
  die eigentlich concern-nahe Fortschrittssemantik braeuchten

V5 setzt deshalb vor V4 noch eine explizitere Klammer:

- Was bedeutet in Careena eigentlich Fortschritt fuer das aktuelle Anliegen?
- Was bedeutet "noch sammeln",
  "Abschluss pruefen",
  "weiter medizinisch",
  "Recommendation freigeben"?

Solange diese Klammer nicht wenigstens minimal existiert,
werden Response- und Call-2-Schnitte weiter gegeneinander arbeiten.


## Quellenbasis und Gewichtung

Hoechste Gewichtung:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN_V3.md`
- `autodoc/2026-06-11/REFACTOR_PLAN_V4.md`
- `autodoc/2026-06-11/ARCHITECTURE_REDUCTION_REBUILD_CONCEPT.md`
- `autodoc/2026-06-12/TARGET_ARCHITECTURE_OBJECT_MODEL.md`

Mittlere Gewichtung:

- `autodoc/2026-06-12/CAREENA_ZIELBILD_UND_AUFARBEITUNG_2026-06-12.md`
- `autodoc/2026-06-11/BUG_REPORTS_V4.md`
- `autodoc/workbench/2026-06-09/BLOCK5_PROCESS_STATE_CONCEPT.md`
- `autodoc/workbench/2026-06-09/BLOCK6_RESPONSE_TRANSITION_CONCEPT.md`

Niedrigere,
aber hilfreiche Gewichtung:

- aeltere 08.06.-Dokumente,
  besonders dort,
  wo sie weiter belastbare Grundsaetze zu
  Case-Truth,
  Call 2
  und Boundary-First liefern

Wichtige Leseregel:

- fruehere Texte werden nicht verworfen
- aber spaetere Korrekturen und Umpriorisierungen haben Vorrang


## Neuer Hauptbefund

Die aktuelle Lage laesst sich am besten nicht als Bugliste,
sondern als verhedderter Dreiklang lesen:

### 1. Antwortpfade sind noch nicht sauber genug

- freie KI-Antwortpfade existieren nur eng oder an falschen Stellen
- statische Antwortbahnen tragen noch zu viel Ersatzsemantik
- Abschlussknoten und Rueckwege sind noch nicht robust genug

### 2. Call 2 ist architektonisch vorbereitet,
### aber noch nicht als minimales stabiles Runtime-Werkzeug voll eingelost

- die Werkzeugkasten-Idee ist sichtbar
- die Runtime arbeitet aber weiter mit Uebergangsobjekten und
  nur teilweise eingeloster Komposition
- dadurch bleibt Extraktion im Lauf noch driftanfaellig

### 3. Das System hat noch kein sauberes Modell dafuer,
### wann es fuer das aktuelle Anliegen "weit genug" ist

- ein einzelner Symptomfokus oder `primary_focus` darf diese Rolle nicht
  weiter still tragen
- `Readiness` darf nicht allein "Anliegen hinreichend verstanden" bedeuten
- dadurch werden Abschluss,
  Recommendation-Freigabe
  und Rueckkehr in den medizinischen Pfad instabil

Die eigentliche Knotenfrage lautet deshalb:

- welche kleine concern-nahe und fortschrittsnahe Semantik braucht Careena,
  damit Readiness,
  Freigabelogik,
  Response
  und Call 2 wieder sauber gegeneinander ausgerichtet werden koennen?


## Neuer Hauptentscheid zur Reihenfolge

V5 setzt die Reihenfolge bewusst anders als ein rein hinterer V4-Weiterbau.

Die Kernreihenfolge lautet:

1. minimale concern-/Fortschrittssemantik explizit machen
2. darauf die Freigabelogik und den Abschlussknoten neu begruenden
3. danach Response und minimalen Call-2-Runtime-Vertrag in kurzen Loops
   gegeneinander stabilisieren
4. erst danach die groesseren Ausbaupfade wieder aufnehmen

Wichtig:

- V5 zieht nicht den grossen Concern-Ausbau vor
- V5 zieht auch nicht sofort den vollen dynamischen Call-2-Ausbau vor

V5 zieht nur die minimale semantische Klammer vor,
ohne die beide Baustellen weiter gegeneinander driften.


## Warum diese Reihenfolge sinnvoller ist

Wenn man jetzt direkt nur Response verbessert,
dann verbessert man leicht das sichtbare Verhalten,
ohne die falsche Fertig-/Abschlusslogik darunter sauber zu treffen.

Wenn man jetzt direkt nur Call 2 fertigzieht,
dann baut man einen besseren Werkzeugkasten
gegen ein noch unklar definiertes Ziel
"wann sind wir fuer dieses Anliegen weit genug?".

Wenn man jetzt aber zuerst die minimale concern-/Fortschrittsfrage sauberer
stellt,
dann koennen spaetere Schichten wieder sinnvoll lesen:

- sammeln wir noch?
- klaeren wir gerade das Anliegen?
- stehen wir an einer Abschlusswahl?
- darf Recommendation ueberhaupt schon angeboten werden?
- ist die aktuelle Nachricht neue medizinische Information
  oder nur dialogische Reaktion auf einen Abschlussknoten?


## Was V5 bewusst noch nicht festnagelt

V5 ist absichtlich vorsichtig.

Folgende Punkte sollen in diesem Plan noch nicht dogmatisch vorentschieden
werden:

### 1. Ob `ConcernState` langfristig ein eigenes persistentes Zentrum bleibt

V5 behandelt Concern zuerst als semantische Notwendigkeit,
nicht als bereits endgueltig bewiesene Modellgrenze.

### 2. Ob Recommendation-Inhalt spaeter ein eigener `Call 3`
### oder ein anderer Werkzeugkasten-Modus wird

Diese Frage bleibt weiter spaeter.

### 3. Wie die finale adaptive Gespraechstiefe genau aussieht

V5 bereitet nur die Grenze vor,
damit spaeter adaptive Rueckfragen sauber andocken koennen.

### 4. Wie dynamisch der volle Call-2-Werkzeugkasten spaeter wirklich wird

V5 will zuerst eine minimallauffaehige,
ehrliche Runtime-Rolle,
nicht sofort die volle Endkomposition.

### 5. Ob das finale Naming schon jetzt gezogen werden sollte

Wie in V3 und V4:

- Verhalten vor Namen
- Rename erst auf stabileren Rollen


## Zielbild von V5

Careena soll nach V5 noch nicht fertig sein,
aber wieder in einem stabileren Rahmen laufen koennen.

Der Zielzustand von V5 ist deshalb bewusst begrenzt:

1. Careena kennt fuer den aktuellen Turn eine kleine concern-nahe
   Fortschrittslesart
2. Readiness ist nicht mehr still gleichbedeutend mit
   "Anliegen fertig genug"
3. die Freigabelogik fuer Abschluss,
   Rueckkehr in den medizinischen Pfad
   und Recommendation ist expliziter
4. Response-Pfade sind klein,
   klar
   und besser an diese Freigabelogik gebunden
5. Call 2 ist als minimal stabiles Runtime-Werkzeug wieder sauberer lesbar,
   auch wenn der volle Werkzeugkasten noch spaeter folgt

V5 will also nicht die ganze Zielarchitektur fertig bauen,
sondern das System wieder auf eine sauberere tragende Mittel- und Oberkante
stellen.


## Arbeitsweise in V5

## 1. Boundary first bleibt gueltig

Keine lokale Antwort-,
Readiness-
oder Extraktionsmagie als Ersatz fuer die fehlende Klammer.

## 2. Behavior over names bleibt gueltig

Auch neue concern-nahe Vertrage sollen erst nach Rolle,
nicht nach wohlklingendem Namen beurteilt werden.

## 3. Sichtbare Platzhalter bleiben erlaubt

Aber:

- nur wenn sie eine Schichtgrenze schuetzen
- nicht wenn sie wieder neue Mischlogik einziehen

## 4. Reihenfolge ist hier wichtiger als Vollstaendigkeit

V5 optimiert nicht fuer "alles halb ein bisschen besser",
sondern fuer:

- erst wieder sauber laufendes Geruest
- danach feinere Qualitaet

## 5. Response und minimaler Call-2-Stabilisierungspfad werden nach den
## ersten zwei Bloecken bewusst iterativ gearbeitet

Ab Block 3 und 4 ist keine starre Einmal-Reihenfolge mehr sinnvoll.
Dann braucht es kurze Schleifen:

- Response wird gehaertet
- dadurch werden neue Call-2-Falschpfade sichtbar
- Call 2 wird minimal nachgeschnitten
- dadurch werden neue Response-/Freigabekanten sichtbar

Diese Loop-Arbeit ist in V5 ausdruecklich eingeplant,
nicht als Planbruch.


## Praktische globale Reihenfolge

1. minimale concern-/Fortschrittssemantik explizit machen
2. Freigabelogik und Abschlussknoten darauf neu begruenden
3. Response-Pfade gegen diese Freigabelogik stabilisieren
4. minimalen Call-2-Runtime-Vertrag gegen dieselbe Freigabelogik
   stabilisieren
5. erst danach dynamischen Call-2-Werkzeugkasten weiterziehen
6. Recommendation-Inhalt,
   Safety,
   Confirmation,
   Naming
   spaeter nachziehen


## Block 0: V5-Arbeitsvertrag [aktiv]

## Ziel

Den Refactor wieder auf die Frage zurueckziehen:

- was muessen wir jetzt minimal klarziehen,
  damit das Framework wieder sauberer traegt?

## Kernfragen

1. wird hier eine echte zustaendige Schicht klarer
2. wird hier concern-/Fortschrittssemantik expliziter
3. wird `Readiness` entlastet
4. wird sichtbares Antwortverhalten auf ehrlicheren Zustand gesetzt
5. wird Call 2 kleiner und ehrlicher,
   statt wieder breiter und "klueger"

## Done

- ein Schritt ist gut,
  wenn er das System wieder besser lesbar und end-to-end stabiler macht
- eine unfertige,
  aber klarere Zwischenstufe ist erlaubt
- eine "praktische" Abkuerzung ist nicht gut,
  wenn sie concern,
  Freigabelogik,
  Response
  und Call 2 wieder vermischt


## Block 1: Minimales concern-/Fortschrittsmodell explizit machen [hoechste Prioritaet]

## Status-Update 2026-06-12

Status:

- in Arbeit
- sinnvoll begonnen
- noch nicht voll abgeschlossen

Aktueller Stand:

- ein kleiner expliziter concern-/fortschrittsnaher Vertrag laeuft jetzt
  sichtbar durch die aktive Runtime
- persistente concern-nahe Signale wurden eingefuehrt:
  `active_concern_id`,
  `phase`,
  `information_sufficiency`,
  `active_closing_node`
- turn-lokale concern-/Fortschrittssignale wurden sichtbar gemacht:
  `concern_relation`,
  `latest_turn_role`,
  `allowed_next_step`
- bestehende Steuersignale aus
  `Entry`,
  aktiver Transition,
  `Readiness`
  und spaeter Response werden jetzt nicht mehr nur implizit gelesen,
  sondern teilweise schon auf diesen kleinen Vertrag umgelegt
- `Readiness` ist damit im aktiven Code bereits etwas entlastet:
  sie bleibt Mindestinformations-Input,
  waehrend der erlaubte naechste Zug jetzt zusaetzlich concern-nah
  abgeleitet wird

Was Block 1 damit schon sichtbar leistet:

- die Frage
  "worum geht es gerade"
  wird nicht mehr nur indirekt ueber
  `recommendation_ready`,
  `response_mode`
  oder lokale Hinterpfade getragen
- die Frage
  "sammeln wir noch,
  klaeren wir,
  stehen wir an einer Abschlusskante,
  oder darf Recommendation naeher ruecken"
  hat jetzt erstmals eine kleine explizite Laufspur
- der aktive Turn hat jetzt einen kleineren expliziten Hebel
  `allowed_next_step`,
  statt die Freigabelesart nur spaet aus verstreuten Booleans
  zusammenzuraten

Was fuer Block 1 noch offen bleibt:

- der Umhaengepunkt von
  `primary_focus`
  ist noch nicht wirklich abgeschlossen;
  aktuell wird er an einzelnen Stellen weiter als Hilfssignal gelesen
  und teilweise noch fuer Summary-/Fokusabwaertsverwendung benutzt
- die concern-nahe Semantik ist noch klein und pragmatisch,
  aber noch nicht an allen relevanten Runtime-Kanten gleich sauber
  durchgezogen
- der eigentliche kleine Freigabevertrag
  "welcher naechste Zug ist auf welcher concern-/Fortschrittslage erlaubt"
  ist erst vorbereitet
  und muss in Block 2 noch klarer als eigene Policy-Lage geschnitten werden
- `Readiness` ist zwar begrifflich und praktisch teilweise entlastet,
  aber noch nicht ueberall so sauber getrennt,
  dass keine alte implizite Restsemantik mehr mitlaeuft

Vorlaeufige Block-1-Einordnung:

- Block 1 ist nicht mehr nur Plantext,
  sondern als kleine echte Runtime-Schicht begonnen
- der Kern des Blocks
  "minimale concern-/Fortschrittssemantik explizit machen"
  ist damit praktisch erreicht
- der Block-Gate ist aber noch nicht voll als erledigt zu markieren,
  weil die spaeteren Umhaengepunkte von
  `primary_focus`
  und die sauberere explizite Freigabelesart noch nicht weit genug
  sichtbar sind

Naechster sinnvoller Schritt aus diesem Stand:

- Block 2 direkt anschliessen
- aus dem neuen Minimalvertrag einen kleinen expliziten Freigabevertrag
  schneiden
- dabei besonders sauber trennen:
  `Readiness` als Teilbefund
  vs.
  `allowed_next_step` als tatsaechlich erlaubter naechster Zug

## Ziel

Die fehlende Frage
"worum geht es gerade eigentlich"
und
"sind wir fuer dieses Anliegen noch im Sammeln oder schon an einer
Abschluss-/Freigabekante"
zumindest minimal explizit machen.

## Warum jetzt zuerst

Der aktuelle Hauptschaden entsteht nicht nur aus schlechter Response-Policy
oder schlechtem Call 2,
sondern daraus,
dass beide auf eine noch fehlende concern-/Fortschrittslesart reagieren.

Ohne diesen Schritt bleibt unklar:

- ob ein Turn das Anliegen weiterexploriert
- ob er ein neues Anliegen aufmacht
- ob er nur dialogisch auf einen Abschlussknoten reagiert
- ob die aktuelle Falltiefe fuer das Anliegen schon hinreichend ist

## Sollzustand

Es gibt einen kleinen expliziten Vertrag,
der mindestens diese Fragen sichtbar macht:

1. welches Careena-relevante Anliegen ist aktuell aktiv
2. setzt der aktuelle Turn dieses Anliegen fort,
   verschiebt es,
   oder reagiert er nur auf eine dialogische Uebergangslage
3. ist das Anliegen noch in Exploration,
   in Klaerung,
   an einer Abschlusswahl
   oder an einer Recommendation-nahen Freigabelage
4. ist fuer dieses Anliegen bereits genug belastbare Information vorhanden,
   unabhaengig von bloss lokaler Symptomvollstaendigkeit

Wichtig:

- dieser Vertrag muss noch nicht das finale Objektmodell festnageln
- er darf klein bleiben
- er darf vorerst concern-nahe und benachbart zu `DialogueState` laufen
- er darf `Readiness` bewusst nicht ersetzen

## Wichtige Fragen

1. welche minimale concern-Semantik ist fuer die Laufentscheidung wirklich
   noetig
2. was davon ist persistenter Zustand,
   was nur turn-lokale Deutung
3. was darf weiter im `MedicalCase` liegen
4. was muss aus `primary_focus` und lokalem Antwortverhalten herausgezogen
   werden
5. welche Teile davon muessen schon im naechsten Turn mitlaufen,
   ohne sofort eine grosse neue Sammelschicht zu bauen

## Leitplanken

- kein grosser sofortiger Concern-Superstate
- keine Verschmelzung mit `Readiness`
- keine voreilige Fachdogmatik,
  was "ein Anliegen" immer exakt sein muss
- lieber kleine explizite Fragen
  als zu frueh ein grosses fertiges Modell

## Kernaufgaben

1. die minimalen concern-/Fortschrittsfragen explizit benennen
2. vorhandene concern-nahe Signale im Code und in den aktiven Pfaden sammeln:
   `primary_focus`,
   `recommendation_ready`,
   Antwortpfad,
   offene Transition,
   aktuelle medizinische Exploration
3. entscheiden,
   welche dieser Signale kuenftig concern-nah gelesen werden sollen
4. einen kleinen ersten Runtime-Vertrag daraus schneiden,
   ohne schon die halbe Persistenzarchitektur umzubauen

## Betroffene Dateien/Klassen

- `models/domain/concern.py`
- `models/domain/dialogue.py`
- `models/turn/context.py`
- `application/managers/dialogue_manager.py`
- `application/managers/entry_manager.py`
- `application/services/readiness_evaluator.py`
- `application/services/recommendation_state_service.py`
- spaeter auch `application/managers/response_manager.py`

## Nicht innerhalb dieses Blocks still loesen

- freie Antwortverbesserung ohne concern-/Fortschrittsvertrag
- neue lokale `primary_focus`-Heuristiken
- grosse Recommendation-Logik

## Block-Gate / Done

- es gibt eine kleine explizite concern-/Fortschrittslesart
- `Readiness` ist begrifflich davon getrennt
- der Plan fuer spaetere Umhaengepunkte von `primary_focus` ist sichtbar


## Block 2: Freigabelogik und Abschlussknoten darauf neu begruenden [sehr hoch]

## Status-Update 2026-06-12

Status:

- in Arbeit
- Kernschnitt umgesetzt
- noch nicht voll abgeschlossen

Aktueller Stand:

- es gibt jetzt einen kleinen expliziten Freigabevertrag als eigene
  Turn-Stufe nach Process-State und `Readiness`
- dieser Vertrag laeuft als `gate_decision` sichtbar durch die Runtime
  und trennt erstmals explizit:
  `Readiness` als Teilbefund
  vs.
  `allowed_next_step` als tatsaechlich erlaubter naechster Zug
- `RecommendationStateService` liest jetzt nicht mehr nur
  Mindestinformationslage,
  sondern formuliert daraus eine kleine Gate-Entscheidung
  mit expliziten Lagen wie:
  `cannot_assess`,
  `concern_clarification`,
  `closing_check`,
  `return_to_medical`,
  `recommendation_open`,
  `recommendation_allowed`
- `DialogueManager` uebernimmt diese Gate-Entscheidung jetzt sichtbar in den
  Turn-Kontext,
  statt die Freigabelage spaeter wieder indirekt aus Flags zu rekonstruieren
- `ResponseManager` liest diese Gate-Entscheidung jetzt direkt mit
  und wendet sie an,
  statt die Abschluss- und Rueckweglogik implizit nur aus
  `recommendation_ready`,
  Transition-Flags
  oder Antwortpfaden zu erraten

Was Block 2 damit schon sichtbar leistet:

- der aktive Abschlussknoten
  `recommendation_ready_check`
  haengt jetzt expliziter an einer Gate-Lesart
  statt nur lose an spaeter Response
- der Rueckweg
  `report_more_information`
  und der Commit-Pfad
  `request_recommendation`
  laufen jetzt beide ueber denselben kleinen Gate-Vertrag
- `Readiness`
  beantwortet weiter die Frage
  "ist die Mindestinformationslage da",
  aber nicht mehr still allein die Frage
  "was darf als naechster Zug passieren"

Was fuer Block 2 noch offen bleibt:

- die Gate-Lesart ist jetzt explizit,
  aber noch relativ nah an den heutigen bestehenden Pfaden geschnitten;
  sie ist noch nicht die ruhigste oder finale Form
- `models/domain/dialogue.py`
  traegt den aktiven Abschlussknoten weiter als kleinen Zustand,
  aber die Gesamtfreigabelogik ist noch nicht als vollstaendig beruhigte
  eigene Schicht ausmodelliert
- `ResponsePlan`
  selbst traegt die Gate-Lesart noch nicht als eigene explizite Sicht mit;
  aktuell sitzt sie sichtbar im Turn-Kontext und in den Trace-/Response-
  Entscheidungen
- die neue Gate-Entscheidung ist gegen die vorhandenen Block-6-Pfade
  verifiziert,
  aber noch nicht gegen breitere End-to-End-Fehlpfade oder spaetere
  Recommendation-Inhaltsstrecken gehaertet

Vorlaeufige Block-2-Einordnung:

- Block 2 ist praktisch begonnen
  und sein Kern
  "Freigabelogik als eigene kleine Policy-Lage sichtbar machen"
  ist jetzt im Code angekommen
- der Block-Gate ist aber noch nicht voll zu,
  weil die Freigabelogik noch nicht in allen angrenzenden Schichten gleich
  ruhig und vollstaendig lesbar ist

Naechster sinnvoller Schritt aus diesem Stand:

- Block 3 direkt anschliessen
- die sichtbaren Response-Familien noch enger und ehrlicher gegen
  `gate_decision`
  schneiden
- dabei pruefen,
  welche alten Restpfade weiterhin semantisch zu viel aus
  `response_mode`,
  `recommendation_ready`
  oder Fallback-Texten ziehen

## Ziel

Die Freigabelogik neu aufspannen:

- nicht mehr nur
  `recommendation_ready` / `response_mode`
- sondern auf concern-/Fortschrittslage,
  medizinischer Wahrheit,
  Dialogprozess
  und `Readiness` als Teilbefund

## Warum jetzt

Erst damit kann sauber unterschieden werden:

- wir sammeln noch medizinisch
- wir klaeren noch concern-nah
- wir stehen an einer Abschlusswahl
- wir bleiben auf demselben Abschlussknoten
- wir gehen zurueck in den medizinischen Pfad
- Recommendation darf wirklich freigegeben werden

## Sollzustand

Es gibt eine kleine explizitere Freigabelage,
die mindestens sauber unterscheiden kann zwischen:

- weiterer medizinischer Exploration
- concern- oder fallbezogener Klaerung
- aktiver Abschluss-/Freigabefrage
- Rueckweg in den medizinischen Pfad
- wirklicher Recommendation-Freigabe

Wichtig:

- `Readiness` bleibt Eingabe,
  nicht Gesamterklaerung
- der aktive Abschlussknoten bleibt ein kleiner Zustand,
  nicht nur Text
- der Zwei-Wege-Knoten
  `request_recommendation` /
  `report_more_information`
  bleibt erhalten,
  wird aber sauberer in die Gesamtfreigabelogik eingebettet

## Wichtige Fragen

1. welche concern-/Fortschrittssignale muessen die Freigabelogik wirklich
   lesen
2. was ist dort medizinischer Befund,
   was dialogische Uebergangslage,
   was concern-nahe Einschaetzung
3. wie wird verhindert,
   dass `Readiness` weiter still "Anliegen hinreichend verstanden"
   bedeutet
4. welche minimalen Abschluss-/Freigabezustaende braucht das System wirklich

## Leitplanken

- kein neuer grosser Freigabe-Bus
- `DialogueManager` bleibt Anwender,
  nicht Policy-Sammelstelle
- keine Rueckverlagerung in den finalen Text
- keine lokale Sonderfalllisten-Architektur fuer Abschlussantworten

## Kernaufgaben

1. kleinen Freigabevertrag formulieren
2. aktiven Abschlussknoten gegen diese Freigabelage lesen
3. `EntryManager`,
   `RecommendationStateService`
   und `ResponseManager`
   auf dieselbe kleine Freigabelesart ausrichten
4. die Trennung
   `Readiness-Teilbefund`
   vs.
   `tatsaechlich erlaubter naechster Zug`
   im Code sichtbarer machen

## Betroffene Dateien/Klassen

- `application/services/readiness_evaluator.py`
- `application/services/recommendation_state_service.py`
- `application/managers/entry_manager.py`
- `application/managers/response_manager.py`
- `models/domain/dialogue.py`
- `models/turn/response_plan.py`

## Nicht innerhalb dieses Blocks still loesen

- Recommendation-Inhalt
- neue breite KI-Antwortbahnen
- Call-2-Dynamik

## Block-Gate / Done

- Abschlussknoten und Rueckwege haengen an expliziterer Freigabelogik
- `Readiness` ist sichtbar Teilbefund,
  nicht stilles Gesamtzielmodell
- concern-/Fortschrittssignale koennen kuenftig sauber andocken


## Block 3: Response-Pfade gegen die neue Freigabelogik stabilisieren [hoch]

## Status-Update 2026-06-12

Status:

- in Arbeit
- Kernschnitt umgesetzt
- noch nicht voll abgeschlossen

Aktueller Stand:

- die sichtbare Response-Schicht liest die neue Freigabelage jetzt enger
  ueber `gate_decision`
  und weniger ueber alte implizite Kombinationen aus
  `recommendation_ready`,
  `response_mode`
  und spaeten Text-Fallbacks
- `ResponseManager` trennt den `continue`-Pfad jetzt sauberer:
  Rueckweg in den medizinischen Pfad bleibt statisch,
  enger freier `llm_continue`-Pfad laeuft nur noch fuer echte aktive
  medizinische Progress-/Klaerungszuege in medizinischer Exploration,
  und ein kleiner statischer medizinischer Acknowledgement-Pfad deckt den
  restlichen `continue`-Bereich ab
- `ResponseTextBuilder` kennt jetzt diesen neuen statischen kleinen
  Acknowledgement-Pfad explizit,
  statt alles,
  was nicht Rueckweg oder Recommendation ist,
  in dieselbe generische Continue-Bahn zu werfen
- `LLMResponseGenerationService` bekommt die concern- und gate-nahe Lage jetzt
  expliziter im Prompt:
  `concern_relation`,
  `latest_turn_role`,
  `phase`,
  `information_sufficiency`,
  `allowed_next_step`
  und
  `gate_status`

Was Block 3 damit schon sichtbar leistet:

- statische und freie Antwortfamilien sind hinten klarer getrennt
- der enge freie KI-Pfad ist jetzt staerker an eine erlaubte Gate-Lage
  gekoppelt
- `guide_next_step`,
  Recommendation,
  Rueckweg,
  Follow-up
  und `cannot_assess`
  bleiben als klarere sichtbare Familien erhalten,
  waehrend der fruehere breite `continue`-Rest etwas kleiner und ehrlicher
  wird

Was fuer Block 3 noch offen bleibt:

- die sichtbaren Antwortfamilien sind enger geschnitten,
  aber noch nicht voll end-to-end gegen die realen Laufpfade gehaertet
- `ResponsePlan`
  und die spaetere Textschicht tragen die neue Antwortfamilienlogik noch
  nicht maximal explizit als eigene benannte Antwortsicht
- die jetzige Trennung ist bewusst klein;
  spaetere Feinschnitte koennen noch zeigen,
  wo `continue`
  weiter reduziert oder anders aufgefaechert werden sollte

Vorlaeufige Block-3-Einordnung:

- Block 3 ist praktisch begonnen
  und sein Kern
  "sichtbare Antwortpfade enger gegen die Freigabelage schneiden"
  ist jetzt im Code angekommen
- der Block-Gate ist aber noch nicht voll zu,
  weil die Antwortfamilien noch nicht ueber breitere reale End-to-End-Pfade
  und spaetere Recommendation-Strecken ausreichend beruhigt sind

Naechster sinnvoller Schritt aus diesem Stand:

- den Response-Stand zunaechst nicht ueberreizen,
  sondern mit Block 4 die minimalen Call-2-Pfade gegen dieselbe Gate-Lage
  nachziehen
- dabei beobachten,
  welche sichtbaren Antwortreste eigentlich noch aus unnoetigen oder
  zu breiten Extraktionsstarts stammen

## Ziel

Das sichtbare Antwortverhalten moeglichst schnell wieder sauberer und
berechenbarer machen,
ohne jetzt schon die volle Endarchitektur zu verlangen.

## Warum hier

Das ist der schnellste Hebel fuer:

- das aktuell sichtbare "Antwortverhalten ist scheisse"
- bessere End-to-End-Lesbarkeit
- ehrlichere Loops beim Nachschnitt von Call 2

## Sollzustand

Die Response-Schicht arbeitet mit einem kleinen begrenzten Satz klarer
Antwortfamilien,
die an der Freigabelogik haengen.

Mindestens sauber lesbar bleiben sollen:

- medizinische Rueckfrage
- dialogische Abschlussfrage
- Rueckweg in den medizinischen Pfad
- enger freier `continue`-Pfad
- Recommendation-Placeholder / Recommendation-Ausgabe
- Notfall / Out-of-scope / Cannot-assess

## Wichtige Fragen

1. wo braucht es wirklich statische Texte
2. wo darf der enge freie KI-Pfad laufen
3. welche Pfade sind concern- oder fortschrittsabhaengig
4. wie bleibt der Text klein,
   wenn die Freigabelage noch nicht perfekt ist

## Leitplanken

- `ResponseTextBuilder` darf keine fehlende Freigabelogik kaschieren
- freier KI-Text darf nur auf freigegebenen Pfaden laufen
- keine Erweiterung des freien Pfads,
  solange der Abschlussknoten noch weich ist

## Kernaufgaben

1. aktuelle Antwortfamilien gegen die neue Freigabelogik mappen
2. statische und freie Pfade klarer trennen
3. `guide_next_step` bzw. seinen Nachfolger nicht mehr als blosse Textidee
   lesen
4. Fallbacks ehrlich halten,
   statt sie semantisch zu ueberfrachten

## Betroffene Dateien/Klassen

- `application/managers/response_manager.py`
- `application/services/response_text_builder.py`
- `application/services/response_generation_service.py`
- `application/services/llm_response_generation_service.py`
- `models/turn/response_plan.py`

## Nicht innerhalb dieses Blocks still loesen

- vollen Recommendation-Content
- adaptive freie Rueckfragetiefe als Grossprojekt
- Call-2-Werkzeugkasten-Dynamik

## Block-Gate / Done

- sichtbare Antwortpfade sind kleiner,
  ehrlicher
  und besser von der Freigabelage getragen
- freie KI-Antwort laeuft nur auf dafuer vorgesehenen Bahnen


## Block 4: Minimalen Call-2-Runtime-Vertrag stabilisieren [hoch]

## Status-Update 2026-06-12

Status:

- begonnen
- erster kleiner Vertragsnachschnitt umgesetzt
- noch klar offen

Aktueller Stand:

- die aktive Call-2-Strecke traegt jetzt ein kleines explizites
  Ergebnisfeld
  `case_extension_status`
  mit den Lagen:
  `no_relevant_change`,
  `updates_existing_information`,
  `adds_new_information`,
  `mixed_update_and_new`
- damit ist im aktiven Extraktionsvertrag erstmals sichtbarer,
  ob eine Nachricht den Fall vor allem erweitert,
  bestehende Information aktualisiert
  oder praktisch keinen relevanten medizinischen Zuwachs bringt
- der Call-2-Prompt wurde auf diese kleine Fall-Erweiterungslesart
  ausgerichtet,
  statt diese Frage nur spaeter indirekt aus
  `focus_update`,
  `new_items`
  oder Merge-Effekten herauszulesen
- der Python-Normalizer schaerft diese Lesart jetzt eng gegen
  `focus_update`
  vs.
  `new_item`
  und gegen den
  `operation_mode`
  nach,
  statt die Ergebnisbedeutung nur still ueber Reparaturlogik zu tragen
- observability-seitig ist der neue Status jetzt im Call-2-Lauf sichtbar

Was Block 4 damit schon sichtbar leistet:

- die aktuelle Runtime kann den Extraktionsausgang kleiner und ehrlicher
  lesen,
  ohne schon den grossen Werkzeugkasten oder Confirmation vorzuziehen
- zwischen
  `Call 2 lief`
  und
  `was bedeutet dieses Ergebnis fuer den Fall?`
  liegt jetzt eine erste explizite Vertragskante
- der spaetere Pfad
  `Extraktion ohne relevanten Fallzuwachs`
  vs.
  `Update bestehender Information`
  vs.
  `echte Fall-Erweiterung`
  ist nicht mehr nur implizite Wunschlesart

Was fuer Block 4 noch offen bleibt:

- der neue Status wird bisher vor allem als explizitere Ergebnislesart und
  Observability genutzt;
  die eigentliche Merge-Kante liest ihn noch nicht als ruhige eigene kleine
  Runtime-Policy mit
- die Startentscheidung
  wann `Call 2` wirklich laufen soll
  ist damit noch nicht grundsaetzlich neu geschnitten;
  sie haengt weiter primaer an
  `extraction_required`
  plus
  `operation_mode` und `tasks`
- die Runtime arbeitet weiter mit der Uebergangskette
  `Call2ExtractionResult -> ExtractionResult -> CaseUpdateBridge`,
  auch wenn diese Kette jetzt in ihrer Ergebnisbedeutung etwas klarer
  geworden ist
- die Truth-write-Schwelle ist noch nicht als ruhigere eigene Vertragskante
  voll eingelost;
  aktuell ist nur ihre Vorstufe expliziter lesbar

Vorlaeufige Block-4-Einordnung:

- Block 4 ist jetzt nicht mehr nur vorbereitet,
  sondern praktisch begonnen
- sein erster sinnvoller Kernschnitt
  "Call-2-Ergebnis vor dem Merge expliziter lesbar machen"
  ist im aktiven Code angekommen
- der Block-Gate ist aber noch deutlich offen,
  weil die Merge-/Truth-Kante und die eigentliche Call-2-Startstrategie noch
  nicht entsprechend ruhig nachgezogen sind

Naechster sinnvoller Schritt aus diesem Stand:

- die neue Ergebnislesart nicht sofort ueberdehnen,
  sondern jetzt gezielt pruefen,
  wo die Merge-Kante dieses Signal nur mitlesen
  oder bereits in kleinen Guards gegen unnoetige Fallfortschreibung
  verwenden sollte
- parallel im Blick behalten,
  ob weitere reale Fehlpfade eher von zu breitem
  `Call 2`-Start
  oder von noch unruhiger Merge-Fortschreibung kommen

## Ziel

Nicht den vollen spaeteren Werkzeugkasten sofort bauen,
sondern Call 2 wieder zu einer kleinen,
ehrlichen und weniger stoerenden Runtime-Rolle machen.

## Warum hier

Nach Block 1 bis 3 wird deutlicher sichtbar,
welche Extraktionspfade das System ueberhaupt wirklich braucht,
und welche nur wegen frueherer Abschluss-/Readiness-Verwirrung mitliefen.

## Sollzustand

Call 2 ist als minimales Runtime-Werkzeug sauberer lesbar:

- optional
- nur bei echter tieferer medizinischer Arbeit
- mit kleinem Kontext
- mit kleinerem Output
- ohne Rueckkehr zur breiten Fallzweitwahrheit

Wichtig:

- V5 will hier noch nicht die volle Enddynamik
- V5 will den Runtime-Vertrag so weit fertigziehen,
  dass er Response und Freigabelogik nicht weiter stoert

## Wichtige Fragen

1. welche Call-2-Aufgaben muessen im aktuellen System wirklich jetzt stabil
   laufen
2. welche Teile des vorhandenen Werkzeugkastenbilds sind schon ausreichend
3. welche Uebergangsadaptionen duerfen vorerst noch bleiben
4. wie wird die Truth-write-Schwelle ehrlicher lesbar

## Leitplanken

- keine Wiedereinfuhrung breiter Summaries als Abkuerzung
- kein "intelligenterer" Einheits-Call als Ersatz fuer saubere Freigabelogik
- keine neue nachgelagerte Reparaturmagie in Mappern oder Texten

## Kernaufgaben

1. minimalen aktuellen Call-2-Runtime-Vertrag neu gegen Block 1 bis 3 lesen
2. klar halten:
   `focus_update`,
   `new_items`,
   optionale weitere kleine Aufgaben
3. den Pfad
   `keine Extraktion`
   vs.
   `Extraktion ohne Truth-Write`
   vs.
   `Extraktion mit Truth-Write`
   runtime-seitig sauberer machen
4. die heutige Truth-write-Schwelle expliziter benennen oder enger
   vertraglich fassen

## Betroffene Dateien/Klassen

- `llm/context.py`
- `llm/prompts/case_extraction.py`
- `application/managers/extraction_manager.py`
- `application/services/resilient_extraction_service.py`
- `application/services/extraction_result_mapper.py`
- `models/extraction/result.py`
- `application/managers/case_state_manager.py`

## Nicht innerhalb dieses Blocks still loesen

- vollen dynamischen Werkzeugkasten
- Recommendation-Inhalt
- concern-Semantik in Call 2 selbst hineinziehen

## Block-Gate / Done

- Call 2 stoert den oberen Fluss weniger
- seine Runtime-Rolle ist kleiner und ehrlicher
- die grobe Drift durch unnoetige Extraktionsstarts wird kleiner


## Arbeitsregel fuer Block 3 und 4

Nach Block 1 und 2 sollen Block 3 und 4 bewusst in kurzen Schleifen
bearbeitet werden.

Empfohlene Schleife:

1. Freigabe- und Antwortkante pruefen
2. sichtbaren Fehlpfad identifizieren
3. nur den noetigen Response- oder Call-2-Nachschnitt machen
4. erneut gegen den Gesamtpfad
   `Nachricht -> Verarbeitung -> Antwort -> naechste Nachricht`
   pruefen

Wichtig:

- nicht in einem der beiden Bloecke allein "perfekt werden" wollen
- beide solange gegeneinander glatten,
  bis das Framework wieder sauberer traegt

### Wichtiger Zwischenpfad fuer die Praxis

Wenn die expliziten Runtime-Vertraege vorne und hinten zwar klarer werden,
die sichtbare Gespraechsfuehrung aber weiter zu stumpf bleibt,
kann als bewusster Entstau-Schritt temporaer eine
`bounded master prompt response lane`
sinnvoll sein.

Gemeint ist:

- ein staerkerer LLM-Antwortpfad auf Basis des historischen
  `MASTER_PROMPT`
- aber nicht als Rueckkehr zum unkontrollierten Voll-Chat
- sondern als begrenzte Gespraechsfuehrungs-Schicht unter
  Concern-,
  Gate-,
  Safety-
  und harten Runtime-Grenzen

Diese Lane darf:

- natuerlicher formulieren
- gezieltere Rueckfragen stellen
- das Nutzeranliegen sprachlich besser tragen

Sie soll nicht:

- medizinische Wahrheit festlegen
- Recommendation eigenmaechtig freigeben
- die expliziten Runtime-Vertraege wieder unsichtbar machen

Wichtige Lesart:

- dieser Zwischenpfad ist kein Gegenmodell zu V5
- er ist eine temporaere Stabilisierungsbruecke,
  damit die weitere Refactor-Arbeit nicht auf einer zu stumpfen
  Antwortschicht aufsetzt


## Block 5: Call 2 vom minimalen Runtime-Werkzeug zum echten Werkzeugkasten weiterziehen [spaeter, nach Stabilisierung]

## Ziel

Erst nach stabilerer concern-,
Freigabe-
und Response-Lage
den schon vorbereiteten Werkzeugkasten wirklich dynamischer machen.

## Warum spaeter

Der volle Mehrwert liegt hier erst dann,
wenn das System schon wieder auf stabileren oberen Kanten laeuft.

## Sollzustand

- Aufgabenbereiche werden dynamischer komponiert
- `operation_mode` und `tasks` arbeiten als echter Kasten
- neue Werkzeuge koennen andocken,
  ohne Call 2 wieder zu vergroessern

## Block-Gate / Done

- Werkzeugkasten-Idee ist praktisch und nicht nur rhetorisch realer


## Block 6: Recommendation-Inhalt erst nach stabilerer Freigabelage ausbauen [spaeter]

## Ziel

Recommendation-Freigabe und Recommendation-Inhalt sauber getrennt halten
und den Inhalt erst dann ausbauen,
wenn die Zugangslogik wirklich stabiler ist.

## Block-Gate / Done

- Recommendation bleibt ein gestufter Pfad
- Inhaltsausbau baut nicht auf noch weichen Freigabekanten


## Block 7: Safety, Confirmation und Rename-Nachschnitt bewusst spaeter halten [spaeter]

## Ziel

Diese Themen nicht vergessen,
aber den aktuellen Kernknoten nicht wieder verwischen.

## Begruendung

- Safety ist real,
  aber nicht der schnellste Hebel fuer die heutige Framework-Stabilisierung
- Confirmation braucht stabilere Truth- und Freigabepfade
- Rename lohnt erst auf ruhigeren Rollen


## Konkrete Startempfehlung fuer V5

Der erste praktische Schritt fuer V5 ist nicht:

- sofort mehr freie KI-Antwort
- sofort den ganzen Werkzeugkasten finalisieren
- sofort Recommendation tiefer bauen

Sondern:

1. die minimalen concern-/Fortschrittsfragen explizit aufschreiben,
   die das System kuenftig beantworten koennen muss
2. diese Fragen gegen
   `primary_focus`,
   `Readiness`,
   Abschlussknoten
   und aktuelle Response-Pfade halten
3. daraus eine kleine Freigabelesart ableiten
4. erst dann die sichtbaren Response-Pfade und den minimalen Call-2-
   Runtime-Vertrag in kurzen Schleifen daran ausrichten


## Schlussbewertung

V5 liest die Lage weder als reines Response-Problem
noch als reines Call-2-Problem.

V5 liest sie als fehlende semantische Klammer zwischen:

- aktuellem Nutzeranliegen
- medizinischer Wahrheit
- concern-nahem Fortschritt
- `Readiness`
- Freigabelogik
- Antwortpfaden

Der wichtigste neue Merksatz lautet deshalb:

- nicht zuerst noch klueger extrahieren
- nicht zuerst nur Antworten verschoenern
- sondern zuerst minimal klarziehen,
  woran Careena fuer das aktuelle Anliegen eigentlich Fortschritt,
  Abschlussnaehe
  und Freigabe festmacht

Wenn dieser Schritt gelingt,
koennen Response und Call 2 wieder an demselben System arbeiten
statt an zwei halben Bildern davon.
